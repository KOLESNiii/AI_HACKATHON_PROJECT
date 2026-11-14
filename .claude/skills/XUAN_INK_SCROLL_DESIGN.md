---
name: xuan-ink-scroll-design-system
description: Design system and frontend implementation skill for crafting traditional Chinese Xuan-paper ink-wash (Shuǐmòhuà) web interfaces, editorial scrolls, and 3D spatial studios.
version: 1.0.0
tags:
  - design-system
  - style-guide
  - chinese-ink-wash
  - shuimo
  - threejs
  - tailwind
---

# Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill

> **Skill Purpose:** Instructs designers, frontend engineers, and AI coding agents how to build modern web applications and interactive 3D studios inspired by classical Chinese handscrolls (*Shǒujuàn*), unbleached mulberry Xuan paper (*Shēngxuān*), pine-soot ink washes (*Shuǐmò*), and vermilion mineral chop seals (*Yìnzhāng*).

---

## 1. Core Aesthetic Philosophy

1. **Tactile Materiality Over Flat Digital Screens:** Never use pure `#FFFFFF` or `#000000`. Every surface should evoke warm, fibrous handmade paper and diluted natural pigments.
2. **Liúbái (`留白` — Intentional Emptiness):** Maintain **30%–40% open parchment breathing room** around major modules. Negative space represents mist, stillness, and spatial *Qi* flow.
3. **Unfolding Handscroll Rhythm:** Layout sections and multi-step pipelines should progress like unrolling a scroll—deliberate, calm, and structured with clear colophon markers.
4. **Restrained Vermilion Focal Points:** Reserve high-saturation cinnabar red strictly for primary actions, active stage seals, and verified status stamps.

---

## 2. Design Tokens (`tokens.css`)

Copy these CSS custom properties directly into your root stylesheet:

```css
:root {
  /* === Paper & Parchment Surfaces === */
  --paper-base: #EAE0CE;        /* Raw Xuan (生宣) — primary page canvas */
  --paper-card: #F3ECE0;        /* Aged Silk (古绢) — elevated panels & cards */
  --paper-deep: #DFD1B8;        /* Tea-Stained Scroll (茶染) — recessed wells & inactive tabs */
  --paper-border: #C4B190;      /* Warm Fiber Edge — secondary structural dividers */

  /* === Pine-Soot Ink Hierarchy === */
  --ink-primary: #1C1A17;       /* Concentrated Pine Ink (焦墨) — headlines & focal 3D edges */
  --ink-secondary: #2E2B27;     /* Dark Charcoal (浓墨) — primary body text */
  --ink-medium: #4A453E;        /* Diluted Ink (淡墨) — secondary copy & descriptions */
  --ink-mist: #8A8174;          /* Ink Wash Mist (墨韵) — muted labels, grids & disabled states */

  /* === Mineral & Botanical Accents === */
  --seal-vermilion: #C43A31;    /* Cinnabar Seal (朱砂红) — primary CTAs & active chop stamps */
  --seal-vermilion-dark: #9E2A22; /* Pressed Seal Border — hover/active seal depth */
  --accent-celadon: #4E6352;    /* Longquan Celadon (青瓷) — positive Qi / verified metrics */
  --accent-ochre: #A67C52;      /* Mineral Ochre (赭石) — warm timber & selection rings */

  /* === Typography Stacks === */
  --font-display: 'Cinzel', 'Cormorant Garamond', Georgia, serif;
  --font-serif: 'Cormorant Garamond', Georgia, serif;
  --font-sc: 'Noto Serif SC', 'Songti SC', serif;
  --font-calligraphy: 'Ma Shan Zheng', 'ZCOOL XiaoWei', 'Noto Serif SC', serif;
  --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, monospace;

  /* === Borders, Shadows & Motion === */
  --hairline-ink: 1px solid rgba(28, 26, 23, 0.18);
  --shadow-scroll: 0 14px 34px -12px rgba(46, 43, 39, 0.18);
  --ease-scroll: cubic-bezier(0.22, 1, 0.36, 1);
}
```

---

## 3. Typography & Bilingual Hierarchy Rules

| Role | Font Family | Size / Weight | Tracking & Leading | Usage Guidelines |
| :--- | :--- | :--- | :--- | :--- |
| **Hero & Section Titles** | `--font-serif` (`Cormorant Garamond`) | `28px–48px` / `600` | `-0.01em` / `1.15` | Use italic emphasis for poetic spatial concepts. |
| **Brand Wordmark** | `--font-display` (`Cinzel`) | `20px–28px` / `700` | `+0.08em` / `1.1` | Pair adjacent to a square Chinese chop seal (`墨境`). |
| **Chinese Proverbs & Seals** | `--font-sc` (`Noto Serif SC`) | `14px–30px` / `700` | `+0.12em` / `1.4` | Always accompany Chinese proverbs with Pinyin and English translation. |
| **UI Body & Descriptions** | `--font-sans` (`Plus Jakarta Sans`) | `14px–15px` / `400` | `0em` / `1.65` | Keep paragraphs concise (`max-width: 65ch`). |
| **Telemetry & Pipeline Logs** | `--font-mono` (`JetBrains Mono`) | `11px–12px` / `500` | `+0.06em` / `1.4` | Room dimensions (`5.4m × 4.2m`), Feng Shui scores, and `fal.ai` status. |

