import { isFiniteNumber, isRecord, requestWithTimeout } from './api'
import { isLibraryAsset } from '../data/catalog'
import {
  MAX_LAYOUT_INSTRUCTION_CHARS,
  type LayoutGoal,
  type FurnitureItem,
  type Pose2D,
  type AuditReport,
  type LayoutProposal,
  type LayoutProgress,
  type RoomScene,
} from './contracts'
import type { ProductOption } from './products'
import { readAudit, postSpatial, SpatialError, toServiceScene } from './spatial'

const LAYOUT_GOALS: readonly LayoutGoal[] = [
  'balanced',
  'brighter',
  'roomier',
  'minimal_changes',
  'feng_shui',
  'custom',
]

/** Reject an entire proposal rather than applying a subset of unverified changes. */
export interface EditorProposal extends LayoutProposal {
  additions?: FurnitureItem[]
  /** IDs of existing non-fixed items deleted when the proposal is applied. */
  removals?: string[]
}
export interface EditorReply {
  text: string
  proposal?: EditorProposal
  /** Real products found online for the user to pick from. */
  products?: ProductOption[]
}

/**
 * `baseline` is the audit of `scene` itself. As in the backend's `is_acceptable_proposal`,
 * a door already blocked there may stay blocked; without it every changed blocker is refused.
 */
export function readProposal(
  value: unknown,
  scene: RoomScene,
  baseline?: AuditReport,
): EditorProposal {
  if (
    !isRecord(value) ||
    typeof value.proposal_id !== 'string' ||
    !isRecord(value.poses) ||
    typeof value.improved !== 'boolean' ||
    typeof value.explanation !== 'string' ||
    !['completed', 'stopped_early', 'assistant_unavailable'].includes(
      String(value.outcome),
    ) ||
    !(value.goal === null || LAYOUT_GOALS.includes(value.goal as LayoutGoal))
  )
    throw new Error('The layout agent returned an invalid proposal. Try again.')
  const report = readAudit(value.report, scene)
  const additions = value.additions ?? []
  if (
    !Array.isArray(additions) ||
    scene.furniture.length + additions.length > 60
  )
    throw new Error(
      'The layout agent returned invalid additions. Nothing was applied.',
    )
  const items = new Map(scene.furniture.map((item) => [item.id, item]))
  const ids = new Set(items.keys())
  for (const item of additions) {
    if (!validAddition(item) || ids.has(item.id))
      throw new Error(
        'The layout agent returned an invalid new item. Nothing was applied.',
      )
    if (!isLibraryAsset(item))
      throw new Error(
        'The agent can only add mesh models from Library. Nothing was applied.',
      )
    ids.add(item.id)
  }
  const removals = value.removals ?? []
  if (
    !Array.isArray(removals) ||
    new Set(removals).size !== removals.length ||
    removals.some(
      (id) =>
        typeof id !== 'string' ||
        !items.has(id) ||
        items.get(id)!.is_fixed ||
        Object.hasOwn(value.poses as object, id),
    )
  )
    throw new Error(
      'The layout agent returned an invalid removal. Nothing was applied.',
    )
  for (const [id, pose] of Object.entries(value.poses)) {
    const item = items.get(id)
    if (
      !item ||
      item.is_fixed ||
      !isRecord(pose) ||
      !isFiniteNumber(pose.x) ||
      !isFiniteNumber(pose.z) ||
      !isFiniteNumber(pose.yaw_deg)
    )
      throw new Error(
        'The layout agent returned an invalid furniture move. Nothing was applied.',
      )
  }
  const count =
    Object.keys(value.poses).length + additions.length + removals.length
  const changed = new Set([
    ...Object.keys(value.poses),
    ...additions.map((i) => i.id),
  ])
  const blockedBefore = new Set(
    baseline?.blocked_doors.map((d) => d.door_id) ?? [],
  )
  const newlyBlocked = report.blocked_doors.some(
    (d) => changed.has(d.blocked_by_item_id) && !blockedBefore.has(d.door_id),
  )
  const invalidFindings =
    additions.length > 0 || removals.length > 0
      ? report.collisions.some(
          (c) => changed.has(c.item_a) || changed.has(c.item_b),
        ) ||
        report.out_of_bounds_item_ids.some((id) => changed.has(id)) ||
        newlyBlocked
      : report.collisions.length > 0 ||
        report.out_of_bounds_item_ids.length > 0 ||
        newlyBlocked
  if (
    (!value.improved && count > 0) ||
    (value.improved &&
      (count === 0 ||
        value.outcome === 'assistant_unavailable' ||
        invalidFindings))
  )
    throw new Error(
      'The layout agent returned an unverified layout. Nothing was applied.',
    )
  return {
    ...value,
    report,
    ...(additions.length ? { additions } : {}),
    ...(removals.length ? { removals } : {}),
  } as unknown as EditorProposal
}

