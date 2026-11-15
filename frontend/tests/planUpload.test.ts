import { afterEach, expect, jest, test } from 'bun:test'
import cached from '../../services/reconstruction/room/fixtures/scene_cache/plan-83a12322e933.json'
import { demoPlan, findPlanRoom, planFromParsed } from '../src/data/homePlan'
import type { ParsedFloorPlan } from '../src/lib/contracts'
import { isParsedFloorPlan } from '../src/lib/floorPlan'
import { addFiles, isPlanImage, isVideo } from '../src/lib/uploadFiles'
import { ROOM_POLL_MS, useStore } from '../src/store'

const parsed = cached.plan as unknown as ParsedFloorPlan
const initial = useStore.getState()
const originalFetch = globalThis.fetch

afterEach(() => {
  globalThis.fetch = originalFetch
  useStore.setState(initial)
})

/** Lets pending promise chains (fetch, json) settle; timers stay frozen. */
const flush = async () => {
  for (let i = 0; i < 50; i++) await Promise.resolve()
}

const file = (name: string, type: string, body = name) =>
  new File([body], name, { type, lastModified: 1 })

test('the cached parse of the demo plan is a readable plan', () => {
  expect(isParsedFloorPlan(parsed)).toBe(true)
  expect(isParsedFloorPlan({ ...parsed, floors: [{ rooms: [{}] }] })).toBe(
    false,
  )
})

test('a parsed plan becomes floors of pickable rooms with their own scenes', () => {
  const home = planFromParsed(parsed)
  expect(home.planId).toBe(parsed.plan_id)
  expect(home.floors.map((f) => f.label)).toEqual(
    parsed.floors.map((f) => f.name),
  )
  const reception = findPlanRoom(home, 'floor-0-room-3')!
  expect(reception.label).toBe('Reception Room / Kitchen (1)')
  expect(reception.selectable).toBe(true)
  expect(reception.area).toBeGreaterThan(1)
  const scene = reception.scene()
  expect(scene.scene_id).toBe(`${parsed.plan_id}-floor-0-room-3`)
  // Each call is a fresh copy the editor may change.
  expect(reception.scene()).not.toBe(scene)
  expect(home.floors[0].mass).toHaveLength(parsed.floors[0].rooms.length)
  expect(home.floors[0].massStroke).toBeGreaterThan(0)
})

test('files are added once, by type, up to the limit', () => {
  const a = file('a.png', 'image/png')
  const { files, skipped } = addFiles(
    [a],
    [a, file('b.jpg', 'image/jpeg'), file('c.pdf', 'application/pdf')],
    5,
    isPlanImage,
  )
  expect(files.map((f) => f.name)).toEqual(['a.png', 'b.jpg'])
  expect(skipped).toBe(1)
  const many = Array.from({ length: 7 }, (_, i) =>
    file(`${i}.mp4`, 'video/mp4'),
  )
  const capped = addFiles([], many, 5, isVideo)
  expect(capped.files).toHaveLength(5)
  expect(capped.skipped).toBe(2)
})

test('uploading sends every plan and video, then shows the parsed plan', async () => {
  let sent: FormData | null = null
  let url = ''
  globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    url = String(input)
    sent = init?.body as FormData
    return new Response(JSON.stringify(parsed), {
      headers: { 'Content-Type': 'application/json' },
    })
  }) as typeof fetch
  const plans = [file('p1.png', 'image/png'), file('p2.png', 'image/png')]
  const videos = [
    file('v1.mp4', 'video/mp4'),
    file('v2.mov', 'video/quicktime'),
  ]
  useStore.getState().setUploadFiles('plans', plans)
  useStore.getState().setUploadFiles('videos', videos)

  const done = useStore.getState().submitUpload()
  expect(useStore.getState().screen).toBe('reading')
  expect(useStore.getState().planStatus).toBe('loading')
  await done

  expect(url).toBe('/api/reconstruction/floor-plans')
  expect(sent!.getAll('files').map((f) => (f as File).name)).toEqual([
    'p1.png',
    'p2.png',
  ])
  expect(sent!.getAll('videos').map((f) => (f as File).name)).toEqual([
    'v1.mp4',
    'v2.mov',
  ])
  const s = useStore.getState()
  expect(s.planStatus).toBe('ready')
  expect(s.home.planId).toBe(parsed.plan_id)

  // Opening a room loads that parsed room, not a demo one.
  s.selectSegment('floor-0-room-3')
  useStore.getState().openRoom()
  expect(useStore.getState().scene.scene_id).toBe(
    `${parsed.plan_id}-floor-0-room-3`,
  )
})

