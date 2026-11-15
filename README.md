# SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin

> **Tracks:** Voice, Vision & Generative Media · Figma Design Sub-Track · Autonomous Agents  
> **Core Sponsors:** fal.ai · Figma · Linkup / Tavily

---

## 1. The Core Differentiator (Why We Beat Existing Tools)

Competitor research across **IKEA Kreativ, Decato, PromptDecor, RoomCraft, Stage, AI Home Designer, BuyByFit, GENA Interior, airender.ai, and Furnish It** reveals a sharp divide in the market:
1. **Photorealistic image generators** (`BuyByFit`, `airender.ai`) hallucinate room dimensions and cannot let you physically move individual items.
2. **2D/3D editors** (`AI Home Designer`, `RoomCraft`, `PromptDecor`) require manual dragging or generic furniture blocks, and ignore your *existing* belongings.
3. **LiDAR scanners** (`IKEA Kreativ`) require specialized hardware and erase your room's contents rather than separating and re-using them.

**SpaceShift bridges all three:**
* **Floor Plan + Video Grounding:** We anchor exact metric geometry from a 2D floor plan while extracting your *existing* furniture from walkthrough video via **fal.ai** (`fal-ai/trellis-2` / `fal-ai/sam-3/3d-objects`) into separate, movable `.glb` meshes.
* **Paste-Any-Link / Grounded Fit-Check:** Paste a URL or search for any real product (via Linkup/Tavily); we extract its true dimensions (`W × D × H`), generate a scaled `.glb`, and test whether it fits without breaking your room.
* **Falsifiable Spatial Audit & Auto-Solver:** Instead of vague "vibe" advice, custom GLSL rasterisation shaders visualize **walkable floor clearance**, **door-swing collisions**, **solar monitor glare** (using floor-plan compass orientation when present, or a user-adjustable sun dial when absent), and **computational Feng Shui / ergonomic sightlines**. One click auto-reconfigures your existing + new furniture to eliminate every red flag.
* **Generative Photoreal Finale:** Using the 3D viewport's depth map and layout as structural conditioning, **fal.ai** (`fal-ai/flux-control-lora-depth` + video generation) renders a photorealistic architectural preview and virtual walkthrough of the validated layout.

---

## 2. What We Stole (And Improved) From Competitors

| Competitor Reference | Architectural Pattern Adopted | How SpaceShift Improves It |
| :--- | :--- | :--- |
| **RoomCraft / PromptDecor** | React Three Fiber (`R3F`) + Drei + Zustand state store with collision-validated agent tool calls. | Replaces static geometric primitives with **fal.ai**-reconstructed `.glb` meshes of your *real* furniture + custom GLSL audit shaders. |
| **AI Home Designer / Stage** | Separating the 3D scene representation from live retailer search (**Linkup / Tavily**). | Enforces **strict metric bounding-box locking** from scraped retailer specs so generated 3D proxies never lie about fit. |
| **Furnish It** | Using room photography/HDRI cues and real IKEA product metadata inside Three.js. | Automates base-shell extrusion directly from floor plans + extracts movable furniture meshes automatically. |
| **BuyByFit / airender.ai** | Dramatic photorealistic before/after visual reveal. | Conditions **fal.ai Flux Depth** on our *geometrically verified* 3D scene so the photoreal output obeys real physics and dimensions. |

---

## 3. Full Tech Stack

### **Design & Frontend (`frontend/`)**
* **Figma:** Design system tokens, glassmorphic floating HUD components, interactive sun-dial & spatial audit badges (designed first, mirrored in CSS variables).
* **Framework:** React 19 + TypeScript + Vite + Tailwind CSS + Framer Motion.
* **3D & Shaders:** Three.js + `@react-three/fiber` + `@react-three/drei` + custom **GLSL Fragment/Vertex Shaders** (volumetric solar glare cones, architectural walkable-floor hatching, animated door-swing collision arcs, depth-buffer export).
* **State & Local Fast-Path:** Zustand (instant 60fps drag/rotate/snap + client-side AABB collision preview).

