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
  `AuditReport.glare_orientation_grounded` is False when that fallback is assessed;
  it is None when glare is not assessed).
- Every furniture .glb has its bounding-box bottom-centre at the origin and its front facing +Z.
  `Pose2D.x/z` is where that bottom-centre sits in room coordinates; Y is currently always 0
  (on the floor).
  `bbox_m` is authoritative: the mesh is scaled to fit it and its bounds match `bbox_m` within
  GLB_BBOX_TOLERANCE_M per axis (see `FurnitureItem.glb_url`).
- `floor_polygon` is a simple (non-self-intersecting) polygon wound clockwise in plan view
  (+X right, +Z down the page). Equivalently, its shoelace sum over (x, z),
  sum(x[i] * z[i+1] - x[i+1] * z[i]), is positive. Walls run start -> end in the same direction,
  so for a wall direction d = (dx, dz) the room is on the (-dz, dx) side and the outward normal is
  (dz, -dx). This holds for non-convex (e.g. L-shaped) rooms.
- Wall `start`/`end` lie on the wall's interior (room-side) face. The wall's thickness extends
  along the outward normal. So `floor_polygon` is the usable interior floor and an item flush
  against a wall has its back exactly on the wall line.
- The shell .glb (`RoomScene.shell_glb_url`) is NOT normalised like furniture: it is authored in
  room coordinates with identity transforms, with the floor's top surface at Y=0. It is derived
  from `floor_polygon`/`walls`/`windows`/`doors`, which stay authoritative; the audit never reads
  it. It contains one node per element, named `floor`, `ceiling` and `wall_<wall_id>`. Viewers
  hide `ceiling` whenever the camera is above it (plan and orbit views, renders from above).

Occupied volume and collision (the editor preview and the audit MUST agree on these):

- `FurnitureItem.collision_parts` lists boxes in the item's local frame. An empty list means
  one solid box filling `bbox_m`. Every part lies inside `bbox_m` (tolerance
  GLB_BBOX_TOLERANCE_M).
- Parts rotate with the item's yaw, so each stays a vertical prism: a rotated rectangle in
  plan with a height range [y_min, y_max].
- Two items collide when some part of one and some part of the other overlap in plan by more
  than MIN_PLAN_OVERLAP_M2 and in height by more than MIN_HEIGHT_OVERLAP_M. Touching is not a
  collision. Test `bbox_m` footprints first as a broad phase.
- `CollisionIssue.overlap_area_m2` is the plan area of the union of overlapping part pairs.
- Walkable floor is blocked by any part whose y_min is below WALK_HEADROOM_M.
- A door leaf and a sun ray test against the parts in their height range.
- `is_fixed` items take part in every check but are never moved by the editor or the solver.
- A chair never blocks another item's `requires_front_clear_m` zone: it is pushed in or out
  in use (e.g. tucked under a desk).

Room inputs and scale (see `RoomCaptureInputs`):

- A room is captured from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images and 1..MAX_ROOM_VIDEOS
  videos.
- Metric scale comes from the dimension labels printed on the floor plan. Labelled lengths are
  read directly and the remaining walls are scaled from them; geometry sized this way is
  `dimension_source = "measured"`. Without readable labels, sizes are `estimated` and
  `"dimensions"` is added to `correction_needed`.
"""

from typing import Annotated, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

GLB_BBOX_TOLERANCE_M = 0.001
"""Maximum per-axis difference between a furniture mesh's bounds and its `bbox_m`."""

# An absolute http(s) URL or a site-root path; rejects relative and protocol-relative ("//") paths.
GLB_URL_PATTERN = r"^(https?://|/[^/])"

# Opaque and URL-safe. No code may parse meaning out of an item ID.
ITEM_ID_PATTERN = r"^[a-z0-9][a-z0-9_-]{0,63}$"

MAX_COLLISION_PARTS = 12
MIN_PART_DIMENSION_M = 0.01
MIN_PLAN_OVERLAP_M2 = 0.0001
"""Two parts overlap in plan only when their intersection exceeds this area (1 cm^2)."""
MIN_HEIGHT_OVERLAP_M = 0.005
"""Two parts overlap in height only when their ranges share more than this."""
WALK_HEADROOM_M = 2.0
"""A part whose y_min is below this blocks the floor beneath it for walking."""

MAX_LAYOUT_INSTRUCTION_CHARS = 500

