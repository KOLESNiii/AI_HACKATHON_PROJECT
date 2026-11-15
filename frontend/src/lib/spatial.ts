import { isFiniteNumber, isRecord, requestJson } from './api'
import type {
  AuditReport,
  RoomScene,
  LayoutGoal,
  LayoutProposal,
  OptimiseRequest,
} from './contracts'

const nullableNumber = (v: unknown) => v === null || isFiniteNumber(v)
const records = (v: unknown, check: (r: Record<string, unknown>) => boolean) =>
  Array.isArray(v) && v.every((r) => isRecord(r) && check(r))

/** Validate fields the UI reads before retaining an external report. */
export function readAudit(value: unknown, scene: RoomScene): AuditReport {
  if (
    !isRecord(value) ||
    value.scene_id !== scene.scene_id ||
    value.scene_revision !== scene.revision ||
    !nullableNumber(value.overall_score) ||
    !nullableNumber(value.walkable_floor_ratio) ||
    !(
      value.glare_orientation_grounded === null ||
      typeof value.glare_orientation_grounded === 'boolean'
    ) ||
    !records(
      value.collisions,
      (r) =>
        typeof r.item_a === 'string' &&
        typeof r.item_b === 'string' &&
        isFiniteNumber(r.overlap_area_m2),
    ) ||
    !records(
      value.blocked_doors,
      (r) =>
        typeof r.door_id === 'string' &&
        typeof r.blocked_by_item_id === 'string',
    ) ||
    !Array.isArray(value.out_of_bounds_item_ids) ||
    !value.out_of_bounds_item_ids.every((id) => typeof id === 'string') ||
    !records(
      value.clearance_issues,
      (r) =>
        typeof r.item_id === 'string' &&
        isFiniteNumber(r.actual_m) &&
        isFiniteNumber(r.required_m),
    ) ||
    !(
      value.glare_alerts === null ||
      records(
        value.glare_alerts,
        (r) =>
          typeof r.item_id === 'string' &&
          ['none', 'warning', 'severe'].includes(String(r.severity)),
      )
    ) ||
    !(
      value.feng_shui === null ||
      (isRecord(value.feng_shui) &&
        isFiniteNumber(value.feng_shui.score) &&
        records(
          value.feng_shui.sightlines,
          (r) =>
            typeof r.from_item_id === 'string' &&
            typeof r.to_door_id === 'string' &&
            typeof r.reason === 'string' &&
            ['command_position', 'back_to_door', 'coffin_alignment'].includes(
              String(r.status),
            ),
        ))
    )
  )
    throw new Error(
      'The room service returned an invalid or outdated audit. Try again.',
    )
  return value as unknown as AuditReport
}

export async function fetchAudit(
  scene: RoomScene,
  signal?: AbortSignal,
): Promise<AuditReport> {
  const { data } = await requestJson(
    '/api/spatial_engine/audit',
    scene,
    signal,
    10_000,
  )
  return readAudit(data, scene)
}