### **AI & Generative Media (`services/reconstruction` & `services/media_gen`)**
* **fal.ai Endpoints:**
  * `fal-ai/sam-3/3d-objects` & `fal-ai/trellis-2`: Single-image / cropped-frame $\rightarrow$ normalized `.glb` 3D mesh extraction (both for video-extracted existing furniture and searched catalog items).
  * `fal-ai/flux-control-lora-depth` (or `fal-ai/flux-pro/v1.1-ultra` + depth conditioning): Converts 3D viewport depth + RGB render into photorealistic architectural photography.
  * `fal-ai/kling-video` / `fal-ai/veo3`: Generates a 5-second cinematic walkthrough between two photoreal camera angles.
* **Vision & Floor Plan Parsing:** Gemini 2.5 Flash / GPT-4o Vision (structured JSON extraction of walls, doors, windows, and optional North compass arrow) + OpenCV + `trimesh`.
* **Grounded Product Search:** Linkup API / Tavily API (live retailer lookup + URL scraping for dimensions, price, and product imagery).

### **Spatial Audit & Solver Engine (`services/spatial_engine`)**
* **Backend:** Python 3.11 + FastAPI + Pydantic v2.
* **Computational Geometry:** `Shapely` (2D polygon boolean ops, door-swing sector intersection, connected walkable-area reachability), `NumPy` / `SciPy` (3D solar ray-casting & simulated annealing layout optimization).

---

## 4. Quickstart (Local Development)

Install Bun 1.3.2+ and uv. uv provisions Python 3.11 from `.python-version`.
Video reconstruction also requires FFmpeg and FFprobe on `PATH` (verified with FFmpeg 8).
Video-dependent tests skip when those executables are absent; other checks still run.
Run all commands from the repository root.

```bash
bun run setup
cp .env.example .env
```

Start each component in a separate terminal:

```bash
bun run dev:reconstruction # http://localhost:8001/docs
bun run dev:spatial        # http://localhost:8002/docs
bun run dev:media          # http://localhost:8003/docs
bun run dev               # http://localhost:5173
```

Start the reconstruction backend when using the demo editor: it serves mock furniture
directly from `contracts/mock_room/assets/` and generates room-shell GLBs on request.
The frontend requests them through `/api/reconstruction`; no GLBs are copied into
`frontend/public`, and no demo asset-build step is needed. Legacy mock-room GLBs live
in `services/reconstruction/fixtures/mock_room/`. These demo routes need no API keys.

