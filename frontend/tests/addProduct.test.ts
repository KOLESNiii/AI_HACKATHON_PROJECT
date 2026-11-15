import { afterEach, expect, test } from 'bun:test'
import { sendAgentMessage } from '../src/lib/agent'
import type { FurnitureItem } from '../src/lib/contracts'
import { freshItemId, type ProductOption } from '../src/lib/products'
import { useStore } from '../src/store'

const initial = useStore.getState()
const originalFetch = globalThis.fetch

afterEach(() => {
  useStore.setState(initial)
  globalThis.fetch = originalFetch
})

const product: ProductOption = {
  name: 'MICKE Desk',
  retailer: 'ikea.com',
  product_url: 'https://www.ikea.com/gb/en/p/micke-1/',
  image_url: 'https://www.ikea.com/gb/en/images/micke.jpg',
  category: 'desk',
  price_gbp: 79,
  bbox_m: null,
  dimensions_text: null,
}

function imported(): FurnitureItem {
  return {
    ...initial.scene.furniture[0],
    id: 'cat-0123456789ab',
    name: 'MICKE Desk',
    category: 'desk',
    source: 'catalog_search',
    glb_url: '/api/reconstruction/assets/abc.glb',
    bbox_m: { width: 1.05, height: 0.75, depth: 0.5 },
    pose: { x: 0, z: 0, yaw_deg: 0 },
    is_fixed: false,
    is_proxy: false,
    dimension_source: 'catalog',
  }
}

/** Reconstruction import, then spatial placement; records the calls. */
function services(calls: string[]) {
  globalThis.fetch = (async (url, options) => {
    calls.push(String(url))
    const body = JSON.parse(options?.body as string)
    if (url === '/api/reconstruction/catalog/imports') {
      expect(body.product_url).toBe(product.product_url)
      expect(body.scene_id).toBe(useStore.getState().scene.scene_id)
      return Response.json(imported())
    }
    expect(url).toBe('/api/spatial_engine/place')
    return Response.json({
      text: 'Placed MICKE Desk against a wall.',
      poses: {},
      additions: [{ ...body.item, pose: { x: 1, z: 0.3, yaw_deg: 0 } }],
      report: null,
    })
  }) as typeof fetch
}

test('chat replies carry found products', async () => {
  globalThis.fetch = (async () =>
    Response.json({
      text: 'Found 1 option',
      poses: {},
      additions: [],
      products: [product],
    })) as unknown as typeof fetch
  const reply = await sendAgentMessage(initial.scene, 'Find a desk')
  expect(reply.products).toEqual([product])
  expect(reply.additions).toBeUndefined()
})

test('adding a product imports it into the library and places it in the room', async () => {
  const calls: string[] = []
  services(calls)
  const before = useStore.getState().scene
  await useStore.getState().addProductToScene(product)
  const s = useStore.getState()
  expect(calls).toEqual([
    '/api/reconstruction/catalog/imports',
    '/api/spatial_engine/place',
  ])
  expect(s.library.map((e) => e.product.product_url)).toEqual([
    product.product_url,
  ])
  expect(s.scene.revision).toBe(before.revision + 1)
  const added = s.scene.furniture.at(-1)!
  expect(added.id).toBe('cat-0123456789ab')
  expect(added.pose).toEqual({ x: 1, z: 0.3, yaw_deg: 0 })
  expect(s.selectedId).toBe(added.id)
  expect(s.adding).toEqual([])
})

test('a second copy reuses the library and gets a new ID', async () => {
  const calls: string[] = []
  services(calls)
  await useStore.getState().addProductToScene(product)
  await useStore.getState().addProductToScene(product)
  expect(calls.filter((c) => c.includes('imports'))).toHaveLength(1)
  const ids = useStore.getState().scene.furniture.map((i) => i.id)
  expect(ids).toContain('cat-0123456789ab')
  expect(ids).toContain('cat-0123456789ab-2')
})

test('a failed import changes nothing and says why', async () => {
  globalThis.fetch = (async () =>
    Response.json(
      { detail: 'the page does not name a product' },
      { status: 422 },
    )) as unknown as typeof fetch
  const before = useStore.getState().scene
  await useStore.getState().addProductToScene(product)
  const s = useStore.getState()
  expect(s.scene).toBe(before)
  expect(s.library).toEqual([])
  expect(s.toasts.at(-1)?.text).toContain('the page does not name a product')
})

test('fresh IDs stay unique', () => {
  expect(freshItemId('a', new Set())).toBe('a')
  expect(freshItemId('a', new Set(['a', 'a-2']))).toBe('a-3')
})
