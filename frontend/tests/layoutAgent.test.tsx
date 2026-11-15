import { afterEach, beforeEach, expect, test } from 'bun:test'
import { renderToStaticMarkup } from 'react-dom/server'
import { LayoutProposalCard } from '../src/components/editor/LayoutProposalCard'
import { freshMockScene } from '../src/data/mockScene'
import {
  readProposal,
  streamAgentMessage as sendAgentMessage,
} from '../src/lib/agent'
import { requestJson } from '../src/lib/api'
import type {
  AuditReport,
  LayoutProposal,
  RoomScene,
} from '../src/lib/contracts'
import { connectEditorServices } from '../src/lib/editorServices'
import { layoutChanges } from '../src/lib/layoutDiff'
import { useStore, type ChatMessage } from '../src/store'

import { solveResponse } from './solveStream'
import { scoreResult } from './fengShuiFixtures'

const initial = useStore.getState()
const originalFetch = globalThis.fetch
let disconnect: (() => void) | undefined

function scene(): RoomScene {
  const room = freshMockScene()
  room.furniture = room.furniture
    .slice(0, 2)
    .map((item, i) => ({ ...item, is_fixed: i === 1 }))
  return room
}
function audit(room = useStore.getState().scene): AuditReport {
  return {
    scene_id: room.scene_id,
    scene_revision: room.revision,
    collisions: [],
    blocked_doors: [],
    out_of_bounds_item_ids: [],
    clearance_issues: [],
    walkable_floor_ratio: 0.7,
    feng_shui: null,
    glare_alerts: null,
    glare_orientation_grounded: null,
    overall_score: null,
  }
}
function proposal(room = useStore.getState().scene): LayoutProposal {
  const item = room.furniture[0]
  return {
    proposal_id: 'proposal-1',
    poses: {
      [item.id]: {
        ...item.pose,
        x: item.pose.x + 1,
        yaw_deg: item.pose.yaw_deg + 90,
      },
    },
    improved: true,
    outcome: 'completed',
    explanation: 'Moved one item to clear access.',
    goal: 'roomier',
    report: audit(room),
  }
}
function response(
  value: unknown,
  status = 200,
  headers: Record<string, string> = {},
) {
  if (
    status === 200 &&
    value !== null &&
    typeof value === 'object' &&
    'proposal_id' in value
  )
    return solveResponse(value)
  return new Response(JSON.stringify(value), {
    status,
    headers: { 'Content-Type': 'application/json', ...headers },
  })
}
function stubFetch(
  fn: (path: string, init?: RequestInit) => Response | Promise<Response>,
) {
  globalThis.fetch = ((path, init) => fn(String(path), init)) as typeof fetch
}
function deferred<T>() {
  let resolve!: (value: T) => void
  const promise = new Promise<T>((done) => {
    resolve = done
  })
  return { promise, resolve }
}
const delay = (ms = 10) => new Promise((resolve) => setTimeout(resolve, ms))

beforeEach(() =>
  useStore.setState({ ...initial, scene: scene(), screen: 'editor' }),
)
afterEach(() => {
  disconnect?.()
  disconnect = undefined
  const state = useStore.getState()
  state.agentAbort?.abort()
  state.auditAbort?.abort()
  state.roomAbort?.abort()
  globalThis.fetch = originalFetch
  useStore.setState(initial)
})

test('chat sends the existing solve contract without overriding the interpreted goal', async () => {
  let sent: unknown
  stubFetch((path, init) => {
    expect(path).toBe('/api/spatial_engine/chat/stream')
    expect(init?.method).toBe('POST')
    sent = JSON.parse(String(init?.body))
    return response(proposal())
  })
  const result = await sendAgentMessage(
    useStore.getState().scene,
    '  Make it roomier  ',
  )
  expect(sent).toEqual({
    scene: useStore.getState().scene,
    instruction: 'Make it roomier',
  })
  expect(result.proposal?.goal).toBe('roomier')
})

