import { PushNotifications } from '@capacitor/push-notifications';
import { Capacitor } from '@capacitor/core';
import { API_BASE } from '../store/useLifeOSStore';
import { DeepLinkRouter } from './DeepLinkRouter';

export class PushNotificationService {
  /**
   * Initializes and registers push notification listeners.
   */
  public static async init(authToken: string | null): Promise<boolean> {
    if (!Capacitor.isNativePlatform()) return false;

    try {
      let permStatus = await PushNotifications.checkPermissions();
      
      if (permStatus.receive === 'prompt') {
        permStatus = await PushNotifications.requestPermissions();
      }

      if (permStatus.receive === 'granted') {
        // Register with Apple / Google to receive the FCM device token
        await PushNotifications.register();
        this.registerEventListeners(authToken);
        return true;
      } else {
        console.warn('Push notification permissions denied by user.');
        return false;
      }
    } catch (error) {
      console.error('Failed to initialize push notifications:', error);
      return false;
    }
  }

  /**
   * Listen to push events and register FCM tokens with the backend database.
   */
  private static registerEventListeners(authToken: string | null): void {
    // On successful registration, save the device token to the backend
    PushNotifications.addListener('registration', async (token) => {
      console.log('FCM Registration Token received:', token.value);
      if (authToken) {
        await this.sendTokenToBackend(token.value, authToken);
      }
    });

    // Handle registration errors
    PushNotifications.addListener('registrationError', (error: any) => {
      console.error('FCM Registration Error:', JSON.stringify(error));
    });

    // Handle push notification received when app is in foreground
    PushNotifications.addListener('pushNotificationReceived', (notification) => {
      console.log('Push notification received in foreground:', notification);
    });

    // Handle click actions on notifications (deep linking / actions)
    PushNotifications.addListener('pushNotificationActionPerformed', (notification) => {
      console.log('Push notification action performed:', notification);
      if (notification.notification.data && notification.notification.data.route) {
        const route = notification.notification.data.route;
        DeepLinkRouter.handleUrl(route);
      }
    });
  }

  /**
   * Sends the FCM device token to the FastAPI backend.
   */
  private static async sendTokenToBackend(token: string, authToken: string): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE}/devices/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({ 
          token: token,
          platform: 'android',
          device_name: 'Android Physical Device'
        })
      });
      return response.ok;
    } catch (error) {
      console.error('Failed to register FCM device token with backend:', error);
      return false;
    }
  }
}
