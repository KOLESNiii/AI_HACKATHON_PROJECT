import type {
  AuditReport,
  LayoutProposal,
  OptimiseRequest,
  RoomScene,
} from './contracts'

/**
 * Service calls through the Vite proxy (/api/<service>/...).
 * The audit and optimise route paths are assumptions until Dev 4 publishes them; callers treat
 * any failure as "service not connected" and keep the local preview.
 */
export const services = [
  'reconstruction',
  'spatial_engine',
  'media_gen',
] as const
export type Service = (typeof services)[number]

const AUDIT_URL = '/api/spatial_engine/audit'
const OPTIMISE_URL = '/api/spatial_engine/optimize'

async function postJson<T>(
  url: string,
  body: unknown,
  signal?: AbortSignal,
): Promise<T> {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal,
  })
  if (!res.ok) throw new Error(`${url} → ${res.status}`)
  return (await res.json()) as T
}

export function requestAudit(scene: RoomScene, signal?: AbortSignal) {
  return postJson<AuditReport>(AUDIT_URL, scene, signal)
}

export function requestOptimise(req: OptimiseRequest, signal?: AbortSignal) {
  return postJson<LayoutProposal>(OPTIMISE_URL, req, signal)
}

export async function checkHealth(
  service: Service,
  signal?: AbortSignal,
): Promise<boolean> {
  try {
    const res = await fetch(`/api/${service}/health`, { signal })
    if (!res.ok) return false
    const body: unknown = await res.json()
    return (
      !!body &&
      typeof body === 'object' &&
      'status' in body &&
      body.status === 'ok'
    )
  } catch {
    return false
  }
}
