import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import {
  BoxGeometry,
  Group,
  Mesh,
  MeshBasicMaterial,
  MeshStandardMaterial,
  Texture,
} from 'three'
import { preparePlayMaterials } from '../src/components/play/materials'
import { freshMockScene } from '../src/data/mockScene'
import {
  ceilingLights,
  DEFAULT_PLAY_LIGHTING,
  formatTimeOfDay,
  roomHeight,
  sunlightAt,
  windowLights,
} from '../src/lib/lighting'
import { canStand } from '../src/lib/walk'
import { useStore } from '../src/store'

const initial = useStore.getState()
beforeEach(() => useStore.setState({ ...initial, screen: 'editor' }))
afterEach(() => useStore.setState(initial))

describe('illustrative daylight', () => {
  test('sun rises east, peaks south and sets west', () => {
    const morning = sunlightAt(6)
    const noon = sunlightAt(12)
    const evening = sunlightAt(18)
    expect(morning.direction[0]).toBeCloseTo(1)
    expect(noon.direction[0]).toBeCloseTo(0)
    expect(noon.direction[1]).toBeCloseTo(Math.sin(Math.PI / 3))
    expect(noon.direction[2]).toBeGreaterThan(0)
    expect(evening.direction[0]).toBeCloseTo(-1)
    expect(noon.intensity).toBeGreaterThan(sunlightAt(8).intensity)
    expect(sunlightAt(8).color.b).toBeLessThan(noon.color.b)
  })
  test('dawn and dusk fade to zero and midnight wraps continuously', () => {
    for (const hour of [0, 5, 6, 18, 22, 24]) {
      expect(sunlightAt(hour).intensity).toBe(0)
      expect(sunlightAt(hour).daylight).toBe(0)
    }
    expect(sunlightAt(6.001).intensity).toBeLessThan(0.001)
    expect(sunlightAt(17.999).intensity).toBeLessThan(0.001)
    expect(sunlightAt(24)).toEqual(sunlightAt(0))
    expect(sunlightAt(NaN).daylight).toBe(0)
  })
  test('north rotates the world bearing, preserving elevation and intensity', () => {
    const base = sunlightAt(9)
    const rotated = sunlightAt(9, 90)
    expect(rotated.direction[0]).toBeCloseTo(-base.direction[2])
    expect(rotated.direction[2]).toBeCloseTo(base.direction[0])
    expect(rotated.direction[1]).toBe(base.direction[1])
    expect(rotated.intensity).toBe(base.intensity)
  })
  test('time labels include quarter hours and the end-of-day endpoint', () => {
    expect(formatTimeOfDay(0)).toBe('00:00')
    expect(formatTimeOfDay(14.25)).toBe('14:15')
    expect(formatTimeOfDay(23.75)).toBe('23:45')
    expect(formatTimeOfDay(24)).toBe('24:00')
  })
})

describe('room light placement', () => {
  test('window position, size and direction come from its wall', () => {
    const scene = freshMockScene()
    scene.walls = [
      {
        id: 'wall',
        start: { x: 0, z: 0 },
        end: { x: 4, z: 0 },
        height_m: 2.6,
        thickness_m: 0.15,
      },
    ]
    scene.windows = [
      {
        id: 'window',
        wall_id: 'wall',
        offset_along_wall_m: 1,
        width_m: 2,
        sill_height_m: 1,
        head_height_m: 2,
        plan_normal_deg: 123,
      },
    ]
    const win = windowLights(scene)[0]
    expect(win.position).toEqual([2, 1.5, 0.025])
    expect(win.width).toBe(2)
    expect(win.height).toBe(1)
    expect(Math.cos(win.rotationY)).toBeCloseTo(-1)
    scene.windows[0].width_m = 20
    expect(windowLights(scene)[0].width).toBe(3)
  })
  test('no windows, missing walls and unusable openings produce no sources', () => {
    const scene = freshMockScene()
    scene.windows = []
    expect(windowLights(scene)).toEqual([])
    const original = freshMockScene()
    original.walls = []
    expect(windowLights(original)).toEqual([])
    const invalid = freshMockScene()
    invalid.windows.forEach((win) => {
      win.head_height_m = win.sill_height_m
    })
    expect(windowLights(invalid)).toEqual([])
  })
  test('ceiling sources stay inside a concave room even when its centre is outside', () => {
    const scene = freshMockScene()
    scene.floor_polygon = [
      { x: 0, z: 0 },
      { x: 10, z: 0 },
      { x: 10, z: 2 },
      { x: 2, z: 2 },
      { x: 2, z: 10 },
      { x: 0, z: 10 },
    ]
    const lights = ceilingLights(scene)
    expect(lights.length).toBeGreaterThan(0)
    expect(lights.length).toBeLessThanOrEqual(4)
    for (const [x, y, z] of lights) {
      expect(canStand({ x, z }, scene, [])).toBe(true)
      expect(y).toBeCloseTo(roomHeight(scene) - 0.03)
    }
    scene.walls.forEach((wall) => {
      wall.height_m = 2.2
    })
    expect(ceilingLights(scene)[0][1]).toBeCloseTo(2.17)
  })
  test('ceiling placement has a triangulated fallback in narrow rooms', () => {
    const scene = freshMockScene()
    scene.floor_polygon = [
      { x: 0, z: 0 },
      { x: 3, z: 0 },
      { x: 3, z: 0.4 },
      { x: 0, z: 0.4 },
    ]
    const lights = ceilingLights(scene)
    expect(lights).toHaveLength(1)
    expect(lights[0][0]).toBeGreaterThan(0)
    expect(lights[0][0]).toBeLessThan(3)
    expect(lights[0][2]).toBeGreaterThan(0)
    expect(lights[0][2]).toBeLessThan(0.4)
  })
})

