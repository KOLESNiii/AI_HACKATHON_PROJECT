import { Color, ShapeUtils, Vector2 } from 'three'
import type { RoomScene } from './contracts'
import { bounds, DEG, inwardNormal } from './geometry'
import { canStand } from './walk'

export interface PlayLightingSettings {
  artificialPercent: number
  timeOfDay: number
}

export const DEFAULT_PLAY_LIGHTING: Readonly<PlayLightingSettings> = {
  artificialPercent: 50,
  timeOfDay: 14,
}

export type LightPosition = [number, number, number]

export interface WindowLight {
  id: string
  position: LightPosition
  rotationY: number
  width: number
  height: number
}

/** Illustrative northern-hemisphere day, not an astronomical prediction. */
export function sunlightAt(timeOfDay: number, northCompassDeg = 0) {
  const hour = Number.isFinite(timeOfDay) ? ((timeOfDay % 24) + 24) % 24 : 0
  const progress = Math.max(0, Math.min(1, (hour - 6) / 12))
  const daylight = hour > 6 && hour < 18 ? Math.sin(progress * Math.PI) : 0
  const brightness = daylight * (1 + daylight)
  const elevation = (daylight * Math.PI) / 3
  const bearing = (90 + progress * 180 + northCompassDeg) * DEG
  return {
    daylight,
    brightness,
    intensity: brightness * 3.5,
    direction: [
      Math.sin(bearing) * Math.cos(elevation),
      Math.sin(elevation),
      -Math.cos(bearing) * Math.cos(elevation),
    ] as LightPosition,
    color: new Color('#ffac65').lerp(new Color('#f4f6ff'), Math.sqrt(daylight)),
    sky: new Color('#03050a').lerp(new Color('#91b8da'), daylight),
  }
}

/** Wall geometry wins over the redundant window bearing in the shared contract. */
export function windowLights(scene: RoomScene): WindowLight[] {
  return scene.windows.flatMap((win) => {
    const wall = scene.walls.find((w) => w.id === win.wall_id)
    if (!wall) return []
    const dx = wall.end.x - wall.start.x
    const dz = wall.end.z - wall.start.z
    const length = Math.hypot(dx, dz)
    if (!length) return []
    const start = Math.max(0, win.offset_along_wall_m)
    const end = Math.min(length, win.offset_along_wall_m + win.width_m)
    const sill = Math.max(0, win.sill_height_m)
    const head = Math.min(wall.height_m, win.head_height_m)
    if (
      ![start, end, sill, head].every(Number.isFinite) ||
      end <= start ||
      head <= sill
    )
      return []
    const normal = inwardNormal(wall)
    const t = (start + end) / 2 / length
    return [
      {
        id: win.id,
        position: [
          wall.start.x + dx * t + normal.x * 0.025,
          (sill + head) / 2,
          wall.start.z + dz * t + normal.z * 0.025,
        ] as LightPosition,
        rotationY: Math.atan2(-normal.x, -normal.z),
        width: end - start,
        height: head - sill,
      },
    ]
  })
}

export function roomHeight(scene: RoomScene): number {
  return scene.walls.length
    ? Math.max(...scene.walls.map((w) => w.height_m))
    : 2.6
}

/** Up to four well-spaced ceiling sources, including in concave rooms. */
export function ceilingLights(scene: RoomScene): LightPosition[] {
  const polygon = scene.floor_polygon
  if (polygon.length < 3) return []
  const b = bounds(polygon)
  const triangles = ShapeUtils.triangulateShape(
    polygon.map((p) => new Vector2(p.x, p.z)),
    [],
  )
  const area =
    Math.abs(
      polygon.reduce((sum, p, i) => {
        const next = polygon[(i + 1) % polygon.length]
        return sum + p.x * next.z - next.x * p.z
      }, 0),
    ) / 2
  const candidates: { x: number; z: number }[] = []
  for (let x = 0; x < 12; x++)
    for (let z = 0; z < 12; z++) {
      const p = {
        x: b.minX + ((x + 0.5) * (b.maxX - b.minX)) / 12,
        z: b.minZ + ((z + 0.5) * (b.maxZ - b.minZ)) / 12,
      }
      // Furniture does not determine where virtual ceiling lighting can be mounted.
      if (canStand(p, scene, [])) candidates.push(p)
    }
  if (!candidates.length)
    for (const triangle of triangles) {
      candidates.push({
        x: triangle.reduce((sum, i) => sum + polygon[i].x, 0) / 3,
        z: triangle.reduce((sum, i) => sum + polygon[i].z, 0) / 3,
      })
    }
  const count = Math.min(
    4,
    Math.max(1, Math.ceil(area / 16)),
    candidates.length,
  )
  const chosen: typeof candidates = []
  const centre = { x: (b.minX + b.maxX) / 2, z: (b.minZ + b.maxZ) / 2 }
  const distance = (a: typeof centre, c: typeof centre) =>
    Math.hypot(a.x - c.x, a.z - c.z)
  for (let i = 0; i < count; i++) {
    candidates.sort((a, c) =>
      chosen.length
        ? Math.min(...chosen.map((p) => distance(c, p))) -
          Math.min(...chosen.map((p) => distance(a, p)))
        : distance(a, centre) - distance(c, centre),
    )
    chosen.push(candidates.shift()!)
  }
  return chosen.map((p) => [p.x, roomHeight(scene) - 0.03, p.z])
}

export function formatTimeOfDay(hour: number): string {
  const minutes = Math.round(hour * 60)
  return `${Math.floor(minutes / 60)
    .toString()
    .padStart(2, '0')}:${(minutes % 60).toString().padStart(2, '0')}`
}
