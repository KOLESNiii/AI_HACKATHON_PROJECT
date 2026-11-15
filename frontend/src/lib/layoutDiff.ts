import type { AuditReport, FurnitureItem, Pose2D, RoomScene } from './contracts'
import type { EditorProposal } from './agent'

export interface FurnitureChange {
  id: string
  name: string
  bbox: FurnitureItem['bbox_m']
  before: Pose2D
  added?: boolean
  removed?: boolean
  after: Pose2D
  distance: number
  turn: number
}

export function layoutChanges(
  scene: RoomScene,
  proposal: EditorProposal,
): FurnitureChange[] {
  const moves = scene.furniture.flatMap((item) => {
    const after = Object.hasOwn(proposal.poses, item.id)
      ? proposal.poses[item.id]
      : undefined
    if (!after) return []
    const before = item.pose
    const distance = Math.hypot(after.x - before.x, after.z - before.z)
    const turn =
      (((((after.yaw_deg % 360) - (before.yaw_deg % 360) + 540) % 360) + 360) %
        360) -
      180
    if (distance < 1e-9 && Math.abs(turn) < 1e-9) return []
    return [
      {
        id: item.id,
        name: item.name,
        bbox: { ...item.bbox_m },
        before: { ...before },
        after: { ...after },
        distance,
        turn,
      },
    ]
  })
  return [
    ...moves,
    ...(proposal.additions ?? []).map((item) => ({
      id: item.id,
      name: item.name,
      bbox: { ...item.bbox_m },
      before: { ...item.pose },
      after: { ...item.pose },
      distance: 0,
      turn: 0,
      added: true,
    })),
    ...scene.furniture
      .filter((item) => proposal.removals?.includes(item.id))
      .map((item) => ({
        id: item.id,
        name: item.name,
        bbox: { ...item.bbox_m },
        before: { ...item.pose },
        after: { ...item.pose },
        distance: 0,
        turn: 0,
        removed: true,
      })),
  ]
}

export function matchingAudit(
  audit: AuditReport | null,
  scene: RoomScene,
): audit is AuditReport {
  return (
    audit?.scene_id === scene.scene_id &&
    audit.scene_revision === scene.revision
  )
}
