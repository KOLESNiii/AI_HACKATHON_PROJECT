"""SpaceShift shared contracts. This file is the source of truth; schema.ts mirrors it.

Coordinate conventions (all services and the editor MUST agree on these):

- Units are metres. Right-handed, Y-up: X = width, Y = height (Y=0 is the floor), Z = depth.
- Plan view is looking down -Y from above. On screen +X points right and -Z points up,
  so +Z points down the page.
- Furniture yaw (`Pose2D.yaw_deg`): rotation about +Y, counter-clockwise when viewed from above
  (the right-hand rule, identical to Three.js `rotation.y = yaw_deg * PI / 180`).
  The item's front direction is (sin(yaw), 0, cos(yaw)):
  yaw 0 = front faces +Z, 90 = +X, 180 = -Z, 270 = -X.
- Plan bearings (`WindowOpening.plan_normal_deg`, `RoomScene.north_compass_deg`) use a DIFFERENT,
  compass-style convention: clockwise from -Z when viewed from above. Direction is
  (sin(b), 0, -cos(b)): 0 = -Z ("up"), 90 = +X, 180 = +Z, 270 = -X.
  Convert between them with: bearing = (180 - yaw) mod 360.
- True compass azimuth of any plan bearing b: azimuth = (b - north) mod 360, where
  north = `RoomScene.north_compass_deg`, or 0 when it is None (fallback: -Z is North, and
  `AuditReport.glare_orientation_grounded` is False).
- Every furniture .glb has its bounding-box bottom-centre at the origin and its front facing +Z.
  `Pose2D.x/z` is where that bottom-centre sits in room coordinates; Y is always 0 (on the floor).
- Wall `start`/`end` lie on the wall's interior (room-side) face. The wall's thickness extends
  outward, away from `floor_polygon`. So `floor_polygon` is the usable interior floor and an
  item flush against a wall has its back exactly on the wall line.
"""

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ContractModel(BaseModel):
    # Publish the attribute docstrings below as field descriptions in OpenAPI (/docs).
    model_config = ConfigDict(use_attribute_docstrings=True)


class Vec2(ContractModel):
    """A point on the floor plan (Y omitted)."""

    x: float
    z: float


class Vec3(ContractModel):
    x: float
    y: float
    z: float


class WallSegment(ContractModel):
    id: str
    start: Vec2
    """Interior (room-side) face; thickness extends outward, away from the floor polygon."""
    end: Vec2
    height_m: float = 2.6
    thickness_m: float = 0.15


class WindowOpening(ContractModel):
    id: str
    wall_id: str
    offset_along_wall_m: float
    """Distance from the wall's `start` to the near edge of the opening, along the wall."""
    width_m: float
    sill_height_m: float = 0.9
    head_height_m: float = 2.1
    plan_normal_deg: float
    """Outward normal as a plan bearing: clockwise from -Z viewed from above (see module doc)."""
    compass_azimuth_deg: Optional[float] = None
    """True compass azimuth (0 = North). None when the floor plan has no compass."""


class DoorOpening(ContractModel):
    """A hinged door in a wall.

    `hinge_pos` lies on the wall's interior-face line. The closed leaf runs along the wall from
    the hinge for `width_m`. Opening rotates the leaf about the hinge, clockwise (viewed from
    above) when `swing_clockwise` is true, towards the room side when `swings_into_room` is true.
    Those two fields decide which way along the wall the closed leaf lies: rotating the
    wall-parallel closed leaf by 90 degrees in the swing direction must point it to the swing side.
    `swing_angle_deg` is only how far it opens.
    Example: hinge on a wall running along X with the room on +Z, swinging clockwise into the
    room, means the closed leaf extends toward +X and the leaf at 90 degrees points +Z.
    """

    id: str
    wall_id: str
    hinge_pos: Vec2
    width_m: float = 0.85
    swing_angle_deg: float = 90.0
    swing_clockwise: bool = True
    """Direction of opening, viewed from above (plan view, -Z up)."""
    swings_into_room: bool = True
    """False when the door opens outward, away from the floor polygon."""


class BBoxM(ContractModel):
    """Canonical metric bounds in the item's local frame: width along X, height along Y,
    depth along Z (front faces +Z)."""

    width: float
    height: float
    depth: float


class Pose2D(ContractModel):
    """Floor placement of an item's bounding-box bottom-centre. See module doc for yaw."""

    x: float
    z: float
    yaw_deg: float = 0.0
    """Counter-clockwise about +Y viewed from above. Equals Three.js rotation.y (in degrees)."""


class FurnitureItem(ContractModel):
    id: str
    """Stable across reconstruction, editing, audit and proposals. Never reassigned."""
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
    is_proxy: bool = False
    """True when `glb_url` is a dimensioned placeholder box because mesh extraction failed.
    The editor must label proxies visibly."""
    dimension_source: Literal["measured", "estimated", "user_corrected"] = "estimated"
    """Provenance of `bbox_m`. Only `measured`/`user_corrected` count as exact."""
    needs_correction: bool = False
    """True when scale or placement is uncertain; the editor prompts the user to correct it."""


