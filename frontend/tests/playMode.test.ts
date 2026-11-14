import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { PerspectiveCamera, Vector3 } from 'three'
import {
  captureEditorView,
  pointOnFloor,
  restoreEditorView,
} from '../src/components/play/controls'
import { handleItemKey } from '../src/components/editor/keyboard'
import { freshMockScene } from '../src/data/mockScene'
import type { FurnitureItem, RoomScene } from '../src/lib/contracts'
import {
  canStand,
  humanPoseAt,
  walkingDelta,
  walkingObstacles,
  walkStep,
} from '../src/lib/walk'
import { useStore } from '../src/store'

const initial = useStore.getState()
function room(): RoomScene {
  return {
    ...freshMockScene(),
    furniture: [],
    floor_polygon: [
      { x: 0, z: 0 },
      { x: 10, z: 0 },
      { x: 10, z: 10 },
      { x: 0, z: 10 },
    ],
  }
}
function item(overrides: Partial<FurnitureItem> = {}): FurnitureItem {
  return {
    ...freshMockScene().furniture[0],
    id: 'obstacle',
    bbox_m: { width: 1, depth: 1, height: 1 },
    pose: { x: 5, z: 5, yaw_deg: 0 },
    collision_parts: [],
    ...overrides,
  }
}
beforeEach(() =>
  useStore.setState({ ...initial, screen: 'editor', scene: room() }),
)
afterEach(() => useStore.setState(initial))

describe('walking geometry', () => {
  test('fits the whole 50 cm body inside the floor; touching is allowed', () => {
    const scene = room()
    expect(canStand({ x: 5, z: 5 }, scene)).toBe(true)
    expect(canStand({ x: 0.25, z: 0.25 }, scene)).toBe(true)
    expect(canStand({ x: 0.24, z: 5 }, scene)).toBe(false)
    expect(canStand({ x: 11, z: 5 }, scene)).toBe(false)
    expect(canStand({ x: NaN, z: 5 }, scene)).toBe(false)
  })
  test('respects concave floor notches rather than the bounding box', () => {
    const scene = room()
    scene.floor_polygon = [
      { x: 0, z: 0 },
      { x: 10, z: 0 },
      { x: 10, z: 4 },
      { x: 4, z: 4 },
      { x: 4, z: 10 },
      { x: 0, z: 10 },
    ]
    expect(canStand({ x: 8, z: 8 }, scene)).toBe(false)
    expect(canStand({ x: 3.9, z: 5 }, scene)).toBe(false)
    expect(canStand({ x: 3, z: 5 }, scene)).toBe(true)
  })
  test('rotated and fixed furniture block walking', () => {
    const scene = room()
    scene.furniture = [
      item({
        is_fixed: true,
        bbox_m: { width: 4, depth: 1, height: 1 },
        pose: { x: 5, z: 5, yaw_deg: 90 },
      }),
    ]
    expect(canStand({ x: 5, z: 6.5 }, scene)).toBe(false)
    expect(canStand({ x: 6.5, z: 5 }, scene)).toBe(true)
  })
  test('uses collision parts and headroom, including chairs', () => {
    const scene = room()
    scene.furniture = [
      item({
        category: 'chair',
        bbox_m: { width: 4, depth: 4, height: 3 },
        collision_parts: [
          { x: 0, z: 0, width: 4, depth: 4, y_min: 2, y_max: 3 },
          { x: -1.5, z: 0, width: 0.2, depth: 4, y_min: 0, y_max: 2 },
        ],
      }),
    ]
    expect(walkingObstacles(scene)).toHaveLength(1)
    expect(canStand({ x: 5, z: 5 }, scene)).toBe(true)
    expect(canStand({ x: 3.5, z: 5 }, scene)).toBe(false)
    scene.furniture[0].collision_parts[0].y_min = 1.99
    expect(canStand({ x: 5, z: 5 }, scene)).toBe(false)
  })
  test('can pass a 51 cm corridor but not a 49 cm corridor', () => {
    for (const gap of [0.49, 0.51]) {
      const scene = room()
      scene.furniture = [
        item({
          pose: { x: 3, z: 5, yaw_deg: 0 },
          bbox_m: { width: 4 - gap, depth: 8, height: 1 },
        }),
        item({
          id: 'right',
          pose: { x: 7, z: 5, yaw_deg: 0 },
          bbox_m: { width: 4 - gap, depth: 8, height: 1 },
        }),
      ]
      expect(canStand({ x: 5, z: 5 }, scene)).toBe(gap > 0.5)
    }
  })
  test('substeps prevent crossing thin furniture on a long step', () => {
    const scene = room()
    scene.furniture = [item({ bbox_m: { width: 0.01, depth: 10, height: 1 } })]
    const next = walkStep({ x: 1, z: 5 }, { x: 8, z: 0 }, scene)
    expect(next.x).toBeLessThanOrEqual(4.745 + 1e-9)
    expect(canStand(next, scene)).toBe(true)
  })
  test('slides alongside walls and obstacles', () => {
    const scene = room()
    const next = walkStep({ x: 0.25, z: 2 }, { x: -1, z: 1 }, scene)
    expect(next.x).toBeCloseTo(0.25)
    expect(next.z).toBeCloseTo(3)
    scene.furniture = [item()]
    const beside = walkStep({ x: 4.25, z: 5 }, { x: 0.1, z: 0.2 }, scene)
    expect(beside.x).toBeCloseTo(4.25)
    expect(beside.z).toBeCloseTo(5.2)
  })
  test('diagonal input has constant speed, respects facing and caps long frames', () => {
    const straight = walkingDelta(Math.PI, 0, 1, 0.05)
    const diagonal = walkingDelta(Math.PI, 1, 1, 0.05)
    expect(Math.hypot(diagonal.x, diagonal.z)).toBeCloseTo(
      Math.hypot(straight.x, straight.z),
    )
    expect(straight.z).toBeCloseTo(-0.07)
    expect(walkingDelta(Math.PI, 1, 0, 0.05).x).toBeCloseTo(0.07)
    expect(walkingDelta(Math.PI, 0, 1, 2)).toEqual(straight)
    expect(walkingDelta(0, 0, 0, 0.05)).toEqual({ x: 0, z: 0 })
  })
})

