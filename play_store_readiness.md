# LifeOS AI – Google Play Store Readiness & Release Audit

**Audit Status:** **REJECTED (Critical Build & Manifest Blockers)**

Before we can upload the LifeOS AI Android App Bundle (AAB) to Google Play Console for Closed Testing, we must resolve a series of compilation and manifest-level requirements.

---

## 1. Google Play Console Compliance Matrix

| Requirement | Target Standard | Current Status | Notes / Actions Needed |
|---|---|---|---|
| **Target SDK Version** | API Level 34+ (Android 14) | **PASS** | Set to `34` in `variables.gradle`. |
| **Release Package Format** | Android App Bundle (`.aab`) | **PENDING** | Currently only compiling debug APKs. |
| **Keystore Signing** | Release Key with RSA 2048 | **MISSING** | No production Keystore file exists. |
| **Privacy Policy Link** | Public URL hosted externally | **MISSING** | Need to host and configure privacy link. |
| **Google Services Config** | `google-services.json` | **MISSING** | Required for FCM push notifications initialization. |
| **Application ID** | Unique DNS string | **PASS** | Registered as `com.lifeos.app`. |

---

## 2. Release Blockers Checklist (Google Play Console Requirements)

### Blocker 1: Missing Release Keystore and Signing Config
* **Description:** A release Keystore is not defined or declared. The application currently compiles with the auto-generated debug certificate.
* **Impact:** Google Play Console will reject the application package because it is signed with a debug key.
* **Action Required:**
  1. Generate a production signing key:
     ```bash
     keytool -genkey -v -keystore lifeos-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias lifeos-alias
     ```
  2. Configure Gradle release signing configs inside `android/app/build.gradle`.

### Blocker 2: Missing Firebase Configuration File (`google-services.json`)
* **Description:** The `google-services.json` configuration file is missing from the `frontend/android/app/` folder.
* **Impact:** The build logs show the Google Services plugin is skipped. At runtime on a physical device, push notification registration will throw a connection exception because the Firebase API credentials are blank.
* **Action Required:** Create a project in Firebase Console, register the package `com.lifeos.app`, download the generated `google-services.json`, and place it in the `android/app/` directory.

### Blocker 3: Undeclared Permissions in Manifest
* **Description:** The required permissions for biometrics and push notifications are completely missing from `AndroidManifest.xml`.
* **Impact:** Android will restrict the app from interacting with biometric hardware or receiving notifications, leading to silent failures or security exceptions.
* **Action Required:** Inject the following permissions above the `<application>` block:
  ```xml
  <uses-permission android:name="android.permission.USE_BIOMETRIC" />
  <uses-permission android:name="android.permission.USE_FINGERPRINT" />
  <uses-permission android:name="android.permission.WAKE_LOCK" />
  <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
  ```

### Blocker 4: Missing App Shortcut XML File
* **Description:** The application metadata in `AndroidManifest.xml` references `@xml/shortcuts`, but there is no `shortcuts.xml` in `android/app/src/main/res/xml`.
* **Impact:** The app compilation will fail if shortcut metadata is referenced without compiling the corresponding resource XML.
* **Action Required:** Generate `shortcuts.xml` in the resources path defining shortcuts for `quick_task` and `ai_assistant`.

---

## 3. Recommended Roadmap for Closed Testing Release

1. **Step 1:** Add all required permission tags, intent filters (deep link & share intent), and shortcuts metadata directly into `AndroidManifest.xml`.
2. **Step 2:** Generate the release keystore `lifeos-release-key.jks`, copy it into `android/app/`, and update the `build.gradle` file to sign release builds using the keystore.
3. **Step 3:** Download and place the `google-services.json` file inside `android/app/`.
4. **Step 4:** Compile the production release App Bundle (AAB):
   ```bash
   cd frontend
   npm run build
   npx cap sync android
   cd android
   $env:ANDROID_HOME = "C:\Users\admin\AppData\Local\Android\Sdk"; $env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"; .\gradlew.bat bundleRelease
   ```
5. **Step 5:** Upload the compiled AAB (`android/app/build/outputs/bundle/release/app-release.aab`) to the Closed Testing track in Google Play Console.
