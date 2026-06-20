import { NativeBiometric } from '@capgo/capacitor-native-biometric';
import { Capacitor } from '@capacitor/core';

export class BiometricService {
  private static serviceName = 'com.lifeos.app';

  /**
   * Checks if biometric hardware is available and enrolled.
   */
  public static async isAvailable(): Promise<boolean> {
    if (!Capacitor.isNativePlatform()) return false;
    try {
      const result = await NativeBiometric.isAvailable();
      return !!result.isAvailable;
    } catch (error) {
      console.error('Biometrics check failed:', error);
      return false;
    }
  }

  /**
   * Verifies the user's identity using Face ID or Fingerprint.
   */
  public static async verifyIdentity(): Promise<boolean> {
    if (!Capacitor.isNativePlatform()) return false;
    try {
      await NativeBiometric.verifyIdentity({
        reason: 'Authenticate to access your LifeOS AI planner',
        title: 'Biometric Login',
        subtitle: 'Log in with Face ID or Fingerprint',
        description: 'Please scan your fingerprint or face to authenticate.',
      });
      return true;
    } catch (error) {
      console.error('Biometric authentication failed:', error);
      return false;
    }
  }

  /**
   * Securely saves the login credentials (JWT token as password) inside the device KeyStore/Keychain.
   */
  public static async saveCredentials(email: string, token: string): Promise<boolean> {
    if (!Capacitor.isNativePlatform()) return false;
    try {
      await NativeBiometric.setCredentials({
        username: email,
        password: token,
        server: this.serviceName,
      });
      return true;
    } catch (error) {
      console.error('Failed to save biometric credentials:', error);
      return false;
    }
  }

  /**
   * Retrieves the securely stored JWT token using biometric verification.
   */
  public static async getStoredToken(email: string): Promise<string | null> {
    if (!Capacitor.isNativePlatform()) return null;
    try {
      const verified = await this.verifyIdentity();
      if (!verified) return null;

      const credentials = await NativeBiometric.getCredentials({
        server: this.serviceName,
      });
      
      if (credentials && credentials.username === email) {
        return credentials.password;
      }
      return null;
    } catch (error) {
      console.error('Failed to retrieve biometric credentials:', error);
      return null;
    }
  }

  /**
   * Deletes securely stored biometric credentials.
   */
  public static async clearCredentials(): Promise<boolean> {
    if (!Capacitor.isNativePlatform()) return false;
    try {
      await NativeBiometric.deleteCredentials({
        server: this.serviceName,
      });
      return true;
    } catch (error) {
      console.error('Failed to delete biometric credentials:', error);
      return false;
    }
  }
}
