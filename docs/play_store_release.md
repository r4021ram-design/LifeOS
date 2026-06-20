# Play Store Release & Keystore Guide – LifeOS AI Mobile App

This guide outlines the steps needed to generate a release Keystore, compile a signed Android App Bundle (AAB) or APK, and publish the application on the Google Play Store.

---

## 1. Generating a Release Keystore

The Google Play Store requires every uploaded app bundle to be signed with a digital certificate.

Run the following command in your terminal to generate a secure keystore file:

```bash
keytool -genkey -v -keystore lifeos-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias lifeos-alias
```

* **Important Prompts:**
  * Enter a secure password (and write it down somewhere safe!).
  * Enter your name, organization details, and country code.
* **Warning:** Save the `lifeos-release-key.jks` file securely. If you lose this file, you will not be able to push updates to your application on the Play Store. Do **NOT** commit this keystore file or passwords to version control.

---

## 2. Configuring Gradle Release Signing (Optional)

To automate signing in your Gradle configuration, copy `lifeos-release-key.jks` into `android/app/` and edit your `android/app/build.gradle` file:

```gradle
android {
    ...
    signingConfigs {
        release {
            storeFile file("lifeos-release-key.jks")
            storePassword System.getenv("PLAY_STORE_KEYSTORE_PASSWORD") ?: "YOUR_KEYSTORE_PASSWORD"
            keyAlias "lifeos-alias"
            keyPassword System.getenv("PLAY_STORE_KEY_PASSWORD") ?: "YOUR_KEY_PASSWORD"
        }
    }
    buildTypes {
        release {
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
            signingConfig signingConfigs.release
        }
    }
}
```

---

## 3. Creating Signed Builds

### A. Generating a Release AAB (Android App Bundle)
The AAB format is required for all new apps submitted to the Google Play Store.

1. Build the production bundle:
   ```bash
   cd frontend
   npm run build
   npx cap sync android
   ```
2. Open the project in Android Studio:
   ```bash
   npx cap open android
   ```
3. In the Android Studio toolbar, go to **Build > Generate Signed Bundle / APK**.
4. Select **Android App Bundle** and click **Next**.
5. Select your Keystore Path (`lifeos-release-key.jks`), enter your password details, choose the alias `lifeos-alias`, and enter the key password.
6. Click **Next**, choose destination folder, select **release** build type, and click **Create**.
7. The output `.aab` file will be generated in:
   `android/app/release/app-release.aab`

### B. Generating a Signed APK (For Direct Install / Sideloading)
To generate an installable `.apk` file for physical testing without using the App Store:

1. Follow the same steps as above, but select **APK** instead of **Android App Bundle**.
2. Alternatively, run the following CLI command in the `android/` directory:
   ```bash
   ./gradlew assembleRelease
   ```
3. The output `.apk` file will be generated in:
   `android/app/build/outputs/apk/release/app-release.apk`
4. Copy this file to any Android device to sideload and test it.

---

## 4. Google Play Console Setup & Submission

1. **Create developer account:** Create a developer account at [Google Play Console](https://play.google.com/console) (requires a $25 one-time registration fee).
2. **Create New App:**
   * Click **Create app**.
   * App name: `LifeOS AI`.
   * Default language: `English (United States)` (or your preferred default).
   * App type: `App`.
   * Free or Paid: `Free`.
3. **Privacy Policy Link:**
   * Google Play requires you to host a public Privacy Policy URL.
   * Host a privacy policy page on your main web portal (e.g. `https://lifeos-production.up.railway.app/privacy-policy`).
   * Add the URL inside Play Console under **Policy and programmes > App content**.
4. **App Content Questionnaire:**
   * Fill out the target audience questionnaires (e.g., target age 18+).
   * Declare permissions: declare that the app uses internet connectivity, biometrics, and push notification access.
5. **Store Listing Assets:**
   * **App Icon:** 512 x 512 pixels, 32-bit PNG format (max 1MB).
   * **Feature Graphic:** 1024 x 500 pixels, PNG format.
   * **Screenshots:** At least 2-4 screenshots of the app UI. Provide screenshots representing a phone (16:9 or 9:16 aspect ratio) and tablet if supported.
6. **Closed Testing Track:**
   * Under **Release > Testing > Closed testing**, click **Create track**.
   * Set up a release name, upload your compiled signed `app-release.aab` bundle.
   * Add test user email addresses under the **Testers** tab.
   * Submit the release for review. Once Google approves the review (typically takes 1-3 days), testers can download the app via a private link.