test('proposal is a reviewable diff; accepting changes poses once and preserves assets and fixed items', async () => {
  const before = useStore.getState().scene
  const baseline = audit(before)
  useStore.setState({ audit: baseline })
  const candidate = proposal(before)
  stubFetch(() => response(candidate))
  await useStore.getState().sendChat('Make it roomier')
  const state = useStore.getState()
  expect(state.scene).toBe(before)
  expect(state.audit).toBe(baseline)
  expect(state.chat[1].baselineAudit).toBe(baseline)
  const changes = layoutChanges(before, candidate)
  expect(changes).toHaveLength(1)
  expect(changes[0].distance).toBeCloseTo(1)
  expect(changes[0].turn).toBe(90)
  state.applyPoses(1)
  const accepted = useStore.getState()
  expect(accepted.scene.revision).toBe(before.revision + 1)
  expect(accepted.scene.furniture[0].pose).toEqual(
    candidate.poses[before.furniture[0].id],
  )
  expect(accepted.scene.furniture[0].glb_url).toBe(before.furniture[0].glb_url)
  expect(accepted.scene.furniture[0].bbox_m).toBe(before.furniture[0].bbox_m)
  expect(accepted.scene.furniture[1]).toBe(before.furniture[1])
  expect(accepted.scene.shell_glb_url).toBe(before.shell_glb_url)
  expect(accepted.chat[1].applied).toBe(true)
  expect(accepted.audit).toBeNull()
  accepted.applyPoses(1)
  expect(useStore.getState().scene).toBe(accepted.scene)
})

test('reject leaves the scene, revision and current audit untouched and prevents acceptance', async () => {
  const before = useStore.getState().scene
  const baseline = audit(before)
  useStore.setState({ audit: baseline })
  stubFetch(() => response(proposal()))
  await useStore.getState().sendChat('Rearrange')
  useStore.getState().rejectProposal(1)
  useStore.getState().applyPoses(1)
  expect(useStore.getState().chat[1].rejected).toBe(true)
  expect(useStore.getState().scene).toBe(before)
  expect(useStore.getState().audit).toBe(baseline)
})

test('same-revision live edits and committed edits make a proposal stale', async () => {
  stubFetch(() => response(proposal()))
  await useStore.getState().sendChat('Rearrange')
  const s = useStore.getState()
  s.setPose(s.scene.furniture[0].id, { x: 2 })
  const live = useStore.getState().scene
  expect(live.revision).toBe(s.scene.revision)
  s.applyPoses(1)
  expect(useStore.getState().scene).toBe(live)
  s.commitEdit(null)
  const committed = useStore.getState().scene
  s.applyPoses(1)
  expect(useStore.getState().scene).toBe(committed)
})

test('accept is blocked while interacting, loading a room, or in play', async () => {
  stubFetch(() => response(proposal()))
  await useStore.getState().sendChat('Rearrange')
  const before = useStore.getState().scene
  for (const state of [
    { interacting: true },
    { roomLoading: true },
    { mode: 'play' as const },
  ]) {
    useStore.setState({
      interacting: false,
      roomLoading: false,
      mode: 'edit',
      ...state,
    })
    useStore.getState().applyPoses(1)
    expect(useStore.getState().scene).toBe(before)
  }
})

test('invalid unknown, fixed, nonfinite, mismatched or unverified proposals are rejected atomically', () => {
  const room = useStore.getState().scene
  const good = proposal(room)
  const pose = good.poses[room.furniture[0].id]
  for (const bad of [
    { ...good, poses: { missing: pose } },
    { ...good, poses: { [room.furniture[1].id]: pose } },
    { ...good, poses: { [room.furniture[0].id]: { ...pose, x: NaN } } },
    { ...good, report: { ...good.report, scene_revision: 999 } },
    {
      ...good,
      report: {
        ...good.report,
        collisions: [{ item_a: 'a', item_b: 'b', overlap_area_m2: 1 }],
      },
    },
    { ...good, improved: false },
    { ...good, outcome: 'assistant_unavailable' },
    { ...good, poses: {} },
  ])
    expect(() => readProposal(bad, room)).toThrow()
  expect(useStore.getState().scene).toBe(room)
})