test('a failed upload reports the service detail and keeps the files', async () => {
  globalThis.fetch = (async () =>
    new Response(JSON.stringify({ detail: 'image 0 is unreadable' }), {
      status: 422,
      headers: { 'Content-Type': 'application/json' },
    })) as unknown as typeof fetch
  useStore.getState().setUploadFiles('plans', [file('p.png', 'image/png')])
  await useStore.getState().submitUpload()
  const s = useStore.getState()
  expect(s.planStatus).toBe('error')
  expect(s.planError).toContain('image 0 is unreadable')
  expect(s.home).toBe(demoPlan)
  expect(s.uploadPlans).toHaveLength(1)
})

test('choosing the demo home drops an upload in flight', async () => {
  let release: (r: Response) => void = () => {}
  globalThis.fetch = (() =>
    new Promise<Response>((resolve) => {
      release = resolve
    })) as unknown as typeof fetch
  useStore.getState().setUploadFiles('plans', [file('p.png', 'image/png')])
  const done = useStore.getState().submitUpload()
  useStore.getState().chooseDemoHome()
  release(new Response(JSON.stringify(parsed)))
  await done
  const s = useStore.getState()
  expect(s.home).toBe(demoPlan)
  expect(s.planStatus).toBe('idle')
})

test('a room whose furniture is still extracting is fetched again until it arrives', async () => {
  const home = planFromParsed(parsed)
  const room = findPlanRoom(home, 'floor-0-room-3')!
  const empty = room.scene()
  const furnished = { ...empty, furniture: initial.scene.furniture }
  const replies = [
    {
      scene: empty,
      pending: true,
      warnings: ['Extracting furniture (finding)'],
    },
    {
      scene: empty,
      pending: true,
      warnings: ['Extracting furniture (models)'],
    },
    { scene: furnished, pending: false, warnings: [] },
  ]
  let calls = 0
  globalThis.fetch = (async () => {
    const r = replies[Math.min(calls++, replies.length - 1)]
    return new Response(JSON.stringify(r.scene), {
      headers: {
        'Content-Type': 'application/json',
        'X-Reconstruction-Warnings': JSON.stringify(r.warnings),
        ...(r.pending
          ? {
              'X-Furniture-Pending': 'true',
              'X-Furniture-Progress': JSON.stringify({
                step: calls,
                steps: 3,
                stage: r.warnings[0],
                elapsed_s: 10 * calls,
              }),
            }
          : {}),
      },
    })
  }) as unknown as typeof fetch
  useStore.setState({ home, segmentId: room.room_id })
  useStore.getState().openRoom()
  useStore.setState({ screen: 'editor' })
  jest.useFakeTimers()
  try {
    await useStore.getState().loadRoom()
    expect(useStore.getState().scene.furniture).toHaveLength(0)
    expect(useStore.getState().roomWarnings[0]).toContain('finding')
    expect(useStore.getState().furnitureProgress).toMatchObject({
      step: 1,
      steps: 3,
      elapsedS: 10,
    })

    jest.advanceTimersByTime(ROOM_POLL_MS)
    await flush()
    expect(useStore.getState().roomWarnings[0]).toContain('models')
    expect(useStore.getState().furnitureProgress?.step).toBe(2)

    jest.advanceTimersByTime(ROOM_POLL_MS)
    await flush()
    expect(calls).toBe(3)
    expect(useStore.getState().scene.furniture).toHaveLength(
      initial.scene.furniture.length,
    )
    expect(useStore.getState().roomWarnings).toEqual([])
    expect(useStore.getState().furnitureProgress).toBeNull()
  } finally {
    jest.useRealTimers()
  }
})
