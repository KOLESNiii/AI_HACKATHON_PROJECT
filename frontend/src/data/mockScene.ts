import sceneJson from '../../../contracts/mock_room/mock_scene.json'
import type { RoomScene } from '../lib/contracts'

/** Shared fixture room; the floor-plan picker reads its compass grounding. */
export const mockScene = sceneJson as unknown as RoomScene
