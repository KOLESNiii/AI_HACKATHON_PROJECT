import { isFiniteNumber, isRecord } from './api'
import type { ParsedFloorPlan } from './contracts'

/** A new plan is read by a vision model, and videos travel with it, so allow minutes. */
export const PLAN_UPLOAD_TIMEOUT_MS = 180_000

/**
 * Uploads the floor-plan images (and any walkthrough videos) to the reconstruction service,
 * which parses every floor and room. Videos are kept by the service but not extracted.
 */
export async function uploadFloorPlan(
  plans: File[],
  videos: File[],
  signal?: AbortSignal,
  timeoutMs = PLAN_UPLOAD_TIMEOUT_MS,
): Promise<ParsedFloorPlan> {
  const body = new FormData()
  for (const f of plans) body.append('files', f, f.name)
  for (const f of videos) body.append('videos', f, f.name)

  const controller = new AbortController()
  const abort = () => controller.abort(signal?.reason)
  if (signal?.aborted) abort()
  else signal?.addEventListener('abort', abort, { once: true })
  const timer = setTimeout(
    () =>
      controller.abort(
        new DOMException(
          'Reading the floor plan took too long. Try again.',
          'TimeoutError',
        ),
      ),
    timeoutMs,
  )
  try {
    const response = await fetch('/api/reconstruction/floor-plans', {
      method: 'POST',
      headers: { Accept: 'application/json' },
      body,
      signal: controller.signal,
    })
    if (!response.ok) throw new Error(await failure(response))
    const data: unknown = await response.json()
    if (!isParsedFloorPlan(data))
      throw new Error(
        'The floor plan service returned an unreadable plan. Try again.',
      )
    return data
  } catch (error) {
    if (controller.signal.aborted) throw controller.signal.reason
    if (error instanceof TypeError)
      throw new Error(
        'The floor plan service could not be reached. Check that it is running and try again.',
      )
    throw error
  } finally {
    clearTimeout(timer)
    signal?.removeEventListener('abort', abort)
  }
}

async function failure(response: Response): Promise<string> {
  let detail = ''
  try {
    const body: unknown = await response.json()
    if (isRecord(body) && typeof body.detail === 'string') detail = body.detail
  } catch {
    /* Fall back to the status. */
  }
  if (detail) return `The floor plan could not be read: ${detail}.`
  if (response.status === 413)
    return 'A file is too large to upload. Try a smaller one.'
  return `The floor plan service could not read the plan (${response.status}). Try again.`
}

/** Enough of the contract for the room picker: every room has a usable outline and scene. */
export function isParsedFloorPlan(value: unknown): value is ParsedFloorPlan {
  return (
    isRecord(value) &&
    typeof value.plan_id === 'string' &&
    Array.isArray(value.warnings) &&
    value.warnings.every((w) => typeof w === 'string') &&
    Array.isArray(value.floors) &&
    value.floors.every(
      (f) =>
        isRecord(f) &&
        typeof f.floor_id === 'string' &&
        typeof f.name === 'string' &&
        Array.isArray(f.rooms) &&
        f.rooms.every(
          (r) =>
            isRecord(r) &&
            typeof r.room_id === 'string' &&
            typeof r.name === 'string' &&
            isRecord(r.scene) &&
            typeof r.scene.scene_id === 'string' &&
            typeof r.scene.shell_glb_url === 'string' &&
            Array.isArray(r.scene.walls) &&
            Array.isArray(r.scene.doors) &&
            Array.isArray(r.scene.windows) &&
            Array.isArray(r.scene.furniture) &&
            Array.isArray(r.scene.floor_polygon) &&
            r.scene.floor_polygon.length >= 3 &&
            r.scene.floor_polygon.every(
              (p) => isRecord(p) && isFiniteNumber(p.x) && isFiniteNumber(p.z),
            ),
        ),
    )
  )
}
