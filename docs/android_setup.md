# Android Setup Guide – LifeOS AI Mobile App

This guide walks you through setting up the local Android development environment, configuring native permissions, adding home screen widget configurations, defining app shortcuts, and deploying the app.

---

## 1. Prerequisites & Environment Setup

Ensure you have the following installed on your system:
* **Java Development Kit (JDK):** JDK 17 (recommended for Gradle build compatibility). Set your `JAVA_HOME` environment variable to point to your JDK installation.
* **Android Studio:** Download and install the latest stable version.
* **Android SDK:** Open Android Studio, go to the SDK Manager, and install:
  * Android SDK Platform 34 (API Level 34) or higher.
  * Android SDK Build-Tools.
  * Android Emulator (for local testing if you don't use a physical device).
* **Android Home Environment Variables:**
  * Add the following to your environment variables:
    * `ANDROID_HOME` = `C:\Users\<username>\AppData\Local\Android\Sdk` (or your custom SDK install path).
    * Add `%ANDROID_HOME%\platform-tools` and `%ANDROID_HOME%\emulator` to your system `PATH`.

---

## 2. Opening the Android Project

1. Build the production web assets:
   ```bash
   cd frontend
   npm run build
   ```
2. Sync the compiled assets and Capacitor configuration with the Android project:
   ```bash
   npx cap sync android
   ```
3. Open the Android project in Android Studio:
   ```bash
   npx cap open android
   ```

---

## 3. Native Permissions & AndroidManifest Configuration

To support Biometrics, Push Notifications, Internet connectivity, and Deep Linking, update the `android/app/src/main/AndroidManifest.xml` file.

Open `android/app/src/main/AndroidManifest.xml` and verify or add the following configurations:

### A. Add Permissions
Add these permissions inside the `<manifest>` tag, above the `<application>` tag:

```xml
<!-- Internet & Network State -->
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

<!-- Biometric Login (Face Unlock / Fingerprint) -->
<uses-permission android:name="android.permission.USE_BIOMETRIC" />
<uses-permission android:name="android.permission.USE_FINGERPRINT" />

<!-- Push Notifications (FCM) -->
<uses-permission android:name="android.permission.WAKE_LOCK" />
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
<uses-permission android:name="com.google.android.c2dm.permission.RECEIVE" />
```

### B. Deep Links Configuration
Add an `<intent-filter>` inside the main `<activity>` block to handle deep links (`lifeos://app/*`):

```xml
<intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="lifeos" android:host="app" />
</intent-filter>
```

---

## 4. Android Enhancements

### A. App Shortcuts (Static & Dynamic)
App shortcuts allow users to long-press the app icon and instantly jump into a specific feature.

1. Create a file named `shortcuts.xml` in `android/app/src/main/res/xml/shortcuts.xml`:
   ```xml
   <?xml version="1.0" encoding="utf-8"?>
   <shortcuts xmlns:android="http://schemas.android.com/apk/res/android">
       <shortcut
           android:shortcutId="quick_task"
           android:enabled="true"
           android:icon="@drawable/ic_shortcut_task"
           android:shortcutShortLabel="@string/shortcut_task_short"
           android:shortcutLongLabel="@string/shortcut_task_long">
           <intent
               android:action="android.intent.action.VIEW"
               android:targetPackage="com.lifeos.app"
               android:targetClass="com.lifeos.app.MainActivity"
               android:data="lifeos://app/tasks" />
       </shortcut>
       <shortcut
           android:shortcutId="ai_assistant"
           android:enabled="true"
           android:icon="@drawable/ic_shortcut_ai"
           android:shortcutShortLabel="@string/shortcut_ai_short"
           android:shortcutLongLabel="@string/shortcut_ai_long">
           <intent
               android:action="android.intent.action.VIEW"
               android:targetPackage="com.lifeos.app"
               android:targetClass="com.lifeos.app.MainActivity"
               android:data="lifeos://app/ai" />
       </shortcut>
   </shortcuts>
   ```
2. Reference the shortcuts file inside the main activity of your `AndroidManifest.xml`:
   ```xml
   <meta-data android:name="android.app.shortcuts" android:resource="@xml/shortcuts" />
   ```

### B. Home Screen Widget Setup
To add a Home Screen Widget showing today's tasks and Panchanag focus:

1. In Android Studio, right-click your app folder, choose **New > Widget > App Widget**.
2. Specify the Widget properties (e.g., 4x2 grid size, name it `LifeOSWidget`).
3. The setup will automatically create:
   * `LifeOSWidget.java` (extending `AppWidgetProvider`) inside `app/src/main/java/com/lifeos/app/`.
   * `life_o_s_widget_info.xml` inside `app/src/main/res/xml/`.
   * Layout XML layouts for your widget inside `app/src/main/res/layout/`.
4. Update `LifeOSWidget.java` to fetch data from the SQLite local DB (`lifeos_local_db`) or call the REST API, updating the layout's `RemoteViews` with local tasks.

### C. Share Intent (Share into LifeOS)
To allow other apps to share text or URLs into LifeOS (e.g., sharing a web article to a Quick Note):

1. Install the Capacitor Share Intent plugin or handle standard share intents in `MainActivity.java`:
   ```java
   // MainActivity.java
   package com.lifeos.app;
   import android.content.Intent;
   import android.os.Bundle;
   import com.getcapacitor.BridgeActivity;

   public class MainActivity extends BridgeActivity {
       @Override
       protected void onCreate(Bundle savedInstanceState) {
           super.onCreate(savedInstanceState);
           handleShareIntent(getIntent());
       }

       @Override
       protected void onNewIntent(Intent intent) {
           super.onNewIntent(intent);
           handleShareIntent(intent);
       }

       private void handleShareIntent(Intent intent) {
           String action = intent.getAction();
           String type = intent.getType();

           if (Intent.ACTION_SEND.equals(action) && type != null) {
               if ("text/plain".equals(type)) {
                   String sharedText = intent.getStringExtra(Intent.EXTRA_TEXT);
                   if (sharedText != null) {
                       // Pass sharedText to the web layer via a custom JS event or direct bridge URL
                       this.getBridge().triggerJSEvent("shareIntoApp", "window", "{ \"text\": \"" + sharedText + "\" }");
                   }
               }
           }
       }
   }
   ```
2. Register the send intent filter in your `AndroidManifest.xml` activity block:
   ```xml
   <intent-filter>
       <action android:name="android.intent.action.SEND" />
       <category android:name="android.intent.category.DEFAULT" />
       <data android:mimeType="text/plain" />
   </intent-filter>
   ```

---

## 5. Development Build & Deployment

* **Run on Physical Device/Emulator:**
  Run the following command to compile the app and run it directly on an active device/emulator:
  ```bash
  npx cap run android
  ```
  Alternatively, open Android Studio and click the green **Run** button to launch it.