LayoutGoal = Literal["balanced", "brighter", "roomier", "minimal_changes", "feng_shui", "custom"]
"""What a layout suggestion should favour once it fits and doors are clear. `balanced`: access
in front of furniture, then walking space. `brighter`: unobstructed windows first. `roomier`:
walking space first. `minimal_changes`: move furniture only to fix a fit or access problem.
`feng_shui`: raise the Feng Shui placement score (`AuditReport.feng_shui`).
`custom`: the request is something else (e.g. "a cosy reading corner"); the assistant
follows the user's wording and only fit, doors and access are checked, so the user judges
the rest in the preview."""

MAX_FLOOR_PLAN_IMAGES = 5
MAX_ROOM_VIDEOS = 5
MediaUrl = Annotated[str, Field(pattern=GLB_URL_PATTERN)]


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
    id: str = Field(pattern=r"^[A-Za-z0-9_-]+$")
    """Also names the shell node `wall_<id>`. Restricted because Three.js strips characters such
    as `.`, `:` and `/` from glTF node names."""
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
    """Outward normal of `wall_id` as a plan bearing (clockwise from -Z viewed from above, see
    module doc). Derived: the wall's geometry wins if they disagree."""
    compass_azimuth_deg: Optional[float] = None
    """True compass azimuth (0 = North) = (plan_normal_deg - north_compass_deg) mod 360. Derived:
    `north_compass_deg` wins if they disagree. None when the floor plan has no compass."""


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
    head_height_m: float = 2.05
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


class CollisionPart(ContractModel):
    """One box of an item's occupied volume, in the item's local frame (the .glb frame):
    origin at the bounding-box bottom-centre, +Y up, front facing +Z. See module doc."""

    # A NaN would pass every bounds comparison and make the part never collide.
    model_config = ConfigDict(allow_inf_nan=False)

    x: float
    """Centre along X."""
    z: float
    """Centre along Z."""
    width: float
    """Extent along X."""
    depth: float
    """Extent along Z."""
    y_min: float
    """Bottom, metres above the floor."""
    y_max: float
    """Top, metres above the floor."""


class FurnitureItem(ContractModel):
    id: str = Field(pattern=ITEM_ID_PATTERN)
    """Stable across reconstruction, editing, audit and proposals. Never reassigned. Opaque:
    category and source are fields, never parsed out of the ID."""
    name: str
    category: Literal[
        "bed", "desk", "chair", "table", "wardrobe", "sofa", "storage", "fixture", "other"
    ]
    """`fixture` is part of the room (e.g. a radiator) and requires `is_fixed`."""
    source: Literal["extracted_video", "catalog_search", "url_import"]
    glb_url: str = Field(pattern=GLB_URL_PATTERN)
    """An absolute http(s) URL or a site-root path (e.g. `/mock_room/bed.glb`) that the frontend
    fetches as-is. Never a filesystem path or a raw provider (fal) URL: generated meshes are
    downloaded, normalised and re-hosted (by convention: the pattern only rejects relative URLs).
    The file behind a URL is immutable, so replacing a mesh (e.g. a proxy with a real mesh) means a
    new `glb_url` on the same `id`, and clients may cache by URL. `bbox_m` is authoritative: the
    mesh is scaled to fit it, within GLB_BBOX_TOLERANCE_M per axis, so swapping the mesh never
    invalidates an audit."""
    product_url: Optional[str] = None
    price_gbp: Optional[float] = None
    bbox_m: BBoxM
    """Authoritative metric size; the mesh is fitted to it (see `glb_url`)."""
    pose: Pose2D
    has_screen: bool = False
    requires_front_clear_m: float = 0.6
    wall_flush_preferred: bool = True
    is_proxy: bool = False
    """True when `glb_url` is a dimensioned placeholder box because mesh extraction failed.
    The editor must label proxies visibly."""
    dimension_source: Literal["measured", "catalog", "estimated", "user_corrected"] = "estimated"
    """Provenance of `bbox_m`: `measured` from the capture, `catalog` from retailer-published
    dimensions, `user_corrected` by the user, or `estimated`. All but `estimated` are trusted."""
    correction_needed: List[Literal["dimensions", "placement", "orientation"]] = []
    """What is uncertain and should be confirmed by the user; the editor prompts for each entry."""
    collision_parts: List[CollisionPart] = []
    """Occupied volume as boxes inside `bbox_m`, so items can nest (a chair under a desk).
    Empty means one solid box filling `bbox_m`. See module doc for the collision rule."""
    collision_source: Literal["template", "mesh", "user_corrected"] = "template"
    """Where `collision_parts` came from: a category template fitted to `bbox_m`, the mesh, or the
    user. A nested fit that relies on `template` parts is an estimate. Ignored when empty."""
    is_fixed: bool = False
    """True when the item is part of the room. The editor does not drag it and the solver does
    not move it; it still takes part in every check."""

    @model_validator(mode="after")
    def _check_collision_parts(self) -> "FurnitureItem":
        if len(self.collision_parts) > MAX_COLLISION_PARTS:
            raise ValueError(f"at most {MAX_COLLISION_PARTS} collision parts per item")
        tol, box = GLB_BBOX_TOLERANCE_M, self.bbox_m
        for i, part in enumerate(self.collision_parts):
            if min(part.width, part.depth, part.y_max - part.y_min) < MIN_PART_DIMENSION_M:
                raise ValueError(f"collision part {i} is thinner than {MIN_PART_DIMENSION_M} m")
            if (
                abs(part.x) + part.width / 2 > box.width / 2 + tol
                or abs(part.z) + part.depth / 2 > box.depth / 2 + tol
                or part.y_min < -tol
                or part.y_max > box.height + tol
            ):
                raise ValueError(f"collision part {i} lies outside bbox_m")
        if self.category == "fixture" and not self.is_fixed:
            raise ValueError("a `fixture` item must have is_fixed set")
        return self