function validAddition(value: unknown): value is FurnitureItem {
  if (
    !isRecord(value) ||
    typeof value.id !== 'string' ||
    !/^[a-z0-9][a-z0-9_-]{0,63}$/.test(value.id) ||
    typeof value.name !== 'string' ||
    value.is_fixed !== false ||
    ![
      'bed',
      'desk',
      'chair',
      'table',
      'wardrobe',
      'sofa',
      'storage',
      'other',
    ].includes(String(value.category)) ||
    !['extracted_video', 'catalog_search', 'url_import'].includes(
      String(value.source),
    ) ||
    typeof value.glb_url !== 'string' ||
    !/^(https?:\/\/|\/[^/])/.test(value.glb_url) ||
    !isRecord(value.pose) ||
    ![value.pose.x, value.pose.z, value.pose.yaw_deg].every(isFiniteNumber) ||
    !isRecord(value.bbox_m) ||
    ![value.bbox_m.width, value.bbox_m.height, value.bbox_m.depth].every(
      (n) => isFiniteNumber(n) && n > 0,
    ) ||
    !isFiniteNumber(value.requires_front_clear_m) ||
    value.requires_front_clear_m < 0 ||
    typeof value.is_proxy !== 'boolean' ||
    typeof value.wall_flush_preferred !== 'boolean' ||
    !['measured', 'catalog', 'estimated', 'user_corrected'].includes(
      String(value.dimension_source),
    ) ||
    !Array.isArray(value.correction_needed) ||
    !value.correction_needed.every((f) =>
      ['dimensions', 'placement', 'orientation'].includes(String(f)),
    ) ||
    !Array.isArray(value.collision_parts) ||
    value.collision_parts.length > 12
  )
    return false
  const box = value.bbox_m as unknown as FurnitureItem['bbox_m']
  return value.collision_parts.every(
    (p) =>
      isRecord(p) &&
      [p.x, p.z, p.width, p.depth, p.y_min, p.y_max].every(isFiniteNumber) &&
      Number(p.width) >= 0.01 &&
      Number(p.depth) >= 0.01 &&
      Number(p.y_max) - Number(p.y_min) >= 0.01 &&
      Math.abs(Number(p.x)) + Number(p.width) / 2 <= box.width / 2 + 0.001 &&
      Math.abs(Number(p.z)) + Number(p.depth) / 2 <= box.depth / 2 + 0.001 &&
      Number(p.y_min) >= -0.001 &&
      Number(p.y_max) <= box.height + 0.001,
  )
}

function readStreamReply(
  value: unknown,
  scene: RoomScene,
  baseline?: AuditReport,
): EditorReply {
  if (isRecord(value) && typeof value.proposal_id === 'string') {
    const proposal = readProposal(value, scene, baseline)
    return { text: proposal.explanation, proposal }
  }
  if (!isRecord(value) || typeof value.text !== 'string')
    throw new Error('The chat agent returned an invalid reply.')
  if (value.proposal) {
    const proposal = readProposal(value.proposal, scene, baseline)
    return { text: value.text, proposal }
  }
  const poses = value.poses ?? {}
  const additions = value.additions ?? []
  const removals = value.removals ?? []
  if (!isRecord(poses) || !Array.isArray(additions) || !Array.isArray(removals))
    throw new Error('The chat proposal is invalid.')
  if (!Object.keys(poses).length && !additions.length && !removals.length) {
    const products = readProducts(value.products)
    return products.length
      ? { text: value.text, products }
      : { text: value.text }
  }
  const proposal = readProposal(
    {
      proposal_id: crypto.randomUUID(),
      poses,
      additions,
      removals,
      report: value.report,
      improved: true,
      outcome: 'completed',
      goal: null,
      explanation: value.text,
    },
    scene,
    baseline,
  )
  return { text: value.text, proposal }
}