describe('local human and mode state', () => {
  const drop = (x: number, z: number) => {
    useStore.getState().beginHumanPlacement()
    return useStore.getState().finishHumanPlacement({ x, z })
  }
  test('placing and relocating one human leave RoomScene unchanged', () => {
    const scene = useStore.getState().scene
    expect(drop(2, 2)).toBe(true)
    expect(useStore.getState().human).toMatchObject({ x: 2, z: 2 })
    expect(drop(3, 3)).toBe(true)
    expect(useStore.getState().human).toMatchObject({ x: 3, z: 3 })
    expect(useStore.getState().scene).toBe(scene)
  })
  test('preview and invalid or cancelled relocation preserve the original pose', () => {
    drop(2, 2)
    const previous = useStore.getState().human
    useStore.getState().beginHumanPlacement()
    useStore.getState().previewHuman({ x: 3, z: 3 })
    expect(useStore.getState().humanPreview).toMatchObject({ x: 3, z: 3 })
    expect(useStore.getState().human).toBe(previous)
    expect(useStore.getState().finishHumanPlacement({ x: -1, z: 1 })).toBe(
      false,
    )
    expect(useStore.getState().human).toBe(previous)
    useStore.getState().beginHumanPlacement()
    useStore.getState().previewHuman({ x: 3, z: 3 })
    useStore.getState().cancelHumanPlacement()
    expect(useStore.getState()).toMatchObject({
      human: previous,
      placingHuman: false,
      humanPreview: null,
      interacting: false,
    })
    useStore.getState().beginHumanPlacement()
    expect(useStore.getState().finishHumanPlacement(null)).toBe(false)
    expect(useStore.getState().human).toBe(previous)
  })
  test('faces the centre initially and preserves the last walked heading', () => {
    expect(humanPoseAt({ x: 5, z: 2 }, room(), null).yaw_deg).toBe(0)
    expect(
      humanPoseAt({ x: 3, z: 3 }, room(), { x: 2, z: 2, yaw_deg: 123 }).yaw_deg,
    ).toBe(123)
  })
  test('Play requires valid placement and no active drag', () => {
    expect(useStore.getState().startPlay()).toBe(false)
    drop(2, 2)
    useStore.getState().beginHumanPlacement()
    expect(useStore.getState().startPlay()).toBe(false)
    useStore.getState().cancelHumanPlacement()
    useStore.getState().select('furniture')
    expect(useStore.getState().startPlay()).toBe(true)
    expect(useStore.getState().selectedId).toBeNull()
    expect(useStore.getState().beginHumanPlacement()).toBe(false)
  })
  test('returning to edit saves position and heading without changing scene revision', () => {
    drop(2, 2)
    const scene = useStore.getState().scene
    useStore.getState().startPlay()
    useStore.getState().finishPlay({ x: 3, z: 3, yaw_deg: 45 })
    expect(useStore.getState()).toMatchObject({
      mode: 'edit',
      human: { x: 3, z: 3, yaw_deg: 45 },
    })
    expect(useStore.getState().scene).toBe(scene)
  })
  test('furniture edits can invalidate re-entry; removing human and opening a room reset placement', () => {
    drop(2, 2)
    const scene = useStore.getState().scene
    useStore.setState({
      scene: {
        ...scene,
        furniture: [item({ pose: { x: 2, z: 2, yaw_deg: 0 } })],
      },
    })
    expect(useStore.getState().startPlay()).toBe(false)
    useStore.getState().removeHuman()
    expect(useStore.getState().human).toBeNull()
    useStore.setState({ scene })
    drop(2, 2)
    useStore.getState().startPlay()
    useStore.getState().openRoom()
    expect(useStore.getState()).toMatchObject({
      mode: 'edit',
      human: null,
      placingHuman: false,
    })
  })
  test('editor rotation and deletion shortcuts are inactive in play', () => {
    useStore.setState({
      mode: 'play',
      selectedId: 'obstacle',
      scene: { ...room(), furniture: [item()] },
    })
    const scene = useStore.getState().scene
    for (const key of [
      'q',
      'e',
      'ArrowLeft',
      'ArrowRight',
      'Delete',
      'Backspace',
    ])
      handleItemKey({
        key,
        preventDefault: () => {
          throw new Error('editor shortcut consumed')
        },
      } as unknown as KeyboardEvent)
    expect(useStore.getState().scene).toBe(scene)
  })
})

