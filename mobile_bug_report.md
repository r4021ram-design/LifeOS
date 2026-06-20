# LifeOS AI – Mobile Bug & UX Audit Report

This report logs all layout, interaction, and system-level bugs found during physical device certification.

---

## 1. High-Priority Bugs (Functionality & Storage)

### Bug 1.1: Disconnected SQLite Database & Sync Queue
* **Severity:** High
* **Component:** `useLifeOSStore.ts` and `offlineSyncService.ts`
* **Description:** Offline CRUD operations in the Zustand store (tasks, notes, habits) only fall back to web `localStorage` and never enqueue actions into the native SQLite database (`lifeos_local_db`).
* **Impact:** The local SQLite database remains completely empty. Actions are never enqueued or replayed to the server when network is restored.
* **Resolution:** Update Zustand CRUD actions in the store to import `OfflineSyncService` and invoke `OfflineSyncService.enqueueAction` when offline fallback is triggered.

### Bug 1.2: Insecure JWT Storage (Security Risk)
* **Severity:** High
* **Component:** `useLifeOSStore.ts`
* **Description:** The JWT token is saved using plain `localStorage` on line 170.
* **Impact:** Mobile OSs frequently prune web-layer cache/storage when space is low. Additionally, `localStorage` is stored in plaintext on-device, which violates basic mobile security practices for authentication tokens.
* **Resolution:** Connect the login flow to `NativeService.setSecureItem('lifeos_token', token)` to store the token in the Android Keystore.

### Bug 1.3: Missing Offline Network Listener
* **Severity:** High
* **Component:** `App.tsx` / `nativeService.ts`
* **Description:** There are no active window event listeners listening for `'online'` state changes.
* **Impact:** If the user opens the app offline, then moves into network range, the app will not detect it is online and will not automatically sync the local queue.
* **Resolution:** Add a `window.addEventListener('online', ...)` block that triggers `OfflineSyncService.syncWithBackend(store.token)`.

---

## 2. Medium-Priority Bugs (Layout & Keyboard)

### Bug 2.1: Safe Area Layout Overlap (Notch Display Clipping)
* **Severity:** Medium
* **Component:** `App.tsx` (Mobile Header)
* **Description:** The mobile header (`<header>` element on line 682) is styled with `h-14` but lacks the `safe-top` padding utility.
* **Impact:** On notch/punch-hole Android devices, the header title ("LifeOS AI") and the Search button bleed directly into the status bar and overlap with system clock/notifications.
* **Resolution:** Add the `safe-top` class (which applies `padding-top: env(safe-area-inset-top)`) and remove the fixed `h-14` height constraints.

### Bug 2.2: Mobile Navigation Squash on Notch Devices
* **Severity:** Medium
* **Component:** `App.tsx` (Mobile Navigation Bar)
* **Description:** The bottom navigation container (`<nav>` element on line 1987) uses both `h-16` (fixed height) and `safe-bottom` (adds safe area padding).
* **Impact:** When running on devices with a software navigation bar/pill, the safe area bottom padding pushes the icons upward, but because of the fixed `h-16` height, the text label is compressed out of view or overlapping.
* **Resolution:** Replace `h-16` with `min-h-[4rem]` and manage padding-bottom explicitly using the safe area inset.

### Bug 2.3: Keyboard Event Listener Mismatch (Android)
* **Severity:** Medium
* **Component:** `nativeService.ts`
* **Description:** Native listeners in `nativeService.ts` listen for `'keyboardWillShow'` and `'keyboardWillHide'` on lines 26-34.
* **Impact:** Android does not trigger `keyboardWillShow`/`keyboardWillHide` (which are iOS-specific). Consequently, keyboard state changes are never intercepted on Android devices, and `.keyboard-open` is never added to the body.
* **Resolution:** Use `keyboardDidShow` and `keyboardDidHide` on Android platforms.

---

## 3. Low-Priority Bugs (Aesthetics & Touch Targets)

### Bug 3.1: Sub-44px Touch Targets
* **Severity:** Low
* **Component:** `App.tsx` (Task Checklist and Badges)
* **Description:** Checklist tick boxes (`w-6 h-6`, equivalent to `24x24px`) and inline priority badges in the Task Registry fall below the standard WCAG AA touch target threshold of `44x44px`.
* **Impact:** Accidental clicks and frustrating navigation for mobile touch users.
* **Resolution:** Apply the `.touch-target` helper class or increase padding around interactive items.
