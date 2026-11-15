import { afterEach, expect, test } from 'bun:test'
import { importCatalogUrl } from '../src/lib/catalogImport'
import { useStore } from '../src/store'

const initial = useStore.getState()
const originalFetch = globalThis.fetch

afterEach(() => {
  globalThis.fetch = originalFetch
  useStore.setState(initial)
})

test('URL import preserves retailer geometry and provenance when added', async () => {
  const { pose: _pose, ...base } = initial.scene.furniture[0]
  const asset = {
    ...base,
    id: 'cat-test',
    source: 'url_import',
    is_proxy: false,
    glb_url: '/api/reconstruction/assets/test.glb',
    product_url: 'https://www.ikea.com/gb/en/p/test/',
    dimension_source: 'catalog',
    correction_needed: [],
    bbox_m: { width: 0.4, height: 0.5, depth: 0.4 },
  }
  const controller = new AbortController()
  globalThis.fetch = (async (url, options) => {
    expect(url).toBe('/api/reconstruction/catalog/import')
    expect(options?.signal).toBe(controller.signal)
    expect(JSON.parse(options?.body as string)).toEqual({
      url: asset.product_url,
      scene_id: initial.scene.scene_id,
    })
    return Response.json({
      asset: { ...asset, evidence: { frames: [] } },
      warnings: [],
    })
  }) as typeof fetch
  const result = await importCatalogUrl(
    asset.product_url,
    initial.scene.scene_id,
    controller.signal,
  )
  useStore.getState().addFromCatalog(result.item)
  const added = useStore.getState().scene.furniture.at(-1)!
  expect(added.glb_url).toBe(asset.glb_url)
  expect(added.source).toBe('url_import')
  expect('evidence' in added).toBe(false)
  expect(added.is_proxy).toBe(false)
  expect(added.bbox_m).toEqual(asset.bbox_m)
})

test('retailer failures are surfaced to the library', async () => {
  globalThis.fetch = (async () =>
    Response.json(
      { detail: 'Retailer blocked the request' },
      { status: 422 },
    )) as typeof fetch
  await expect(
    importCatalogUrl(
      'https://www.ikea.com/',
      'room',
      new AbortController().signal,
    ),
  ).rejects.toThrow('Retailer blocked the request')
})