class RoomCaptureInputs(ContractModel):
    """What the user uploads for one room. Scale is read from the dimension labels on the floor
    plan (see module doc)."""

    scene_id: str
    floor_plan_image_urls: List[MediaUrl] = Field(min_length=1, max_length=MAX_FLOOR_PLAN_IMAGES)
    """Images of the same floor plan (pages, crops or photos). Same URL rules as `glb_url`."""
    video_urls: List[MediaUrl] = Field(min_length=1, max_length=MAX_ROOM_VIDEOS)
    """Walkthrough videos of the room. Same URL rules as `glb_url`."""


class RoomScene(ContractModel):
    scene_id: str
    revision: int = Field(default=0, ge=0)
    """Increments on every edit (the editor owns it after load). Services echo the revision they
    computed against so consumers can discard stale responses."""
    shell_glb_url: str = Field(pattern=GLB_URL_PATTERN)
    """Room-coordinate shell derived from the fields below (see module doc for its frame and
    node names). Same URL rules as `FurnitureItem.glb_url`."""
    floor_polygon: List[Vec2]
    """Interior floor outline (the walls' room-side faces). Simple polygon, wound clockwise in plan
    view (positive shoelace sum over (x, z)); see module doc."""
    walls: List[WallSegment]
    windows: List[WindowOpening]
    doors: List[DoorOpening]
    furniture: List[FurnitureItem]
    north_compass_deg: Optional[float] = None
    """Plan bearing (clockwise from -Z) at which true North points. Compass azimuth of a plan
    bearing b is (b - north_compass_deg) mod 360. None => -Z is North, glare is ungrounded."""
    sun_hour: float = Field(default=14.0, ge=6.0, le=21.0)

    @model_validator(mode="after")
    def _check_winding(self) -> "RoomScene":
        """floor_polygon is clockwise in plan view and every wall has the room on its (-dz, dx)
        side. Self-intersection is not checked."""
        poly = [(p.x, p.z) for p in self.floor_polygon]
        n = len(poly)
        if n < 3:
            raise ValueError("floor_polygon needs at least 3 points")
        shoelace = sum(poly[i - 1][0] * poly[i][1] - poly[i][0] * poly[i - 1][1] for i in range(n))
        if shoelace <= 0:
            raise ValueError("floor_polygon must be wound clockwise in plan view")

        def inside(x: float, z: float) -> bool:
            hits = False
            for (x0, z0), (x1, z1) in zip(poly, poly[1:] + poly[:1]):
                if (z0 > z) != (z1 > z) and x < x0 + (z - z0) * (x1 - x0) / (z1 - z0):
                    hits = not hits
            return hits

        for w in self.walls:
            dx, dz = w.end.x - w.start.x, w.end.z - w.start.z
            length = (dx * dx + dz * dz) ** 0.5
            mid_x, mid_z = (w.start.x + w.end.x) / 2, (w.start.z + w.end.z) / 2
            if length == 0 or not inside(mid_x - 0.01 * dz / length, mid_z + 0.01 * dx / length):
                raise ValueError(f"wall {w.id} must run with the room on its (-dz, dx) side")
        return self


