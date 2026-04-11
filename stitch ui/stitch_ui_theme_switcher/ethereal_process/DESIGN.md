# Design System Document: The Ethereal Observer

## 1. Overview & Creative North Star

### Creative North Star: "The Digital Curator"
This design system rejects the frantic, cluttered aesthetic of traditional technical monitors. Instead, it treats system data as a curated gallery. We move beyond "utility" into "prestige," utilizing **Atmospheric Depth** and **Editorial Precision**. By leveraging high-contrast typography scales against soft, blurred surfaces, we create a UI that feels less like a dashboard and more like a high-end digital publication.

### Breaking the Template
To avoid a generic "SaaS" look, this system utilizes **Intentional Asymmetry**. We favor large, bold headlines (Space Grotesk) offset against wide, sweeping margins. Elements should feel like they are floating in a pressurized environment—held in place by gravity and light rather than rigid boxes and lines.

---

## 2. Colors

The palette is rooted in a sophisticated interplay of obsidian purples and frosted silvers. 

### Surface Hierarchy & Nesting
We define depth through **Tonal Layering** rather than structural lines. 
- **Base Layer:** `surface` (#0f0c19)
- **Secondary Sections:** `surface_container_low` (#151123)
- **Prominent Cards:** `surface_container` (#1b162e)
- **High-Interaction Floating Elements:** `surface_container_high` (#221b39)

### The "No-Line" Rule
**Explicit Instruction:** Do not use 1px solid borders to define sections. Boundaries must be established through color shifts. A `surface_container_low` element sitting on a `surface` background provides all the definition needed. 

### The "Glass & Gradient" Rule
Floating panels (Modals, Hover Menus, or Active Process Details) must use **Glassmorphism**. Use `surface_variant` at 60% opacity with a `backdrop-filter: blur(24px)`. Main CTAs should utilize a subtle linear gradient from `primary` (#b5c7ed) to `primary_container` (#364766) at a 135-degree angle to provide a "soul" to the monochrome base.

---

## 3. Typography

The typographic system creates an editorial rhythm by pairing the technical, geometric **Space Grotesk** with the humanist, approachable **Manrope**.

*   **Display & Headlines (Space Grotesk):** Used for "Big Data" moments—CPU percentages, total memory, or section headers. The bold, wide stance of Space Grotesk provides an authoritative, modern voice.
*   **Body & Titles (Manrope):** Used for process names, descriptions, and metadata. Manrope ensures high legibility at smaller scales and balances the "brutalism" of the headlines with warmth.

**Hierarchy as Identity:** 
Always lead with a `display-sm` or `headline-lg` to anchor a page. Don't be afraid of the "Empty Space" surrounding a small `label-md`; let the typography breathe to signal premium quality.

---

## 4. Elevation & Depth

### The Layering Principle
Depth is achieved by stacking `surface-container` tiers. To elevate a process card, do not add a border; instead, move it from `surface_container` to `surface_container_highest`.

### Ambient Shadows
When a component must "float" (e.g., a dragged process or a dropdown), use **Ambient Shadows**:
- **Color:** `on_surface` (#eae1ff) at 6% opacity.
- **Blur:** 40px to 60px.
- **Spread:** -10px.
This creates a natural light falloff that mimics physical frosted glass.

### The "Ghost Border" Fallback
If contrast testing fails for accessibility, use a **Ghost Border**: `outline_variant` at 15% opacity. Never use a 100% opaque border.

---

## 5. Components

### Buttons
*   **Primary:** A gradient of `primary` to `primary_container`. Text: `on_primary`. Roundedness: `full`.
*   **Secondary:** Glassmorphic background (`surface_variant` at 40%) with a `Ghost Border`.
*   **Interaction:** On hover, increase `backdrop-blur` and scale the button by 1.02x.

### Cards & Process Lists
*   **Rule:** Forbid the use of divider lines. 
*   **Execution:** Separate list items using 16px of vertical white space. Use a subtle `surface_container_low` background on hover to indicate selection.
*   **Active State:** Use a `primary` vertical accent bar (4px width) on the left edge of the card, with `primary_fixed_dim` as a soft glow behind it.

### Progress Bars & Gauges
*   **Track:** `surface_variant`.
*   **Indicator:** `primary` gradient. For error states (high CPU), transition the gradient to `error_dim`.
*   **Micro-interaction:** The indicator should have a "pulse" animation (opacity 0.8 to 1.0) when a process is under heavy load.

### Input Fields
*   **Style:** Minimalist. No bottom line or full box. Use a `surface_container_highest` background with `xl` (1.5rem) rounded corners.
*   **Focus:** Transition the `Ghost Border` from 15% to 40% opacity.

---

## 6. Do's and Don'ts

### Do
*   **Do** use `display-lg` for single-number metrics to create a visual "hero" on the dashboard.
*   **Do** allow 24px+ of padding inside cards. Negative space is a luxury.
*   **Do** use `tertiary` (#fff8f5) for subtle highlights in status chips to provide a warm, "paper-like" contrast to the cool purple tones.

### Don't
*   **Don't** use pure black (#000000) for shadows or backgrounds; it kills the "Glass" illusion. Use `surface_container_lowest`.
*   **Don't** use standard 1px dividers. If you need to separate content, use a 48px gap or a tonal shift.
*   **Don't** use sharp corners. Every interaction should feel "soft" to the touch; stick to the `lg` (1rem) or `xl` (1.5rem) scale for all containers.