export async function fetchRoom(
  sceneId: string,
  signal?: AbortSignal,
): Promise<{
  scene: RoomScene
  warnings: string[]
  pending: boolean
  progress: FurnitureProgress | null
}> {
  const { data, headers } = await requestJson(
    `/api/reconstruction/scenes/${encodeURIComponent(sceneId)}`,
    undefined,
    signal,
    15_000,
  )
  if (
    !isRecord(data) ||
    data.scene_id !== sceneId ||
    !Number.isInteger(data.revision) ||
    Number(data.revision) < 0 ||
    typeof data.shell_glb_url !== 'string' ||
    !Array.isArray(data.floor_polygon) ||
    data.floor_polygon.length < 3 ||
    !data.floor_polygon.every(
      (p) => isRecord(p) && isFiniteNumber(p.x) && isFiniteNumber(p.z),
    ) ||
    !Array.isArray(data.walls) ||
    !Array.isArray(data.doors) ||
    !Array.isArray(data.windows) ||
    !records(
      data.furniture,
      (r) =>
        typeof r.id === 'string' &&
        typeof r.name === 'string' &&
        typeof r.glb_url === 'string' &&
        isRecord(r.pose) &&
        isFiniteNumber(r.pose.x) &&
        isFiniteNumber(r.pose.z) &&
        isFiniteNumber(r.pose.yaw_deg) &&
        isRecord(r.bbox_m) &&
        [r.bbox_m.width, r.bbox_m.height, r.bbox_m.depth].every(
          (n) => isFiniteNumber(n) && n > 0,
        ),
    )
  )
    throw new Error('The room service returned an invalid room.')
  let warnings: string[] = []
  try {
    const raw: unknown = JSON.parse(
      headers.get('X-Reconstruction-Warnings') ?? '[]',
    )
    if (Array.isArray(raw))
      warnings = raw.filter((v): v is string => typeof v === 'string')
  } catch {
    /* Warnings never prevent a valid room from opening. */
  }
  // Furniture is still being extracted from the plan's videos: ask again later.
  const pending = headers.get('X-Furniture-Pending') === 'true'
  const progress = pending
    ? readProgress(headers.get('X-Furniture-Progress'))
    : null
  return { scene: data as unknown as RoomScene, warnings, pending, progress }
}

/** True for the service's "still extracting" warning, which this panel replaces. */
export const isExtractingWarning = (w: string) =>
  w.startsWith('Extracting furniture from your videos')

/** Where the extraction of a room's furniture from video is. */
export interface FurnitureProgress {
  /** 1..steps once a stage has started; 0 while starting. */
  step: number
  steps: number
  stage: string
  /** Seconds since the extraction started, as of `receivedAt`. */
  elapsedS: number
  /** `Date.now()` when this was read. */
  receivedAt: number
}

function readProgress(header: string | null): FurnitureProgress | null {
  if (!header) return null
  try {
    const raw: unknown = JSON.parse(header)
    if (
      isRecord(raw) &&
      isFiniteNumber(raw.step) &&
      isFiniteNumber(raw.steps) &&
      raw.steps > 0 &&
      typeof raw.stage === 'string' &&
      isFiniteNumber(raw.elapsed_s)
    )
      return {
        step: raw.step,
        steps: raw.steps,
        stage: raw.stage,
        elapsedS: raw.elapsed_s,
        receivedAt: Date.now(),
      }
  } catch {
    /* Progress is decoration: the room still loads. */
  }
  return null
}

// Compatibility exports for main's JSON clients; the editor uses the validated helpers above.
export class SpatialError extends Error {}
export function toServiceScene(scene: RoomScene): RoomScene {
  return {
    ...scene,
    furniture: scene.furniture.map((item) =>
      item.glb_url ? item : { ...item, glb_url: '/proxy-box.glb' },
    ),
  }
}
export async function postSpatial<T>(
  path: string,
  body: unknown,
  timeoutMs: number,
  signal?: AbortSignal,
): Promise<T> {
  return (
    await requestJson('/api/spatial_engine' + path, body, signal, timeoutMs)
  ).data as T
}
export const auditScene = fetchAudit
export async function solveLayout(
  scene: RoomScene,
  instruction: string,
  signal?: AbortSignal,
  goal: LayoutGoal | null = null,
): Promise<LayoutProposal> {
  const request: OptimiseRequest = {
    scene: toServiceScene(scene),
    instruction,
    goal,
    locked_item_ids: [],
    max_candidates: 200,
  }
  const result = await postSpatial<LayoutProposal>(
    '/solve',
    request,
    100_000,
    signal,
  )
  if (
    result.report.scene_id !== scene.scene_id ||
    result.report.scene_revision !== scene.revision
  )
    throw new SpatialError('The room changed while I was thinking. Ask again.')
  return result
}
