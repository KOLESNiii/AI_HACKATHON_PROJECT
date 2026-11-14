/**
 * SpaceShift shared contracts. Mirrors contracts/schema.py (the source of truth); keep in sync.
 *
 * Coordinate conventions:
 * - Metres. Right-handed, Y-up: X = width, Y = height (0 = floor), Z = depth.
 * - Plan view looks down -Y: +X is right, -Z is up the page, +Z is down the page.
 * - Furniture yaw (`Pose2D.yaw_deg`): counter-clockwise about +Y viewed from above.
 *   Identical to Three.js `rotation.y = yaw_deg * Math.PI / 180`.
 *   Front direction = (sin(yaw), 0, cos(yaw)): 0 = +Z, 90 = +X, 180 = -Z, 270 = -X.
 * - Plan bearings (`plan_normal_deg`, `north_compass_deg`) are compass-style instead: clockwise
 *   from -Z viewed from above. Direction = (sin(b), 0, -cos(b)): 0 = -Z, 90 = +X, 180 = +Z, 270 = -X.
 *   bearing = (180 - yaw) mod 360.
 * - Compass azimuth of a plan bearing b = (b - north) mod 360, north = north_compass_deg ?? 0
 *   (null => -Z is North and glare_orientation_grounded is false).
 * - Furniture .glb: bounding-box bottom-centre at origin, front faces +Z. `Pose2D.x/z` is where
 *   that bottom-centre sits in the room; Y is currently always 0. `bbox_m` is authoritative: the
 *   mesh is scaled to fit it, within 1 mm per axis.
 * - `floor_polygon` is a simple polygon wound clockwise in plan view (positive shoelace sum
 *   over (x, z)). Walls run start -> end the same way, so for wall direction (dx, dz) the room is
 *   on the (-dz, dx) side and the outward normal is (dz, -dx). Works for non-convex rooms.
 * - Wall start/end lie on the interior (room-side) face; thickness extends along the outward
 *   normal, so `floor_polygon` is the usable interior floor.
 * - Shell .glb: NOT normalised. Room coordinates, identity transforms, floor top at Y=0. Derived
 *   from floor_polygon/walls/windows/doors (which stay authoritative). Nodes: `floor`, `ceiling`,
 *   `wall_<wall_id>`. Hide `ceiling` when the camera is above it.
 *
 * Occupied volume and collision (the editor preview and the audit MUST agree on these):
 * - `FurnitureItem.collision_parts` lists boxes in the item's local frame. An empty list means
 *   one solid box filling `bbox_m`. Every part lies inside `bbox_m` (tolerance
 *   GLB_BBOX_TOLERANCE_M).
 * - Parts rotate with the item's yaw, so each stays a vertical prism: a rotated rectangle in
 *   plan with a height range [y_min, y_max].
 * - Two items collide when some part of one and some part of the other overlap in plan by more
 *   than MIN_PLAN_OVERLAP_M2 and in height by more than MIN_HEIGHT_OVERLAP_M. Touching is not a
 *   collision. Test `bbox_m` footprints first as a broad phase.
 * - `CollisionIssue.overlap_area_m2` is the plan area of the union of overlapping part pairs.
 * - Walkable floor is blocked by any part whose y_min is below WALK_HEADROOM_M.
 * - A door leaf and a sun ray test against the parts in their height range.
 * - `is_fixed` items take part in every check but are never moved by the editor or the solver.
 * - A chair never blocks another item's `requires_front_clear_m` zone: it is pushed in or out
 *   in use (e.g. tucked under a desk).
 *
 * Room inputs and scale (see RoomCaptureInputs):
 * - A room is captured from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images and 1..MAX_ROOM_VIDEOS videos.
 * - Metric scale comes from the dimension labels printed on the floor plan. Labelled lengths are
 *   read directly and the remaining walls are scaled from them (`dimension_source: "measured"`).
 *   Without readable labels, sizes are "estimated" with "dimensions" in `correction_needed`.
 *
 * These types describe the wire format. Pydantic always serialises defaults, so every field is
 * present in service responses and in contracts/mock_room fixtures. `?` marks only nullable
 * fields (`| null`), which may be omitted.
 */

/** Maximum per-axis difference between a furniture mesh's bounds and its bbox_m. */
export const GLB_BBOX_TOLERANCE_M = 0.001;
/** Item IDs are opaque and URL-safe; never parse meaning out of one. */
export const ITEM_ID_PATTERN = /^[a-z0-9][a-z0-9_-]{0,63}$/;
export const MAX_COLLISION_PARTS = 12;
export const MIN_PART_DIMENSION_M = 0.01;
/** Two parts overlap in plan only when their intersection exceeds this area (1 cm^2). */
export const MIN_PLAN_OVERLAP_M2 = 0.0001;
/** Two parts overlap in height only when their ranges share more than this. */
export const MIN_HEIGHT_OVERLAP_M = 0.005;
/** A part whose y_min is below this blocks the floor beneath it for walking. */
export const WALK_HEADROOM_M = 2.0;
export const MAX_FLOOR_PLAN_IMAGES = 5;
export const MAX_ROOM_VIDEOS = 5;

