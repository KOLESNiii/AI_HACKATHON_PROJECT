/**
 * Plan-view placement helpers for the editor (metres, +X right, +Z down the page).
 * Overlap and door-swing shapes here are editor hints only; the spatial engine's
 * AuditReport stays the source of truth for collisions, clearance and walkable floor.
 */
import type { DoorOpening, FurnitureItem, Vec2, WallSegment } from './contracts'

export type Pt = Vec2

export const DEG = Math.PI / 180

/** Plan angle (degrees) of a direction, in the yaw convention: front = (sin, cos). */
export const planAngle = (dx: number, dz: number) => Math.atan2(dx, dz) / DEG

/** Local (x, z) -> world, for a rotation about +Y (Three.js rotation.y = yaw). */
export function toWorld(item: FurnitureItem, lx: number, lz: number): Pt {
  const t = item.pose.yaw_deg * DEG
  const c = Math.cos(t)
  const s = Math.sin(t)
  return { x: item.pose.x + lx * c + lz * s, z: item.pose.z - lx * s + lz * c }
}

/** Bounding-box footprint corners in world plan coordinates. */
export function footprint(item: FurnitureItem): Pt[] {
  const w = item.bbox_m.width / 2
  const d = item.bbox_m.depth / 2
  return [
    toWorld(item, -w, -d),
    toWorld(item, w, -d),
    toWorld(item, w, d),
    toWorld(item, -w, d),
  ]
}

export function bounds(poly: Pt[]) {
  const xs = poly.map((p) => p.x)
  const zs = poly.map((p) => p.z)
  return {
    minX: Math.min(...xs),
    maxX: Math.max(...xs),
    minZ: Math.min(...zs),
    maxZ: Math.max(...zs),
  }
}

/** Room-side unit normal of a wall: (-dz, dx), per the contract winding rule. */
export function inwardNormal(w: WallSegment): Pt {
  const dx = w.end.x - w.start.x
  const dz = w.end.z - w.start.z
  const l = Math.hypot(dx, dz) || 1
  return { x: -dz / l, z: dx / l }
}

/** Keep an item's footprint inside the floor's bounding box. */
export function clampToFloor(
  floor: Pt[],
  item: FurnitureItem,
  x: number,
  z: number,
): Pt {
  const b = bounds(floor)
  const fb = bounds(footprint({ ...item, pose: { ...item.pose, x: 0, z: 0 } }))
  return {
    x: Math.min(Math.max(x, b.minX - fb.minX), b.maxX - fb.maxX),
    z: Math.min(Math.max(z, b.minZ - fb.minZ), b.maxZ - fb.maxZ),
  }
}

/**
 * Pose with the item's back flush against the nearest wall, facing into the room,
 * kept inside the floor's bounding box (so corners don't push it through the next wall).
 */
export function snapToNearestWall(
  walls: WallSegment[],
  floor: Pt[],
  item: FurnitureItem,
) {
  let best: { d: number; wall: WallSegment; px: number; pz: number } | null =
    null
  for (const w of walls) {
    const dx = w.end.x - w.start.x
    const dz = w.end.z - w.start.z
    const len2 = dx * dx + dz * dz || 1
    const t = Math.min(
      1,
      Math.max(
        0,
        ((item.pose.x - w.start.x) * dx + (item.pose.z - w.start.z) * dz) /
          len2,
      ),
    )
    const px = w.start.x + t * dx
    const pz = w.start.z + t * dz
    const d = Math.hypot(item.pose.x - px, item.pose.z - pz)
    if (!best || d < best.d) best = { d, wall: w, px, pz }
  }
  if (!best) return item.pose
  const n = inwardNormal(best.wall)
  // Front (sin(yaw), cos(yaw)) points along the inward normal.
  const yaw = ((Math.round(planAngle(n.x, n.z)) % 360) + 360) % 360
  const half = item.bbox_m.depth / 2
  const snapped = { ...item.pose, yaw_deg: yaw }
  const c = clampToFloor(
    floor,
    { ...item, pose: snapped },
    best.px + n.x * half,
    best.pz + n.z * half,
  )
  return { x: c.x, z: c.z, yaw_deg: yaw }
}

