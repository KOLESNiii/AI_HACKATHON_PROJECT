import { WALK_HEADROOM_M } from '../../../contracts/schema'
import type { Pose2D, RoomScene } from './contracts'
import { bounds, planAngle, type Pt } from './geometry'
import { collisionVolumes } from './spatialPreview'

export const BODY_RADIUS_M = 0.25
export const EYE_HEIGHT_M = 1.6
export const WALK_SPEED_M_S = 1.4
const EPSILON = 1e-9

/** Walking uses the same occupied parts and headroom rule as the audit. */
export function walkingObstacles(scene: RoomScene): Pt[][] {
  return scene.furniture.flatMap((item) =>
    collisionVolumes(item)
      .filter((part) => part.y_min < WALK_HEADROOM_M)
      .map((part) => part.footprint),
  )
}

function inside(p: Pt, polygon: Pt[]): boolean {
  let result = false
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const a = polygon[i]
    const b = polygon[j]
    if (
      a.z > p.z !== b.z > p.z &&
      p.x < ((b.x - a.x) * (p.z - a.z)) / (b.z - a.z) + a.x
    )
      result = !result
  }
  return result
}

function distanceToEdge(p: Pt, a: Pt, b: Pt): number {
  const dx = b.x - a.x
  const dz = b.z - a.z
  const lengthSquared = dx * dx + dz * dz
  const t = lengthSquared
    ? Math.min(
        1,
        Math.max(0, ((p.x - a.x) * dx + (p.z - a.z) * dz) / lengthSquared),
      )
    : 0
  return Math.hypot(p.x - a.x - t * dx, p.z - a.z - t * dz)
}

function touches(p: Pt, polygon: Pt[]): boolean {
  return polygon.some(
    (a, i) =>
      distanceToEdge(p, a, polygon[(i + 1) % polygon.length]) <
      BODY_RADIUS_M - EPSILON,
  )
}

/** A circular body must fit entirely inside the floor and outside occupied parts. */
export function canStand(
  p: Pt,
  scene: RoomScene,
  obstacles = walkingObstacles(scene),
): boolean {
  if (!Number.isFinite(p.x) || !Number.isFinite(p.z)) return false
  if (!inside(p, scene.floor_polygon) || touches(p, scene.floor_polygon))
    return false
  return !obstacles.some((polygon) => inside(p, polygon) || touches(p, polygon))
}

/** Small steps prevent tunnelling; separate axis attempts allow sliding past obstacles. */
export function walkStep(
  from: Pt,
  delta: Pt,
  scene: RoomScene,
  obstacles = walkingObstacles(scene),
): Pt {
  if (
    !Number.isFinite(delta.x) ||
    !Number.isFinite(delta.z) ||
    !canStand(from, scene, obstacles)
  )
    return from
  const steps = Math.max(1, Math.ceil(Math.hypot(delta.x, delta.z) / 0.02))
  const dx = delta.x / steps
  const dz = delta.z / steps
  let p = from
  for (let i = 0; i < steps; i++) {
    const next = { x: p.x + dx, z: p.z + dz }
    if (canStand(next, scene, obstacles)) p = next
    else {
      const xOnly = { x: p.x + dx, z: p.z }
      const zOnly = { x: p.x, z: p.z + dz }
      if (canStand(xOnly, scene, obstacles)) p = xOnly
      else if (canStand(zOnly, scene, obstacles)) p = zOnly
    }
  }
  return p
}

export function humanPoseAt(
  p: Pt,
  scene: RoomScene,
  previous: Pose2D | null,
): Pose2D {
  const b = bounds(scene.floor_polygon)
  const dx = (b.minX + b.maxX) / 2 - p.x
  const dz = (b.minZ + b.maxZ) / 2 - p.z
  const yaw =
    previous?.yaw_deg ?? (Math.hypot(dx, dz) < EPSILON ? 0 : planAngle(dx, dz))
  return { ...p, yaw_deg: ((yaw % 360) + 360) % 360 }
}

/** View-relative input, normalized so diagonals do not walk faster. */
export function walkingDelta(
  yaw: number,
  right: number,
  forward: number,
  dt: number,
): Pt {
  const length = Math.hypot(right, forward) || 1
  const step = (WALK_SPEED_M_S * Math.max(0, Math.min(dt, 0.05))) / length
  return {
    x: (Math.sin(yaw) * forward - Math.cos(yaw) * right) * step,
    z: (Math.cos(yaw) * forward + Math.sin(yaw) * right) * step,
  }
}