export interface Vec2 { x: number; z: number; }
export interface Vec3 { x: number; y: number; z: number; }

export interface WallSegment {
  /** [A-Za-z0-9_-]+. Also names the shell node `wall_<id>` (Three.js strips `.`, `:`, `/`). */
  id: string;
  /** Interior (room-side) face; thickness extends outward. */
  start: Vec2;
  end: Vec2;
  height_m: number; // default 2.6
  thickness_m: number; // default 0.15
}

export interface WindowOpening {
  id: string;
  wall_id: string;
  /** Distance from the wall's `start` to the near edge of the opening, along the wall. */
  offset_along_wall_m: number;
  width_m: number;
  sill_height_m: number; // default 0.9
  head_height_m: number; // default 2.1
  /** Outward normal of wall_id as a plan bearing: clockwise from -Z viewed from above (0 = -Z, 90 = +X, 180 = +Z, 270 = -X). Derived: the wall wins if they disagree. */
  plan_normal_deg: number;
  /** True compass azimuth (0 = North) = (plan_normal_deg - north_compass_deg) mod 360. Derived: north_compass_deg wins. Null if the floor plan has no compass. */
  compass_azimuth_deg?: number | null;
}

/**
 * `hinge_pos` lies on the wall's interior-face line. The closed leaf runs along the wall from the
 * hinge for `width_m`. Opening rotates it about the hinge: clockwise viewed from above when
 * `swing_clockwise`, towards the room side when `swings_into_room`. Those two fields decide which
 * way along the wall the closed leaf lies; `swing_angle_deg` is only how far it opens.
 */
export interface DoorOpening {
  id: string;
  wall_id: string;
  hinge_pos: Vec2;
  width_m: number; // default 0.85
  head_height_m: number; // default 2.05
  swing_angle_deg: number; // default 90
  /** Opening direction viewed from above (plan view, -Z up). Default true. */
  swing_clockwise: boolean;
  /** Default true. False when the door opens away from the floor polygon. */
  swings_into_room: boolean;
}

/** Local-frame metric bounds: width along X, height along Y, depth along Z (front = +Z). */
export interface BBoxM { width: number; height: number; depth: number; }

/** Floor placement of the item's bounding-box bottom-centre. */
export interface Pose2D {
  x: number;
  z: number;
  /** Counter-clockwise about +Y viewed from above; equals Three.js rotation.y in degrees. Default 0. */
  yaw_deg: number;
}

/**
 * One box of an item's occupied volume, in the item's local frame (the .glb frame): origin at
 * the bounding-box bottom-centre, +Y up, front facing +Z.
 */
export interface CollisionPart {
  /** Centre along X. */
  x: number;
  /** Centre along Z. */
  z: number;
  /** Extent along X. */
  width: number;
  /** Extent along Z. */
  depth: number;
  /** Bottom, metres above the floor. */
  y_min: number;
  /** Top, metres above the floor. */
  y_max: number;
}

export interface FurnitureItem {
  /** Stable, never reassigned, and opaque: matches ITEM_ID_PATTERN; never parse it. */
  id: string;
  name: string;
  /** "fixture" is part of the room (e.g. a radiator) and requires is_fixed: true. */
  category: "bed" | "desk" | "chair" | "table" | "wardrobe" | "sofa" | "storage" | "fixture" | "other";
  source: "extracted_video" | "catalog_search" | "url_import";
  /**
   * Absolute http(s) URL or site-root path, fetched as-is. Never a filesystem or raw fal URL.
   * Immutable: a new mesh means a new glb_url on the same id, so cache by URL.
   */
  glb_url: string;
  product_url?: string | null;
  price_gbp?: number | null;
  /** Authoritative metric size (bottom-centre origin, front +Z at yaw 0); the mesh is fitted to it. */
  bbox_m: BBoxM;
  pose: Pose2D;
  has_screen: boolean; // default false
  requires_front_clear_m: number; // default 0.6
  wall_flush_preferred: boolean; // default true
  /** Default false. True when the mesh is a dimensioned placeholder box; label it visibly. */
  is_proxy: boolean;
  /** Default "estimated". Provenance of bbox_m; all but "estimated" are trusted. */
  dimension_source: "measured" | "catalog" | "estimated" | "user_corrected";
  /** Default []. What is uncertain; the editor prompts the user to confirm each entry. */
  correction_needed: ("dimensions" | "placement" | "orientation")[];
  /** Default []. Occupied volume as boxes inside bbox_m, so items can nest. Empty = one solid box. */
  collision_parts: CollisionPart[];
  /** Default "template". Where collision_parts came from; a fit relying on "template" is an estimate. */
  collision_source: "template" | "mesh" | "user_corrected";
  /** Default false. Part of the room: not draggable, not moved by the solver, still checked. */
  is_fixed: boolean;
}

