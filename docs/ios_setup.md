# iOS Setup Guide – LifeOS AI Mobile App

This guide walks you through setting up the iOS development environment, configuring Xcode capabilities, managing plist permissions, and deploying the app.

---

## 1. Prerequisites & macOS Environment Setup

Ensure you have the following installed on your macOS machine:
* **Xcode:** Install Xcode from the Mac App Store.
* **Xcode Command Line Tools:** Install using terminal:
  ```bash
  xcode-select --install
  ```
* **CocoaPods:** Native iOS dependency manager. Install via Homebrew (recommended) or RubyGems:
  ```bash
  brew install cocoapods
  ```
  *(Alternative: `sudo gem install cocoapods`)*

---

## 2. Opening the iOS Project

1. Build the production web assets:
   ```bash
   cd frontend
   npm run build
   ```
2. Sync the compiled assets and Capacitor configuration with the iOS project:
   ```bash
   npx cap sync ios
   ```
3. Open the iOS project in Xcode:
   ```bash
   npx cap open ios
   ```

---

## 3. Configuring Capabilities & Entitlements in Xcode

Double-click on `App.xcworkspace` (or run `npx cap open ios`) to open Xcode. In the left navigator, select the **App** project file, then select the **App** target and open the **Signing & Capabilities** tab.

Add the following capabilities by clicking the **`+ Capability`** button in the top-left:

### A. Push Notifications
* Adds push notifications support required by the FCM plugin.
* Creates the `.entitlements` file and registers your app for APNs.

### B. Background Modes
* Check **Remote notifications** (allows FCM to wake the app for background processing).
* Check **Background fetch** (allows periodic background synchronization).

### C. Keychain Sharing
* Add **Keychain Sharing** to allow `@aparajita/capacitor-secure-storage` and `@capgo/capacitor-native-biometric` to securely cache values.

---

## 4. Info.plist Permissions Auditing

Open the `ios/App/App/Info.plist` file in Xcode (or edit it as raw XML). You must specify descriptions for all native hardware APIs that the app requests.

Add the following keys to your `Info.plist`:

### A. FaceID Permission
Add the description explaining why you require Face ID:
```xml
<key>NSFaceIDUsageDescription</key>
<string>LifeOS AI uses Face ID to securely authenticate you without typing your credentials.</string>
```

### B. Deep Linking URL Schemes
To enable custom deep links (`lifeos://`):
```xml
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLName</key>
        <string>com.lifeos.app</string>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>lifeos</string>
        </array>
    </dict>
</array>
```

---

## 5. Development Build & Deployment

* **Run on iOS Simulator / Physical Device:**
  You can run your app directly from the terminal:
  ```bash
  npx cap run ios
  ```
  Or select your target device (e.g., iPhone 15 Simulator or a connected physical iPhone) inside Xcode, then click the **Build and Run** (Play) button in the top-left toolbar.

---

## 6. TestFlight & App Store Preparation

1. **App Store Connect Account:** Ensure you are enrolled in the Apple Developer Program ($99/year).
2. **Bundle Identifier:** Ensure the bundle ID in Xcode matches your App ID (`com.lifeos.app`).
3. **Provisioning Profile:**
   * In Xcode, under **Signing & Capabilities**, select your developer team.
   * Enable **Automatically manage signing**.
4. **Archive Build:**
   * Select **Any iOS Device (arm64)** from the active schemes dropdown.
   * In Xcode menu, click **Product > Archive**.
   * Once the archive process completes, the Organizer window will appear.
5. **Upload to TestFlight:**
   * Click **Distribute App** in the Organizer.
   * Select **TestFlight & App Store** distribution.
   * Follow the prompts to sign and upload your IPA file.
   * Once uploaded, invite internal and external beta testers on App Store Connect.
