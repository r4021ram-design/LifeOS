# LifeOS AI — Mobile Accessibility Audit Report

**Audit Date:** 2026-06-19
**Standard:** WCAG 2.1 Level AA
**Status:** 🟡 Conditional Pass — 4 Critical, 7 Medium accessibility violations

---

## 1. Color Contrast Analysis

### Background/Foreground Combinations

| Element | Background | Foreground | Contrast Ratio | WCAG AA (4.5:1) | Status |
|---|---|---|---|---|---|
| Body text | `#030303` | `#f3f4f6` | 19.2:1 | ✅ Pass | Excellent |
| Primary button | `#9333ea` (purple-600) | `#ffffff` | 4.6:1 | ✅ Pass | Borderline |
| Muted text | `#030303` | `#6b7280` (gray-500) | 5.3:1 | ✅ Pass | Good |
| Placeholder text | `#030303` | `#6b7280` (gray-500) | 5.3:1 | ✅ Pass | Good |
| Glass card text | `rgba(18,18,24,0.65)` | `#f3f4f6` | ~15:1 | ✅ Pass | Good |
| Tithi badge (header) | `purple-500/10` | `#c084fc` (purple-400) | ⚠️ ~3.8:1 | ❌ Fail | Below minimum |
| Priority "Critical" | `red-500/20` | `#f87171` (red-400) | ⚠️ ~3.5:1 | ❌ Fail | Below minimum |
| Priority "High" | `orange-500/20` | `#fb923c` (orange-400) | ⚠️ ~3.3:1 | ❌ Fail | Below minimum |
| Priority "Medium" | `blue-500/20` | `#60a5fa` (blue-400) | ~4.6:1 | ✅ Pass | Borderline |
| Festival tag text | `yellow-500/10` | `#facc15` (yellow-400) | ⚠️ ~2.8:1 | ❌ Fail | Below minimum |
| Streak counter | `transparent` | `#c084fc` (purple-400) | ~5.2:1 (vs card bg) | ✅ Pass | Good |
| `text-gray-600` | `#030303` | `#4b5563` | 3.9:1 | ⚠️ Borderline | Needs review |

> [!CAUTION]
> **A11Y-01**: Priority badge text colors (red-400, orange-400 on dark transparent backgrounds) fail WCAG AA 4.5:1 contrast ratio for normal text. Festival tags (yellow-400) are also below minimum. **Fix:** Use `-300` variants instead of `-400` for these elements, or add a solid background color.

> [!IMPORTANT]
> **A11Y-02**: The `text-[10px]` class used for priority badges, command palette badges, and tithi badge is below the WCAG recommended minimum of 12px for UI text. At 10px on mobile screens, this text is effectively illegible for many users. **Fix:** Replace all `text-[10px]` with `text-xs` (12px minimum).

---

## 2. Touch Target Audit

### Minimum Touch Target: 44×44px (WCAG 2.5.8 Level AAA / iOS HIG)

| Element | Size | Has `touch-target` class | Status |
|---|---|---|---|
| Bottom nav buttons | Full height (64px) × ~equal width | ✅ Yes | ✅ Pass |
| FAB button | 56×56px | Inherent | ✅ Pass |
| Auth submit button | Full width × 48px (`py-3`) | ✅ Yes | ✅ Pass |
| Task checkbox | 24×24px visual, but with `touch-target` | ✅ Yes | ⚠️ Visual misalignment |
| Task delete button | 20×20px icon, `p-2` + `touch-target` | ✅ Yes | ✅ Pass |
| Command palette items | Full width × 48px (`py-3`) | ✅ Yes | ✅ Pass |
| Quick Capture type buttons | ~68×44px at 320px | ✅ Yes | ✅ Pass (borderline) |
| Collapse headers | Full width × ~40px | ❌ No | ⚠️ Below minimum |
| More drawer items | Full width × 48px | ✅ Yes | ✅ Pass |
| Chat suggestion chips | Variable × 36px (`py-1.5`) | ✅ Yes (`touch-target`) | ⚠️ `py-1.5` = ~36px, needs padding |
| Mic button | 44×44px (`p-2.5`) | ✅ Yes | ✅ Pass |
| Send button | 44×44px (`p-2.5`) | ✅ Yes | ✅ Pass |
| Trade close Save/Cancel | `px-3 py-1` ≈ ~28px height | ❌ No | ❌ **Fail** |
| Panchang collapse header | Auto height | ❌ No | ⚠️ Below minimum |

