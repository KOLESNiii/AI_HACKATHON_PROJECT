import { afterEach, expect, test } from 'bun:test'
import { catalog } from '../src/data/catalog'
import { proposalSummary, sendAgentMessage } from '../src/lib/agent'
import type { AuditReport } from '../src/lib/contracts'
import { useStore, type ChatMessage } from '../src/store'

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
    expect(options?.signal?.aborted).toBe(false)
    controller.abort()
    expect(options?.signal?.aborted).toBe(true)
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

test('chat preserves readable validation errors from the spatial transport', async () => {
  globalThis.fetch = (async () =>
    Response.json(
      { detail: [{ msg: 'Door hinge must lie on its wall segment' }] },
      { status: 422 },
    )) as typeof fetch
  await expect(sendAgentMessage(initial.scene, 'Add a chair')).rejects.toThrow(
    'The room could not be checked: Door hinge must lie on its wall segment',
  )
})

test('chat previews the proposed audit and rejects a report for another revision', async () => {
  const report = {
    scene_id: initial.scene.scene_id,
    scene_revision: initial.scene.revision,
    collisions: [],
    blocked_doors: [],
    out_of_bounds_item_ids: [],
    clearance_issues: [],
    walkable_floor_ratio: 0.75,
    feng_shui: null,
  }
  globalThis.fetch = (async () =>
    Response.json({
      text: 'Proposed',
      additions: [proposal()],
      report,
    })) as typeof fetch
  const reply = await sendAgentMessage(initial.scene, 'Add a chair')
  expect(reply.outlook).toContain('75% walkable')
  expect(reply.additions?.[0].id).toBe('new-item')
  report.scene_revision += 1
  await expect(sendAgentMessage(initial.scene, 'Add a chair')).rejects.toThrow(
    'The room changed while I was thinking. Ask again.',
  )
})

test('Dismiss prevents both addition-only and pose-only proposals from applying', () => {
  for (const change of [
    { additions: [proposal()] },
    { poses: { [initial.scene.furniture[0].id]: { x: 3, z: 3, yaw_deg: 0 } } },
  ]) {
    useStore.setState({
      ...initial,
      chat: [
        {
          role: 'assistant',
          text: 'Proposed',
          baseRevision: initial.scene.revision,
          ...change,
        },
      ],
    })
    useStore.getState().dismissProposal(0)
    expect(useStore.getState().chat[0].dismissed).toBe(true)
    useStore.getState().applyPoses(0)
    expect(useStore.getState().scene).toBe(initial.scene)
  }
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

test('a Library item keeps the scene acceptable to the spatial service', () => {
  // The services validate RoomScene: an empty glb_url made every chat request fail (422).
  useStore.getState().addFromCatalog(catalog[0])
  const added = useStore.getState().scene.furniture.at(-1)!
  expect(added.is_proxy).toBe(false)
  expect(added.glb_url).toBe(catalog[0].asset!.glb_url)
  expect(added.bbox_m).toEqual(catalog[0].bbox_m)
  expect(added.product_url).toBe(catalog[0].product_url)
  expect(added.collision_parts).toEqual(catalog[0].asset!.collision_parts)
  for (const item of useStore.getState().scene.furniture) {
    expect(item.glb_url).toMatch(/^(https?:\/\/|\/[^/])/) // GLB_URL_PATTERN
    expect(item.id).toMatch(/^[a-z0-9][a-z0-9_-]{0,63}$/) // ITEM_ID_PATTERN
  }
})

test('every Library product has usable metric dimensions', () => {
  for (const { bbox_m } of catalog) {
    for (const [size, limit] of [
      [bbox_m.width, 20],
      [bbox_m.height, 10],
      [bbox_m.depth, 20],
    ]) {
      expect(size).toBeGreaterThan(0.01)
      expect(size).toBeLessThanOrEqual(limit)
    }
  }
})

test('Apply carries the audited report into Stats at the new revision', () => {
  const { scene } = initial
  const report = {
    scene_id: scene.scene_id,
    scene_revision: scene.revision,
    collisions: [],
    blocked_doors: [],
    out_of_bounds_item_ids: [],
    clearance_issues: [],
  } as unknown as AuditReport
  for (const [sent, expected] of [
    [report, scene.revision + 1],
    [{ ...report, scene_id: 'another-room' }, null],
    [{ ...report, scene_revision: scene.revision + 5 }, null],
  ] as const) {
    useStore.setState({
      ...initial,
      chat: [
        {
          role: 'assistant',
          text: 'Proposed',
          baseRevision: scene.revision,
          additions: [proposal()],
          report: sent,
        },
      ],
    })
    useStore.getState().applyPoses(0)
    expect(useStore.getState().scene.revision).toBe(scene.revision + 1)
    expect(useStore.getState().audit?.scene_revision ?? null).toBe(expected)
  }
})

test('the proposal row says what Apply will do', () => {
  const pose = { x: 1, z: 1, yaw_deg: 0 }
  const message = (m: Partial<ChatMessage>): ChatMessage => ({
    role: 'assistant',
    text: '',
    ...m,
  })
  expect(proposalSummary(message({ additions: [proposal()] }))).toBe(
    'Proposed layout · 1 new item',
  )
  expect(
    proposalSummary(message({ additions: [proposal()], poses: { a: pose } })),
  ).toBe('Proposed layout · 1 new item · 1 move')
  expect(proposalSummary(message({ poses: { a: pose, b: pose } }))).toBe(
    'Proposed layout · 2 moves',
  )
})
