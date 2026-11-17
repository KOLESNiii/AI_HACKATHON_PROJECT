/**
 * Recorded layout-agent runs for the demo. Each one is a real `/chat/stream` session
 * (progress events and the final reply), captured against one demo room's starting layout.
 * They replay only there: the agent's reply describes that exact room and layout.
 */
import { roomScene } from '../data/demoHome'
import type { LayoutProgress, RoomScene } from '../lib/contracts'
import recorded from './examples.json'

export interface Example {
  prompt: string
  /** What the run does, in one line, for the prompt card. */
  blurb: string
  /** Progress events, with their replay time in seconds. */
  progress: { t: number; data: LayoutProgress }[]
  duration: number
  /** The terminal `reply` event's data, as the service sent it. */
  reply: Record<string, unknown>
}

const examples = recorded as unknown as Record<string, Example[]>

export const examplesFor = (sceneId: string): Example[] =>
  examples[sceneId] ?? []

export const roomsWithExamples = Object.keys(examples)

export function findExample(
  sceneId: string,
  prompt: string,
): Example | undefined {
  return examplesFor(sceneId).find((e) => e.prompt === prompt)
}

const close = (a: number, b: number) => Math.abs(a - b) < 1e-6

const starts = new Map<string, RoomScene>()

/** True when `scene` still has its demo room's starting furniture, exactly where it began. */
export function isStartingLayout(scene: RoomScene): boolean {
  let start = starts.get(scene.scene_id)
  if (!start) {
    start = roomScene(scene.scene_id)
    starts.set(scene.scene_id, start)
  }
  if (start.scene_id !== scene.scene_id) return false
  if (start.furniture.length !== scene.furniture.length) return false
  const byId = new Map(scene.furniture.map((i) => [i.id, i]))
  return start.furniture.every((s) => {
    const i = byId.get(s.id)
    return (
      !!i &&
      close(i.pose.x, s.pose.x) &&
      close(i.pose.z, s.pose.z) &&
      close(
        ((i.pose.yaw_deg % 360) + 360) % 360,
        ((s.pose.yaw_deg % 360) + 360) % 360,
      )
    )
  })
}