class ParsedRoom(ContractModel):
    """One room parsed from a floor plan. `scene` uses its floor's shared frame (see
    `ParsedFloor`), so rooms on the same floor can be shown alone or together."""

    room_id: str = Field(pattern=ITEM_ID_PATTERN)
    """Unique within the plan. Opaque, like item IDs."""
    name: str
    """The printed label (e.g. "Bedroom (4)"), or "Unlabelled space <n>"."""
    labelled_width_m: Optional[float] = None
    """First printed dimension, when a label was read. Plans do not say which axis it is."""
    labelled_depth_m: Optional[float] = None
    """Second printed dimension, when a label was read."""
    area_m2: float
    """Area of `scene.floor_polygon`."""
    dimension_source: Literal["measured", "estimated", "user_corrected"]
    """`measured` when the floor's scale came from printed dimension labels."""
    correction_needed: List[Literal["dimensions", "openings", "orientation"]] = []
    """What the user should confirm: scale, door/window detection, or north."""
    scene: RoomScene
    """The room with `furniture == []`. `scene.scene_id` is `<plan_id>-<room_id>`."""


class ParsedFloor(ContractModel):
    """One storey. Every room's coordinates share this floor's frame: metres, origin at the
    top-left of the floor's wall bounds, +X right and +Z down the source image."""

    floor_id: str = Field(pattern=ITEM_ID_PATTERN)
    name: str
    """The printed caption (e.g. "First floor"), or "Floor <n>"."""
    level: int
    """0 = ground. Ordered by caption when read, otherwise by position on the sheet."""
    source_image_index: int = Field(ge=0)
    """Index into the uploaded floor-plan images."""
    rooms: List[ParsedRoom]


class ParsedFloorPlan(ContractModel):
    """Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images. The editor
    picks one `ParsedRoom.scene` to load."""

    plan_id: str = Field(pattern=ITEM_ID_PATTERN)
    """Derived from the image bytes, so re-uploading the same plan yields the same ID."""
    floors: List[ParsedFloor]
    warnings: List[str] = []
    """Human-readable notes on anything uncertain (unread labels, rejected scale estimates)."""


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
    overall_score: Optional[int] = None
    """None means scoring is not implemented/assessed; never interpret it as zero."""
    walkable_floor_ratio: Optional[float] = None
    """Reachable floor fraction for a 0.5 m wide standing person, unioned across all doors.
    None means no entry doors are known. Known but blocked entries produce zero.
    This is distinct from raw unoccupied floor area; see the spatial service README."""
    glare_orientation_grounded: Optional[bool] = None
    """None when glare is not assessed; True for grounded orientation, False only for an
    assessment that used the plan-normal/-Z fallback."""
    collisions: List[CollisionIssue]
    blocked_doors: List[BlockedDoorIssue]
    out_of_bounds_item_ids: List[str] = []
    """Items whose footprint leaves the floor polygon or intersects a wall."""
    clearance_issues: List[ClearanceIssue] = []
    glare_alerts: Optional[List[GlareAlert]] = None
    """None means not assessed; an empty list means assessed with no alerts."""
    feng_shui: Optional[FengShuiReport] = None
    """None means not assessed. Do not manufacture a score for an unavailable assessment."""


class OptimiseRequest(ContractModel):
    scene: RoomScene
    locked_item_ids: List[str] = []
    """Items the optimiser must not move."""
    max_candidates: int = Field(default=200, ge=1)
    """Upper bound on layouts evaluated; the server applies its own lower cap."""
    instruction: Optional[str] = Field(default=None, max_length=MAX_LAYOUT_INSTRUCTION_CHARS)
    """The user's request in their own words, e.g. "keep the bed, move the desk near the
    window". Interpreted by the assistant; it can add locks but never unlock or move fixed items."""
    goal: Optional[LayoutGoal] = None
    """An explicit choice from the UI. It overrides any goal read from `instruction`. When both
    are None the goal is `balanced`."""


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
    """False when no candidate beat the current layout. That is an honest result, not an error.
    When False, `poses` is empty and `report` audits the unchanged base scene."""
    outcome: Literal["completed", "stopped_early", "assistant_unavailable"] = "completed"
    """`completed`: the assistant finished exploring. `stopped_early`: a time, call or evaluation
    limit, or an assistant error, cut exploration short; an `improved` proposal is still fully
    verified. `assistant_unavailable`: the assistant could not be used and nothing was found, so
    `improved` is False. Show the last two as such; do not present them as "no better layout"."""
    goal: Optional[LayoutGoal] = None
    """The goal that was applied (explicit, read from the instruction, or `balanced`)."""
    explanation: str = ""
    """Plain text for the preview, built by the server from measured results. It also lists
    parts of the instruction that could not be handled."""


class RenderCamera(ContractModel):
    position: Vec3
    target: Vec3
    fov_deg: float
    """Vertical field of view (perspective camera). The camera's up vector is +Y (no roll)."""
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