/**
 * Rough fit check against the floor's bounding box. Returns the yaw (0 or 90) the item
 * fits at, or null when it fits in neither orientation.
 */
export function fitYaw(
  floor: Pt[],
  width: number,
  depth: number,
): 0 | 90 | null {
  const b = bounds(floor)
  const W = b.maxX - b.minX
  const D = b.maxZ - b.minZ
  if (width <= W && depth <= D) return 0
  if (depth <= W && width <= D) return 90
  return null
}

export function fitsRoom(floor: Pt[], width: number, depth: number): boolean {
  return fitYaw(floor, width, depth) != null
}

const EPS = 1e-3

/**
 * True when two plan polygons (convex, e.g. footprints) overlap by more than a hair.
 * Separating-axis test; items that merely touch (snapped flush) don't count.
 */
export function polygonsOverlap(a: Pt[], b: Pt[]): boolean {
  for (const poly of [a, b]) {
    for (let i = 0; i < poly.length; i++) {
      const p = poly[i]
      const q = poly[(i + 1) % poly.length]
      const ax = -(q.z - p.z)
      const az = q.x - p.x
      const l = Math.hypot(ax, az) || 1
      let aMin = Infinity
      let aMax = -Infinity
      let bMin = Infinity
      let bMax = -Infinity
      for (const v of a) {
        const d = (v.x * ax + v.z * az) / l
        aMin = Math.min(aMin, d)
        aMax = Math.max(aMax, d)
      }
      for (const v of b) {
        const d = (v.x * ax + v.z * az) / l
        bMin = Math.min(bMin, d)
        bMax = Math.max(bMax, d)
      }
      if (aMax - bMin <= EPS || bMax - aMin <= EPS) return false
    }
  }
  return true
}

/**
 * Ids of items whose bounding-box footprints overlap another item's (all items stand
 * on the floor, so footprint overlap means the boxes intersect). Visual hint only; the
 * spatial engine's audit stays the source of truth.
 */
export function overlappingIds(items: FurnitureItem[]): string[] {
  const fps = items.map(footprint)
  const hit = new Set<string>()
  for (let i = 0; i < items.length; i++)
    for (let j = i + 1; j < items.length; j++)
      if (polygonsOverlap(fps[i], fps[j])) {
        hit.add(items[i].id)
        hit.add(items[j].id)
      }
  return items.filter((i) => hit.has(i.id)).map((i) => i.id)
}

/**
 * Floor area a door leaf sweeps, as a fan [hinge, ...arc] in plan coordinates, or null
 * when the door doesn't swing. Follows the DoorOpening contract: the closed leaf lies
 * along the wall, and turning it 90° in the swing direction points it to the swing side.
 */
export function doorSwing(
  door: DoorOpening,
  walls: WallSegment[],
): Pt[] | null {
  const wall = walls.find((w) => w.id === door.wall_id)
  if (!wall || door.swing_angle_deg <= 0 || door.width_m <= 0) return null
  const n = inwardNormal(wall)
  const s = door.swings_into_room ? n : { x: -n.x, z: -n.z }
  // Plan view has +Z down the page, so clockwise (from above) turns (x, z) into (-z, x).
  const leaf = door.swing_clockwise ? { x: s.z, z: -s.x } : { x: -s.z, z: s.x }
  const steps = Math.max(8, Math.ceil(door.swing_angle_deg / 3))
  const pts: Pt[] = [door.hinge_pos]
  for (let k = 0; k <= steps; k++) {
    const t = (door.swing_angle_deg * DEG * k) / steps
    pts.push({
      x:
        door.hinge_pos.x +
        door.width_m * (Math.cos(t) * leaf.x + Math.sin(t) * s.x),
      z:
        door.hinge_pos.z +
        door.width_m * (Math.cos(t) * leaf.z + Math.sin(t) * s.z),
    })
  }
  return pts
}
