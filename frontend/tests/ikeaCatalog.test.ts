import { expect, test } from 'bun:test'
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { catalog, catalogCategories } from '../src/data/catalog'

const publicDir = resolve(import.meta.dir, '../public')

test('the offline library contains 100 unique IKEA products across all categories', () => {
  expect(catalog).toHaveLength(100)
  expect(new Set(catalog.map((item) => item.sku)).size).toBe(100)
  expect(new Set(catalog.map((item) => item.product_url)).size).toBe(100)
  for (const category of catalogCategories) {
    expect(catalog.filter((item) => item.category === category)).toHaveLength(
      category === 'other' ? 9 : 13,
    )
  }
})

test('every product has a bundled GLB, thumbnail and complete retailer metadata', () => {
  for (const item of catalog) {
    expect(item.product_url).toMatch(/^https:\/\/www\.ikea\.com\/gb\/en\/p\//)
    expect(item.price_gbp).toBeGreaterThan(0)
    expect(item.image_url).toMatch(/^\/catalog\/ikea\/images\//)
    expect(existsSync(resolve(publicDir, `.${item.image_url}`))).toBe(true)
    const asset = item
    expect(asset.is_proxy).toBe(false)
    expect(asset.dimension_source).toBe('catalog')
    expect(asset.correction_needed).toEqual([])
    expect(asset.bbox_m).toEqual(item.bbox_m)
    expect(asset.glb_url).toMatch(
      /^\/catalog\/ikea\/assets\/[a-f0-9]{64}\.glb$/,
    )
    const glb = readFileSync(resolve(publicDir, `.${asset.glb_url}`))
    expect(glb.subarray(0, 4).toString()).toBe('glTF')
    expect(glb.readUInt32LE(8)).toBe(glb.length)
    expect(glb.length).toBeLessThanOrEqual(3_000_000)
  }
})
