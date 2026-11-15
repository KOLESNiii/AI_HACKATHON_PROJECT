import type { RoomScene } from '../src/lib/contracts'
import type { FengShuiScore } from '../src/lib/fengShui'

export function scoreResult(
  scene: RoomScene,
  score: number | null = 65,
): FengShuiScore {
  return {
    scene_id: scene.scene_id,
    revision: scene.revision,
    score,
    coverage: 0.8,
    capped_by_audit: false,
    sightlines: [],
    rules: [
      {
        rule: 'balance',
        object_ids: scene.furniture.slice(0, 1).map((i) => i.id),
        score: 0.65,
        weight: 0.5,
        detail: 'Furniture is distributed around the centre.',
      },
    ],
    unassessed: ['mirror_reflection: no mirror inventory supplied'],
  }
}
