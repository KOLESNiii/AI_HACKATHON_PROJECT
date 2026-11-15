import type {
  AuditReport,
  LayoutGoal,
  LayoutProposal,
  OptimiseRequest,
  RoomScene,
} from './contracts'

/** Spatial engine routes, through the Vite proxy (`/api/<service>` is stripped). */
const BASE = '/api/spatial_engine'

/** The server allows 90 s per suggestion; give the network a little longer. */
const SOLVE_TIMEOUT_MS = 100_000
const AUDIT_TIMEOUT_MS = 15_000

/** The contract needs a URL for every mesh, but the engine never reads one. */
const PROXY_GLB = '/proxy-box.glb'

/** A failure with a message that is safe to show to the user. */
export class SpatialError extends Error {}

/**
 * The scene as the spatial service accepts it. Library items added in the editor have no
 * reconstructed mesh yet (`glb_url` is empty), which the shared contract rejects; geometry
 * comes from `bbox_m`, so a placeholder URL changes nothing the audit measures.
 */
export function toServiceScene(scene: RoomScene): RoomScene {
  return {
    ...scene,
    furniture: scene.furniture.map((item) =>
      item.glb_url ? item : { ...item, glb_url: PROXY_GLB },
    ),
  }
}

async function describeFailure(response: Response): Promise<string> {
  if (response.status === 422) {
    try {
      const body = (await response.json()) as {
        detail?: { msg?: unknown }[]
      }
      const messages = (body.detail ?? [])
        .map((d) => d.msg)
        .filter((m): m is string => typeof m === 'string')
        .slice(0, 2)
      if (messages.length)
        return `The room could not be checked: ${messages.join('; ')}`
    } catch {
      // Fall through to the generic message.
    }
    return 'The room could not be checked.'
  }
  return 'The spatial service had a problem. Try again in a moment.'
}

/** Shared spatial transport, including timeout, cancellation and readable errors. */
export async function postSpatial<T>(
  path: string,
  body: unknown,
  timeoutMs: number,
  signal?: AbortSignal,
): Promise<T> {
  const timeout = AbortSignal.timeout(timeoutMs)
  const combined = signal ? AbortSignal.any([signal, timeout]) : timeout
  let response: Response
  try {
    response = await fetch(`${BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: combined,
    })
  } catch (error) {
    if (signal?.aborted) throw error
    throw new SpatialError(
      timeout.aborted
        ? 'The spatial service took too long to answer.'
        : 'The spatial service could not be reached.',
    )
  }
  if (!response.ok) throw new SpatialError(await describeFailure(response))
  return (await response.json()) as T
}

/** Audits one scene revision. The caller must still discard a report for an older one. */
export function auditScene(
  scene: RoomScene,
  signal?: AbortSignal,
): Promise<AuditReport> {
  return postSpatial<AuditReport>(
    '/audit',
    toServiceScene(scene),
    AUDIT_TIMEOUT_MS,
    signal,
  )
}

/**
 * Asks the assistant for a better layout. The result never changes the scene: it is a
 * proposal for the user to apply. Throws if it was computed for a different revision.
 */
export async function solveLayout(
  scene: RoomScene,
  instruction: string,
  signal?: AbortSignal,
  goal: LayoutGoal | null = null,
): Promise<LayoutProposal> {
  const request: OptimiseRequest = {
    scene: toServiceScene(scene),
    locked_item_ids: [],
    max_candidates: 200,
    instruction,
    goal,
  }
  const proposal = await postSpatial<LayoutProposal>(
    '/solve',
    request,
    SOLVE_TIMEOUT_MS,
    signal,
  )
  if (
    proposal.report.scene_id !== scene.scene_id ||
    proposal.report.scene_revision !== scene.revision
  )
    throw new SpatialError('The room changed while I was thinking. Ask again.')
  return proposal
}
