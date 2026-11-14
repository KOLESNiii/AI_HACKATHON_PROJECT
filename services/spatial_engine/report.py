"""Compose the implemented checks into the shared audit response."""

from contracts.schema import AuditReport, RoomScene
from services.spatial_engine.audit import (
    detect_blocked_doors,
    detect_collisions,
    detect_front_clearance,
    detect_out_of_bounds,
)
from services.spatial_engine.reachability import calculate_reachable_floor_ratio


def audit_scene(scene: RoomScene) -> AuditReport:
    """Audit without network access or mutation; unavailable assessments stay null.

    Domain-invalid geometry raises ValueError for the HTTP adapter to map to 422.
    Reachability requires at least one door; unknown entry must not appear clear.
    """
    return AuditReport(
        scene_id=scene.scene_id,
        scene_revision=scene.revision,
        collisions=detect_collisions(scene.furniture),
        out_of_bounds_item_ids=detect_out_of_bounds(scene),
        blocked_doors=detect_blocked_doors(scene),
        clearance_issues=detect_front_clearance(scene),
        walkable_floor_ratio=calculate_reachable_floor_ratio(scene),
        glare_orientation_grounded=False,
        overall_score=None,
        glare_alerts=None,
        feng_shui=None,
    )
