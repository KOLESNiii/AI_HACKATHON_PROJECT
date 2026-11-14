import type { Pose2D, RoomScene } from './contracts'

export interface AgentReply {
  text: string
  /** Proposed poses keyed by item id, when the agent suggests a layout change. */
  poses?: Record<string, Pose2D>
}

/**
 * Redesign agent client. The only place the Chat tab talks to.
 *
 * No agent endpoint exists yet: it needs a contract (chat message + RoomScene in,
 * reply text + LayoutProposal-style poses out). Until then this returns a placeholder,
 * so swapping in the real call only changes this function.
 */
export async function sendAgentMessage(
  scene: RoomScene,
  text: string,
  signal?: AbortSignal,
): Promise<AgentReply> {
  void scene
  void text
  await new Promise<void>((resolve, reject) => {
    const t = setTimeout(resolve, 500)
    signal?.addEventListener('abort', () => {
      clearTimeout(t)
      reject(new DOMException('Aborted', 'AbortError'))
    })
  })
  return {
    text: 'The redesign agent is not connected yet. Once its endpoint exists, I will suggest layout changes here that you can apply in one click.',
  }
}
