import sceneJson from '../../../contracts/mock_room/mock_scene.json'
import type { RoomScene } from '../lib/contracts'

/** Shared fixture room (meshes are served from public/mock_room). */
export const mockScene = sceneJson as unknown as RoomScene

export function freshMockScene(): RoomScene {
  return structuredClone(mockScene)
}
