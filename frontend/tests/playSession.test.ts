import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { PerspectiveCamera, Vector3 } from 'three'
import { PlaySession } from '../src/components/play/session'
import { freshMockScene } from '../src/data/mockScene'
import { useStore } from '../src/store'

const initial = useStore.getState()
beforeEach(() => {
  const scene = freshMockScene()
  scene.furniture = []
  scene.floor_polygon = [
    { x: 0, z: 0 },
    { x: 10, z: 0 },
    { x: 10, z: 10 },
    { x: 0, z: 10 },
  ]
  useStore.setState({
    ...initial,
    screen: 'editor',
    scene,
    human: { x: 5, z: 5, yaw_deg: 0 },
  })
})
afterEach(() => useStore.setState(initial))

function setup() {
  const camera = new PerspectiveCamera()
  const editorCamera = new PerspectiveCamera()
  editorCamera.position.set(2, 10, 12)
  const orbit = {
    enabled: true,
    enableDamping: true,
    target: new Vector3(5, 0, 5),
    update: () => {},
  }
  const look = { enabled: false, isLocked: false }
  const doc = {
    pointerLockElement: null as unknown,
    exitPointerLock: () => {
      doc.pointerLockElement = null
      look.isLocked = false
    },
  }
  const surface = {
    ownerDocument: doc,
    requestPointerLock: () => Promise.resolve(),
  }
  let activeCamera = editorCamera
  const session = new PlaySession({
    camera,
    editorCamera,
    orbit,
    surface: surface as unknown as HTMLCanvasElement,
    look,
    setCamera: (next) => {
      activeCamera = next
    },
  })
  const grant = () => {
    doc.pointerLockElement = surface
    look.isLocked = true
    session.onLock()
  }
  const enter = () => {
    session.requestPlay()
    grant()
  }
  return {
    camera,
    editorCamera,
    orbit,
    look,
    doc,
    surface,
    session,
    grant,
    enter,
    activeCamera: () => activeCamera,
  }
}

function key(key: string) {
  return { key, preventDefault: () => {} } as KeyboardEvent
}

describe('play lighting capture lifecycle', () => {
  test('L clears held movement and retains the camera while sliders are open', () => {
    const t = setup()
    t.enter()
    t.session.onDown(key('w'))
    t.session.update(0.05, [])
    const position = t.camera.position.clone()
    t.session.onDown(key('l'))
    t.session.onUnlock()
    expect(useStore.getState()).toMatchObject({
      mode: 'play',
      playPhase: 'lighting',
    })
    expect(t.session.keys.size).toBe(0)
    expect(t.look.enabled).toBe(false)
    expect(t.activeCamera()).toBe(t.camera)
    t.session.onDown(key('w'))
    t.session.update(0.05, [])
    expect(t.camera.position).toEqual(position)
    t.session.exit()
  })
  test('Resume captures explicitly without resetting position or inheriting held keys', () => {
    const t = setup()
    const scene = useStore.getState().scene
    t.enter()
    t.camera.position.set(6, 1.6, 6)
    t.session.openLighting()
    t.session.onUnlock()
    t.session.resumePlay()
    t.grant()
    expect(useStore.getState()).toMatchObject({
      mode: 'play',
      playPhase: 'walking',
    })
    expect(t.look.enabled).toBe(true)
    t.session.update(0.05, [])
    expect(t.camera.position.toArray()).toEqual([6, 1.6, 6])
    expect(useStore.getState().scene).toBe(scene)
    t.session.exit()
  })
  test('denied resume leaves lighting open and allows a retry', async () => {
    const t = setup()
    t.enter()
    t.session.openLighting()
    t.session.onUnlock()
    t.surface.requestPointerLock = () => Promise.reject(new Error('blocked'))
    t.session.resumePlay()
    await Promise.resolve()
    expect(useStore.getState()).toMatchObject({
      mode: 'play',
      playPhase: 'lighting',
    })
    expect(useStore.getState().toasts.at(-1)?.text).toContain(
      'Click Resume to retry',
    )
    t.surface.requestPointerLock = () => Promise.resolve()
    t.session.resumePlay()
    t.grant()
    expect(useStore.getState().playPhase).toBe('walking')
    t.session.exit()
  })
  test('Escape from the panel saves the human and restores the editor camera', () => {
    const t = setup()
    t.enter()
    t.camera.position.set(6, 1.6, 7)
    t.session.openLighting()
    t.session.onUnlock()
    t.session.onDown(key('Escape'))
    expect(useStore.getState()).toMatchObject({
      mode: 'edit',
      playPhase: 'walking',
      human: { x: 6, z: 7 },
    })
    expect(t.activeCamera()).toBe(t.editorCamera)
    expect(t.editorCamera.position.toArray()).toEqual([2, 10, 12])
    expect(t.orbit.enabled).toBe(true)
  })
  test('unexpected unlock and focus-loss exit preserve existing safe behaviour', () => {
    const t = setup()
    t.enter()
    t.doc.exitPointerLock()
    t.session.onUnlock()
    expect(useStore.getState().mode).toBe('edit')
    t.enter()
    t.session.openLighting()
    t.session.onUnlock()
    t.session.exit() // Browser blur/visibility events use this same handler.
    expect(useStore.getState().mode).toBe('edit')
    expect(t.activeCamera()).toBe(t.editorCamera)
  })
  test('opening a room cancels a pending resume and rejects its late lock event', () => {
    const t = setup()
    const unsubscribe = useStore.subscribe(t.session.sync)
    t.enter()
    t.session.openLighting()
    t.session.onUnlock()
    t.session.resumePlay()
    useStore.getState().openRoom()
    t.grant()
    expect(useStore.getState()).toMatchObject({
      mode: 'edit',
      human: null,
      screen: 'building',
    })
    expect(t.doc.pointerLockElement).toBeNull()
    expect(t.activeCamera()).toBe(t.editorCamera)
    unsubscribe()
  })
  test('a rejected old request cannot cancel a newer room capture request', async () => {
    const t = setup()
    let rejectOld: (reason?: unknown) => void = () => {}
    t.surface.requestPointerLock = () =>
      new Promise<void>((_, reject) => {
        rejectOld = reject
      })
    t.session.requestPlay()
    t.session.exit()
    t.surface.requestPointerLock = () => Promise.resolve()
    t.session.requestPlay()
    rejectOld(new Error('old denial'))
    await Promise.resolve()
    t.grant()
    expect(useStore.getState().mode).toBe('play')
    expect(useStore.getState().toasts).toHaveLength(0)
    t.session.exit()
  })
})