/** What the user uploads for one room. URLs follow the glb_url rules. */
export interface RoomCaptureInputs {
  scene_id: string;
  /** 1..MAX_FLOOR_PLAN_IMAGES images of the same floor plan. */
  floor_plan_image_urls: string[];
  /** 1..MAX_ROOM_VIDEOS walkthrough videos of the room. */
  video_urls: string[];
}

export interface RoomScene {
  scene_id: string;
  /** Default 0. Incremented on every edit; services echo it so stale responses can be discarded. */
  revision: number;
  /** Room-coordinate shell; see the shell rule above. Same URL rules as glb_url. */
  shell_glb_url: string;
  /** Interior floor outline (the walls' room-side faces); clockwise in plan view. */
  floor_polygon: Vec2[];
  walls: WallSegment[];
  windows: WindowOpening[];
  doors: DoorOpening[];
  furniture: FurnitureItem[];
  /** Plan bearing at which true North points; azimuth(b) = (b - north) mod 360. Null => -Z is North. */
  north_compass_deg?: number | null;
  /** Current simulated hour of day (6.0 to 21.0, default 14.0) */
  sun_hour: number;
}

export interface CollisionIssue { item_a: string; item_b: string; overlap_area_m2: number; }

export interface BlockedDoorIssue { door_id: string; blocked_by_item_id: string; }

/** An item's requires_front_clear_m is not met. */
export interface ClearanceIssue {
  item_id: string;
  required_m: number;
  actual_m: number;
  /** Furniture in the way, or null when a wall or the room boundary is in the way. */
  blocked_by_item_id?: string | null;
}

export interface GlareAlert {
  item_id: string;
  window_id: string;
  severity: "none" | "warning" | "severe";
  sun_ray_start: Vec3;
  sun_ray_end: Vec3;
}

export interface FengShuiSightline {
  from_item_id: string;
  to_door_id: string;
  status: "command_position" | "back_to_door" | "coffin_alignment";
  reason: string;
}

export interface FengShuiReport { score: number; sightlines: FengShuiSightline[]; }

export interface AuditReport {
  /** Echo of the audited scene (required). */
  scene_id: string;
  /** Echo of the audited RoomScene.revision (required); ignore reports older than the current scene. */
  scene_revision: number;
  /** 0..100 when assessed; null means scoring unavailable, never zero. */
  overall_score: number | null;
  /** Reachable floor fraction for a 0.5 m person, unioned across doors; not raw empty floor. */
  walkable_floor_ratio: number; // 0.0 - 1.0
  glare_orientation_grounded: boolean; // True if derived from floor-plan compass or manual calibration
  collisions: CollisionIssue[];
  blocked_doors: BlockedDoorIssue[];
  /** Items whose footprint leaves the floor polygon or intersects a wall. Default []. */
  out_of_bounds_item_ids: string[];
  /** Default []. */
  clearance_issues: ClearanceIssue[];
  /** null = not assessed; [] = assessed with no alerts. */
  glare_alerts: GlareAlert[] | null;
  /** null = not assessed. */
  feng_shui: FengShuiReport | null;
}

export interface OptimiseRequest {
  scene: RoomScene;
  /** Items the optimiser must not move. Default []. */
  locked_item_ids: string[];
  max_candidates: number; // default 200
}

/**
 * Proposed poses only: shell, openings, item IDs and glb_urls are preserved. To apply, copy
 * `poses` onto matching items, bump the revision and re-audit.
 * `report` audits the base scene with `poses` applied, so report.scene_id/scene_revision identify
 * the base scene. The proposal is stale when the current revision differs from report.scene_revision.
 */
export interface LayoutProposal {
  proposal_id: string;
  /** item_id -> proposed pose; unlisted items keep their pose. */
  poses: Record<string, Pose2D>;
  report: AuditReport;
  /** False when nothing beat the current layout. That is an honest result, not an error. */
  improved: boolean;
}

export interface RenderCamera {
  position: Vec3;
  target: Vec3;
  /** Vertical field of view. Camera up is +Y (no roll). */
  fov_deg: number;
  near_m: number;
  far_m: number;
}

/**
 * Aligned render maps from one scene revision, camera and resolution.
 * - rgb_png: 8-bit sRGB PNG.
 * - depth_png: 16-bit greyscale, linear view-axis distance. Values 0..65534:
 *   depth_m = near_m + (value / 65534) * (far_m - near_m), beyond far clamped to 65534.
 *   65535 is reserved for "no geometry" (background).
 * - mask_png: 8-bit object indices (see mask_ids).
 * PNG fields are data URLs.
 */
export interface RenderBundle {
  scene_id: string;
  scene_revision: number;
  width: number;
  height: number;
  camera: RenderCamera;
  rgb_png: string;
  depth_png: string;
  mask_png: string;
  /** Every index in mask_png -> ID. Always 0 -> "background", 1 -> "shell"; 2+ -> furniture item IDs. */
  mask_ids: Record<number, string>;
}