test('all non-improved outcomes remain honest results without an Apply action', async () => {
  for (const outcome of [
    'completed',
    'stopped_early',
    'assistant_unavailable',
  ] as const) {
    const p = { ...proposal(), poses: {}, improved: false, outcome }
    stubFetch(() => response(p))
    await useStore.getState().sendChat('Rearrange')
    const message = useStore.getState().chat.at(-1)!
    expect(message.proposal?.outcome).toBe(outcome)
    const html = renderToStaticMarkup(
      <LayoutProposalCard
        message={message}
        stale={false}
        blocked={false}
        onAccept={() => {}}
        onReject={() => {}}
      />,
    )
    expect(html).not.toContain('Accept layout')
    expect(html).toContain(
      outcome === 'completed'
        ? 'No improved layout found'
        : outcome === 'stopped_early'
          ? 'Search stopped before finding an improvement'
          : 'Layout agent unavailable',
    )
  }
})

test('cancellation and a late response cannot replace a newer request', async () => {
  const late = deferred<Response>()
  const old = proposal()
  stubFetch(() => late.promise)
  const pending = useStore.getState().sendChat('First request')
  useStore.getState().cancelAgent()
  stubFetch(() => response({ ...proposal(), proposal_id: 'new' }))
  await useStore.getState().sendChat('Second request')
  late.resolve(response(old))
  await pending
  expect(useStore.getState().chat.at(-1)?.proposal?.proposal_id).toBe('new')
  expect(useStore.getState().agentBusy).toBe(false)
  expect(useStore.getState().chat.filter((m) => m.proposal)).toHaveLength(1)
})

test('a room switch drops an in-flight proposal even when its revision matches', async () => {
  const late = deferred<Response>()
  const old = proposal()
  stubFetch(() => late.promise)
  const pending = useStore.getState().sendChat('Rearrange')
  useStore.getState().openRoom()
  late.resolve(response(old))
  await pending
  expect(useStore.getState().chat).toEqual([])
  expect(useStore.getState().agentBusy).toBe(false)
})

test('invalid input, validation errors and network errors never mutate the room or retry', async () => {
  let calls = 0
  stubFetch(() => {
    calls++
    return response({}, 422)
  })
  await expect(
    sendAgentMessage(useStore.getState().scene, 'x'.repeat(501)),
  ).rejects.toThrow('500')
  expect(calls).toBe(0)
  const before = useStore.getState().scene
  await useStore.getState().sendChat('Rearrange')
  expect(calls).toBe(1)
  expect(useStore.getState().chat.at(-1)?.text).toContain('validated')
  stubFetch(() => {
    calls++
    throw new TypeError('offline')
  })
  await useStore.getState().sendChat('Rearrange')
  expect(calls).toBe(2)
  expect(useStore.getState().chat.at(-1)?.text).toContain(
    'could not be reached',
  )
  expect(useStore.getState().scene).toBe(before)
})

test('timeout aborts a request and reports a timeout rather than a successful result', async () => {
  stubFetch(
    (_path, init) =>
      new Promise((_resolve, reject) => {
        init?.signal?.addEventListener(
          'abort',
          () => reject(init.signal?.reason),
          { once: true },
        )
      }),
  )
  await expect(requestJson('/test', {}, undefined, 5)).rejects.toThrow(
    'timed out',
  )
})

test('audit ignores same-revision live changes and supports explicit retry after failure', async () => {
  const late = deferred<Response>()
  const old = audit()
  stubFetch(() => late.promise)
  const pending = useStore.getState().refreshAudit()
  useStore
    .getState()
    .setPose(useStore.getState().scene.furniture[0].id, { x: 3 })
  late.resolve(response(old))
  await pending
  expect(useStore.getState().audit).toBeNull()
  stubFetch(() => response({}, 500))
  await useStore.getState().refreshAudit()
  expect(useStore.getState().auditStatus).toBe('error')
  stubFetch(() => response(audit()))
  await useStore.getState().refreshAudit()
  expect(useStore.getState().auditStatus).toBe('ready')
  expect(useStore.getState().auditError).toBeNull()
})

test('canonical room loading preserves warnings and never overwrites a newer room session', async () => {
  const first = useStore.getState().scene
  const canonical = { ...first, revision: 0 }
  stubFetch(() =>
    response(canonical, 200, {
      'X-Reconstruction-Warnings': JSON.stringify(['Review dimensions']),
    }),
  )
  await useStore.getState().loadRoom()
  expect(useStore.getState().scene).toEqual(canonical)
  expect(useStore.getState().roomWarnings).toEqual(['Review dimensions'])
  const late = deferred<Response>()
  stubFetch(() => late.promise)
  const pending = useStore.getState().loadRoom()
  useStore.getState().openRoom()
  const newer = useStore.getState().scene
  late.resolve(response(canonical))
  await pending
  expect(useStore.getState().scene).toBe(newer)
  stubFetch(() => response({}, 500))
  await useStore.getState().loadRoom()
  expect(useStore.getState().scene).toBe(newer)
  expect(useStore.getState().roomWarnings[0]).toContain('local demo room')
})

