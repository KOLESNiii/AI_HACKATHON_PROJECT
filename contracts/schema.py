from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class Vec2(BaseModel):
    x: float
    z: float


class Vec3(BaseModel):
    x: float
    y: float
    z: float


class WallSegment(BaseModel):
    id: str
    start: Vec2
    end: Vec2
    height_m: float = 2.6
    thickness_m: float = 0.15


class WindowOpening(BaseModel):
    id: str
    wall_id: str
    offset_along_wall_m: float
    width_m: float
    sill_height_m: float = 0.9
    head_height_m: float = 2.1
    plan_normal_deg: float
    compass_azimuth_deg: Optional[float] = None


class DoorOpening(BaseModel):
    id: str
    wall_id: str
    hinge_pos: Vec2
    width_m: float = 0.85
    swing_angle_deg: float = 90.0
    swing_clockwise: bool = True


class BBoxM(BaseModel):
    width: float
    height: float
    depth: float


class Pose2D(BaseModel):
    x: float
    z: float
    yaw_deg: float = 0.0


class FurnitureItem(BaseModel):
    id: str
    name: str
    category: Literal["bed", "desk", "chair", "wardrobe", "sofa", "storage", "other"]
    source: Literal["extracted_video", "catalog_search", "url_import"]
    glb_url: str
    product_url: Optional[str] = None
    price_gbp: Optional[float] = None
    bbox_m: BBoxM
    pose: Pose2D
    has_screen: bool = False
    requires_front_clear_m: float = 0.6
    wall_flush_preferred: bool = True


class RoomScene(BaseModel):
    scene_id: str
    shell_glb_url: str
    floor_polygon: List[Vec2]
    walls: List[WallSegment]
    windows: List[WindowOpening]
    doors: List[DoorOpening]
    furniture: List[FurnitureItem]
    north_compass_deg: Optional[float] = None
    sun_hour: float = Field(default=14.0, ge=6.0, le=21.0)


class CollisionIssue(BaseModel):
    item_a: str
    item_b: str
    overlap_area_m2: float


class BlockedDoorIssue(BaseModel):
    door_id: str
    blocked_by_item_id: str


class GlareAlert(BaseModel):
    item_id: str
    window_id: str
    severity: Literal["none", "warning", "severe"]
    sun_ray_start: Vec3
    sun_ray_end: Vec3


class FengShuiSightline(BaseModel):
    from_item_id: str
    to_door_id: str
    status: Literal["command_position", "back_to_door", "coffin_alignment"]
    reason: str


class FengShuiReport(BaseModel):
    score: int
    sightlines: List[FengShuiSightline]


class AuditReport(BaseModel):
    overall_score: int
    walkable_floor_ratio: float
    glare_orientation_grounded: bool
    collisions: List[CollisionIssue]
    blocked_doors: List[BlockedDoorIssue]
    glare_alerts: List[GlareAlert]
    feng_shui: FengShuiReport