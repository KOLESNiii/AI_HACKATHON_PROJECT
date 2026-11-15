import { afterEach, expect, test } from 'bun:test'
import { catalog } from '../src/data/catalog'
import { proposalSummary, sendAgentMessage } from '../src/lib/agent'
import type { AuditReport } from '../src/lib/contracts'
import { useStore } from '../src/store'

import { solveEvent } from './solveStream'
import { readProposal } from '../src/lib/agent'
import { layoutChanges } from '../src/lib/layoutDiff'

const initial = useStore.getState()
const originalFetch = globalThis.fetch

afterEach(() => {
  useStore.setState(initial)
  globalThis.fetch = originalFetch
})

function proposal() {
  const { sku: _sku, ...existing } = catalog[0]
  return {
    ...existing,
    id: 'new-item',
    is_fixed: false,
    is_proxy: false,
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
  await expect(
    sendAgentMessage(initial.scene, 'Add a chair', controller.signal),
  ).rejects.toThrow()
})

test('agent errors do not become successful proposals', async () => {
  globalThis.fetch = (async () =>
    new Response('', { status: 503 })) as typeof fetch
  await expect(sendAgentMessage(initial.scene, 'Add a chair')).rejects.toThrow()
})

test('the JSON chat client also rejects proxy or altered Library assets', async () => {
  for (const change of [
    { is_proxy: true },
    { glb_url: '/api/spatial_engine/proxies/1/1/1.glb' },
    { name: 'Invented desk' },
  ]) {
    let calls = 0
    globalThis.fetch = (async () => {
      calls++
      return Response.json({
        text: 'Proposed',
        additions: [{ ...proposal(), ...change }],
      })
    }) as typeof fetch
    await expect(sendAgentMessage(initial.scene, 'Add a desk')).rejects.toThrow(
      'Library',
    )
    expect(calls).toBe(1)
  }
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

function report(): AuditReport {
  return {
    scene_id: initial.scene.scene_id,
    scene_revision: initial.scene.revision,
    collisions: [],
    blocked_doors: [],
    out_of_bounds_item_ids: [],
    clearance_issues: [],
    walkable_floor_ratio: 0.75,
    overall_score: null,
    feng_shui: null,
    glare_alerts: null,
    glare_orientation_grounded: null,
  }
}
async function propose(poses = {}) {
  useStore.setState({
    ...initial,
    screen: 'editor',
    scene: structuredClone(initial.scene),
  })
  const base = useStore.getState().scene
  globalThis.fetch = (async () =>
    new Response(
      solveEvent('reply', {
        text: 'Proposed one item',
        poses,
        additions: [proposal()],
        report: report(),
      }),
      { headers: { 'Content-Type': 'text/event-stream' } },
    )) as typeof fetch
  await useStore.getState().sendChat('Add a chair')
  return base
}

test('Reject prevents additions from applying through the reviewed proposal', async () => {
  const base = await propose()
  useStore.getState().rejectProposal(1)
  useStore.getState().applyPoses(1)
  expect(useStore.getState().chat[1].rejected).toBe(true)
  expect(useStore.getState().scene).toBe(base)
})

test('Accept adds the Library mesh and moves furniture once in one saved version, preserving fixed items', async () => {
  const movable = initial.scene.furniture.find((i) => !i.is_fixed)!
  const base = await propose({ [movable.id]: { x: 3, z: 3, yaw_deg: 90 } })
  const preview = useStore.getState().chat[1].proposal!
  expect(layoutChanges(base, preview).some((c) => c.added)).toBe(true)
  useStore.getState().applyPoses(1)
  const applied = useStore.getState()
  expect(applied.scene.furniture.length).toBe(base.furniture.length + 1)
  expect(applied.scene.furniture.find((i) => i.id === movable.id)?.pose.x).toBe(
    3,
  )
  for (const item of base.furniture.filter((i) => i.is_fixed))
    expect(applied.scene.furniture.find((i) => i.id === item.id)).toEqual(item)
  expect(applied.scene.revision).toBe(base.revision + 1)
  expect(applied.versions.at(-1)?.source).toBe('agent')
  expect(applied.audit).toBeNull() // The normal lifecycle re-audits this exact new revision.
  applied.applyPoses(1)
  expect(useStore.getState().scene).toBe(applied.scene)
})

test('stale proposals and active gestures cannot add furniture', async () => {
  for (const interacting of [true, false]) {
    const base = await propose()
    if (interacting) useStore.setState({ interacting: true })
    else useStore.getState().commitEdit(null)
    const before = useStore.getState().scene
    useStore.getState().applyPoses(1)
    expect(useStore.getState().scene).toBe(before)
    expect(useStore.getState().scene.furniture).toEqual(base.furniture)
  }
})

test('duplicate additions, unknown moves, fixed moves and invalid metadata are rejected atomically', () => {
  const room = initial.scene
  const added = proposal()
  const fixed = room.furniture.find((i) => i.is_fixed)!
  const good = {
    proposal_id: 'addition',
    poses: {},
    additions: [added],
    report: report(),
    improved: true,
    outcome: 'completed',
    goal: null,
    explanation: 'Add one item',
  }
  for (const bad of [
    { ...good, additions: [added, added] },
    { ...good, additions: [{ ...added, id: room.furniture[0].id }] },
    { ...good, additions: [{ ...added, is_fixed: true }] },
    { ...good, additions: [{ ...added, glb_url: '' }] },
    { ...good, additions: [{ ...added, is_proxy: true }] },
    {
      ...good,
      additions: [
        { ...added, glb_url: '/api/spatial_engine/proxies/1/1/1.glb' },
      ],
    },
    { ...good, additions: [{ ...added, name: 'Invented asset' }] },
    {
      ...good,
      additions: [
        {
          ...added,
          bbox_m: { ...added.bbox_m, width: added.bbox_m.width / 2 },
        },
      ],
    },
    {
      ...good,
      additions: [
        {
          ...added,
          collision_parts: [
            { x: 0, z: 0, width: 0.1, depth: 0.1, y_min: 0, y_max: 0.1 },
          ],
        },
      ],
    },
    {
      ...good,
      additions: [{ ...added, bbox_m: { ...added.bbox_m, width: NaN } }],
    },
    { ...good, poses: { unknown: { x: 0, z: 0, yaw_deg: 0 } } },
    { ...good, poses: { [fixed.id]: { x: 0, z: 0, yaw_deg: 0 } } },
  ])
    expect(() => readProposal(bad, room)).toThrow()
})

test('unchanged existing findings do not reject an addition, but findings involving it do', () => {
  const added = proposal()
  const existing = initial.scene.furniture[0].id
  const good = {
    proposal_id: 'addition',
    poses: {},
    additions: [added],
    report: { ...report(), out_of_bounds_item_ids: [existing] },
    improved: true,
    outcome: 'completed',
    goal: null,
    explanation: 'Add one item',
  }
  expect(readProposal(good, initial.scene).additions).toHaveLength(1)
  expect(() =>
    readProposal(
      {
        ...good,
        report: { ...good.report, out_of_bounds_item_ids: [added.id] },
      },
      initial.scene,
    ),
  ).toThrow()
})

test('Library additions retain the existing mesh, dimensions and valid service URLs', () => {
  useStore.setState({ ...initial, screen: 'editor' })
  useStore.getState().addFromCatalog(catalog[0])
  const added = useStore.getState().scene.furniture.at(-1)!
  expect(added.is_proxy).toBe(catalog[0].is_proxy)
  expect(added.glb_url).toBe(catalog[0].glb_url)
  expect(added.bbox_m).toEqual(catalog[0].bbox_m)
  for (const item of useStore.getState().scene.furniture) {
    expect(item.glb_url).toMatch(/^(https?:\/\/|\/[^/])/)
    expect(item.id).toMatch(/^[a-z0-9][a-z0-9_-]{0,63}$/)
  }
})

test('the proposal summary names additions and moves', () => {
  const pose = { x: 1, z: 1, yaw_deg: 0 }
  expect(proposalSummary({ additions: [proposal()] })).toBe(
    'Proposed layout · 1 new item',
  )
  expect(proposalSummary({ additions: [proposal()], poses: { a: pose } })).toBe(
    'Proposed layout · 1 new item · 1 move',
  )
})
