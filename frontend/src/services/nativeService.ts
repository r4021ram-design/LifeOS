import { SecureStorage } from '@aparajita/capacitor-secure-storage';
import { App } from '@capacitor/app';
import { Keyboard } from '@capacitor/keyboard';
import { Capacitor } from '@capacitor/core';
import { BiometricService } from './biometricService';
import { PushNotificationService } from './pushNotificationService';
import { OfflineSyncService } from './offlineSyncService';
import { DeepLinkRouter } from './DeepLinkRouter';

export class NativeService {
  /**
   * Initializes all required native mobile capabilities: SQLite, FCM, keyboard listeners.
   */
  public static async initialize(authToken: string | null): Promise<{ pushAvailable: boolean }> {
    let pushAvailable = false;
    if (!Capacitor.isNativePlatform()) return { pushAvailable };

    try {
      // 1. Initialize SQLite Database
      await OfflineSyncService.init();

      // 2. Initialize Push Notifications (FCM)
      if (authToken) {
        pushAvailable = await PushNotificationService.init(authToken);
      }

      // 3. Configure Keyboard Native listeners
      if (Capacitor.getPlatform() === 'android') {
        Keyboard.addListener('keyboardDidShow', (info) => {
          console.log('Keyboard did show with height:', info.keyboardHeight);
          document.body.classList.add('keyboard-open');
        });

        Keyboard.addListener('keyboardDidHide', () => {
          console.log('Keyboard did hide');
          document.body.classList.remove('keyboard-open');
        });
      } else {
        Keyboard.addListener('keyboardWillShow', (info) => {
          console.log('Keyboard will show with height:', info.keyboardHeight);
          document.body.classList.add('keyboard-open');
        });

        Keyboard.addListener('keyboardWillHide', () => {
          console.log('Keyboard will hide');
          document.body.classList.remove('keyboard-open');
        });
      }

    } catch (error) {
      console.error('Failed to initialize Native Services:', error);
    }
    return { pushAvailable };
  }

  /**
   * Sets up native hardware back button handler to close modals or exit the application.
   */
  public static registerBackButtonHandler(closeActiveDialogs: () => boolean): void {
    if (!Capacitor.isNativePlatform()) return;

    App.addListener('backButton', (data) => {
      // Try to close active modals / drawers first
      const wasClosed = closeActiveDialogs();
      if (!wasClosed) {
        if (data.canGoBack) {
          window.history.back();
        } else {
          // Exit the app if no history and no open modals
          App.exitApp();
        }
      }
    });
  }

  /**
   * Registers a deep link handler to navigate to specific tabs or routes.
   */
  public static registerDeepLinkHandler(): void {
    if (!Capacitor.isNativePlatform()) return;

    App.addListener('appUrlOpen', (event) => {
      const url = event.url;
      console.log('App opened with URL:', url);
      DeepLinkRouter.handleUrl(url);
    });
  }

  /**
   * Securely saves sensitive data (like JWT tokens) inside iOS Keychain or Android Keystore.
   */
  public static async setSecureItem(key: string, value: string): Promise<boolean> {
    if (!Capacitor.isNativePlatform()) {
      localStorage.setItem(key, value);
      return true;
    }
    try {
      await SecureStorage.set(key, value);
      return true;
    } catch (error) {
      console.error(`SecureStorage failed to save key ${key}:`, error);
      return false;
    }
  }

  /**
   * Retrieves securely stored data.
   */
  public static async getSecureItem(key: string): Promise<string | null> {
    if (!Capacitor.isNativePlatform()) {
      return localStorage.getItem(key);
    }
    try {
      const result = await SecureStorage.get(key);
      return result as string | null;
    } catch (error) {
      console.error(`SecureStorage failed to get key ${key}:`, error);
      return null;
    }
  }

  /**
   * Deletes securely stored data.
   */
  public static async removeSecureItem(key: string): Promise<boolean> {
    if (!Capacitor.isNativePlatform()) {
      localStorage.removeItem(key);
      return true;
    }
    try {
      await SecureStorage.remove(key);
      return true;
    } catch (error) {
      console.error(`SecureStorage failed to remove key ${key}:`, error);
      return false;
    }
  }
}
export { BiometricService, PushNotificationService, OfflineSyncService };
