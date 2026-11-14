/**
 * Plan-view placement helpers for the editor (metres, +X right, +Z down the page).
 * Door sweeps mirror services/spatial_engine/geometry.py so the editor and the audit agree;
 * see lib/spatialPreview.ts for the checks themselves.
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

/**
 * Floor area a door leaf sweeps, in plan coordinates, or null when it doesn't swing.
 * A port of `door_swing_sector` in services/spatial_engine/geometry.py: the same
 * conservative polygon [hinge, closed-leaf end, arc tangent points..., open-leaf end],
 * so the editor and the audit agree on what blocks a door. Convex for 0..180 degrees.
 */
export function doorSwing(
  door: DoorOpening,
  walls: WallSegment[],
): Pt[] | null {
  const wall = walls.find((w) => w.id === door.wall_id)
  if (!wall || door.width_m <= 0) return null
  if (!(door.swing_angle_deg > 0 && door.swing_angle_deg <= 180)) return null
  const n = inwardNormal(wall)
  const side = door.swings_into_room ? n : { x: -n.x, z: -n.z }
  // In X/Z plan coordinates, clockwise on screen is positive mathematical rotation,
  // and turning the closed leaf 90 degrees in the swing direction points it to `side`.
  const swingSign = door.swing_clockwise ? 1 : -1
  const leaf = door.swing_clockwise
    ? { x: side.z, z: -side.x }
    : { x: -side.z, z: side.x }
  const h = door.hinge_pos
  const start = Math.atan2(leaf.z, leaf.x)
  const steps = Math.ceil(door.swing_angle_deg)
  const step = (swingSign * door.swing_angle_deg * DEG) / steps
  const tangentRadius = door.width_m / Math.cos(Math.abs(step) / 2)
  const pts: Pt[] = [
    h,
    { x: h.x + door.width_m * leaf.x, z: h.z + door.width_m * leaf.z },
  ]
  for (let i = 0; i < steps; i++) {
    const a = start + (i + 0.5) * step
    pts.push({
      x: h.x + tangentRadius * Math.cos(a),
      z: h.z + tangentRadius * Math.sin(a),
    })
  }
  const end = start + steps * step
  pts.push({
    x: h.x + door.width_m * Math.cos(end),
    z: h.z + door.width_m * Math.sin(end),
  })
  return pts
}
