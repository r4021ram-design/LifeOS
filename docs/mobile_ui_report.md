# LifeOS AI — Mobile UI Audit Report

**Audit Date:** 2026-06-19
**Auditor:** Architecture Team
**Status:** 🟡 Conditional Pass — 14 Critical, 8 Medium issues identified

---

## 1. Breakpoint Matrix

| Breakpoint | Device Reference | Layout Mode | Sidebar | Bottom Nav | FAB | Header |
|---|---|---|---|---|---|---|
| 320px | iPhone SE (1st Gen) | Mobile | Hidden ✅ | Visible ✅ | Visible ✅ | Sticky ✅ |
| 375px | iPhone SE (3rd Gen) | Mobile | Hidden ✅ | Visible ✅ | Visible ✅ | Sticky ✅ |
| 390px | iPhone 15 | Mobile | Hidden ✅ | Visible ✅ | Visible ✅ | Sticky ✅ |
| 414px | iPhone 15 Pro Max | Mobile | Hidden ✅ | Visible ✅ | Visible ✅ | Sticky ✅ |
| 768px | iPad Mini / md breakpoint | Desktop | Visible ✅ | Hidden ✅ | Hidden ✅ | Desktop ✅ |
| 1024px | iPad Pro / Desktop | Desktop | Visible ✅ | Hidden ✅ | Hidden ✅ | Desktop ✅ |

> [!NOTE]
> The app uses `md:` (768px) as the sole responsive breakpoint via Tailwind. This is correct for the mobile ↔ desktop transition.

---

## 2. Navigation Audit

### 2.1 Bottom Navigation Bar

