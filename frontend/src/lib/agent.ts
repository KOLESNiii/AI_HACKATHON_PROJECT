import type { AuditReport, Pose2D, RoomScene } from './contracts'
import { solveLayout } from './spatial'

export interface AgentReply {
  text: string
  /** Proposed poses keyed by item id; only present for a verified, applicable layout. */
  poses?: Record<string, Pose2D>
  /** The proposed layout's audit in one line, so the user can judge it before applying. */
  outlook?: string
}

/** One line on what the audited proposal leaves, from the engine's own report. */
export function describeOutlook(report: AuditReport): string {
  const overlaps =
    report.collisions.length + report.out_of_bounds_item_ids.length
  const parts = [
    overlaps === 0 ? 'nothing overlapping' : `${overlaps} overlap(s)`,
    report.blocked_doors.length === 0
      ? 'doors clear'
      : `${report.blocked_doors.length} door(s) blocked`,
    `${report.clearance_issues.length} access issue(s)`,
  ]
  if (report.walkable_floor_ratio != null)
    parts.push(`${Math.round(report.walkable_floor_ratio * 100)}% walkable`)
  if (report.feng_shui != null)
    parts.push(`feng shui ${report.feng_shui.score}`)
  return parts.join(' · ')
}

/**
 * Redesign agent client, the only place the Chat tab talks to. It asks the spatial
 * service's `/solve`, which audits every proposal itself; nothing here changes the scene.
 * A reply carries poses only when the engine verified an improvement.
 */
export async function sendAgentMessage(
  scene: RoomScene,
  text: string,
  signal?: AbortSignal,
): Promise<AgentReply> {
  const proposal = await solveLayout(scene, text, signal)
  const poses = proposal.improved ? proposal.poses : {}
  const hasPoses = Object.keys(poses).length > 0
  const fallback = proposal.improved
    ? 'Here is a layout I checked.'
    : proposal.outcome === 'assistant_unavailable'
      ? 'The layout assistant is not available right now. Nothing was changed.'
      : 'I could not find a better layout. Nothing was changed.'
  return {
    text: proposal.explanation || fallback,
    poses: hasPoses ? poses : undefined,
    outlook: hasPoses ? describeOutlook(proposal.report) : undefined,
  }
}
