# SpaceShift — Figma Design System & Spatial UI Spec

**Figma file:** [SpaceShift Editor](https://www.figma.com/design/cS5yxIRlt0eBU92DIXkvTU) (Ai Hackathon team). Pages: `0 Foundations`, `1 Intake`, `2 Editor`, `3 Photoreal`, `4 States`.
**Style source:** [`.claude/skills/XUAN_INK_SCROLL_DESIGN.md`](.claude/skills/XUAN_INK_SCROLL_DESIGN.md) (Xuan Ink & Scroll). Where this spec and the skill disagree, this spec wins for SpaceShift.

## 1. Aesthetic Direction: "Architectural Drawing on Xuan Paper"
* **Canvas Background:** `paper-base` `#EAE0CE` (raw Xuan paper) with faint `paper-border` `#C4B190` metric grid lines (`0.5m` major at 45% opacity, `0.1m` minor at 20%) and a soft aged vignette (`inset 0 0 110px rgba(92, 74, 48, 0.24)`).
* **Never pure white or black.** Leave 30–40% open paper around the room; the HUD stays on the edges.
* **Surface Tokens (Mounted Scroll Panels):**
  * `scroll-panel`: `rgba(243, 236, 224, 0.88)` with `backdrop-filter: blur(4px)`, `1px solid hairline-ink` (`rgba(28, 26, 23, 0.18)`), shadow `0 14px 34px -12px rgba(46, 43, 39, 0.18)`, `4px` radius.
  * `ink-primary`: `#1C1A17` (headings, walls, focal edges, selection outline).
  * `ink-medium`: `#4A453E` (secondary copy, all meter dimensions, angles and scores).
  * `ink-mist`: `#8A8174` (muted labels, disabled and pending states).
  * `paper-deep`: `#DFD1B8` (recessed wells, inactive tabs).
* **Typography:**
  * Titles: `Cormorant Garamond` SemiBold (room title, section titles).
  * UI text: `Plus Jakarta Sans` (Regular body, Medium labels/captions).
  * Telemetry: `JetBrains Mono` Medium, `+0.06em` tracking (dimensions like `1.40m × 0.70m`, scores, times).
* **Semantic Spatial Shader Tokens:**
  * `accent-celadon`: `#4E6352` (clear door arcs, command-position sightlines, valid placement, "fits").
  * `accent-ochre`: `#A67C52` (estimated-compass glare, tight clearance `<0.65m`, proxy/estimated tags).
  * `seal-vermilion`: `#C43A31` (mesh collisions, blocked door swing, severe glare, back-to-door desk, errors).
  * `sunbeam-wash`: `#C9A15B` (window sunbeam cone, drawn at 25% opacity). This colour is SpaceShift's own; the skill doesn't define one.
* **Buttons (`2px` radius, never pill-shaped):**
  * Primary = **vermilion chop seal**: `seal-vermilion` fill, `1.5px seal-vermilion-dark` (`#9E2A22`) border, `seal-paper` (`#F7EFE2`) label, inset `0 0 0 1.5px rgba(247, 239, 226, 0.35)` + `2px 3px 0 rgba(28, 27, 25, 0.18)`.
  * Secondary = **ghost seal outline**: `rgba(243, 236, 224, 0.65)` fill, `1px rgba(196, 58, 49, 0.55)` border, `seal-vermilion-dark` label.
  * Keep vermilion for primary actions, errors and blocking findings; don't use it for decoration.
* **Toasts:** dark `ink-primary` banner, `1.5px seal-vermilion` border, `seal-paper` text. No browser `alert()`.
* **Translucent tokens:** Figma variables carry their own alpha, so translucent uses are separate variables named `<token>/a<percent>` (for example `ink-primary/a6`, CSS `var(--ink-primary-a6)`).

## 2. User Flow
1. **Upload** (`1a`): floor-plan image + walkthrough video → `[Build room]`.
SpaceShift works on **one room at a time**: the floor plan is segmented into separate rooms, and each room becomes its own `RoomScene`.

2. **Reading floor plan** (`1b`): Parsing floor plan → Segmenting rooms (error state with `[Retry]`).
3. **Annotated floor plan** (`1c` / `1d`): the segmented rooms drawn in ink in their plan positions. Each room shows its name, `W × D` dimensions and floor area; doors, windows, compass (if grounded) and a 1 m scale bar are marked. Circulation space (hall) is drawn but not selectable. Selecting a room fills it with a vermilion wash and opens a right panel: room size and area, north grounding, openings detected, a note on what happens next, and `[Build this room]`.
4. **Building room** (`1e`): for the selected room only: Extracting furniture from video → Assembling room.
5. **Room editor** (`2a`–`2f`): see below. The top-left panel has `[← Floor plan]` to go back and pick another room.
6. **Photoreal** (`3a`–`3c`): before/after (editor ink view vs fal.ai photoreal), walkthrough generation.

## 3. Editor Layout
The Editor is split into two regions (1440 × 900 reference frame):
* **Room view (left, fills remaining width, 1060px in the mock):** the interactive 3D room in a simplified, clarity-first **ink illustration** style (§4). Furniture can be selected, dragged and rotated directly in the view. All HUD elements below float over it.
* **Sidebar (right, 380px, `scroll-panel` with a left hairline):** three tabs: **Chat · Stats · Library**. The active tab has an `ink-primary` label and a 2px `seal-vermilion` underline.
  * **Chat:** conversation with the AI to redesign the room. Assistant replies that change the layout end in a **Proposed layout** card (`current → proposed` score + `[Preview]`). Preview puts the editor into Auto-Fix preview mode (dimmed current layout, dashed proposed poses, dock shows `[Reject]` / `[Apply]`). Composer at the bottom: input + `[Send]`.
  * **Stats:** full `AuditReport` breakdown: spatial score, walkable floor %, feng shui score, glare-orientation grounding, then a **Findings** list (one row per collision, blocked door, clearance issue, glare alert and sightline; status dot + label + mono value).
  * **Library:** searchable furniture catalog with paste-a-link import. Search input, category chips (`FurnitureItem.category`), and result cards (image, name, `W × D × H`, `price_gbp`, fit check, `[Add]`). **Replace mode** (opened by `[Swap via Link/Search]` on the object pill) shows a "Replacing <item>" banner with `[Cancel]`, pre-filters to the item's category, and the card action becomes `[Replace]`. Swap is no longer a separate panel.

### HUD over the room view (Zero Clutter)
1. **Top-Left Panel:** `[← Floor plan]` + Room Title (`scene_id`) + Overall Spatial Score Ring (`0–100`, `AuditReport.overall_score`). Detailed numbers live in the Stats tab.
2. **Top-Right Sun & Compass Dial:**
   * Circular time scrubber (`08:00` – `19:00`, `RoomScene.sun_hour`) with a `sunbeam-wash` elapsed arc.
   * **Compass Calibration Ring:** Shows `"North Grounded"` (celadon dot) if extracted from floor plan, or `"Calibrate North"` (dashed ochre, interactive rotatable ring) if floor plan lacked a compass (`north_compass_deg = null`).
3. **Contextual Object Panel (Floats above selected 3D furniture):**
   * Item Name + Dimensions (`1.40m × 0.70m`) + `[Rotate 90°]` + `[Snap Wall]` + `[Swap via Link/Search]` + `[Delete]`.
   * Ochre tag when `is_proxy`, `dimension_source = "estimated"`, or `correction_needed` is non-empty.
4. **Bottom Floating Dock (Mode Switcher & Hero Actions):**
   * Layer Toggles: `[Clearance & Doors]` · `[Solar Glare]` · `[Feng Shui Rays]`
   * Primary CTA 1: **`Auto-Fix Layout`** (Triggers `/optimize` and smoothly tweens furniture over `600ms` `cubic-bezier(0.22, 1, 0.36, 1)`). Preview mode replaces the CTAs with the score change (`current → proposed`) and `[Reject]` / `[Apply]`.
   * Primary CTA 2: **`Photoreal Render`** (Captures depth + RGB $\rightarrow$ opens split-screen before/after slider + `"Generate 5s Walkthrough"` button).

## 4. Room View (R3F)
* **Target look:** coloured cartoon-ink ("ligne claire") drawing, not photoreal. Even-weight pine-ink outlines on every wall, floor and furniture edge, flat colour washes inside the lines (plaster walls, ochre wood, celadon/linen textiles), no photographic textures, so layout and findings read instantly (see the `Canvas/Room Render` mock). In R3F: flat or toon materials (`MeshToonMaterial` / unlit colours with gentle ambient), ink outlines via `EdgesGeometry` + `LineBasicMaterial({ color: 0x1C1B19 })` (or an outline pass), cut-away walls nearest the camera so the room reads like a dollhouse.
* Photorealism exists only in the separate fal.ai render on the Photoreal page.
* **Interaction:** click to select (ink outline + object panel), drag on the floor plane, rotate in 90° steps; metric bounds (`bbox_m`) are always enforced.
* Behind the room, `scene.background = #ECE2D0` so the viewport blends into the paper UI.
* Audit overlays are drawn on the floor/geometry in the semantic tokens above at low fill opacity (~18%) with a solid stroke; dashed outlines for proposed poses and clearance zones.
