import type { FurnitureItem } from '../lib/contracts'
import { demoFloors } from './demoHome'

/** Available, backend-served room models. Retain their dimensions and collision evidence. */
export interface CatalogItem extends Omit<
  FurnitureItem,
  'id' | 'pose' | 'is_fixed'
> {
  sku: string
}

export const catalog: CatalogItem[] = demoFloors.flatMap(({ scene }) =>
  scene.furniture
    .filter((item) => !item.is_fixed && !item.is_proxy && Boolean(item.glb_url))
    .map((item) => {
      const { id, pose: _pose, is_fixed: _fixed, ...asset } = item
      return {
        ...structuredClone(asset),
        sku: id,
        glb_url: item.glb_url.startsWith('/assets/')
          ? `/api/reconstruction/mock-room${item.glb_url}`
          : item.glb_url,
      }
    }),
)

/** Agent additions must be exact copies of a real Library asset, except ID and pose. */
export function isLibraryAsset(item: FurnitureItem): boolean {
  if (item.is_proxy || item.is_fixed) return false
  const metadata = (asset: CatalogItem | FurnitureItem) =>
    JSON.stringify({
      name: asset.name,
      category: asset.category,
      source: asset.source,
      glb_url: asset.glb_url,
      bbox: [asset.bbox_m.width, asset.bbox_m.height, asset.bbox_m.depth],
      has_screen: asset.has_screen ?? false,
      requires_front_clear_m: asset.requires_front_clear_m ?? 0.6,
      wall_flush_preferred: asset.wall_flush_preferred ?? true,
      dimension_source: asset.dimension_source ?? 'estimated',
      correction_needed: [...(asset.correction_needed ?? [])].sort(),
      collision_source: asset.collision_source ?? 'template',
      collision_parts: (asset.collision_parts ?? []).map((p) => [
        p.x,
        p.z,
        p.width,
        p.depth,
        p.y_min,
        p.y_max,
      ]),
      product_url: asset.product_url ?? null,
      price_gbp: asset.price_gbp ?? null,
    })
  const expected = metadata(item)
  return catalog.some(
    (asset) =>
      !asset.is_proxy &&
      asset.glb_url === item.glb_url &&
      metadata(asset) === expected,
  )
}

export const catalogCategories = [
  'bed',
  'desk',
  'chair',
  'table',
  'wardrobe',
  'sofa',
  'storage',
] as const