describe('camera and drop projection', () => {
  test('restores camera pose, zoom and orbit target after draining damping', () => {
    const camera = new PerspectiveCamera()
    camera.position.set(2, 4, 6)
    camera.lookAt(1, 0, 1)
    camera.zoom = 1.5
    const orbit = {
      enabled: false,
      enableDamping: true,
      target: new Vector3(1, 0, 1),
      update: () => {
        camera.position.set(99, 99, 99)
      },
    }
    const saved = captureEditorView(camera, orbit)
    camera.position.set(10, 10, 10)
    orbit.target.set(5, 5, 5)
    restoreEditorView(camera, orbit, saved)
    expect(camera.position.toArray()).toEqual([2, 4, 6])
    expect(camera.quaternion.toArray()).toEqual(saved.quaternion.toArray())
    expect(camera.zoom).toBe(1.5)
    expect(orbit.target.toArray()).toEqual([1, 0, 1])
    expect(orbit.enableDamping).toBe(true)
  })
  test('drop projection uses canvas bounds, rejecting outside and parallel rays', () => {
    const camera = new PerspectiveCamera(60, 2, 0.05, 100)
    camera.position.set(5, 10, 5)
    camera.lookAt(5, 0, 5)
    camera.updateMatrixWorld()
    const rect = { left: 100, top: 50, width: 800, height: 400 }
    const p = pointOnFloor(500, 250, rect, camera)!
    expect(p.x).toBeCloseTo(5)
    expect(p.z).toBeCloseTo(5)
    expect(pointOnFloor(99, 250, rect, camera)).toBeNull()
    expect(pointOnFloor(901, 250, rect, camera)).toBeNull()
    camera.lookAt(5, 10, 0)
    camera.updateMatrixWorld()
    expect(pointOnFloor(500, 250, rect, camera)).toBeNull()
  })
})