class RoomScene(ContractModel):
    scene_id: str
    revision: int = Field(default=0, ge=0)
    """Increments on every edit (the editor owns it after load). Services echo the revision they
    computed against so consumers can discard stale responses."""
    shell_glb_url: str
    floor_polygon: List[Vec2]
    """Interior floor outline (the walls' room-side faces)."""
    walls: List[WallSegment]
    windows: List[WindowOpening]
    doors: List[DoorOpening]
    furniture: List[FurnitureItem]
    north_compass_deg: Optional[float] = None
    """Plan bearing (clockwise from -Z) at which true North points. Compass azimuth of a plan
    bearing b is (b - north_compass_deg) mod 360. None => -Z is North, glare is ungrounded."""
    sun_hour: float = Field(default=14.0, ge=6.0, le=21.0)


class CollisionIssue(ContractModel):
    item_a: str
    item_b: str
    overlap_area_m2: float


class BlockedDoorIssue(ContractModel):
    door_id: str
    blocked_by_item_id: str


class ClearanceIssue(ContractModel):
    """An item's required front clearance (`requires_front_clear_m`) is not met."""

    item_id: str
    required_m: float
    actual_m: float
    blocked_by_item_id: Optional[str] = None
    """The furniture item in the way, or None when a wall or the room boundary is in the way."""


class GlareAlert(ContractModel):
    item_id: str
    window_id: str
    severity: Literal["none", "warning", "severe"]
    sun_ray_start: Vec3
    sun_ray_end: Vec3


class FengShuiSightline(ContractModel):
    from_item_id: str
    to_door_id: str
    status: Literal["command_position", "back_to_door", "coffin_alignment"]
    reason: str


class FengShuiReport(ContractModel):
    score: int
    sightlines: List[FengShuiSightline]


class AuditReport(ContractModel):
    scene_id: str
    """Echo of the audited RoomScene.scene_id. Required so an un-echoed report fails validation."""
    scene_revision: int = Field(ge=0)
    """Echo of the audited RoomScene.revision. Consumers ignore reports older than their scene."""
    overall_score: int
    walkable_floor_ratio: float
    glare_orientation_grounded: bool
    collisions: List[CollisionIssue]
    blocked_doors: List[BlockedDoorIssue]
    out_of_bounds_item_ids: List[str] = []
    """Items whose footprint leaves the floor polygon or intersects a wall."""
    clearance_issues: List[ClearanceIssue] = []
    glare_alerts: List[GlareAlert]
    feng_shui: FengShuiReport


class OptimiseRequest(ContractModel):
    scene: RoomScene
    locked_item_ids: List[str] = []
    """Items the optimiser must not move."""
    max_candidates: int = Field(default=200, ge=1)


class LayoutProposal(ContractModel):
    """Proposed furniture poses. Only poses change: shell, openings, item IDs and glb_urls are
    preserved. To apply, copy `poses` onto matching items, bump the revision and re-audit.

    `report` is the audit of the base scene with `poses` applied, so `report.scene_id` and
    `report.scene_revision` identify the base scene (scene_revision == base revision). The
    proposal is stale when the editor's current revision differs from `report.scene_revision`.
    Remaining violations are read from `report`, not duplicated here.
    """

    proposal_id: str
    poses: Dict[str, Pose2D]
    """item_id -> proposed pose. Items not listed keep their current pose."""
    report: AuditReport
    improved: bool
    """False when no candidate beat the current layout. That is an honest result, not an error."""


class RenderCamera(ContractModel):
    position: Vec3
    target: Vec3
    fov_deg: float
    """Vertical field of view (perspective camera)."""
    near_m: float
    far_m: float


class RenderBundle(ContractModel):
    """Aligned render maps from one scene revision, camera and resolution (produced by the editor,
    consumed by the photoreal adapter).

    - `rgb_png`: 8-bit sRGB PNG.
    - `depth_png`: 16-bit greyscale PNG of linear camera-space distance along the view axis.
      Values 0..65534 encode depth_m = near_m + (value / 65534) * (far_m - near_m), with geometry
      beyond far_m clamped to 65534. 65535 is reserved for "no geometry" (background).
    - `mask_png`: 8-bit greyscale PNG of object indices.
    PNG fields are data URLs (`data:image/png;base64,...`).
    """

    scene_id: str
    scene_revision: int
    width: int
    height: int
    camera: RenderCamera
    rgb_png: str
    depth_png: str
    mask_png: str
    mask_ids: Dict[int, str]
    """Every index used in mask_png -> ID. Always contains 0 -> "background" and 1 -> "shell";
    2 and above map to furniture item IDs."""