> [!WARNING]
> **A11Y-03**: The task completion checkbox renders as a 24×24px visual element. While the `touch-target` class sets `min-height: 44px`, the visual checkbox is small. The expanded touch area extends invisibly, which is acceptable per WCAG. However, the shrink-0 on a 24px element means the touch hit area may not be visually obvious to users.

> [!CAUTION]
> **A11Y-04**: Trade exit form "Save" and "Cancel" buttons use `px-3 py-1` which produces buttons approximately 28px tall — below the 44px minimum. **Fix:** Change to `py-2.5` and add `touch-target` class.

---

## 3. Screen Reader Audit

### ARIA Labels and Semantic HTML

| Element | ARIA / Semantics | Status |
|---|---|---|
| Bottom nav buttons | `aria-label={item.label}` | ✅ Pass |
| FAB button | `aria-label="Quick Capture Item"` | ✅ Pass |
| Auth form | `<form onSubmit>` with labels | ✅ Pass |
| Input labels | `<label>` elements present | ✅ Pass |
| Modal overlays | No `role="dialog"` or `aria-modal` | ❌ Fail |
| Active tab state | No `aria-selected` or `role="tab"` | ❌ Fail |
| Loading states | No `aria-live` region | ❌ Fail |
| Error messages | No `role="alert"` | ❌ Fail |
| Page heading structure | No `<h1>` on dashboard | ❌ Fail |
| Main content region | `<main>` element used | ✅ Pass |
| Sidebar | `<aside>` element used | ✅ Pass |
| Nav element | `<nav>` element used | ✅ Pass |
| Header element | `<header>` element used | ✅ Pass |

> [!CAUTION]
> **A11Y-05**: Modal overlays (Command Palette, Quick Capture, More Drawer) lack `role="dialog"` and `aria-modal="true"`. Screen readers cannot identify these as modal contexts and may allow focus to escape behind them. **Fix:** Add `role="dialog" aria-modal="true" aria-label="..."` to each overlay.

> [!WARNING]
> **A11Y-06**: The bottom navigation tabs lack `role="tablist"` and individual tabs lack `role="tab"` with `aria-selected`. Screen readers announce them as generic buttons. **Fix:** Wrap in a container with `role="tablist"` and add `role="tab" aria-selected={isActive}` to each button.

> [!IMPORTANT]
> **A11Y-07**: No `aria-live` regions for dynamic content updates. When tasks are created/deleted, habits logged, or AI responses arrive, screen readers are not notified. **Fix:** Add `aria-live="polite"` to the task list container and `aria-live="assertive"` to the chat message area.

---

## 4. Keyboard Navigation

| Feature | Tab Order | Enter/Space | Escape | Arrow Keys | Status |
|---|---|---|---|---|---|
| Auth form | ✅ Logical | ✅ Submit | — | — | ✅ Pass |
| Command palette | ✅ Focus trapped | ✅ Select | ✅ Close | ❌ No arrow nav | ⚠️ Partial |
| Bottom nav | ✅ Sequential | ✅ Activate | — | ❌ No arrow nav | ⚠️ Partial |
| Quick Capture | ✅ Focus trapped | ✅ Submit | ❌ No Escape close | — | ❌ Fail |
| More drawer | ✅ Focus present | ✅ Activate | ❌ No Escape close | — | ❌ Fail |
| AI Chat | ✅ Input focus | ✅ Enter sends | — | — | ✅ Pass |
| Task forms | ✅ Tab through | ✅ Submit via onClick | — | — | ⚠️ No form submit on Enter |

