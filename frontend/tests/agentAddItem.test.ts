import { afterEach, expect, test } from 'bun:test'
import { sendAgentMessage } from '../src/lib/agent'
import { useStore } from '../src/store'

const initial = useStore.getState()
const originalFetch = globalThis.fetch

afterEach(() => {
  useStore.setState(initial)
  globalThis.fetch = originalFetch
})

function proposal() {
  const existing = initial.scene.furniture[0]
  return {
    ...existing,
    id: 'new-item',
    is_fixed: false,
    is_proxy: true,
    pose: { x: 2, z: 2, yaw_deg: 0 },
  }
}

test('chat sends scene and instruction, preserving cancellation and additions', async () => {
  const controller = new AbortController()
  globalThis.fetch = (async (url, options) => {
    expect(url).toBe('/api/spatial_engine/chat')
    expect(options?.signal).toBe(controller.signal)
    expect(JSON.parse(options?.body as string)).toEqual({
      scene: initial.scene,
      instruction: 'Add a chair',
    })
    return Response.json({
      text: 'Proposed a chair',
      poses: {},
      additions: [proposal()],
    })
  }) as typeof fetch
  const reply = await sendAgentMessage(
    initial.scene,
    'Add a chair',
    controller.signal,
  )
  expect(reply.additions?.[0].id).toBe('new-item')
  expect(reply.poses).toBeUndefined()
})

test('agent errors do not become successful proposals', async () => {
  globalThis.fetch = (async () =>
    new Response('', { status: 503 })) as typeof fetch
  await expect(sendAgentMessage(initial.scene, 'Add a chair')).rejects.toThrow()
})

test('Apply adds the proxy and moves existing furniture once, in one revision', () => {
  const scene = structuredClone(initial.scene)
  const movable = scene.furniture.find((item) => !item.is_fixed)!
  const fixed = scene.furniture.find((item) => item.is_fixed)!
  const fixedPose = { ...fixed.pose }
  useStore.setState({
    ...initial,
    scene,
    chat: [
      {
        role: 'assistant',
        text: 'Proposed',
        baseRevision: scene.revision,
        additions: [proposal()],
        poses: {
          [movable.id]: { x: 3, z: 3, yaw_deg: 90 },
          [fixed.id]: { x: 8, z: 8, yaw_deg: 90 },
        },
      },
    ],
  })
  useStore.getState().applyPoses(0)
  const applied = useStore.getState()
  expect(applied.scene.furniture.length).toBe(scene.furniture.length + 1)
  expect(
    applied.scene.furniture.find((item) => item.id === movable.id)?.pose.x,
  ).toBe(3)
  expect(
    applied.scene.furniture.find((item) => item.id === fixed.id)?.pose,
  ).toEqual(fixedPose)
  expect(applied.scene.revision).toBe(scene.revision + 1)
  useStore.getState().applyPoses(0)
  expect(useStore.getState().scene).toBe(applied.scene)
})

test('stale proposals and active gestures cannot add furniture', () => {
  for (const interacting of [true, false]) {
    useStore.setState({
      ...initial,
      interacting,
      chat: [
        {
          role: 'assistant',
          text: 'Proposed',
          baseRevision: initial.scene.revision - (interacting ? 0 : 1),
          additions: [proposal()],
        },
      ],
    })
    useStore.getState().applyPoses(0)
    expect(useStore.getState().scene).toBe(initial.scene)
  }
})

test('duplicate addition IDs are rejected atomically', () => {
  useStore.setState({
    ...initial,
    chat: [
      {
        role: 'assistant',
        text: 'Proposed',
        baseRevision: initial.scene.revision,
        additions: [proposal(), proposal()],
      },
    ],
  })
  useStore.getState().applyPoses(0)
  expect(useStore.getState().scene).toBe(initial.scene)
})
