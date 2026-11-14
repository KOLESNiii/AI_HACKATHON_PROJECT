import { expect, test } from 'bun:test'
import { demoRooms, roomScene } from '../src/data/demoHome'
import { freshMockScene } from '../src/data/mockScene'

test('each demo room requests its shell and furniture from the reconstruction backend', () => {
  for (const room of demoRooms) {
    const scene = roomScene(room.room_id)
    expect(scene.shell_glb_url).toBe(
      `/api/reconstruction/mock-room/shells/${room.room_id}.glb`,
    )
    for (const item of scene.furniture)
      expect(item.glb_url).toStartWith('/api/reconstruction/mock-room/assets/')
  }
})

test('legacy fixture geometry stays intact while its model URLs target the backend', () => {
  const scene = freshMockScene()
  expect(scene.shell_glb_url).toBe('/api/reconstruction/mock_room/shell.glb')
  for (const item of scene.furniture)
    expect(item.glb_url).toStartWith('/api/reconstruction/mock_room/')
  expect(scene.revision).toBe(0)
  expect(scene.furniture).toHaveLength(6)
})
