# SpaceShift — Figma Design System & Spatial UI Spec

## 1. Aesthetic Direction: "Architectural CAD meets Spatial Glass"
* **Canvas Background:** `#0E1015` (Deep Obsidian Slate) with subtle `#1C202B` metric grid lines (`0.5m` major, `0.1m` minor).
* **Surface Tokens (Glassmorphic HUD):**
  * `hud-bg`: `rgba(18, 21, 29, 0.78)` with `backdrop-filter: blur(16px)` and `1px solid rgba(255, 255, 255, 0.10)`.
  * `text-primary`: `#F4F6FB` (`Inter` / `Geist Sans`).
  * `text-mono`: `#9AA5B8` (`JetBrains Mono` — used for all meter dimensions, angles, and scores).
* **Semantic Spatial Shader Tokens:**
  * `valid-emerald`: `#10B981` (Clear door arcs, command-position sightlines, valid placement).
  * `warning-amber`: `#F59E0B` (Estimated-compass glare, tight clearance `<0.65m`).
  * `danger-coral`: `#EF4444` (Mesh collisions, blocked door swing, severe monitor glare, back-to-door desk).
  * `sunbeam-gold`: `#FBBF24` (Additive volumetric shader cone from windows).

## 2. Screen Choreography (Zero Clutter)
1. **Top-Left Pill:** Room Title + Overall Spatial Score Ring (`0–100`) + Walkable Floor `%` badge.
2. **Top-Right Sun & Compass Dial:**
   * Circular time scrubber (`08:00` – `19:00`).
   * **Compass Calibration Ring:** Shows `"North Grounded"` (emerald dot) if extracted from floor plan, or `"Calibrate North"` (interactive rotatable ring) if floor plan lacked a compass.
3. **Contextual Object Pill (Floats above selected 3D furniture):**
   * Item Name + Dimensions (`1.40m × 0.70m`) + `[Rotate 90°]` + `[Snap Wall]` + `[Swap via Link/Search]` + `[Delete]`.
4. **Bottom Floating Dock (Mode Switcher & Hero Actions):**
   * Layer Toggles: `[Clearance & Doors]` · `[Solar Glare]` · `[Feng Shui Rays]`
   * Primary CTA 1: **`Auto-Fix Layout`** (Triggers `/optimize` and smoothly tweens furniture over `600ms` cubic-bezier).
   * Primary CTA 2: **`Photoreal Render`** (Captures depth + RGB $\rightarrow$ opens split-screen before/after slider + `"Generate 5s Walkthrough"` button).