/** Products are shown as links and images only, so drop any without safe http(s) URLs. */
function readProducts(value: unknown): ProductOption[] {
  if (!Array.isArray(value)) return []
  return value.filter(
    (p): p is ProductOption =>
      isRecord(p) &&
      typeof p.name === 'string' &&
      typeof p.retailer === 'string' &&
      typeof p.product_url === 'string' &&
      /^https?:\/\//.test(p.product_url) &&
      typeof p.image_url === 'string' &&
      /^https?:\/\//.test(p.image_url),
  )
}

/** Existing backend agent owns tool calls, feasibility checks and scoring. */
export async function streamAgentMessage(
  scene: RoomScene,
  text: string,
  signal?: AbortSignal,
  onProgress: (progress: LayoutProgress) => void = () => {},
  baseline?: AuditReport,
): Promise<EditorReply> {
  const instruction = text.trim()
  if (!instruction || [...instruction].length > MAX_LAYOUT_INSTRUCTION_CHARS)
    throw new Error(
      `Enter a room request of up to ${MAX_LAYOUT_INSTRUCTION_CHARS} characters.`,
    )
  const request = { scene: toServiceScene(scene), instruction }
  return requestWithTimeout(
    '/api/spatial_engine/chat/stream',
    request,
    signal,
    120_000,
    (response, requestSignal) =>
      readSolveStream(response, scene, requestSignal, onProgress, baseline),
    'text/event-stream',
  )
}

const PROGRESS_STAGES = new Set([
  'validating',
  'interpreting',
  'exploring',
  'evaluating',
  'retrying',
  'verifying',
])

async function readSolveStream(
  response: Response,
  scene: RoomScene,
  signal: AbortSignal,
  onProgress: (progress: LayoutProgress) => void,
  baseline?: AuditReport,
): Promise<EditorReply> {
  if (
    !response.headers.get('Content-Type')?.startsWith('text/event-stream') ||
    !response.body
  )
    throw new Error(
      'The layout service did not return a progress stream. Try again.',
    )
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  const abort = () => {
    void reader.cancel().catch(() => {})
  }
  signal.addEventListener('abort', abort, { once: true })
  let pending = ''
  let event = ''
  let data: string[] = []
  let dataLength = 0
  try {
    while (true) {
      signal.throwIfAborted()
      const { value, done } = await reader.read()
      signal.throwIfAborted()
      pending += decoder.decode(value, { stream: !done })
      if (pending.length + dataLength > 2_000_000)
        throw new Error(
          'The layout service returned an oversized progress event.',
        )
      while (true) {
        const newline = /\r\n|\r|\n/.exec(pending)
        if (
          !newline ||
          (!done && newline[0] === '\r' && newline.index === pending.length - 1)
        )
          break
        const line = pending.slice(0, newline.index)
        pending = pending.slice(newline.index + newline[0].length)
        if (line === '') {
          if (data.length) {
            const payload: unknown = JSON.parse(data.join('\n'))
            if (event === 'reply')
              return readStreamReply(payload, scene, baseline)
            if (
              event === 'error' &&
              isRecord(payload) &&
              typeof payload.message === 'string' &&
              payload.message.length > 0 &&
              payload.message.length <= 300
            )
              throw new Error(payload.message)
            if (
              event !== 'progress' ||
              !isRecord(payload) ||
              !PROGRESS_STAGES.has(String(payload.stage)) ||
              typeof payload.message !== 'string' ||
              payload.message.length === 0 ||
              payload.message.length > 300
            )
              throw new Error(
                'The layout service returned an invalid progress event.',
              )
            onProgress(payload as unknown as LayoutProgress)
          }
          event = ''
          data = []
          dataLength = 0
        } else if (!line.startsWith(':')) {
          const colon = line.indexOf(':')
          const field = colon < 0 ? line : line.slice(0, colon)
          const content =
            colon < 0 ? '' : line.slice(colon + 1).replace(/^ /, '')
          if (field === 'event') event = content
          else if (field === 'data') {
            data.push(content)
            dataLength += content.length
          }
        }
      }
      if (done)
        throw new Error(
          'The layout connection ended before a result arrived. Try again.',
        )
    }
  } finally {
    signal.removeEventListener('abort', abort)
    await reader.cancel().catch(() => {})
    reader.releaseLock()
  }
}

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
    reply.additions?.some(
      (item) => !validAddition(item) || !isLibraryAsset(item),
    )
  )
    throw new Error(
      'The agent can only add mesh models from Library. Nothing was applied.',
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
