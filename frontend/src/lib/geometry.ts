/**
 * Client-side plan geometry for instant editor feedback (the "local fast path").
 * Follows the collision rules in contracts/schema.py; the spatial engine's AuditReport stays
 * authoritative whenever it is available.
 */
import {
  MIN_HEIGHT_OVERLAP_M,
  WALK_HEADROOM_M,
  type CollisionPart,
  type DoorOpening,
  type FurnitureItem,
  type RoomScene,
  type Vec2,
  type WallSegment,
} from './contracts'

export type Pt = Vec2

const DEG = Math.PI / 180
/** Plan penetration (m) below which shapes count as touching, not colliding. */
const TOUCH_EPS = 0.005

/** Local (x, z) -> world, for a rotation about +Y (Three.js rotation.y = yaw). */
export function toWorld(item: FurnitureItem, lx: number, lz: number): Pt {
  const t = item.pose.yaw_deg * DEG
  const c = Math.cos(t)
  const s = Math.sin(t)
  return { x: item.pose.x + lx * c + lz * s, z: item.pose.z - lx * s + lz * c }
}

export function partsOf(item: FurnitureItem): CollisionPart[] {
  if (item.collision_parts && item.collision_parts.length > 0)
    return item.collision_parts
  const { width, depth, height } = item.bbox_m
  return [{ x: 0, z: 0, width, depth, y_min: 0, y_max: height }]
}

function rect(
  item: FurnitureItem,
  cx: number,
  cz: number,
  w: number,
  d: number,
): Pt[] {
  return [
    toWorld(item, cx - w / 2, cz - d / 2),
    toWorld(item, cx + w / 2, cz - d / 2),
    toWorld(item, cx + w / 2, cz + d / 2),
    toWorld(item, cx - w / 2, cz + d / 2),
  ]
}

/** Bounding-box footprint corners in world plan coordinates. */
export function footprint(item: FurnitureItem): Pt[] {
  return rect(item, 0, 0, item.bbox_m.width, item.bbox_m.depth)
}

export function partPolygon(item: FurnitureItem, p: CollisionPart): Pt[] {
  return rect(item, p.x, p.z, p.width, p.depth)
}

/** Separating-axis overlap depth of two convex polygons (<= 0 means separate or touching). */
export function overlapDepth(a: Pt[], b: Pt[]): number {
  let min = Infinity
  for (const poly of [a, b]) {
    for (let i = 0; i < poly.length; i++) {
      const p = poly[i]
      const q = poly[(i + 1) % poly.length]
      const len = Math.hypot(q.x - p.x, q.z - p.z)
      if (len < 1e-9) continue
      const nx = -(q.z - p.z) / len
      const nz = (q.x - p.x) / len
      let aMin = Infinity,
        aMax = -Infinity,
        bMin = Infinity,
        bMax = -Infinity
      for (const v of a) {
        const d = v.x * nx + v.z * nz
        aMin = Math.min(aMin, d)
        aMax = Math.max(aMax, d)
      }
      for (const v of b) {
        const d = v.x * nx + v.z * nz
        bMin = Math.min(bMin, d)
        bMax = Math.max(bMax, d)
      }
      min = Math.min(min, Math.min(aMax, bMax) - Math.max(aMin, bMin))
      if (min <= 0) return min
    }
  }
  return min
}

export interface LocalCollision {
  a: string
  b: string
}

export function findCollisions(items: FurnitureItem[]): LocalCollision[] {
  const out: LocalCollision[] = []
  for (let i = 0; i < items.length; i++) {
    for (let j = i + 1; j < items.length; j++) {
      const A = items[i],
        B = items[j]
      if (overlapDepth(footprint(A), footprint(B)) <= TOUCH_EPS) continue // broad phase
      const hit = partsOf(A).some((pa) =>
        partsOf(B).some((pb) => {
          const h = Math.min(pa.y_max, pb.y_max) - Math.max(pa.y_min, pb.y_min)
          return (
            h > MIN_HEIGHT_OVERLAP_M &&
            overlapDepth(partPolygon(A, pa), partPolygon(B, pb)) > TOUCH_EPS
          )
        }),
      )
      if (hit) out.push({ a: A.id, b: B.id })
    }
  }
  return out
}

function unit(dx: number, dz: number): Pt {
  const l = Math.hypot(dx, dz) || 1
  return { x: dx / l, z: dz / l }
}

/** Room-side unit normal of a wall: (-dz, dx). */
export function inwardNormal(w: WallSegment): Pt {
  return unit(-(w.end.z - w.start.z), w.end.x - w.start.x)
}

/**
 * Door swing sector as a polygon (hinge + arc). The closed leaf runs along the wall from the hinge;
 * opening rotates it clockwise (plan view, +Z down) when swing_clockwise, towards the room side
 * when swings_into_room. Those two decide which way along the wall the leaf lies.
 */