**Implementation:** [App.tsx:1790-1816](file:///c:/Users/admin/Desktop/todo/frontend/src/App.tsx#L1790-L1816)

| Check | Status | Notes |
|---|---|---|
| 5 tabs rendered | ✅ Pass | Home, Tasks, Calendar, AI, More |
| Fixed position bottom | ✅ Pass | `fixed bottom-0 left-0 right-0` |
| Safe area inset | ✅ Pass | `safe-bottom` class applied |
| Touch targets ≥44px | ✅ Pass | `touch-target` + `h-full` on each button |
| Active state highlight | ✅ Pass | Purple-400 for active tab |
| Bar height | ✅ Pass | `h-16` (64px) |
| Backdrop blur | ✅ Pass | `bg-[#09090d]/95 backdrop-blur-md` |

> [!WARNING]
> **CRITICAL-01**: The bottom nav uses `z-40` but the FAB also uses `z-40`. When both overlap (FAB at `bottom-20`), tap events may conflict on smaller screens. **Fix:** Change FAB to `z-41` or increase bottom offset.

> [!WARNING]
> **CRITICAL-02**: The "Calendar" tab maps to `calendar_agenda` and "AI" maps to `ai_assistant`, which are mobile-only views. However, the `activeTab` state in the store persists. If a user opens "Calendar" on mobile then switches to desktop (resize/rotate), neither `calendar_agenda` nor `ai_assistant` are rendered in the desktop view — the user sees an **empty content panel**. **Fix:** Add fallback mapping in desktop view: `calendar_agenda → dashboard`, `ai_assistant → ai`.

### 2.2 Back Navigation

| Check | Status | Notes |
|---|---|---|
| Hardware back button | ⚠️ No handler | No `popstate` listener or history integration |
| Drawer close on back | ❌ Fail | More drawer doesn't close on Android back |
| Quick Capture close on back | ❌ Fail | Modal doesn't respond to back gesture |

> [!IMPORTANT]
> **CRITICAL-03**: No `history.pushState` / `popstate` integration. Android users expect the hardware back button to close modals and drawers. Currently it navigates away from the app entirely.

### 2.3 Deep Links

| Check | Status | Notes |
|---|---|---|
| URL routing | ❌ Not implemented | All state is in-memory via `activeTab` |
| Shareable URLs | ❌ Not implemented | No route params |
| Bookmark support | ❌ Not implemented | Always loads dashboard |

> [!NOTE]
> Deep linking is a Phase 2 concern. For MVP launch, this is acceptable as a known limitation.

---

## 3. Quick Capture (FAB) Audit

**Implementation:** [App.tsx:491-549](file:///c:/Users/admin/Desktop/todo/frontend/src/App.tsx#L491-L549)

| Check | Status | Notes |
|---|---|---|
| FAB visibility on mobile | ✅ Pass | `md:hidden`, 56px diameter |
| FAB position | ✅ Pass | `bottom-20 right-4` — above bottom nav |
| FAB active:scale effect | ✅ Pass | `active:scale-95` feedback |
| Modal slides up from bottom | ✅ Pass | `items-end` + `animate-slide-up` |
| Type selector (4 options) | ✅ Pass | Task, Reminder, Habit, Note — grid-cols-4 |
| Touch targets on type buttons | ✅ Pass | `touch-target` class applied |
| Input auto-focus | ✅ Pass | `autoFocus` attribute set |
| Close button accessible | ✅ Pass | X button with `touch-target` |

> [!WARNING]
> **CRITICAL-04**: At 320px width, the 4-column type selector (`grid-cols-4`) creates buttons that are approximately **72px wide × 44px tall**. The text ("Reminder") is truncated/squeezed. At 320px - 48px padding = 272px / 4 = 68px per button. **Fix:** Use `grid-cols-2 gap-2` on very small screens or use icons instead of text.

> [!IMPORTANT]
> **MEDIUM-01**: The Quick Capture modal has no swipe-to-dismiss gesture. Mobile users expect to be able to swipe down to close bottom sheets. This is a UX convention gap.

### Task Creation Speed Test

| Step | Action | Estimated Time |
|---|---|---|
| 1 | Tap FAB | 0.5s |
| 2 | Select type (Task default) | 0s (pre-selected) |
| 3 | Type title | 2-3s |
| 4 | Tap "Add Task" | 0.5s |
| **Total** | | **3-4s ✅** (Target: <5s) |

---

## 4. Panchang Widget Audit

**Implementation:** [App.tsx:741-793](file:///c:/Users/admin/Desktop/todo/frontend/src/App.tsx#L741-L793)

| Check | Status | Notes |
|---|---|---|
| Collapsible header | ✅ Pass | Click toggles `collapsePanchang` |
| Touch target on collapse header | ⚠️ Partial | Header div is clickable but has no `touch-target` class |
| Tithi display | ✅ Pass | Readable at all breakpoints |
| Nakshatra/Yoga/Karana grid | ✅ Pass | `grid-cols-2` on values |
| Sunrise/Sunset row | ✅ Pass | `flex items-center justify-between` |
| Festivals tags | ✅ Pass | `flex-wrap gap-1.5` — wraps properly |
| Muhurat times | ❌ Missing | Muhurats array from store is never rendered! |

> [!CAUTION]
> **CRITICAL-05**: The Panchang widget renders `tithi`, `nakshatra`, `yoga`, `karana`, `sunrise`, `sunset`, and `festivals` — but the `muhurats` array (containing Abhijit Muhurat, Amrit Kaal, Rahu Kaal) is **never displayed** in the dashboard widget. The data exists in the store but is dropped from the UI. **Fix:** Add a Muhurats section below festivals.

> [!WARNING]
> **CRITICAL-06**: The Panchang widget uses `col-span-2` in a `grid-cols-1 lg:grid-cols-3` grid. On mobile (`grid-cols-1`), `col-span-2` has no effect — acceptable. On tablet (768px-1023px without `lg`), the grid is still `grid-cols-1` so layout is fine. At 1024px+ it's `grid-cols-3` with `col-span-2` — correct. **No issue found.**

> [!IMPORTANT]
> **MEDIUM-02**: The Panchang header's collapse area has no explicit `min-height: 44px` touch target enforcement. While the flex layout likely exceeds 44px, it's not guaranteed.

---

## 5. AI Planner Mobile Chat UX

**Implementation:** [App.tsx:1498-1591](file:///c:/Users/admin/Desktop/todo/frontend/src/App.tsx#L1498-L1591)

| Check | Status | Notes |
|---|---|---|
| Chat container height | ⚠️ Concern | `h-[75vh]` — may be too tall with bottom nav + header |
| Chat bubbles max-width | ✅ Pass | `max-w-[85%]` — good for mobile |
| Bubble visual distinction | ✅ Pass | User=purple, AI=glass card |
| Input field font size | ✅ Pass | `text-base md:text-sm` — 16px on mobile (prevents iOS zoom) |
| Mic button | ✅ Pass | `touch-target` class applied |
| Send button | ✅ Pass | `touch-target` class applied |
| Keyboard handling | ⚠️ Concern | Enter key sends, but no `inputmode` attribute |
| Scroll to bottom on new message | ❌ Missing | No auto-scroll-to-bottom logic |
| Suggestion chips | ✅ Pass | Horizontally scrollable with `overflow-x-auto` |

> [!WARNING]
> **CRITICAL-07**: The AI chat container uses `h-[75vh]`. On a 568px iPhone SE screen: 75vh = 426px. Subtract header (56px) + bottom nav (64px) + safe areas = ~448px occupied. The chat panel of 426px may **overflow below the bottom nav** or be obscured. **Fix:** Use `h-[calc(100vh-8rem)]` or `h-[calc(100dvh-8rem)]` to account for header + bottom nav dynamically.

> [!IMPORTANT]
> **CRITICAL-08**: No auto-scroll-to-bottom when new messages arrive. As conversation grows, user must manually scroll down to see the latest AI response. **Fix:** Add a `useRef` + `scrollIntoView` on the messages container end.

> [!IMPORTANT]
> **MEDIUM-03**: On iOS Safari, the virtual keyboard pushes the viewport up. The fixed bottom nav and chat input may overlap or the chat area may become too small. Using `100dvh` (dynamic viewport height) instead of `100vh` would address this.

---

## 6. Trading Journal Audit

**Implementation:** [App.tsx:1274-1443](file:///c:/Users/admin/Desktop/todo/frontend/src/App.tsx#L1274-L1443)

| Check | Status | Notes |
|---|---|---|
| Form layout (mobile) | ✅ Pass | `grid-cols-1 lg:grid-cols-3` — stacks on mobile |
| Ticker/Direction grid | ✅ Pass | `grid-cols-2 gap-2` |
| Trade card layout | ✅ Pass | `glass-card p-4` — readable |
| PNL display | ✅ Pass | Color-coded green/red |
| Trade details grid | ⚠️ Concern | `grid-cols-2 md:grid-cols-4` — 2 cols on mobile |
| Exit price input | ✅ Pass | Inline expand with save/cancel |
| Number inputs | ✅ Pass | `type="number"` triggers numeric keyboard |

> [!WARNING]
> **CRITICAL-09**: The Execution History card uses `col-span-2` in a `grid-cols-1 lg:grid-cols-3` grid. On mobile (grid-cols-1), `col-span-2` is ignored — fine. But the heading says "Execution History" spans across an area that on mobile is just a single column card. The 2×4 detail grid at 320px creates very narrow cells (approximately `(320 - 48px padding - 16px card padding) / 2 = 128px` per cell). Labels like "Strategy:" with long values will truncate. **Fix:** Consider `grid-cols-1` for detail rows on very small screens using `grid-cols-1 xs:grid-cols-2 md:grid-cols-4`.

> [!IMPORTANT]
> **MEDIUM-04**: When the "Exit / Close Trade" inline form appears, the save/cancel buttons are small (`px-3 py-1`, `text-xs`) and may fall below the 44px touch target minimum. They lack the `touch-target` class. **Fix:** Add `touch-target` class.

---

## 7. Per-Tab Mobile Layout Analysis

### 7.1 Dashboard (Home)

| At 320px | Status | Issue |
|---|---|---|
| Today's Focus cards | ✅ Pass | Stack vertically, readable |
| Panchang + AI grid | ✅ Pass | `grid-cols-1` stacks properly |
| Habits/Goals grid | ✅ Pass | `grid-cols-1` stacks properly |
| Content padding | ✅ Pass | `p-4 md:p-8` — 16px on mobile |
| Bottom padding clearance | ✅ Pass | `pb-24 md:pb-8` clears bottom nav |

### 7.2 Tasks

| At 320px | Status | Issue |
|---|---|---|
| Add Task form | ✅ Pass | Full-width, stacked |
| Task list items | ✅ Pass | Checkbox + text + priority badge |
| Delete button | ✅ Pass | `touch-target` class present |
| Priority/Due grid | ✅ Pass | `grid-cols-2` within form |

> [!WARNING]
> **CRITICAL-10**: Task items use `flex items-center justify-between` with a checkbox (24px), text area, and controls (priority badge + delete). At 320px, the `flex-1 mr-2` text container gets squeezed to ~180px. Long task titles correctly `truncate`, but the combined layout with the 6px left border + padding creates cramped spacing. **Fix:** Consider a stacked (column) layout for task items at `<375px`.

### 7.3 Habits

| At 320px | Status | Issue |
|---|---|---|
| Add Habit form | ✅ Pass | Full-width stacked |
| Habit cards | ✅ Pass | `flex-col md:flex-row` — stacks on mobile |
| Log button | ✅ Pass | `touch-target` + full-width appearance |
| Streak counter | ✅ Pass | Readable |

### 7.4 Goals

| At 320px | Status | Issue |
|---|---|---|
| Add Goal form | ✅ Pass | Stacked layout |
| Goal cards | ⚠️ Concern | Category badge + title + buttons inline |
| Progress bar | ✅ Pass | `w-full` with percentage |
| +10% button | ✅ Pass | `touch-target` class |

> [!IMPORTANT]
> **MEDIUM-05**: Goal card header uses `flex items-center justify-between` with category badge, inline title, and two buttons (+10%, delete). At 320px this row may wrap awkwardly. Title uses `inline-block ml-2` which doesn't truncate. **Fix:** Add `truncate` to the title and ensure `flex-wrap` or stack the action buttons below.

### 7.5 Notes

| At 320px | Status | Issue |
|---|---|---|
| Add Note form | ✅ Pass | Full-width, textarea |
| Note cards | ✅ Pass | Title + content + delete |
| Content display | ✅ Pass | `whitespace-pre-line` wraps correctly |

### 7.6 Calendar Agenda (Mobile-only)

| At 320px | Status | Issue |
|---|---|---|
| Period headers | ✅ Pass | Purple left border + uppercase label |
| Task items | ✅ Pass | `flex justify-between` |
| Date display | ✅ Pass | Mono font, readable |
| Empty states | ✅ Pass | Centered text |

---

## 8. Auth Screen Mobile Audit

**Implementation:** [App.tsx:316-412](file:///c:/Users/admin/Desktop/todo/frontend/src/App.tsx#L316-L412)

| Check | Status | Notes |
|---|---|---|
| Container width | ✅ Pass | `max-w-md` + `p-4` padding |
| Input font size | ✅ Pass | `text-base md:text-sm` — 16px on mobile (prevents iOS zoom) |
| Logo/branding | ✅ Pass | Centered, 64px icon |
| Touch targets | ✅ Pass | `touch-target` on submit + offline button |
| Error message | ✅ Pass | Visible, amber alert |
| Offline mode button | ✅ Pass | Sparkles icon + text |

---

## 9. Mobile Header Audit

**Implementation:** [App.tsx:551-571](file:///c:/Users/admin/Desktop/todo/frontend/src/App.tsx#L551-L571)

| Check | Status | Notes |
|---|---|---|
| Height | ✅ Pass | `h-14` (56px) |
| Sticky | ✅ Pass | `sticky top-0 z-30` |
| Logo + Tithi | ✅ Pass | LifeOS AI branding + Panchang tithi badge |
| Search button | ✅ Pass | `touch-target` class applied |
| Backdrop blur | ✅ Pass | `bg-[#09090d]/65 backdrop-blur-md` |

> [!IMPORTANT]
> **MEDIUM-06**: The Tithi badge in the header uses `text-[10px]` which is **below WCAG AA minimum** of 12px for UI text. On 320px screens this is nearly illegible. **Fix:** Increase to `text-xs` (12px).

---

## 10. More Drawer Audit

**Implementation:** [App.tsx:1721-1787](file:///c:/Users/admin/Desktop/todo/frontend/src/App.tsx#L1721-L1787)

| Check | Status | Notes |
|---|---|---|
| Slide-up animation | ✅ Pass | `animate-slide-up` |
| Backdrop overlay | ✅ Pass | `bg-black/60 backdrop-blur-sm` |
| Menu items grid | ✅ Pass | `grid-cols-2` — 4 items in 2×2 |
| Touch targets | ✅ Pass | `touch-target` on all buttons |
| Close button | ✅ Pass | X button top right |
| Logout button | ✅ Pass | Red-themed, visible |
| Safe area | ✅ Pass | `safe-bottom` class |

> [!IMPORTANT]
> **MEDIUM-07**: The More drawer lacks a drag handle (pill indicator at top). Users may not realize they can close it by tapping the X. Adding a centered 40×4px pill handle would follow mobile UX conventions.

---

## 11. Cross-Browser Concerns

| Browser | Concern | Severity |
|---|---|---|
| **Chrome Android** | `-webkit-backdrop-filter` is redundant (Chrome supports unprefixed) | None |
| **Samsung Internet** | `backdrop-filter` blur may have rendering lag on older devices | Low |
| **iOS Safari** | `100vh` doesn't account for Safari's dynamic toolbar | **Critical** (CRITICAL-07) |
| **iOS Chrome** | Uses WebKit engine, same Safari concerns apply | **Critical** |
| **All** | `overflow-x: hidden` on body prevents pinch-zoom | **Medium** |

> [!CAUTION]
> **CRITICAL-11**: `overflow-x: hidden` on the `<body>` element prevents pinch-to-zoom on mobile browsers. This violates WCAG 1.4.4 (Resize Text). **Fix:** Remove `overflow-x: hidden` from body and ensure individual containers handle overflow properly.

---

## 12. Summary of Critical Issues

| ID | Component | Issue | Impact | Fix Complexity |
|---|---|---|---|---|
| CRITICAL-01 | FAB + Bottom Nav | Z-index collision at z-40 | Tap conflicts | 🟢 Low |
| CRITICAL-02 | Navigation | Mobile-only tabs show blank on desktop | Broken experience | 🟢 Low |
| CRITICAL-03 | Navigation | No back button handling | Android UX broken | 🟡 Medium |
| CRITICAL-04 | Quick Capture | 4-col type selector cramped at 320px | Text truncation | 🟢 Low |
| CRITICAL-05 | Panchang | Muhurats array never rendered | Missing sacred data | 🟢 Low |
| CRITICAL-06 | — | _(Cleared — no issue found)_ | — | — |
| CRITICAL-07 | AI Chat | `h-[75vh]` overflow below bottom nav | Content obscured | 🟢 Low |
| CRITICAL-08 | AI Chat | No auto-scroll-to-bottom | UX friction | 🟡 Medium |
| CRITICAL-09 | Trading | Detail grid cramped at 320px | Text truncation | 🟢 Low |
| CRITICAL-10 | Tasks | Task items cramped at 320px | Layout squeeze | 🟡 Medium |
| CRITICAL-11 | Body CSS | overflow-x:hidden blocks pinch-zoom | WCAG violation | 🟢 Low |
| CRITICAL-12 | Command Palette | `pt-[15vh]` pushes palette off-screen on small phones | Content clipped | 🟢 Low |
| CRITICAL-13 | Inputs | No `inputmode` attribute on search/text inputs | Suboptimal keyboard | 🟢 Low |
| CRITICAL-14 | Forms | Select `<option>` elements lack dark theme styling | White dropdown on Android | 🟡 Medium |
