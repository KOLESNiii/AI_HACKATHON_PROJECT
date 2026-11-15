import type {
  AuditReport,
  FurnitureItem,
  ProductOption,
  RoomScene,
} from './contracts'
import { postSpatial, SpatialError, toServiceScene } from './spatial'

export type { ProductOption }

/** A product imported through the reconstruction pipeline, ready to place again. */
export interface LibraryEntry {
  product: ProductOption
  /** The delivered item, unplaced. Its `bbox_m` is the retailer-published size. */
  item: FurnitureItem
}

/** Importing downloads the page and model and may generate a mesh with fal.ai. */
const IMPORT_TIMEOUT_MS = 240_000
const PLACE_TIMEOUT_MS = 20_000

/** Sends a product page through Dev 2's import (IKEA model, SAM 3D, or proxy box). */
export async function importProduct(
  product: ProductOption,
  sceneId: string,
  signal?: AbortSignal,
): Promise<FurnitureItem> {
  const timeout = AbortSignal.timeout(IMPORT_TIMEOUT_MS)
  const combined = signal ? AbortSignal.any([signal, timeout]) : timeout
  let response: Response
  try {
    response = await fetch('/api/reconstruction/catalog/imports', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        product_url: product.product_url,
        scene_id: sceneId,
        category: product.category,
        source: 'catalog_search',
      }),
      signal: combined,
    })
  } catch (error) {
    if (signal?.aborted) throw error
    throw new SpatialError(
      timeout.aborted
        ? `Importing ${product.name} took too long.`
        : 'The import service could not be reached.',
    )
  }
  if (!response.ok) {
    let detail = ''
    try {
      const body = (await response.json()) as { detail?: unknown }
      if (typeof body.detail === 'string') detail = `: ${body.detail}`
    } catch {
      // Keep the generic message.
    }
    throw new SpatialError(`${product.name} could not be imported${detail}.`)
  }
  return (await response.json()) as FurnitureItem
}

interface PlaceReply {
  text: string
  additions: FurnitureItem[]
  report: AuditReport | null
}

/** Asks the spatial engine for an audited spot. The item ID must be new to the scene. */
export async function placeItem(
  scene: RoomScene,
  item: FurnitureItem,
  signal?: AbortSignal,
): Promise<{ item: FurnitureItem; report: AuditReport | null; text: string }> {
  const reply = await postSpatial<PlaceReply>(
    '/place',
    { scene: toServiceScene(scene), item },
    PLACE_TIMEOUT_MS,
    signal,
  )
  const placed = reply.additions[0]
  if (!placed) throw new SpatialError(`No spot was found for ${item.name}.`)
  return { item: placed, report: reply.report, text: reply.text }
}

/** An ID for another copy of the same product: IDs are unique within a scene. */
export function freshItemId(base: string, taken: Set<string>): string {
  if (!taken.has(base)) return base
  for (let n = 2; ; n += 1) {
    const id = `${base.slice(0, 58)}-${n}`
    if (!taken.has(id)) return id
  }
}

const LIBRARY_KEY = 'spaceshift.library.v1'

/** Per-browser convenience only: an empty library is always a valid state. */
export function loadLibrary(): LibraryEntry[] {
  try {
    const raw = localStorage.getItem(LIBRARY_KEY)
    const parsed: unknown = raw ? JSON.parse(raw) : []
    return Array.isArray(parsed) ? (parsed as LibraryEntry[]) : []
  } catch {
    return []
  }
}

export function saveLibrary(entries: LibraryEntry[]) {
  try {
    localStorage.setItem(LIBRARY_KEY, JSON.stringify(entries.slice(0, 50)))
  } catch {
    // Storage may be unavailable (private window); the library still works this session.
  }
}
