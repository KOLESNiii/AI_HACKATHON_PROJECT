import ikeaCatalog from './ikeaCatalog.json'
import type { BBoxM, FurnitureItem } from '../lib/contracts'

/** Offline IKEA products, refreshed by scripts/cache_ikea_library.py. */
export interface CatalogItem {
  sku: string
  name: string
  category: FurnitureItem['category']
  bbox_m: BBoxM
  price_gbp: number | null
  asset?: Omit<FurnitureItem, 'pose'>
  product_url?: string
  image_url?: string
}

// The generated JSON also retains source URLs, fetch timestamps and validation evidence.
export const catalog = ikeaCatalog as CatalogItem[]

export const catalogCategories = [
  'bed',
  'desk',
  'chair',
  'table',
  'wardrobe',
  'sofa',
  'storage',
  'other',
] as const
