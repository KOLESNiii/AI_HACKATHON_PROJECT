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
 *   that bottom-centre sits in the room; Y is always 0.
 * - Wall start/end lie on the interior (room-side) face; thickness extends outward, away from
 *   `floor_polygon`, which is therefore the usable interior floor.
 *
 * These types describe the wire format. Pydantic always serialises defaults, so every field is
 * present in service responses and in contracts/mock_room fixtures. `?` marks only nullable
 * fields (`| null`), which may be omitted.
 */

export interface Vec2 { x: number; z: number; }
export interface Vec3 { x: number; y: number; z: number; }

export interface WallSegment {
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
  /** Outward normal as a plan bearing: clockwise from -Z viewed from above (0 = -Z, 90 = +X, 180 = +Z, 270 = -X). */
  plan_normal_deg: number;
  /** Optional true compass azimuth (0 = North, 180 = South). Null if floor plan has no compass arrow. */
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

export interface FurnitureItem {
  /** Stable across reconstruction, editing, audit and proposals. Never reassigned. */
  id: string;
  name: string;
  category: "bed" | "desk" | "chair" | "wardrobe" | "sofa" | "storage" | "other";
  source: "extracted_video" | "catalog_search" | "url_import";
  glb_url: string;
  product_url?: string | null;
  price_gbp?: number | null;
  /** Canonical metric bounding box (bottom-center origin at 0,0,0; front faces +Z at yaw=0) */
  bbox_m: BBoxM;
  pose: Pose2D;
  has_screen: boolean; // default false
  requires_front_clear_m: number; // default 0.6
  wall_flush_preferred: boolean; // default true
  /** Default false. True when the mesh is a dimensioned placeholder box; label it visibly. */
  is_proxy: boolean;
  /** Default "estimated". Provenance of bbox_m; only measured/user_corrected are exact. */
  dimension_source: "measured" | "estimated" | "user_corrected";
  /** Default false. Scale or placement is uncertain; prompt the user to correct it. */
  needs_correction: boolean;
}

export interface RoomScene {
  scene_id: string;
  /** Default 0. Incremented on every edit; services echo it so stale responses can be discarded. */
  revision: number;
  shell_glb_url: string;
  /** Interior floor outline (the walls' room-side faces). */
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
  overall_score: number; // 0 - 100
  walkable_floor_ratio: number; // 0.0 - 1.0
  glare_orientation_grounded: boolean; // True if derived from floor-plan compass or manual calibration
  collisions: CollisionIssue[];
  blocked_doors: BlockedDoorIssue[];
  /** Items whose footprint leaves the floor polygon or intersects a wall. Default []. */
  out_of_bounds_item_ids: string[];
  /** Default []. */
  clearance_issues: ClearanceIssue[];
  glare_alerts: GlareAlert[];
  feng_shui: FengShuiReport;
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
  /** Vertical field of view. */
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