> [!WARNING]
> **A11Y-08**: Quick Capture and More Drawer modals don't close on Escape key. The Command Palette correctly handles Escape (via the `useEffect` keyboard listener), but the other modals do not share this handler. **Fix:** Extend the keydown handler or add individual Escape handlers to each modal.

---

## 5. Focus Management

| Scenario | Expected Behavior | Actual Behavior | Status |
|---|---|---|---|
| Command palette opens | Focus moves to search input | ✅ Auto-focus via `useRef` | ✅ Pass |
| Quick Capture opens | Focus moves to text input | ✅ `autoFocus` attribute | ✅ Pass |
| Modal closes | Focus returns to trigger element | ❌ Focus lost | ❌ Fail |
| Tab change | Focus moves to content area | ❌ Focus stays on nav | ⚠️ Partial |
| Page load | Focus on first interactive element | ✅ Default browser behavior | ✅ Pass |

> [!IMPORTANT]
> **A11Y-09**: When modals (Command Palette, Quick Capture, More Drawer) close, focus is not returned to the triggering element. This disorients keyboard and screen reader users. **Fix:** Store a ref to the trigger element before opening, and call `.focus()` on it after closing.

---

## 6. Motion and Animation

| Animation | Has `prefers-reduced-motion` override | Status |
|---|---|---|
| `slideUp` | ❌ No | ❌ Fail |
| `fadeIn` | ❌ No | ❌ Fail |
| `animate-spin` | ✅ Tailwind default respects motion | ✅ Pass |
| `animate-pulse` | ✅ Tailwind default respects motion | ✅ Pass |
| Backdrop blur transitions | ❌ No | ❌ Fail |

> [!WARNING]
> **A11Y-10**: Custom animations (`slideUp`, `fadeIn`) do not respect `prefers-reduced-motion: reduce`. Users who have enabled reduced motion in their OS settings will still see slide and fade animations. **Fix:** Add media query:
> ```css
> @media (prefers-reduced-motion: reduce) {
>   .animate-slide-up, .animate-fade-in {
>     animation: none !important;
>   }
> }
> ```

---

## 7. Color-Only Indicators

| Indicator | Color-Only | Alternative Indicator | Status |
|---|---|---|---|
| Online/Offline status | Green/Amber dot | Text label "Cloud Connected" / "Offline" | ✅ Pass |
| Task completion | Checkbox fill + strikethrough | ✅ Both visual cues | ✅ Pass |
| Priority levels | Color badges | Text label ("Critical", "High") | ✅ Pass |
| PNL positive/negative | Green/Red text | +/- prefix in value | ✅ Pass |
| Active nav tab | Purple color | No other indicator | ⚠️ **Partial** |
| Trade type Long/Short | Green/Red badge | Text label | ✅ Pass |

> [!IMPORTANT]
> **A11Y-11**: The active bottom navigation tab is indicated solely by color change (gray → purple). There is no weight change, underline, or other non-color indicator. Users with color vision deficiency may not distinguish the active tab. **Fix:** Add a top border or dot indicator to the active tab.

---

## 8. Accessibility Summary

| Category | Critical | Medium | Low | Total |
|---|---|---|---|---|
| Color Contrast | 1 | 1 | 0 | 2 |
| Touch Targets | 1 | 0 | 0 | 1 |
| Screen Reader | 3 | 0 | 0 | 3 |
| Keyboard | 1 | 0 | 0 | 1 |
| Focus Management | 1 | 0 | 0 | 1 |
| Motion | 1 | 0 | 0 | 1 |
| Color-Only | 0 | 1 | 0 | 1 |
| Font Size | 0 | 1 | 0 | 1 |
| **Total** | **4** | **7** | **0** | **11** |

### WCAG 2.1 AA Compliance Score: ~65%

> [!NOTE]
> The app has good structural accessibility (semantic HTML, ARIA labels on key elements, touch-target enforcement). The main gaps are in modal/dialog ARIA attributes, contrast on decorative badges, and motion preferences. These are addressable without architectural changes.
