import sceneJson from '../../../contracts/mock_room/mock_scene.json'
import type { FurnitureItem, RoomScene } from '../lib/contracts'

/** Shared fixture room (meshes are served from public/mock_room). */
export const mockScene = sceneJson as unknown as RoomScene

const byId = (id: string) => {
  const item = mockScene.furniture.find((i) => i.id === id)
  if (!item) throw new Error(`mock_scene.json is missing ${id}`)
  return item
}

/**
 * The demo bedroom: bed, desk, wardrobe and a small table. Built on top of the shared
 * fixture (contracts/ is read-only here), re-posed so nothing overlaps or blocks the door.
 */
const demoFurniture = (): FurnitureItem[] => [
  // Headboard against the east wall.
  { ...byId('item_bed'), pose: { x: 3.2, z: 1.4, yaw_deg: 270 } },
  // Against the north wall, clear of the door swing.
  { ...byId('item_wardrobe'), pose: { x: 1.8, z: 0.3, yaw_deg: 0 } },
  // Back to the south wall, under the window.
  { ...byId('vid-desk-01'), pose: { x: 1.2, z: 3.25, yaw_deg: 180 } },
  {
    ...byId('vid-table-01'),
    id: 'vid-small-table-01',
    name: 'Small Table (proxy)',
    bbox_m: { width: 0.45, height: 0.55, depth: 0.45 },
    pose: { x: 3.95, z: 2.45, yaw_deg: 270 },
    requires_front_clear_m: 0.3,
    collision_parts: [],
  },
]

export function freshMockScene(): RoomScene {
  return { ...structuredClone(mockScene), furniture: demoFurniture() }
}
