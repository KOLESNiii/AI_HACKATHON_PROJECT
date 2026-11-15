import { isFiniteNumber, isRecord, requestJson } from './api'
import type { FengShuiScore, RoomScene } from './contracts'
import type { EditorProposal } from './agent'

/**
 * Mirrors `FengShuiResult` in services/spatial_engine/feng_shui.py. That endpoint is
 * service-local (not in contracts/), so only the fields the UI reads are typed here.
 */
export interface FengShuiFinding {
  object_ids: string[]
  principle: string
  evidence: string
  confidence: 'low' | 'medium' | 'high'
  recommendation: string
}

export interface FengShuiAssessment {
  summary: string
  findings: FengShuiFinding[]
  missing_information: string[]
}

export interface FengShuiResult {
  scene_id: string
  revision: number
  outcome: 'completed' | 'assistant_unavailable'
  assessment: FengShuiAssessment | null
}

/** `/feng-shui/score` response; contracts/schema.py is the source of truth. */
export type { FengShuiScore }

export type ScoreStatus = 'idle' | 'loading' | 'ready' | 'error'

export function matchingFengShuiScore(
  value: FengShuiScore | null | undefined,
  scene: RoomScene,
): value is FengShuiScore {
  return value?.scene_id === scene.scene_id && value.revision === scene.revision
}

export function readFengShuiScore(
  value: unknown,
  scene: RoomScene,
): FengShuiScore {
  const items = new Set(scene.furniture.map((item) => item.id))
  const doors = new Set(scene.doors.map((door) => door.id))
  const ids = new Set([
    ...items,
    ...doors,
    ...scene.walls.map((w) => w.id),
    ...scene.windows.map((w) => w.id),
  ])
  const ratio = (n: unknown) => isFiniteNumber(n) && n >= 0 && n <= 1
  if (
    !isRecord(value) ||
    value.scene_id !== scene.scene_id ||
    value.revision !== scene.revision ||
    !(
      value.score === null ||
      (Number.isInteger(value.score) &&
        Number(value.score) >= 0 &&
        Number(value.score) <= 100)
    ) ||
    !ratio(value.coverage) ||
    typeof value.capped_by_audit !== 'boolean' ||
    !strings(value.unassessed) ||
    !Array.isArray(value.rules) ||
    !value.rules.every(
      (r) =>
        isRecord(r) &&
        typeof r.rule === 'string' &&
        strings(r.object_ids) &&
        (r.object_ids as string[]).every((id) => ids.has(id)) &&
        ratio(r.score) &&
        isFiniteNumber(r.weight) &&
        r.weight > 0 &&
        typeof r.detail === 'string',
    ) ||
    !Array.isArray(value.sightlines) ||
    !value.sightlines.every(
      (r) =>
        isRecord(r) &&
        typeof r.from_item_id === 'string' &&
        items.has(r.from_item_id) &&
        typeof r.to_door_id === 'string' &&
        doors.has(r.to_door_id) &&
        ['command_position', 'back_to_door', 'coffin_alignment'].includes(
          String(r.status),
        ) &&
        typeof r.reason === 'string',
    )
  )
    throw new Error(
      'The room service returned an invalid or outdated feng shui score. Try again.',
    )
  return value as unknown as FengShuiScore
}

export async function fetchFengShuiScore(
  scene: RoomScene,
  signal?: AbortSignal,
): Promise<FengShuiScore> {
  const { data } = await requestJson(
    '/api/spatial_engine/feng-shui/score',
    { scene },
    signal,
    10_000,
  )
  return readFengShuiScore(data, scene)
}

/** Score the immutable before/proposed snapshots without applying the proposal. */
export async function fetchProposalFengShuiScores(
  scene: RoomScene,
  proposal: EditorProposal,
  signal?: AbortSignal,
) {
  const candidate: RoomScene = {
    ...scene,
    furniture: [
      ...scene.furniture.map((item) => ({
        ...item,
        pose: Object.hasOwn(proposal.poses, item.id)
          ? { ...proposal.poses[item.id] }
          : { ...item.pose },
      })),
      ...structuredClone(proposal.additions ?? []),
    ],
  }
  const [before, after] = await Promise.all([
    fetchFengShuiScore(scene, signal),
    fetchFengShuiScore(candidate, signal),
  ])
  return { before, after }
}

const strings = (v: unknown) =>
  Array.isArray(v) && v.every((s) => typeof s === 'string')

/** Validate the result against the scene it was requested for before retaining it. */
export function readFengShui(value: unknown, scene: RoomScene): FengShuiResult {
  const ids = new Set([
    ...scene.furniture.map((i) => i.id),
    ...scene.doors.map((d) => d.id),
    ...scene.windows.map((w) => w.id),
    ...scene.walls.map((w) => w.id),
  ])
  const a = isRecord(value) ? value.assessment : undefined
  const valid =
    isRecord(value) &&
    value.scene_id === scene.scene_id &&
    value.revision === scene.revision &&
    (value.outcome === 'assistant_unavailable'
      ? a === null || a === undefined
      : value.outcome === 'completed' &&
        isRecord(a) &&
        typeof a.summary === 'string' &&
        strings(a.missing_information) &&
        Array.isArray(a.findings) &&
        a.findings.every(
          (f) =>
            isRecord(f) &&
            strings(f.object_ids) &&
            (f.object_ids as string[]).length > 0 &&
            (f.object_ids as string[]).every((id) => ids.has(id)) &&
            typeof f.principle === 'string' &&
            typeof f.evidence === 'string' &&
            typeof f.recommendation === 'string' &&
            ['low', 'medium', 'high'].includes(String(f.confidence)),
        ))
  if (!valid)
    throw new Error(
      'The room service returned an invalid or outdated feng shui assessment. Try again.',
    )
  return {
    ...(value as unknown as FengShuiResult),
    assessment: (a ?? null) as FengShuiAssessment | null,
  }
}

/** One model call on the server (60 s provider timeout); advice only, never moves furniture. */
export async function fetchFengShui(
  scene: RoomScene,
  signal?: AbortSignal,
): Promise<FengShuiResult> {
  const { data } = await requestJson(
    '/api/spatial_engine/feng-shui',
    { scene },
    signal,
    90_000,
  )
  return readFengShui(data, scene)
}
