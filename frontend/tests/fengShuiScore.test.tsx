import { afterEach, beforeEach, expect, test } from 'bun:test'
import { renderToStaticMarkup } from 'react-dom/server'
import { FengShuiScoreCard } from '../src/components/editor/FengShuiScoreCard'
import { AuditStats } from '../src/components/editor/Sidebar'
import { AuditDiff } from '../src/components/editor/LayoutProposalCard'
import { freshMockScene } from '../src/data/mockScene'
import type {
  AuditReport,
  LayoutProposal,
  RoomScene,
} from '../src/lib/contracts'
import { connectEditorServices } from '../src/lib/editorServices'
import {
  fetchFengShuiScore,
  fetchProposalFengShuiScores,
  readFengShuiScore,
} from '../src/lib/fengShui'
import { useStore } from '../src/store'
import { scoreResult } from './fengShuiFixtures'

const initial = useStore.getState()
const originalFetch = globalThis.fetch
let disconnect: (() => void) | undefined
const tick = (ms = 10) => new Promise((r) => setTimeout(r, ms))
function response(data: unknown, status = 200) {
  return Response.json(data, { status })
}
function audit(room: RoomScene): AuditReport {
  return {
    scene_id: room.scene_id,
    scene_revision: room.revision,
    overall_score: null,
    walkable_floor_ratio: 0.7,
    glare_orientation_grounded: null,
    collisions: [],
    blocked_doors: [],
    out_of_bounds_item_ids: [],
    clearance_issues: [],
    glare_alerts: null,
    feng_shui: null,
  }
}
beforeEach(() =>
  useStore.setState({ ...initial, scene: freshMockScene(), screen: 'editor' }),
)
afterEach(() => {
  disconnect?.()
  disconnect = undefined
  useStore.getState().fengShuiScoreAbort?.abort()
  useStore.getState().auditAbort?.abort()
  useStore.getState().roomAbort?.abort()
  globalThis.fetch = originalFetch
  useStore.setState(initial)
})

test('posts the current scene to the score endpoint, preserving null and zero', async () => {
  const scene = useStore.getState().scene
  for (const score of [null, 0, 100]) {
    globalThis.fetch = (async (path, options) => {
      expect(path).toBe('/api/spatial_engine/feng-shui/score')
      expect(options?.method).toBe('POST')
      expect(JSON.parse(String(options?.body))).toEqual({ scene })
      return response(scoreResult(scene, score))
    }) as typeof fetch
    expect((await fetchFengShuiScore(scene)).score).toBe(score)
  }
})

test('rejects invalid scores, coverage, rule data, object references and outdated results', () => {
  const scene = useStore.getState().scene
  const good = scoreResult(scene)
  for (const bad of [
    { ...good, scene_id: 'another' },
    { ...good, revision: scene.revision + 1 },
    { ...good, score: 101 },
    { ...good, score: -1 },
    { ...good, score: 50.5 },
    { ...good, coverage: 1.1 },
    { ...good, coverage: NaN },
    { ...good, capped_by_audit: 'false' },
    { ...good, unassessed: [null] },
    { ...good, rules: [{ ...good.rules[0], weight: 0 }] },
    { ...good, rules: [{ ...good.rules[0], score: -1 }] },
    { ...good, rules: [{ ...good.rules[0], object_ids: ['unknown'] }] },
    {
      ...good,
      sightlines: [
        {
          from_item_id: 'unknown',
          to_door_id: 'unknown',
          status: 'command_position',
          reason: 'Wrong',
        },
      ],
    },
  ])
    expect(() => readFengShuiScore(bad, scene)).toThrow()
})

test('room load and committed edits score automatically; continuous dragging does not', async () => {
  let scores = 0
  globalThis.fetch = (async (path, options) => {
    if (String(path).includes('/scenes/'))
      return response(useStore.getState().scene)
    const room =
      JSON.parse(String(options?.body)).scene ??
      JSON.parse(String(options?.body))
    if (String(path).endsWith('/score')) {
      scores++
      return response(scoreResult(room))
    }
    return response(audit(room))
  }) as typeof fetch
  disconnect = connectEditorServices(5)
  await tick(30)
  expect(scores).toBe(1)
  expect(useStore.getState().fengShuiScoreStatus).toBe('ready')
  const scene = useStore.getState().scene
  useStore.getState().setInteracting(true)
  useStore.getState().setPose(scene.furniture[0].id, { x: 3 })
  await tick(20)
  expect(scores).toBe(1)
  expect(useStore.getState().fengShuiScore).toBeNull()
  useStore.getState().commitEdit(null)
  useStore.getState().setInteracting(false)
  await tick(30)
  expect(scores).toBe(2)
  expect(useStore.getState().fengShuiScore?.revision).toBe(scene.revision + 1)
})