The frontend opens on the Refresh home screen. Choose **Redesign my home**, then
upload your inputs or **Skip with demo home**. Pick a floor and room; use **Build
this room**, double-click the room, or press Enter on the selected room to open it.
Processing screens show an ink landscape and progress indicator while the demo
advances through its simulated processing steps.
The landscape images are included in the frontend assets. To regenerate them
optionally, run `bun frontend/scripts/generate-landscapes.ts` with Chromium
available (`CHROME_BIN` can point to its executable).
`GET /scenes/<room_id>` returns a whole room assembled for the editor and the audit: a demo
room (`g-reception`) or a room of an uploaded floor plan (see [architecture](docs/architecture.md#scene-assembly-route-9)).
The real-input room (`examples/three_floor.png` with the furniture of `examples/three_floor_3.mp4`)
is described in [architecture](docs/architecture.md#real-input-room-10). It loads on a fresh
checkout with no upload, key or network: `GET /scenes/plan-83a12322e933-floor-0-room-3` returns
it as soon as the reconstruction service is up. Its plan comes from a committed scene cache
([architecture](docs/architecture.md#demo-scene-cache-12)) and its four furniture meshes from a
committed furniture cache. Other floor plans still need `FAL_KEY` to read their labels.
Provider keys, endpoints and extras are listed in
[the asset README](services/reconstruction/assets/README.md#provider-configuration-and-dependencies).
`PUT /scenes/<scene_id>` keeps the user's furniture poses and `POST /scenes/<scene_id>/scale`
corrects a floor's scale from one wall's real length (see [architecture](docs/architecture.md#corrections-11)).

The editor loads assembled rooms from reconstruction, then updates **Stats** from
`POST /audit` after each committed furniture edit. It shows collisions, boundaries,
blocked doors, front clearance and 50 cm walking reachability. Feng Shui scores
refresh separately after committed edits, with rule coverage, breakdowns, assumptions
and any cap caused by fit or door findings. The score is a traditional placement
guide; a room that cannot be scored shows **Not assessable**. Proposal previews
compare the original and proposed scores and coverage before acceptance. Overall
score and glare remain **Not checked**. Audits and Feng Shui scoring need no
provider credentials.
If reconstruction is unavailable, the editor keeps its local demo room with a
warning; some local rooms cannot pass the backend's stricter door validation.

In **Chat**, ask for a rearrangement, e.g. “Unblock the door, but keep the bed where
it is.” Set `ANTHROPIC_API_KEY` in root `.env` and run the spatial service for live
layout suggestions. The existing tool-calling agent returns a **Room diff**:
dashed/current and green/proposed footprints, item moves and turns, and measured
findings. **Accept layout** moves the furniture together and refreshes Stats;
**Reject** leaves the room untouched. Editing the room makes older proposals
outdated. Requests can take up to 90 seconds; Cancel stops waiting without changing
the room (it does not guarantee an in-progress provider call stops). Each request
uses the current room and your new instruction; include any locks in that request.
While Refresh works, Chat streams its current execution stage and an expandable
activity log. The log remains with the final or cancelled reply; the layout preview
appears only after validation. Cancel stops later harness work, although an active
provider call may finish within its timeout. Streaming requires no new configuration.

Ask **“optimise the feng shui”** to propose a layout using the Feng Shui skill
and the same full-rule score shown in Stats. The agent uses the weighted rule
breakdown and coverage to choose moves; review the preview before accepting.
Unknown mirrors and assumed occupant positions remain visible limitations.

Scoring and goal ranking remain backend-owned. See the
[spatial service guide](services/spatial_engine/README.md) and
[frontend handoff](docs/dev3-spatial-handoff.md).

**Room versions** on the left keeps the starting layout, accepted agent layouts
and explicitly saved manual layouts. Manual moves, rotations, additions and deletions
remain a working draft until **Ctrl+S** (**Cmd+S** on Mac) or **Save version** saves
them together as one version. Repeated saves without changes create nothing.
Successive saves form a linear chain; go back, edit and save an older version to
create a branch while preserving its existing successors. Save or **Discard changes**
before selecting another version. Clicking a saved version restores its full layout
and refreshes Stats. Agent acceptance still saves immediately. Versions are kept
while the room is open; opening another room or reloading starts a new history.

**Library** offers the 31 movable mesh models from the demo home. Select a model's
name to preview and rotate it, then **Add** to place a copy in the room. Mesh URLs,
metric bounds and collision parts are preserved, so additions work with chat,
Stats and version history. These are simplified room models with estimated
dimensions; Library no longer shows invented retail products or prices. Live
product search and URL import remain separate integrations.

```bash
bun run build             # TypeScript check + production frontend bundle
bun run check             # Frontend lint/format/types + Python lint/format/types/tests
```

In the room editor, select furniture and use the ↶ / ↷ buttons or Q / E to
rotate it 90° counterclockwise / clockwise. Left / right arrows rotate it 5°
at a time (hold to repeat). Hold WASD to pan the camera relative to its current
view. Shortcuts are inactive while typing or dragging furniture; fixed fixtures
cannot be rotated. Run editor control tests with `bun test ./frontend/tests`.

To explore at human scale, drag the human from the bottom-right launcher onto
clear floor. The green/red preview shows whether there is room to stand. Press
Play, then use WASD to walk and the mouse to look around. Esc returns to the
previous editor camera and leaves the human where you walked. Drag the mannequin
to relocate it or use Remove human. Walking respects walls and furniture using
a 50 cm body and 1.6 m eye height; it does not change the room layout or revision.
Play requires mouse capture in a desktop browser. Jumping, stairs and leaving
the room through doorways are not supported.

In Play, press **L** to pause walking and open **Room lighting**. Adjust
**Artificial light** (0–100%) independently of **Time of day** (15-minute steps),
then click **Resume** to capture the mouse again. Esc or **Return to editor**
restores the editor camera. Lighting starts at 50% artificial light and 14:00;
settings survive play sessions until another room is opened.

Music and editor sounds are on by default. Browsers may wait for the first click
or keypress before playing audio. Use the speaker button or **M** to mute; open
**Sound** for independent music/effects toggles and volumes. Preferences are saved
in this browser. M is inactive while typing. In Play, M still works; press L or
Esc before using the sound panel. Hidden tabs pause audio and resume when visible.
The bundled soundtrack is “Reverie” by Scott Buckley (CC BY 4.0); credits are in
the sound panel and [audio notice](frontend/public/audio/NOTICE.md). Include that
credit in the description when uploading a recorded demo to YouTube.

Play uses textured, physically based materials, window daylight, moving sunlight
and furniture shadows. The editor retains its ink style. Daylight is an
illustrative clear day, rising east at 06:00 and setting west at 18:00, using the
floor-plan north when present (otherwise north is up the plan). Bounced light
and broad reflections are approximated; this is not a measured daylight or glare
assessment. No location, API key or external lighting assets are required.

For smaller Python installs, use `uv sync --extra spatial`, `--extra reconstruction`,
or `--extra media` instead of `--all-extras`. `uv sync` installs the common API and
development tools. Frontend dependencies and lockfile live in `frontend/`;
Python dependencies and `uv.lock` live at the root. Use `bun add --cwd frontend`
for frontend libraries and `uv add` for Python libraries, coordinating shared manifest edits.

See [architecture](docs/architecture.md) for ownership and API boundaries and
[decisions](docs/decisions.md) for bootstrap trade-offs.

Dev 2's [furniture frame selector](services/reconstruction/assets/README.md#implemented-frame-selection-and-identity-14)
can now sample walkthroughs, persist furniture identities and produce a local evidence report.
It requires FFmpeg/FFprobe. Offline reviewed replay needs no keys; live fal vision proposals
require inventory review. Its [mask stage](services/reconstruction/assets/README.md#implemented-masks-and-placement-evidence-15)
then stores an instance mask and cut-out per item view, offline with GrabCut or through fal SAM 3.
The [mesh stage](services/reconstruction/assets/README.md#implemented-individual-raw-meshes-and-proxy-fallback-16)
now reconstructs individual raw meshes with explicit proxy fallback. Mesh normalisation
and final room placement remain later stages.

In the editor's **Chat** tab, ask to add one item (for example, “Add a small
desk from Library”) or rearrange existing furniture. Start the spatial service
and configure `ANTHROPIC_API_KEY` in the root `.env` for agent requests. Review the
proposal, then choose **Accept layout**. The bot can only select real mesh models from Library, retaining their
dimensions and collision metadata; collision, floor-boundary and door checks run on it,
and on anything moved to make room, before it is proposed. Problems the room already
had are reported rather than blocking the addition. The preview includes streamed
execution updates; acceptance saves a room version and refreshes Stats, including
any front-clearance warnings. Editing the room invalidates older proposals. Retailer search and live
furniture-mesh generation are separate from this flow. If no suitable Library model
is available or fits, the bot offers other choices instead of creating a proxy.

In the editor's **Library**, paste an IKEA or other retailer product URL, click
**Import product** (or press Enter), then **Add** on the imported result. Run the
reconstruction service on port 8001. This uses published product dimensions and
models first. With `FAL_KEY` configured, SAM 3 creates masks and SAM 3D
generates geometry when retailer models are unusable; otherwise it shows a labelled
proxy. Check any dimension warnings before relying on the fit indicator. Retailer
blocking or unreadable pages are reported in the Library so you can retry.