test('editor lifecycle loads, debounces commits, audits acceptance, and ignores continuous drags', async () => {
  let audits = 0
  stubFetch((path, init) => {
    if (path.includes('/scenes/')) return response(useStore.getState().scene)
    if (path.endsWith('/chat/stream')) return response(proposal())
    if (path.endsWith('/feng-shui/score'))
      return response(scoreResult(JSON.parse(String(init?.body)).scene))
    const room = JSON.parse(String(init?.body)) as RoomScene
    audits++
    return response(audit(room))
  })
  disconnect = connectEditorServices(5)
  await delay(20)
  expect(audits).toBe(1)
  useStore.getState().setTab('library')
  useStore.getState().setInteracting(true)
  useStore
    .getState()
    .setPose(useStore.getState().scene.furniture[0].id, { x: 3 })
  await delay()
  expect(audits).toBe(1)
  useStore.getState().commitEdit(null)
  useStore.getState().setInteracting(false)
  useStore.getState().commitEdit(null)
  await delay(20)
  expect(audits).toBe(2)
  await useStore.getState().sendChat('Rearrange')
  useStore.getState().applyPoses(1)
  await delay(20)
  expect(audits).toBe(3)
  expect(useStore.getState().audit?.scene_revision).toBe(
    useStore.getState().scene.revision,
  )
  disconnect()
  disconnect = undefined
  useStore.getState().commitEdit(null)
  await delay()
  expect(audits).toBe(3)
})

test('room diff renders before/after measurements, turn wrapping, and accepted/rejected/stale states', () => {
  const room = useStore.getState().scene
  const p = proposal(room)
  p.poses[room.furniture[0].id] = {
    ...room.furniture[0].pose,
    yaw_deg: room.furniture[0].pose.yaw_deg + 355,
  }
  expect(layoutChanges(room, p)[0].turn).toBe(-5)
  const message: ChatMessage = {
    role: 'assistant',
    text: p.explanation,
    proposal: { ...p, outcome: 'stopped_early' },
    baseScene: room,
    baselineAudit: { ...audit(room), walkable_floor_ratio: 0.5 },
    roomSession: 0,
  }
  const render = (m: ChatMessage, stale = false) =>
    renderToStaticMarkup(
      <LayoutProposalCard
        message={m}
        stale={stale}
        blocked={false}
        onAccept={() => {}}
        onReject={() => {}}
      />,
    )
  const html = render(message)
  expect(html).toContain('Room diff')
  expect(html).toContain('50%')
  expect(html).toContain('70%')
  expect(html).toContain('Checking…')
  expect(html).toContain('5° clockwise')
  expect(html).toContain('Search stopped early')
  expect(html).toContain('Accept layout')
  expect(html).toContain('Reject')
  for (const [m, stale, status] of [
    [{ ...message, applied: true }, false, 'Accepted'],
    [{ ...message, rejected: true }, false, 'Rejected'],
    [message, true, 'Outdated'],
  ] as const) {
    const result = render(m, stale)
    expect(result).toContain(status)
    expect(result).not.toContain('Accept layout')
  }
})

test('custom-goal proposals from /solve are accepted and flagged as partly checked', () => {
  const room = useStore.getState().scene
  const custom = readProposal({ ...proposal(room), goal: 'custom' }, room)
  expect(custom.goal).toBe('custom')
  const html = renderToStaticMarkup(
    <LayoutProposalCard
      message={{
        role: 'assistant',
        text: '',
        proposal: custom,
        baseScene: room,
      }}
      stale={false}
      blocked={false}
      onAccept={() => {}}
      onReject={() => {}}
    />,
  )
  expect(html).toContain('only fit, doors and access were checked')
  expect(() =>
    readProposal({ ...proposal(room), goal: 'cosy' }, room),
  ).toThrow()
})
