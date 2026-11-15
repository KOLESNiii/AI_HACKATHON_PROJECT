import type { AuditReport, FurnitureItem, Pose2D, RoomScene } from './contracts'
import type { ProductOption } from './products'
import { postSpatial, SpatialError, toServiceScene } from './spatial'

export interface AgentReply {
  text: string
  poses?: Record<string, Pose2D>
  additions?: FurnitureItem[]
  report?: AuditReport | null
  /** The proposed audit, shown before Apply. */
  outlook?: string
  /** Real products found online for the user to pick from. */
  products?: ProductOption[]
}

/** What Apply would do, e.g. "Proposed layout · 1 new item · 2 moves". */
export function proposalSummary(
  m: Pick<AgentReply, 'poses' | 'additions'>,
): string {
  const moves = Object.keys(m.poses ?? {}).length
  const added = m.additions?.length ?? 0
  return [
    'Proposed layout',
    ...(added ? [`${added} new item${added === 1 ? '' : 's'}`] : []),
    ...(moves || !added ? [`${moves} move${moves === 1 ? '' : 's'}`] : []),
  ].join(' · ')
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

/** Return a proposal; application is a separate, revision-guarded user action. */
export async function sendAgentMessage(
  scene: RoomScene,
  text: string,
  signal?: AbortSignal,
): Promise<AgentReply> {
  const reply = await postSpatial<AgentReply>(
    '/chat',
    { scene: toServiceScene(scene), instruction: text },
    100_000,
    signal,
  )
  if (
    reply.report &&
    (reply.report.scene_id !== scene.scene_id ||
      reply.report.scene_revision !== scene.revision)
  )
    throw new SpatialError('The room changed while I was thinking. Ask again.')
  return {
    text: reply.text,
    report: reply.report,
    poses:
      reply.poses && Object.keys(reply.poses).length ? reply.poses : undefined,
    additions: reply.additions?.length ? reply.additions : undefined,
    outlook: reply.report ? describeOutlook(reply.report) : undefined,
    products: reply.products?.length ? reply.products : undefined,
  }
}
