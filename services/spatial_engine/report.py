"""Compose the implemented checks into the shared audit response."""

from contracts.schema import AuditReport, RoomScene
from services.spatial_engine.audit import (
    detect_blocked_doors,
    detect_collisions,
    detect_front_clearance,
    detect_out_of_bounds,
)
from services.spatial_engine.geometry import prepare_scene
from services.spatial_engine.reachability import calculate_reachable_floor_ratio


def audit_scene(scene: RoomScene) -> AuditReport:
    """Audit without network access or mutation; unavailable assessments stay null.

    Domain-invalid geometry raises ValueError for the HTTP adapter to map to 422.
    No known doors leaves reachability null while preserving other findings.
    """
    prepared = prepare_scene(scene)
    blocked_doors = detect_blocked_doors(scene, _prepared=prepared)
    return AuditReport(
        scene_id=scene.scene_id,
        scene_revision=scene.revision,
        collisions=detect_collisions(scene.furniture, _prepared=prepared.furniture),
        out_of_bounds_item_ids=detect_out_of_bounds(scene, _prepared=prepared),
        blocked_doors=blocked_doors,
        clearance_issues=detect_front_clearance(scene, _prepared=prepared),
        walkable_floor_ratio=calculate_reachable_floor_ratio(
            scene, _prepared=prepared, _blocked_door_ids={issue.door_id for issue in blocked_doors}
        ),
        glare_orientation_grounded=None,
        overall_score=None,
        glare_alerts=None,
        feng_shui=None,
    )
