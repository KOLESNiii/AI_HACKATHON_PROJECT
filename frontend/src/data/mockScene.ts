import sceneJson from '../../../contracts/mock_room/mock_scene.json'
import type { RoomScene } from '../lib/contracts'

const fixture = sceneJson as unknown as RoomScene
const modelUrl = (url: string) =>
  url.startsWith('/mock_room/') ? `/api/reconstruction${url}` : url

/** Shared fixture geometry; its meshes are served by the reconstruction backend. */
export const mockScene: RoomScene = {
  ...fixture,
  shell_glb_url: modelUrl(fixture.shell_glb_url),
  furniture: fixture.furniture.map((item) => ({
    ...item,
    glb_url: modelUrl(item.glb_url),
  })),
}

export function freshMockScene(): RoomScene {
  return structuredClone(mockScene)
}
