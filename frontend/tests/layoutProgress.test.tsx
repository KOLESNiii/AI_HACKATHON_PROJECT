import { afterEach, beforeEach, expect, test } from 'bun:test'
import { renderToStaticMarkup } from 'react-dom/server'
import {
  HarnessProgress,
  HarnessStatus,
} from '../src/components/editor/Sidebar'
import { freshMockScene } from '../src/data/mockScene'
import { streamAgentMessage as sendAgentMessage } from '../src/lib/agent'
import type {
  AuditReport,
  LayoutProgress,
  LayoutProposal,
} from '../src/lib/contracts'
import { useStore } from '../src/store'
import { solveEvent, solveResponse } from './solveStream'

const initial = useStore.getState()
const originalFetch = globalThis.fetch
const encode = new TextEncoder()
const update: LayoutProgress = {
  stage: 'evaluating',
  message: 'Checking placement…',
}
const tick = () => new Promise((resolve) => setTimeout(resolve, 0))

beforeEach(() =>
  useStore.setState({
    ...initial,
    scene: freshMockScene(),
    screen: 'editor',
    tab: 'chat',
  }),
)
afterEach(() => {
  useStore.getState().agentAbort?.abort()
  globalThis.fetch = originalFetch
  useStore.setState(initial)
})

function proposal(): LayoutProposal {
  const scene = useStore.getState().scene
  const item = scene.furniture.find((i) => !i.is_fixed)!
  return {
    proposal_id: 'streamed-proposal',
    poses: { [item.id]: { ...item.pose, x: item.pose.x + 1 } },
    improved: true,
    outcome: 'completed',
    goal: 'custom',
    explanation: 'A checked alternative.',
    report: {
      scene_id: scene.scene_id,
      scene_revision: scene.revision,
      collisions: [],
      blocked_doors: [],
      out_of_bounds_item_ids: [],
      clearance_issues: [],
      overall_score: null,
      walkable_floor_ratio: null,
      glare_orientation_grounded: null,
      glare_alerts: null,
      feng_shui: null,
    } satisfies AuditReport,
  }
}

function mockResponse(response: Response) {
  globalThis.fetch = (async () => response) as typeof fetch
}

function liveStream() {
  let controller!: ReadableStreamDefaultController<Uint8Array>
  const body = new ReadableStream<Uint8Array>({
    start(c) {
      controller = c
    },
  })
  mockResponse(
    new Response(body, { headers: { 'Content-Type': 'text/event-stream' } }),
  )
  return {
    push(event: string, data: unknown) {
      controller.enqueue(encode.encode(solveEvent(event, data)))
    },
    close() {
      controller.close()
    },
  }
}

test('progress updates status and the expandable log before any proposal can be accepted', async () => {
  const base = useStore.getState().scene
  const candidate = proposal()
  const stream = liveStream()
  const pending = useStore.getState().sendChat('Move the wardrobe')
  stream.push('progress', update)
  await tick()
  const working = useStore.getState()
  expect(working.agentBusy).toBe(true)
  expect(working.agentProgress).toEqual([update])
  expect(working.chat.some((m) => m.proposal)).toBe(false)
  const html = renderToStaticMarkup(
    <HarnessStatus updates={working.agentProgress} onCancel={() => {}} />,
  )
  expect(html).toContain('Checking placement…')
  expect(html).toContain('<details')
  expect(html).toContain('Activity · 1')
  expect(html).toContain('Cancel')
  expect(html).not.toContain('Accept layout')
  stream.push('result', candidate)
  await pending
  const complete = useStore.getState()
  expect(complete.scene).toBe(base)
  expect(complete.agentBusy).toBe(false)
  expect(complete.agentProgress).toEqual([])
  expect(complete.chat.at(-1)?.progress).toEqual([update])
  expect(complete.chat.at(-1)?.proposal?.proposal_id).toBe(
    candidate.proposal_id,
  )
  expect(
    renderToStaticMarkup(
      <HarnessProgress updates={complete.chat.at(-1)!.progress!} />,
    ),
  ).toContain('Checking placement…')
})

