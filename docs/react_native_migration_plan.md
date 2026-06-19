# React Native Migration Plan (Phase 2 Native App Strategy)

This document presents the architectural roadmap to port LifeOS AI to native mobile platforms (iOS and Android) using React Native, maximizing code reuse between web and mobile.

## 1. Code Sharing Architecture

To preserve development velocity, we will establish a monorepo workspace (e.g., using turborepo or yarn workspaces) separating core business logic from target-specific UI presentation layers:

```text
packages/
  ├── core/               # Shared business logic
  │    ├── store/         # Zustand state management
  │    ├── services/      # API wrappers (fetch, websocket connector)
  │    └── validation/    # Zod schemas (Tasks, Reminders, Trades)
  │
  ├── web/                # React 19 web frontend
  │    └── src/components # Tailwind web UI elements
  │
  └── mobile/             # React Native native app
       └── src/components # Native UI widgets (Pressable, Text, View)
```

---

## 2. React Web vs. React Native Translation Map

While state management and HTTP API connectors can be reused 100%, HTML DOM elements must be translated to React Native primitive UI components:

| React Web Component | React Native Equivalent | Description |
|---|---|---|
| `<div>` | `<View>` | Non-scrolling container |
| `<span>`, `<p>`, `<h1>` | `<Text>` | Typography wrapper |
| `<button>`, `<a>` | `<Pressable>`, `<TouchableOpacity>` | Touch handler |
| `<input>`, `<textarea>` | `<TextInput>` | Keyboard text capture |
| `<img>` | `<Image>` | Graphic renderer |
| Vertical Scroll container | `<ScrollView>`, `<FlatList>` | List rendering with virtual scrolling |

---

## 3. State Management & Persistent Storage

- **Zustand Portability:** Zustand is 100% compatible with React Native. The same state store hooks used on web will govern mobile state transitions.
- **Storage Adapter:** React Native does not support `localStorage`. We will configure the Zustand persistence middleware to use `@react-native-async-storage/async-storage` or `expo-sqlite` as the storage provider for offline sync.

---

## 4. Phase 2 Implementation Timeline

1. **Week 1: Monorepo Setup & Core Extraction**
   - Extract Zustand store, validation schemas, and API handlers into `@lifeos/core`.
2. **Week 2: React Native Project Initialization**
   - Bootstrap React Native app using Expo CLI. Add Tailwind engine support (e.g., via `nativewind`).
3. **Week 3: Mobile View Coding**
   - Re-implement UI views (Dashboard, Tasks, AI, Panchang, Trading) using native components.
4. **Week 4: Push Notifications & Store Launch**
   - Integrate native Firebase Cloud Messaging (FCM) for iOS/Android background alerts and publish to Apple App Store & Google Play.
