import type { AuditReport, FurnitureItem, Pose2D, RoomScene } from './contracts'

export interface AgentReply {
  text: string
  poses?: Record<string, Pose2D>
  additions?: FurnitureItem[]
  report?: AuditReport | null
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

/** Return a proposal; application is a separate, revision-guarded user action. */
export async function sendAgentMessage(
  scene: RoomScene,
  text: string,
  signal?: AbortSignal,
): Promise<AgentReply> {
  const response = await fetch('/api/spatial_engine/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scene, instruction: text }),
    signal,
  })
  if (!response.ok) throw new Error(`Agent request failed (${response.status})`)
  const reply: AgentReply = await response.json()
  return {
    text: reply.text,
    report: reply.report,
    poses:
      reply.poses && Object.keys(reply.poses).length ? reply.poses : undefined,
    additions: reply.additions?.length ? reply.additions : undefined,
  }
}
