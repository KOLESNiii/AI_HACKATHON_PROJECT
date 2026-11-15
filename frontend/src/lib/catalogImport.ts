import type { CatalogItem } from '../data/catalog'
import type { FurnitureItem } from './contracts'

export async function importCatalogUrl(
  url: string,
  sceneId: string,
  signal: AbortSignal,
): Promise<{ item: CatalogItem; warnings: string[] }> {
  const response = await fetch('/api/reconstruction/catalog/import', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, scene_id: sceneId }),
    signal,
  })
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(
      typeof body?.detail === 'string'
        ? body.detail
        : 'Could not import this product. Check the link and that the reconstruction service is running.',
    )
  }
  const result = (await response.json()) as {
    asset: Omit<FurnitureItem, 'pose'> & { evidence?: unknown }
    warnings: string[]
  }
  // Evidence belongs to reconstruction, not the shared RoomScene contract.
  const { evidence: _evidence, ...asset } = result.asset
  return {
    item: {
      sku: asset.id,
      name: asset.name,
      category: asset.category,
      bbox_m: asset.bbox_m,
      price_gbp: asset.price_gbp ?? null,
      product_url: asset.product_url ?? undefined,
      asset,
    },
    warnings: [
      ...result.warnings,
      ...(asset.is_proxy
        ? ['Shown as a proxy box; no usable 3D model was available.']
        : []),
      ...(asset.correction_needed.includes('dimensions')
        ? ['Dimensions are estimated. Check them before judging fit.']
        : []),
    ],
  }
}