test('decoder handles split UTF-8, CRLF, comments and multiline JSON event data', async () => {
  const candidate = proposal()
  const message = { ...update, message: 'Checking café…' }
  const wire =
    ': keep-alive\r\n\r\nevent: progress\r\ndata: ' +
    JSON.stringify(message, null, 2).split('\n').join('\r\ndata: ') +
    '\r\n\r\n' +
    solveEvent('result', candidate).replaceAll('\n', '\r\n')
  const bytes = encode.encode(wire)
  let offset = 0
  mockResponse(
    new Response(
      new ReadableStream<Uint8Array>({
        pull(controller) {
          if (offset === bytes.length) controller.close()
          else controller.enqueue(bytes.slice(offset, ++offset))
        },
      }),
      { headers: { 'Content-Type': 'text/event-stream' } },
    ),
  )
  const seen: LayoutProgress[] = []
  const result = await sendAgentMessage(
    useStore.getState().scene,
    'Rearrange',
    undefined,
    (p) => seen.push(p),
  )
  expect(seen).toEqual([message])
  expect(result.proposal?.proposal_id).toBe(candidate.proposal_id)
})

test('several events in one chunk are processed in order and reading stops at the result', async () => {
  const candidate = proposal()
  mockResponse(
    new Response(
      solveEvent('progress', update) +
        solveEvent('result', candidate) +
        solveEvent('progress', update),
      { headers: { 'Content-Type': 'text/event-stream' } },
    ),
  )
  const seen: LayoutProgress[] = []
  await sendAgentMessage(
    useStore.getState().scene,
    'Rearrange',
    undefined,
    (p) => seen.push(p),
  )
  expect(seen).toEqual([update])
})

test('cancellation retains activity and cannot pollute the next request', async () => {
  const stream = liveStream()
  const pending = useStore.getState().sendChat('First')
  stream.push('progress', update)
  await tick()
  useStore.getState().cancelAgent()
  await pending
  expect(useStore.getState().chat.at(-1)?.progress).toEqual([update])
  expect(useStore.getState().agentProgress).toEqual([])
  mockResponse(solveResponse(proposal()))
  await useStore.getState().sendChat('Second')
  expect(useStore.getState().chat.at(-1)?.progress).toEqual([])
  expect(useStore.getState().chat.filter((m) => m.proposal)).toHaveLength(1)
})

test('a room change aborts the stream and drops all prior activity', async () => {
  const stream = liveStream()
  const pending = useStore.getState().sendChat('First')
  stream.push('progress', update)
  await tick()
  useStore.getState().openRoom()
  await pending
  expect(useStore.getState().agentProgress).toEqual([])
  expect(useStore.getState().chat).toEqual([])
})

test('a timeout during the stream retains activity but never creates a proposal or retries', async () => {
  const realTimeout = globalThis.setTimeout
  globalThis.setTimeout = ((
    fn: TimerHandler,
    ms?: number,
    ...args: unknown[]
  ) => realTimeout(fn, ms === 120_000 ? 10 : ms, ...args)) as typeof setTimeout
  try {
    const stream = liveStream()
    const pending = useStore.getState().sendChat('First')
    stream.push('progress', update)
    await pending
    expect(useStore.getState().chat.at(-1)?.text).toContain('timed out')
    expect(useStore.getState().chat.at(-1)?.progress).toEqual([update])
    expect(useStore.getState().chat.at(-1)?.proposal).toBeUndefined()
  } finally {
    globalThis.setTimeout = realTimeout
  }
})

test('malformed events, terminal errors and truncated streams fail without a proposal or retries', async () => {
  for (const wire of [
    solveEvent('progress', { ...update, stage: 'imagined' }),
    'event: progress\ndata: {broken}\n\n',
    solveEvent('error', { message: 'Layout validation failed.' }),
    solveEvent('progress', update),
    solveEvent('result', {
      ...proposal(),
      poses: { unknown: { x: 0, z: 0, yaw_deg: 0 } },
    }),
  ]) {
    let calls = 0
    globalThis.fetch = (async () => {
      calls++
      return new Response(wire, {
        headers: { 'Content-Type': 'text/event-stream' },
      })
    }) as typeof fetch
    await useStore.getState().sendChat('Rearrange')
    expect(calls).toBe(1)
    expect(useStore.getState().agentBusy).toBe(false)
    expect(useStore.getState().chat.at(-1)?.proposal).toBeUndefined()
    expect(useStore.getState().chat.at(-1)?.text).not.toBe(
      'A checked alternative.',
    )
  }
})
