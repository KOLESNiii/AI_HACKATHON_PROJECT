export interface Vec2 { x: number; z: number; }
export interface Vec3 { x: number; y: number; z: number; }

export interface WallSegment {
  id: string;
  start: Vec2;
  end: Vec2;
  height_m: number;
  thickness_m: number;
}

export interface WindowOpening {
  id: string;
  wall_id: string;
  offset_along_wall_m: number;
  width_m: number;
  sill_height_m: number;
  head_height_m: number;
  /** Outward normal angle on the 2D floor plan (0 = Up/-Z, 90 = Right/+X, 180 = Down/+Z, 270 = Left/-X) */
  plan_normal_deg: number;
  /** Optional true compass azimuth (0 = North, 180 = South). Null if floor plan has no compass arrow. */
  compass_azimuth_deg?: number | null;
}

export interface DoorOpening {
  id: string;
  wall_id: string;
  hinge_pos: Vec2;
  width_m: number;
  swing_angle_deg: number; // e.g., 90
  swing_clockwise: boolean;
}

export interface FurnitureItem {
  id: string;
  name: string;
  category: "bed" | "desk" | "chair" | "wardrobe" | "sofa" | "storage" | "other";
  source: "extracted_video" | "catalog_search" | "url_import";
  glb_url: string;
  product_url?: string | null;
  price_gbp?: number | null;
  /** Canonical metric bounding box (bottom-center origin at 0,0,0; front faces +Z at yaw=0) */
  bbox_m: { width: number; height: number; depth: number };
  pose: {
    x: number;
    z: number;
    yaw_deg: number;
  };
  has_screen?: boolean;
  requires_front_clear_m: number;
  wall_flush_preferred: boolean;
}

export interface RoomScene {
  scene_id: string;
  shell_glb_url: string;
  floor_polygon: Vec2[];
  walls: WallSegment[];
  windows: WindowOpening[];
  doors: DoorOpening[];
  furniture: FurnitureItem[];
  /** True North orientation of floor plan (-Z axis) in degrees, if detected or manually calibrated */
  north_compass_deg?: number | null;
  /** Current simulated hour of day (8.0 to 19.0) */
  sun_hour: number;
}

export interface AuditReport {
  overall_score: number; // 0 - 100
  walkable_floor_ratio: number; // 0.0 - 1.0
  glare_orientation_grounded: boolean; // True if derived from floor-plan compass or manual calibration
  collisions: Array<{
    item_a: string;
    item_b: string;
    overlap_area_m2: number;
  }>;
  blocked_doors: Array<{
    door_id: string;
    blocked_by_item_id: string;
  }>;
  glare_alerts: Array<{
    item_id: string;
    window_id: string;
    severity: "none" | "warning" | "severe";
    sun_ray_start: Vec3;
    sun_ray_end: Vec3;
  }>;
  feng_shui: {
    score: number;
    sightlines: Array<{
      from_item_id: string;
      to_door_id: string;
      status: "command_position" | "back_to_door" | "coffin_alignment";
      reason: string;
    }>;
  };
}