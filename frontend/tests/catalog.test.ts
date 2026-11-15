import { afterEach, beforeEach, expect, test } from 'bun:test'
import { existsSync, readFileSync } from 'node:fs'
import { catalog, catalogCategories } from '../src/data/catalog'
import { demoFloors } from '../src/data/demoHome'
import { freshMockScene } from '../src/data/mockScene'
import { initialRoomHistory } from '../src/lib/roomVersions'
import { useStore } from '../src/store'

const initial = useStore.getState()
beforeEach(() => {
  const scene = freshMockScene()
  scene.floor_polygon = [
    { x: 0, z: 0 },
    { x: 10, z: 0 },
    { x: 10, z: 10 },
    { x: 0, z: 10 },
  ]
  scene.furniture = []
  useStore.setState({
    ...initial,
    scene,
    ...initialRoomHistory(scene),
    screen: 'editor',
  })
})
afterEach(() => useStore.setState(initial))

test('Library uses existing movable meshes and their actual metadata, rather than invented products', () => {
  const movable = demoFloors
    .flatMap((f) => f.scene.furniture)
    .filter((i) => !i.is_fixed && !i.is_proxy && i.glb_url)
  expect(catalog).toHaveLength(movable.length)
  expect(new Set(catalog.map((i) => i.sku)).size).toBe(catalog.length)
  for (const item of catalog) {
    const source = movable.find((i) => i.id === item.sku)!
    expect(source).toBeDefined()
    expect(item.glb_url).toBe(`/api/reconstruction/mock-room${source.glb_url}`)
    expect(item.bbox_m).toEqual(source.bbox_m)
    expect(item.dimension_source).toBe(source.dimension_source)
    expect(item.collision_parts).toEqual(source.collision_parts)
    expect(item.is_proxy).toBe(false)
    expect(item.price_gbp).toBeNull()
    expect(item).not.toHaveProperty('pose')
    expect(item).not.toHaveProperty('is_fixed')
  }
  for (const category of catalogCategories)
    expect(catalog.some((i) => i.category === category)).toBe(true)
})

test('every Library URL points at a real canonical GLB file served by reconstruction', () => {
  for (const item of catalog) {
    const relative = item.glb_url.replace('/api/reconstruction/mock-room/', '')
    const path = new URL(
      `../../contracts/mock_room/${relative}`,
      import.meta.url,
    )
    expect(existsSync(path)).toBe(true)
    expect(readFileSync(path).subarray(0, 4).toString()).toBe('glTF')
  }
})

test('adding a mesh preserves provenance, metric bounds, access rules and collision parts', () => {
  const source = catalog.find(
    (i) => i.category === 'desk' && i.collision_parts.length > 0,
  )!
  const before = useStore.getState().scene
  useStore.getState().addFromCatalog(source)
  useStore.getState().saveVersion()
  const state = useStore.getState()
  const added = state.scene.furniture[0]
  expect(state.scene.revision).toBe(before.revision + 1)
  expect(added).toMatchObject({
    name: source.name,
    category: source.category,
    source: source.source,
    glb_url: source.glb_url,
    is_proxy: false,
    is_fixed: false,
    dimension_source: source.dimension_source,
    bbox_m: source.bbox_m,
    correction_needed: source.correction_needed,
    collision_parts: source.collision_parts,
    collision_source: source.collision_source,
    requires_front_clear_m: source.requires_front_clear_m,
    wall_flush_preferred: source.wall_flush_preferred,
    has_screen: source.has_screen,
  })
  expect(added).not.toHaveProperty('sku')
  expect(added.id).not.toBe(source.sku)
  expect(state.versions.at(-1)?.scene.furniture[0].glb_url).toBe(source.glb_url)
  expect(state.toasts.at(-1)?.text).not.toContain('proxy')
})

test('multiple copies have unique IDs and independent geometry metadata; restoring versions retains meshes', () => {
  const source = catalog.find(
    (i) => i.category === 'desk' && i.collision_parts.length > 0,
  )!
  const sourceWidth = source.collision_parts[0].width
  useStore.getState().addFromCatalog(source)
  useStore.getState().saveVersion()
  const savedVersion = useStore.getState().currentVersionId
  useStore.getState().addFromCatalog(source)
  useStore.getState().saveVersion()
  const [a, b] = useStore.getState().scene.furniture
  expect(a.id).not.toBe(b.id)
  expect(a.glb_url).toBe(b.glb_url)
  a.collision_parts[0].width = 0.01
  expect(b.collision_parts[0].width).toBe(sourceWidth)
  expect(source.collision_parts[0].width).toBe(sourceWidth)
  useStore.getState().selectVersion('version-1')
  expect(useStore.getState().scene.furniture).toHaveLength(0)
  useStore.getState().selectVersion(savedVersion)
  expect(useStore.getState().scene.furniture).toHaveLength(1)
  expect(useStore.getState().scene.furniture[0].glb_url).toBe(source.glb_url)
  expect(useStore.getState().scene.furniture[0].collision_parts[0].width).toBe(
    sourceWidth,
  )
})

test('models that cannot fit and additions during loading do not change the room or history', () => {
  const before = useStore.getState().scene
  useStore.getState().addFromCatalog({
    ...catalog[0],
    bbox_m: { width: 100, depth: 100, height: 1 },
  })
  expect(useStore.getState().scene).toBe(before)
  useStore.setState({ roomLoading: true })
  useStore.getState().addFromCatalog(catalog[0])
  expect(useStore.getState().scene).toBe(before)
  expect(useStore.getState().versions).toHaveLength(1)
})