test('same-revision edits, version changes and a new room reject late score responses', async () => {
  for (const change of ['pose', 'version', 'room']) {
    useStore.setState({ ...initial, scene: freshMockScene(), screen: 'editor' })
    const scene = useStore.getState().scene
    let finish!: (r: Response) => void
    globalThis.fetch = (() =>
      new Promise<Response>((resolve) => {
        finish = resolve
      })) as typeof fetch
    const pending = useStore.getState().refreshFengShuiScore()
    const controller = useStore.getState().fengShuiScoreAbort!
    if (change === 'pose')
      useStore.getState().setPose(scene.furniture[0].id, { x: 4 })
    else if (change === 'version') {
      useStore.getState().rotateItem(scene.furniture[0].id, 90)
      useStore.getState().saveVersion()
      useStore.getState().selectVersion('version-1')
      expect(controller.signal.aborted).toBe(true)
    } else {
      useStore.getState().openRoom()
      expect(controller.signal.aborted).toBe(true)
    }
    finish(response(scoreResult(scene)))
    await pending
    expect(useStore.getState().fengShuiScore).toBeNull()
  }
})

test('score failures have an independent retry and never discard the audit or AI advice', async () => {
  const scene = useStore.getState().scene
  const report = audit(scene)
  useStore.setState({ audit: report, auditStatus: 'ready' })
  let calls = 0
  globalThis.fetch = (async () => {
    calls++
    return response({}, 503)
  }) as typeof fetch
  await useStore.getState().refreshFengShuiScore()
  expect(calls).toBe(1)
  expect(useStore.getState().fengShuiScoreStatus).toBe('error')
  expect(useStore.getState().audit).toBe(report)
  globalThis.fetch = (async () => response(scoreResult(scene))) as typeof fetch
  await useStore.getState().refreshFengShuiScore()
  expect(useStore.getState().fengShuiScoreStatus).toBe('ready')
  expect(useStore.getState().scene).toBe(scene)
  expect(useStore.getState().audit).toBe(report)
})

test('score UI exposes coverage, caps, rule breakdown and unknowns; null is not zero', () => {
  const scene = useStore.getState().scene
  const props = {
    scene,
    status: 'ready' as const,
    error: null,
    blocked: false,
    onRetry: () => {},
  }
  const score = { ...scoreResult(scene, 50), capped_by_audit: true }
  const html = renderToStaticMarkup(
    <FengShuiScoreCard {...props} score={score} />,
  )
  for (const text of [
    '50 / 100',
    '80',
    'Score capped',
    'Rule breakdown',
    'mirror_reflection',
    'Weight',
    'Furniture is distributed',
  ])
    expect(html).toContain(text)
  const unknown = renderToStaticMarkup(
    <FengShuiScoreCard {...props} score={scoreResult(scene, null)} />,
  )
  expect(unknown).toContain('Not assessable')
  expect(unknown).not.toContain('0 / 100')
  expect(
    renderToStaticMarkup(
      <FengShuiScoreCard {...props} score={scoreResult(scene, 0)} />,
    ),
  ).toContain('0 / 100')
  expect(
    renderToStaticMarkup(
      <FengShuiScoreCard {...props} score={score} blocked />,
    ),
  ).not.toContain('50 / 100')
  expect(
    renderToStaticMarkup(
      <FengShuiScoreCard
        {...props}
        score={score}
        status="error"
        error="Offline"
      />,
    ),
  ).toContain('Retry score')
  expect(
    renderToStaticMarkup(
      <AuditStats scene={scene} audit={audit(scene)} fengShuiScore={score} />,
    ),
  ).toContain('50 / 100')
})

test('proposal comparison scores exact before/proposed layouts without mutating the room or ranking', async () => {
  const scene = useStore.getState().scene
  const original = structuredClone(scene)
  const item = scene.furniture.find((i) => !i.is_fixed)!
  const proposal: LayoutProposal = {
    proposal_id: 'p',
    poses: { [item.id]: { ...item.pose, x: item.pose.x + 1 } },
    improved: true,
    goal: 'custom',
    explanation: 'Preview',
    outcome: 'completed',
    report: audit(scene),
  }
  const sent: RoomScene[] = []
  globalThis.fetch = (async (_path, options) => {
    const room = JSON.parse(String(options?.body)).scene as RoomScene
    sent.push(room)
    return response(scoreResult(room, sent.length === 1 ? 0 : 70))
  }) as typeof fetch
  const result = await fetchProposalFengShuiScores(scene, proposal)
  expect(sent[0]).toEqual(original)
  expect(sent[1].furniture.find((i) => i.id === item.id)?.pose).toEqual(
    proposal.poses[item.id],
  )
  expect(sent[1].furniture.find((i) => i.id === item.id)?.glb_url).toBe(
    item.glb_url,
  )
  expect(scene).toEqual(original)
  expect(proposal.goal).toBe('custom')
  const html = renderToStaticMarkup(
    <AuditDiff
      before={audit(scene)}
      after={proposal.report}
      fengShui={{ ...result, status: 'ready', error: null }}
    />,
  )
  expect(html).toContain('0 / 100')
  expect(html).toContain('70 / 100')
  expect(html).toContain('Feng shui rule coverage')
})
