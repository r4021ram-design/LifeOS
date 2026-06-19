# Performance Optimization Plan

This document details the code optimization and build configuration strategies required to achieve loading speeds of under 1.5 seconds on mobile networks.

## 1. Bundle Size Target (< 300KB)

A small JavaScript bundle size is critical for fast parsing and execution on lower-end mobile devices. We will apply the following optimization constraints:

- **ESLint Import Audit:** Enforce direct exports imports for helper libraries (e.g., import only necessary icons from `lucide-react` instead of importing the entire module) to allow tree-shaking by the Vite/Rollup compiler.
- **Rollup Manual Chunk Splitting:** Configure `vite.config.ts` to separate vendor code (React, Zustand, Lucide) from application views:
  ```typescript
  // vite.config.ts snippet
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'zustand'],
          charts: ['recharts']
        }
      }
    }
  }
  ```

---

## 2. Code Splitting & Lazy Loading

Instead of loading the entire dashboard codebase on boot, we split the application by tab routes using React `lazy()` and `Suspense`:

- **Lazy Loaded Views:**
  - Tasks View (`/components/TasksView.tsx`)
  - Notes View (`/components/NotesView.tsx`)
  - Habits View (`/components/HabitsView.tsx`)
  - Goals View (`/components/GoalsView.tsx`)
  - Trading View (`/components/TradingView.tsx`)
  - AI View (`/components/AiView.tsx`)
- **Fallback Loading:** Wrap lazy imports in a lightweight skeleton loader widget to maintain a premium feel during transitions.

---

## 3. List Virtualization & Scrolling Optimization

For views rendering hundreds of active items (such as the task archive or the execution history in the Trading Journal), mobile devices can suffer from layout lag and high CPU consumption due to rendering thousands of nodes.
- We will integrate lightweight virtual list handlers or partition task lists using basic pagination.
- Ensure that the CSS property `content-visibility: auto` is applied to off-screen card items to defer browser rendering calculations.