export function doorSector(
  door: DoorOpening,
  walls: WallSegment[],
  steps = 16,
): Pt[] {
  const wall = walls.find((w) => w.id === door.wall_id)
  if (!wall) return []
  const along = unit(wall.end.x - wall.start.x, wall.end.z - wall.start.z)
  const inward = inwardNormal(wall)
  const side = door.swings_into_room ? inward : { x: -inward.x, z: -inward.z }
  const rot = (u: Pt): Pt =>
    door.swing_clockwise ? { x: -u.z, z: u.x } : { x: u.z, z: -u.x }
  const leaf = [along, { x: -along.x, z: -along.z }].find((u) => {
    const r = rot(u)
    return r.x * side.x + r.z * side.z > 0
  })!
  const a0 = Math.atan2(leaf.z, leaf.x)
  const sweep = door.swing_angle_deg * DEG * (door.swing_clockwise ? 1 : -1)
  const h = door.hinge_pos
  const pts: Pt[] = [{ ...h }]
  for (let i = 0; i <= steps; i++) {
    const a = a0 + (sweep * i) / steps
    pts.push({
      x: h.x + door.width_m * Math.cos(a),
      z: h.z + door.width_m * Math.sin(a),
    })
  }
  return pts
}

/** Door ids whose swing is obstructed by any item part below the door head. */
export function findBlockedDoors(
  scene: RoomScene,
): { door_id: string; item_id: string }[] {
  const out: { door_id: string; item_id: string }[] = []
  for (const door of scene.doors) {
    const sector = doorSector(door, scene.walls)
    if (sector.length < 3) continue
    for (const item of scene.furniture) {
      const blocks = partsOf(item).some(
        (p) =>
          p.y_min < door.head_height_m &&
          overlapDepth(partPolygon(item, p), sector) > TOUCH_EPS,
      )
      if (blocks) {
        out.push({ door_id: door.id, item_id: item.id })
        break
      }
    }
  }
  return out
}

export function polygonArea(poly: Pt[]): number {
  let s = 0
  for (let i = 0; i < poly.length; i++) {
    const p = poly[i],
      q = poly[(i + 1) % poly.length]
    s += p.x * q.z - q.x * p.z
  }
  return Math.abs(s) / 2
}

export function pointInPolygon(pt: Pt, poly: Pt[]): boolean {
  let inside = false
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const a = poly[i],
      b = poly[j]
    if (
      a.z > pt.z !== b.z > pt.z &&
      pt.x < ((b.x - a.x) * (pt.z - a.z)) / (b.z - a.z) + a.x
    )
      inside = !inside
  }
  return inside
}

export function bounds(poly: Pt[]) {
  const xs = poly.map((p) => p.x),
    zs = poly.map((p) => p.z)
  return {
    minX: Math.min(...xs),
    maxX: Math.max(...xs),
    minZ: Math.min(...zs),
    maxZ: Math.max(...zs),
  }
}

/** Share of floor not covered by any part lower than WALK_HEADROOM_M (5 cm grid). */
export function walkableRatio(scene: RoomScene, cell = 0.05): number {
  const b = bounds(scene.floor_polygon)
  const blockers = scene.furniture.flatMap((it) =>
    partsOf(it)
      .filter((p) => p.y_min < WALK_HEADROOM_M)
      .map((p) => partPolygon(it, p)),
  )
  let total = 0,
    free = 0
  for (let x = b.minX + cell / 2; x < b.maxX; x += cell) {
    for (let z = b.minZ + cell / 2; z < b.maxZ; z += cell) {
      const pt = { x, z }
      if (!pointInPolygon(pt, scene.floor_polygon)) continue
      total++
      if (!blockers.some((poly) => pointInPolygon(pt, poly))) free++
    }
  }
  return total ? free / total : 0
}

/** Rough fit check: the item fits the floor's bounding box in either orientation. */
export function fitsRoom(
  scene: RoomScene,
  width: number,
  depth: number,
): boolean {
  const b = bounds(scene.floor_polygon)
  const W = b.maxX - b.minX,
    D = b.maxZ - b.minZ
  return (width <= W && depth <= D) || (depth <= W && width <= D)
}

/** Keep an item's footprint inside the floor's bounding box. */
export function clampToFloor(
  scene: RoomScene,
  item: FurnitureItem,
  x: number,
  z: number,
): Pt {
  const b = bounds(scene.floor_polygon)
  const fp = footprint({ ...item, pose: { ...item.pose, x: 0, z: 0 } })
  const fb = bounds(fp)
  return {
    x: Math.min(Math.max(x, b.minX - fb.minX), b.maxX - fb.maxX),
    z: Math.min(Math.max(z, b.minZ - fb.minZ), b.maxZ - fb.maxZ),
  }
}

/** Pose that puts the item's back flush against the nearest wall, facing into the room. */
export function snapToNearestWall(scene: RoomScene, item: FurnitureItem) {
  let best: { d: number; wall: WallSegment; px: number; pz: number } | null =
    null
  for (const w of scene.walls) {
    const dx = w.end.x - w.start.x,
      dz = w.end.z - w.start.z
    const len2 = dx * dx + dz * dz || 1
    const t = Math.min(
      1,
      Math.max(
        0,
        ((item.pose.x - w.start.x) * dx + (item.pose.z - w.start.z) * dz) /
          len2,
      ),
    )
    const px = w.start.x + t * dx,
      pz = w.start.z + t * dz
    const d = Math.hypot(item.pose.x - px, item.pose.z - pz)
    if (!best || d < best.d) best = { d, wall: w, px, pz }
  }
  if (!best) return item.pose
  const n = inwardNormal(best.wall)
  const yaw = (((Math.atan2(n.x, n.z) / DEG) % 360) + 360) % 360
  const half = item.bbox_m.depth / 2
  return {
    x: best.px + n.x * half,
    z: best.pz + n.z * half,
    yaw_deg: Math.round(yaw * 1000) / 1000,
  }
}