### Vertical Marginalia Colophons (`writing-mode: vertical-rl`)
* Apply `.vertical-seal { writing-mode: vertical-rl; text-orientation: upright; }` only to short 4-to-8 character classical idioms (e.g., `格物致知`, `藏风聚气`) inside card margins or headers.
* Never set long multi-sentence instructions vertically in English/Latin interfaces.

---

## 4. Paper Grain, Vignette & Ink-Bleed Effects

### Global Xuan Paper Texture Overlay
Add a fixed, pointer-transparent SVG turbulence layer above the background so every color block inherits organic plant fibers:

```css
.paper-grain-overlay {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 50;
  opacity: 0.42;
  mix-blend-mode: multiply;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 250 250' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='paperNoise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.82' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='matrix' values='1 0 0 0 0  0 0.96 0 0 0  0 0 0.88 0 0  0 0 0 0.25 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23paperNoise)'/%3E%3C/svg%3E");
}

.aged-vignette {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 49;
  box-shadow: inset 0 0 110px rgba(92, 74, 48, 0.24);
}
```

### Tapered Dry-Brush Divider
Replace rigid horizontal rules with tapered ink gradients:

```css
.ink-divider {
  height: 1px;
  border: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(28, 26, 23, 0.35) 50%,
    transparent 100%
  );
}
```

---

## 5. Signature UI Component Specifications

### A. Vermilion Chop Seal Button (`.chop-seal`)
Used for primary CTAs, active workflow steps, and brand stamps:

```css
.chop-seal {
  background-color: #C43A31;
  color: #F7EFE2;
  border: 1.5px solid #9E2A22;
  border-radius: 2px;
  box-shadow:
    inset 0 0 0 1.5px rgba(247, 239, 226, 0.35),
    2px 3px 0px rgba(28, 27, 25, 0.18);
  transition: all 0.22s cubic-bezier(0.22, 1, 0.36, 1);
}

.chop-seal:hover {
  background-color: #B23027;
  transform: translateY(-1px);
  box-shadow:
    inset 0 0 0 1.5px rgba(247, 239, 226, 0.5),
    3px 4px 0px rgba(28, 27, 25, 0.24);
}
```

### B. Ghost Seal Outline Button (`.seal-outline`)
Used for secondary actions, inactive pipeline steps, and refinement chips:

```css
.seal-outline {
  border: 1px solid rgba(196, 58, 49, 0.55);
  color: #9E2A22;
  background: rgba(243, 236, 224, 0.65);
  border-radius: 2px;
  transition: all 0.2s ease;
}

.seal-outline:hover {
  background: #C43A31;
  color: #F7EFE2;
  border-color: #C43A31;
}
```

### C. Mounted Scroll Card (`.scroll-panel`)
Used for content containers, upload dropzones, and 3D viewport shells:

```css
.scroll-panel {
  background: linear-gradient(
    180deg,
    rgba(245, 238, 224, 0.88) 0%,
    rgba(232, 220, 198, 0.85) 100%
  );
  border: 1px solid rgba(46, 43, 39, 0.22);
  box-shadow: 0 14px 34px -12px rgba(46, 43, 39, 0.18);
  backdrop-filter: blur(4px);
}
```

---

## 6. Three.js & 3D Spatial Viewport Guidelines

When embedding interactive 3D architecture or product canvases inside this style system:

1. **Seamless Canvas Blending:** Set `scene.background = new THREE.Color(0xECE2D0)` so the 3D floor plinth floats naturally on the Xuan parchment without a jarring dark viewport box.
2. **Ink Wash Edge Rendering (`水墨模式`):** Attach `THREE.EdgesGeometry` with `THREE.LineBasicMaterial({ color: 0x1C1B19, transparent: true, opacity: 0.68 })` to walls, floors, and furniture meshes so 3D volumes read like architectural brush-and-ink drawings.
3. **Interactive Raycast Dragging:**
   * Highlight hovered or selected 3D objects with a floor-level vermilion ring (`#C43A31`).
   * Temporarily set `orbitControls.enabled = false` during `pointerdown` on a furniture mesh, project pointer coordinates onto a horizontal `THREE.Plane(new THREE.Vector3(0, 1, 0), 0)`, clamp to room interior bounds, and re-enable `orbitControls.enabled = true` on `pointerup`.
4. **Cultural Loading States:** During multi-step AI synthesis or 3D mesh generation (`fal.ai`), display rotating classical Chinese spatial proverbs (*Yuanye*, *Zangshu*, *Dao De Jing*) with Chinese characters, Pinyin, translation, and architectural design notes.

---

## 7. AI Agent Implementation Guardrails (Do / Don't)

- **DO** use warm parchment tones (`#EAE0CE`, `#F3ECE0`) and charcoal ink (`#1C1A17`) for high-contrast readability.
- **DO** keep square `2px` border radii on buttons and stamps to honor stone-carved chop seals.
- **DO** pair Chinese terms with clear English labels so interfaces remain intuitive and accessible.
- **DON'T** use neon gradients, glassmorphic dark-mode backgrounds, or pill-shaped (`rounded-full`) primary CTA buttons.
- **DON'T** use standard browser `alert()` dialogs; render toast notifications as dark pine-ink banners bordered in vermilion red.