describe('local lighting state', () => {
  test('sliders are independent, validated and never change room or audit state', () => {
    const before = useStore.getState()
    before.setArtificialLight(0)
    before.setTimeOfDay(21.25)
    const after = useStore.getState()
    expect(after.playLighting).toEqual({
      artificialPercent: 0,
      timeOfDay: 21.25,
    })
    expect(after.scene).toBe(before.scene)
    expect(after.audit).toBe(before.audit)
    after.setTimeOfDay(NaN)
    after.setArtificialLight(Infinity)
    expect(useStore.getState().playLighting).toBe(after.playLighting)
    after.setArtificialLight(120)
    after.setTimeOfDay(27)
    expect(useStore.getState().playLighting).toEqual({
      artificialPercent: 100,
      timeOfDay: 24,
    })
    after.setTimeOfDay(8.13)
    expect(useStore.getState().playLighting.timeOfDay).toBe(8.25)
  })
  test('settings survive play exit and reset when a room opens', () => {
    const s = useStore.getState()
    s.setArtificialLight(20)
    s.setTimeOfDay(8)
    useStore.setState({ mode: 'play' })
    s.finishPlay()
    expect(useStore.getState().playLighting).toEqual({
      artificialPercent: 20,
      timeOfDay: 8,
    })
    s.openRoom()
    expect(useStore.getState().playLighting).toEqual(DEFAULT_PLAY_LIGHTING)
    expect(useStore.getState().playPhase).toBe('walking')
  })
})

test('play materials preserve source textures, geometry and cached materials through cleanup', () => {
  const source = new MeshStandardMaterial({
    color: '#123456',
    roughness: 0.4,
    map: new Texture(),
  })
  const geometry = new BoxGeometry()
  const root = new Group()
  const mesh = new Mesh(geometry, [source, source])
  root.add(mesh)
  const cached = root.clone(true)
  const clone = cached.children[0] as Mesh
  const dispose = preparePlayMaterials(cached)
  const materials = clone.material as MeshStandardMaterial[]
  expect(materials[0]).not.toBe(source)
  expect(materials[0].map).toBe(source.map)
  expect(materials[0].roughness).toBe(0.4)
  expect(clone.geometry).toBe(geometry)
  expect(mesh.material).toEqual([source, source])
  expect(clone.castShadow && clone.receiveShadow).toBe(true)
  let disposed = 0
  let sourceDisposed = false
  materials.forEach((m) => m.addEventListener('dispose', () => disposed++))
  source.addEventListener('dispose', () => {
    sourceDisposed = true
  })
  geometry.addEventListener('dispose', () => {
    sourceDisposed = true
  })
  source.map!.addEventListener('dispose', () => {
    sourceDisposed = true
  })
  dispose()
  expect(disposed).toBe(2)
  expect(sourceDisposed).toBe(false)
  geometry.dispose()
  source.map!.dispose()
  source.dispose()
})

test('unlit GLTF textures are retained when converted to lit play materials', () => {
  const source = new MeshBasicMaterial({ map: new Texture(), color: '#aabbcc' })
  const mesh = new Mesh(new BoxGeometry(), source)
  const dispose = preparePlayMaterials(mesh)
  const material = mesh.material as MeshStandardMaterial
  expect(material).toBeInstanceOf(MeshStandardMaterial)
  expect(material.map).toBe(source.map)
  expect(material.color).toEqual(source.color)
  dispose()
  source.map!.dispose()
  source.dispose()
  mesh.geometry.dispose()
})
