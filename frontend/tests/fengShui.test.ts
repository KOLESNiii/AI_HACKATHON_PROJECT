import { afterEach, beforeEach, expect, test } from 'bun:test'
import { freshMockScene } from '../src/data/mockScene'
import { fetchFengShui, readFengShui } from '../src/lib/fengShui'
import { connectEditorServices } from '../src/lib/editorServices'
import { useStore } from '../src/store'

const initial = useStore.getState()
const originalFetch = globalThis.fetch
let disconnect: (() => void) | undefined

const result = (room = useStore.getState().scene) => ({
  scene_id: room.scene_id,
  revision: room.revision,
  outcome: 'completed',
  assessment: {
    summary: 'The bed has a clear view of the door.',
    findings: [
      {
        object_ids: [room.furniture[0].id],
        principle: 'Command position',
        evidence: 'Faces the door diagonally.',
        confidence: 'medium',
        recommendation: 'Keep it here.',
      },
    ],
    missing_information: ['Mirror inventory'],
  },
})
const response = (value: unknown, status = 200) =>
  new Response(JSON.stringify(value), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })

beforeEach(() =>
  useStore.setState({ ...initial, scene: freshMockScene(), screen: 'editor' }),
)
afterEach(() => {
  disconnect?.()
  disconnect = undefined
  useStore.getState().fengShuiAbort?.abort()
  globalThis.fetch = originalFetch
  useStore.setState(initial)
})

test('posts the scene to /feng-shui and returns a validated assessment', async () => {
  const room = useStore.getState().scene
  let sent: unknown
  globalThis.fetch = ((path: string, init?: RequestInit) => {
    expect(String(path)).toBe('/api/spatial_engine/feng-shui')
    sent = JSON.parse(String(init?.body))
    return Promise.resolve(response(result(room)))
  }) as typeof fetch
  const out = await fetchFengShui(room)
  expect(sent).toEqual({ scene: room })
  expect(out.assessment?.findings).toHaveLength(1)
})

test('rejects outdated revisions and findings about unknown objects', () => {
  const room = useStore.getState().scene
  expect(() =>
    readFengShui({ ...result(room), revision: room.revision + 1 }, room),
  ).toThrow()
  const bad = result(room)
  bad.assessment.findings[0].object_ids = ['invented']
  expect(() => readFengShui(bad, room)).toThrow()
})

test('assistant_unavailable is kept as a service outcome with no assessment', () => {
  const room = useStore.getState().scene
  const out = readFengShui(
    {
      scene_id: room.scene_id,
      revision: room.revision,
      outcome: 'assistant_unavailable',
      assessment: null,
    },
    room,
  )
  expect(out.outcome).toBe('assistant_unavailable')
  expect(out.assessment).toBeNull()
})

test('store keeps the assessment until the scene changes', async () => {
  globalThis.fetch = ((path: string) =>
    Promise.resolve(
      String(path).endsWith('/feng-shui')
        ? response(result())
        : response({}, 503),
    )) as typeof fetch
  disconnect = connectEditorServices(1_000)
  while (useStore.getState().roomLoading)
    await new Promise((r) => setTimeout(r, 5))
  await useStore.getState().assessFengShui()
  expect(useStore.getState().fengShuiStatus).toBe('ready')
  useStore.setState({ interacting: true })
  useStore.setState({ interacting: false })
  expect(useStore.getState().fengShui).not.toBeNull()
  const s = useStore.getState().scene
  useStore.setState({ scene: { ...s, revision: s.revision + 1 } })
  expect(useStore.getState().fengShui).toBeNull()
  expect(useStore.getState().fengShuiStatus).toBe('idle')
})
