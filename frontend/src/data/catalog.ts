import type { BBoxM, FurnitureItem } from '../lib/contracts'

/**
 * Library catalog. Mock data until Dev 2's catalog search / URL import lands; added items are
 * placed as labelled proxy boxes (is_proxy) because they have no reconstructed mesh yet.
 */
export interface CatalogItem {
  sku: string
  name: string
  category: FurnitureItem['category']
  bbox_m: BBoxM
  price_gbp: number | null
  asset?: Omit<FurnitureItem, 'pose'>
  product_url?: string
}

export const catalog: CatalogItem[] = [
  {
    sku: 'oak-writing-desk',
    name: 'Oak Writing Desk',
    category: 'desk',
    bbox_m: { width: 1.2, height: 0.75, depth: 0.6 },
    price_gbp: 149,
  },
  {
    sku: 'compact-pine-desk',
    name: 'Compact Pine Desk',
    category: 'desk',
    bbox_m: { width: 1.0, height: 0.74, depth: 0.5 },
    price_gbp: 89,
  },
  {
    sku: 'corner-desk',
    name: 'Corner Desk',
    category: 'desk',
    bbox_m: { width: 1.5, height: 0.75, depth: 1.2 },
    price_gbp: 210,
  },
  {
    sku: 'linen-armchair',
    name: 'Linen Armchair',
    category: 'chair',
    bbox_m: { width: 0.78, height: 0.85, depth: 0.82 },
    price_gbp: 229,
  },
  {
    sku: 'spindle-chair',
    name: 'Spindle Desk Chair',
    category: 'chair',
    bbox_m: { width: 0.48, height: 0.9, depth: 0.5 },
    price_gbp: 69,
  },
  {
    sku: 'single-bed',
    name: 'Single Bed Frame',
    category: 'bed',
    bbox_m: { width: 0.95, height: 0.9, depth: 2.05 },
    price_gbp: 180,
  },
  {
    sku: 'double-bed',
    name: 'Double Bed Frame',
    category: 'bed',
    bbox_m: { width: 1.6, height: 0.95, depth: 2.1 },
    price_gbp: 320,
  },
  {
    sku: 'two-door-wardrobe',
    name: 'Two-Door Wardrobe',
    category: 'wardrobe',
    bbox_m: { width: 1.0, height: 2.0, depth: 0.6 },
    price_gbp: 260,
  },
  {
    sku: 'low-bench',
    name: 'Low Storage Bench',
    category: 'storage',
    bbox_m: { width: 1.1, height: 0.45, depth: 0.4 },
    price_gbp: 119,
  },
  {
    sku: 'bookcase',
    name: 'Narrow Bookcase',
    category: 'storage',
    bbox_m: { width: 0.6, height: 1.8, depth: 0.3 },
    price_gbp: 95,
  },
  {
    sku: 'two-seat-sofa',
    name: 'Two-Seat Sofa',
    category: 'sofa',
    bbox_m: { width: 1.6, height: 0.8, depth: 0.85 },
    price_gbp: 540,
  },
  {
    sku: 'side-table',
    name: 'Round Side Table',
    category: 'table',
    bbox_m: { width: 0.45, height: 0.55, depth: 0.45 },
    price_gbp: 45,
  },
]

export const catalogCategories = [
  'bed',
  'desk',
  'chair',
  'table',
  'wardrobe',
  'sofa',
  'storage',
] as const
