# Firebase Integration Guide – LifeOS AI Mobile App

This guide explains how to set up Firebase Cloud Messaging (FCM) to handle push notifications on Android and iOS devices.

---

## 1. Firebase Console Project Configuration

1. Go to the [Firebase Console](https://console.firebase.google.com/).
2. Click **Add Project** and create a project named `LifeOS AI`.
3. Disable or enable Google Analytics according to your preference, then click **Create Project**.

---

## 2. Android App Registration & Config File

1. In your Firebase Project Overview page, click the **Android icon** to register a new application.
2. Enter the Package Name: `com.lifeos.app` (must match the appId in `capacitor.config.ts`).
3. Enter an optional App nickname: `LifeOS AI Android`.
4. Click **Register App**.
5. Download the `google-services.json` file.
6. Copy the `google-services.json` file into:
   `frontend/android/app/google-services.json`
7. In the Firebase console, complete the steps and exit.

---

## 3. iOS App Registration & Config File

1. In your Firebase Project Overview, click **Add App** and select **iOS**.
2. Enter the iOS Bundle ID: `com.lifeos.app` (must match the appId in `capacitor.config.ts`).
3. Enter an optional App nickname: `LifeOS AI iOS`.
4. Click **Register App**.
5. Download the `GoogleService-Info.plist` file.
6. Open Xcode (`npx cap open ios`), right-click the **App** folder in the left-hand project navigator, click **Add Files to "App"...**, select `GoogleService-Info.plist`, ensure "Copy items if needed" is checked, and click **Add**.
7. In the Firebase console, complete the steps and exit.

---

## 4. Configuring iOS APNs Certificates on Firebase

To send push notifications to iOS devices, Firebase needs to communicate with Apple's APNs server.

1. Log into your [Apple Developer Account](https://developer.apple.com/).
2. Go to **Certificates, Identifiers & Profiles > Keys**.
3. Create a new Key, check **Apple Push Notifications service (APNs)**, and download the `.p8` key file. Note your **Key ID** and **Team ID**.
4. Go back to the Firebase Console, open **Project Settings** (gear icon) > **Cloud Messaging** tab.
5. Under **Apple app share configuration**, upload the downloaded `.p8` key file.
6. Enter your **Key ID** and **Team ID** and click **Upload**.

---

## 5. Firebase Native SDK Setup (Android Gradle changes)

Capacitor relies on the native Firebase SDK to retrieve FCM tokens. Update the Android project build scripts.

### A. Root `build.gradle`
Open `android/build.gradle` and add the google-services dependency to the classpath:
```gradle
buildscript {
    dependencies {
        // ...
        classpath 'com.google.gms:google-services:4.4.1'
    }
}
```

### B. App-Level `build.gradle`
Open `android/app/build.gradle` and apply the plugin at the bottom:
```gradle
apply plugin: 'com.android.application'
apply plugin: 'com.google.gms.google-services' // Add this line
```

---

## 6. How to Test Push Notifications

Once you have initialized the push notification service, compile and run the app. It will register with FCM, print a token to the console logs, and register it to the backend via POST `/auth/device-token`.

### Sample Backend Push Notification Script (Python)
You can use the following backend script to test push notifications using the FCM SDK:

```python
import firebase_admin
from firebase_admin import credentials, messaging

# Initialize Firebase admin SDK
# Obtain serviceAccountKey.json from Firebase Console Settings > Service Accounts
cred = credentials.Certificate("path/to/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

def send_push_notification(token, title, body, route=None):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data={
            "route": route or "dashboard", # deep link routing slug
        },
        token=token,
    )
    
    response = messaging.send(message)
    print("Successfully sent message:", response)

# Replace with the device token registered in your FastAPI database
test_token = "FCM_DEVICE_TOKEN_RECEIVED_FROM_MOBILE_APP"
send_push_notification(
    token=test_token,
    title="LifeOS AI Alert",
    body="Your Solar Sandhya Muhurat has started. Review today's journal.",
    route="dashboard"
)
```
