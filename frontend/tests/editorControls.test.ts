import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { Vector3 } from 'three'
import {
  editorKey,
  handleItemKey,
  panCamera,
} from '../src/components/editor/keyboard'
import { footprint } from '../src/lib/geometry'
import { useStore } from '../src/store'

const initial = useStore.getState()

function keyEvent(key: string, overrides: Partial<KeyboardEvent> = {}) {
  let prevented = false
  const event = {
    key,
    preventDefault: () => (prevented = true),
    ...overrides,
  } as KeyboardEvent
  return { event, prevented: () => prevented }
}

beforeEach(() => {
  const scene = structuredClone(initial.scene)
  scene.floor_polygon = [
    { x: 0, z: 0 },
    { x: 10, z: 0 },
    { x: 10, z: 10 },
    { x: 0, z: 10 },
  ]
  scene.furniture = [
    {
      ...scene.furniture[0],
      id: 'item',
      is_fixed: false,
      bbox_m: { width: 2, depth: 1, height: 1 },
      pose: { x: 5, z: 5, yaw_deg: 0 },
    },
  ]
  useStore.setState({ ...initial, scene, selectedId: 'item' })
})
afterEach(() => useStore.setState(initial))

const item = () => useStore.getState().scene.furniture[0]

describe('furniture keyboard rotation', () => {
  test('Q/E turn in opposite directions and wrap at 360°', () => {
    const revision = useStore.getState().scene.revision
    handleItemKey(keyEvent('e').event)
    expect(item().pose.yaw_deg).toBe(270)
    handleItemKey(keyEvent('Q').event)
    expect(item().pose.yaw_deg).toBe(0)
    expect(useStore.getState().scene.revision).toBe(revision + 2)
  })

  test('arrows rotate by 5° and support held-key repetition', () => {
    const right = keyEvent('ArrowRight')
    handleItemKey(right.event)
    expect(right.prevented()).toBe(true)
    expect(item().pose.yaw_deg).toBe(355)
    handleItemKey(keyEvent('ArrowLeft', { repeat: true }).event)
    expect(item().pose.yaw_deg).toBe(0)
  })

  test('holding Q/E does not repeat quarter turns', () => {
    handleItemKey(keyEvent('q', { repeat: true }).event)
    expect(item().pose.yaw_deg).toBe(0)
  })

  test('rotation keeps the footprint inside room bounds near a wall', () => {
    useStore.getState().setPose('item', { z: 0.5 })
    handleItemKey(keyEvent('q').event)
    expect(item().pose.yaw_deg).toBe(90)
    for (const point of footprint(item())) {
      expect(point.x).toBeGreaterThanOrEqual(-1e-9)
      expect(point.z).toBeGreaterThanOrEqual(-1e-9)
      expect(point.x).toBeLessThanOrEqual(10 + 1e-9)
      expect(point.z).toBeLessThanOrEqual(10 + 1e-9)
    }
  })

  test('fixed fixtures and active drags cannot rotate', () => {
    const revision = useStore.getState().scene.revision
    useStore.setState({ interacting: true })
    handleItemKey(keyEvent('q').event)
    useStore.getState().rotateItem('item', 90)
    expect(item().pose.yaw_deg).toBe(0)
    useStore.setState({ interacting: false })
    useStore.setState({
      scene: {
        ...useStore.getState().scene,
        furniture: [{ ...item(), is_fixed: true }],
      },
    })
    handleItemKey(keyEvent('q').event)
    expect(item().pose.yaw_deg).toBe(0)
    expect(useStore.getState().scene.revision).toBe(revision)
  })

  test('rotation without a selection leaves the scene and arrows alone', () => {
    useStore.getState().select(null)
    const left = keyEvent('ArrowLeft')
    handleItemKey(left.event)
    expect(left.prevented()).toBe(false)
    expect(item().pose.yaw_deg).toBe(0)
  })

  test('Delete still removes the selected item', () => {
    handleItemKey(keyEvent('Delete').event)
    expect(useStore.getState().scene.furniture).toHaveLength(0)
    expect(useStore.getState().selectedId).toBeNull()
  })
})

describe('shortcut guards', () => {
  test('typing and native form controls leave shortcuts alone', () => {
    for (const target of [
      { isContentEditable: true },
      { closest: () => ({ tagName: 'INPUT' }) },
      { closest: () => ({ tagName: 'TEXTAREA' }) },
      { closest: () => ({ tagName: 'SELECT' }) },
    ]) {
      const key = keyEvent('q', { target: target as unknown as HTMLElement })
      expect(editorKey(key.event)).toBeNull()
      handleItemKey(key.event)
      expect(key.prevented()).toBe(false)
    }
    expect(item().pose.yaw_deg).toBe(0)
  })

  test('browser shortcuts, composition and handled events are ignored', () => {
    for (const modifier of [
      'ctrlKey',
      'metaKey',
      'altKey',
      'isComposing',
      'defaultPrevented',
    ]) {
      const event = keyEvent('q', { [modifier]: true }).event
      expect(editorKey(event)).toBeNull()
      handleItemKey(event)
    }
    expect(item().pose.yaw_deg).toBe(0)
  })
})

describe('camera panning', () => {
  test('W moves forward along the floor and preserves camera offset and height', () => {
    const position = new Vector3(0, 8, 10)
    const target = new Vector3()
    const offset = position.clone().sub(target)
    panCamera(position, target, 0, 1, 2)
    expect(target.toArray()).toEqual([0, 0, -2])
    expect(position.clone().sub(target).toArray()).toEqual(offset.toArray())
  })

  test('strafe follows the camera view after orbiting', () => {
    const position = new Vector3(10, 8, 0)
    const target = new Vector3()
    panCamera(position, target, 1, 0, 2)
    expect(target.toArray()).toEqual([0, 0, -2])
    expect(position.toArray()).toEqual([10, 8, -2])
  })

  test('diagonal movement has the same speed and opposite keys cancel', () => {
    const position = new Vector3(0, 8, 10)
    const target = new Vector3()
    panCamera(position, target, 1, 1, 2)
    expect(target.length()).toBeCloseTo(2)
    const before = position.clone()
    panCamera(position, target, 0, 0, 2)
    expect(position.toArray()).toEqual(before.toArray())
  })
})
