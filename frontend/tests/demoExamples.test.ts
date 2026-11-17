import { expect, test } from 'bun:test'
import { roomScene } from '../src/data/demoHome'
import { readStreamReply } from '../src/lib/agent'
import { layoutChanges } from '../src/lib/layoutDiff'
import {
  examplesFor,
  isStartingLayout,
  roomsWithExamples,
} from '../src/demo/examples'

test('recorded demo runs still validate against their room and the Library', () => {
  expect(roomsWithExamples.length).toBeGreaterThan(0)
  for (const room of roomsWithExamples) {
    const scene = roomScene(room)
    expect(scene.scene_id).toBe(room)
    for (const example of examplesFor(room)) {
      const { proposal } = readStreamReply(example.reply, scene)
      if (!proposal)
        throw new Error(`${room}: no proposal in "${example.prompt}"`)
      expect(proposal.improved).toBe(true)
      expect(layoutChanges(scene, proposal).length).toBeGreaterThan(0)
      // Progress replays in recorded order, and the reply lands after the last event.
      const times = example.progress.map((p) => p.t)
      expect(times).toEqual([...times].sort((a, b) => a - b))
      expect(example.duration).toBeGreaterThanOrEqual(times.at(-1) ?? 0)
      expect(example.blurb.length).toBeGreaterThan(0)
    }
  }
})

test('demo runs replay only on the starting layout', () => {
  const scene = roomScene('g-reception')
  expect(isStartingLayout(scene)).toBe(true)
  // Rotating a full turn is the same layout.
  const turned = structuredClone(scene)
  turned.furniture[0].pose.yaw_deg += 360
  expect(isStartingLayout(turned)).toBe(true)
  const moved = structuredClone(scene)
  moved.furniture[0].pose.x += 0.1
  expect(isStartingLayout(moved)).toBe(false)
  const fewer = structuredClone(scene)
  fewer.furniture.pop()
  expect(isStartingLayout(fewer)).toBe(false)
})
