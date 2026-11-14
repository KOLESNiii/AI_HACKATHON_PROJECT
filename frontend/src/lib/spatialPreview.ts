/**
 * Live editor preview of the spatial engine's implemented checks: collisions, items
 * outside the floor, and blocked doors. A line-for-line port of
 * services/spatial_engine/audit.py (the contract requires the editor preview and the
 * audit to agree), checked against services/spatial_engine/fixtures/audit_cases.json.
 *
 * This is NOT an AuditReport: it carries only these three lists, has no scores, and
 * never stands in for the audit endpoint's result in the Stats tab.
 */
import {
  MIN_HEIGHT_OVERLAP_M,
  MIN_PLAN_OVERLAP_M2,
} from '../../../contracts/schema'
import type { BlockedDoorIssue, FurnitureItem, RoomScene } from './contracts'
import { bounds, doorSwing, footprint, toWorld, type Pt } from './geometry'

/** A colliding pair (item_a < item_b). Overlap area is left to the audit. */
export interface PreviewCollision {
  item_a: string
  item_b: string
}

export interface SpatialPreview {
  collisions: PreviewCollision[]
  out_of_bounds_item_ids: string[]
  blocked_doors: BlockedDoorIssue[]
}

interface Volume {
  footprint: Pt[]
  y_min: number
  y_max: number
}

/** Occupied parts as plan prisms; empty collision_parts means one solid bbox. */
export function collisionVolumes(item: FurnitureItem): Volume[] {
  const parts = item.collision_parts.length
    ? item.collision_parts
    : [
        {
          x: 0,
          z: 0,
          width: item.bbox_m.width,
          depth: item.bbox_m.depth,
          y_min: 0,
          y_max: item.bbox_m.height,
        },
      ]
  return parts.map((p) => ({
    footprint: [
      [-1, -1],
      [1, -1],
      [1, 1],
      [-1, 1],
    ].map(([sx, sz]) =>
      toWorld(item, p.x + (sx * p.width) / 2, p.z + (sz * p.depth) / 2),
    ),
    y_min: p.y_min,
    y_max: p.y_max,
  }))
}

/** Same rule as audit.py `_height_overlaps`, including its guard against subtraction noise. */
function heightOverlaps(
  aMin: number,
  aMax: number,
  bMin: number,
  bMax: number,
) {
  const overlap = Math.min(aMax, bMax) - Math.max(aMin, bMin)
  return (
    overlap > MIN_HEIGHT_OVERLAP_M &&
    Math.abs(overlap - MIN_HEIGHT_OVERLAP_M) > 1e-12
  )
}

function signedArea(poly: Pt[]): number {
  let a = 0
  for (let i = 0; i < poly.length; i++) {
    const p = poly[i]
    const q = poly[(i + 1) % poly.length]
    a += p.x * q.z - q.x * p.z
  }
  return a / 2
}

/** Intersection area of two convex polygons (Sutherland-Hodgman clipping). */
export function convexOverlapArea(subject: Pt[], clip: Pt[]): number {
  const orient = Math.sign(signedArea(clip)) || 1
  let out = subject
  for (let i = 0; i < clip.length && out.length; i++) {
    const a = clip[i]
    const b = clip[(i + 1) % clip.length]
    const inside = (p: Pt) =>
      orient * ((b.x - a.x) * (p.z - a.z) - (b.z - a.z) * (p.x - a.x)) >= 0
    const cross = (p: Pt, q: Pt): Pt => {
      const dx = q.x - p.x
      const dz = q.z - p.z
      const ex = b.x - a.x
      const ez = b.z - a.z
      const t = (ex * (p.z - a.z) - ez * (p.x - a.x)) / (ez * dx - ex * dz)
      return { x: p.x + t * dx, z: p.z + t * dz }
    }
    const input = out
    out = []
    for (let j = 0; j < input.length; j++) {
      const p = input[j]
      const q = input[(j + 1) % input.length]
      if (inside(q)) {
        if (!inside(p)) out.push(cross(p, q))
        out.push(q)
      } else if (inside(p)) out.push(cross(p, q))
    }
  }
  return out.length < 3 ? 0 : Math.abs(signedArea(out))
}

const byId = <T extends { id: string }>(a: T, b: T) =>
  a.id < b.id ? -1 : a.id > b.id ? 1 : 0

/** audit.py `detect_collisions`: parts overlap in plan and in height above the thresholds. */
export function detectCollisions(
  furniture: FurnitureItem[],
): PreviewCollision[] {
  const items = [...furniture].sort(byId).map((item) => {
    const parts = collisionVolumes(item)
    const all = [footprint(item), ...parts.map((p) => p.footprint)].flat()
    return { id: item.id, parts, box: bounds(all) }
  })
  const out: PreviewCollision[] = []
  for (let i = 0; i < items.length; i++)
    for (let j = i + 1; j < items.length; j++) {
      const a = items[i]
      const b = items[j]
      // Broad phase on envelopes; touching envelopes still go to the narrow phase.
      if (
        a.box.maxX < b.box.minX ||
        b.box.maxX < a.box.minX ||
        a.box.maxZ < b.box.minZ ||
        b.box.maxZ < a.box.minZ
      )
        continue
      const hit = a.parts.some((pa) =>
        b.parts.some(
          (pb) =>
            heightOverlaps(pa.y_min, pa.y_max, pb.y_min, pb.y_max) &&
            convexOverlapArea(pa.footprint, pb.footprint) > MIN_PLAN_OVERLAP_M2,
        ),
      )
      if (hit) out.push({ item_a: a.id, item_b: b.id })
    }
  return out
}

function onSegment(p: Pt, a: Pt, b: Pt, tol: number) {
  const dx = b.x - a.x
  const dz = b.z - a.z
  const l2 = dx * dx + dz * dz || 1
  const t = Math.min(1, Math.max(0, ((p.x - a.x) * dx + (p.z - a.z) * dz) / l2))
  return Math.hypot(p.x - (a.x + t * dx), p.z - (a.z + t * dz)) <= tol
}

/** Inside or on the boundary (within tol) of a simple polygon. */
function covered(p: Pt, poly: Pt[], tol: number) {
  let inside = false
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const a = poly[i]
    const b = poly[j]
    if (onSegment(p, a, b, tol)) return true
    if (
      a.z > p.z !== b.z > p.z &&
      p.x < ((b.x - a.x) * (p.z - a.z)) / (b.z - a.z) + a.x
    )
      inside = !inside
  }
  return inside
}

/** Strictly inside a convex polygon (not on its boundary). */
function strictlyInsideConvex(p: Pt, poly: Pt[], tol: number) {
  const orient = Math.sign(signedArea(poly)) || 1
  return poly.every((a, i) => {
    const b = poly[(i + 1) % poly.length]
    const l = Math.hypot(b.x - a.x, b.z - a.z) || 1
    return (
      (orient * ((b.x - a.x) * (p.z - a.z) - (b.z - a.z) * (p.x - a.x))) / l >
      tol
    )
  })
}

/**
 * audit.py `detect_out_of_bounds`: the bbox footprint must be covered by the floor
 * (boundary contact allowed, 1e-9 m tolerance). Works for non-convex floors: corners
 * covered and no floor corner poking into the footprint.
 */
export function detectOutOfBounds(scene: RoomScene, tol = 1e-9): string[] {
  const floor = scene.floor_polygon
  return [...scene.furniture]
    .sort(byId)
    .filter((item) => {
      const fp = footprint(item)
      if (!fp.every((c) => covered(c, floor, tol))) return true
      if (floor.some((v) => strictlyInsideConvex(v, fp, tol))) return true
      // Edge midpoints catch a concave notch crossing between two covered corners.
      return fp.some((c, i) => {
        const d = fp[(i + 1) % fp.length]
        return !covered({ x: (c.x + d.x) / 2, z: (c.z + d.z) / 2 }, floor, tol)
      })
    })
    .map((i) => i.id)
}

/** audit.py `detect_blocked_doors`: parts in the door's height range intersecting its sweep. */
export function detectBlockedDoors(scene: RoomScene): BlockedDoorIssue[] {
  const volumes = [...scene.furniture]
    .sort(byId)
    .map((item) => ({ id: item.id, parts: collisionVolumes(item) }))
  const out: BlockedDoorIssue[] = []
  for (const door of [...scene.doors].sort(byId)) {
    const sweep = doorSwing(door, scene.walls)
    if (!sweep) continue
    for (const { id, parts } of volumes)
      if (
        parts.some(
          (p) =>
            heightOverlaps(0, door.head_height_m, p.y_min, p.y_max) &&
            convexOverlapArea(p.footprint, sweep) > MIN_PLAN_OVERLAP_M2,
        )
      )
        out.push({ door_id: door.id, blocked_by_item_id: id })
  }
  return out
}

export function spatialPreview(scene: RoomScene): SpatialPreview {
  return {
    collisions: detectCollisions(scene.furniture),
    out_of_bounds_item_ids: detectOutOfBounds(scene),
    blocked_doors: detectBlockedDoors(scene),
  }
}

/** Ids of items involved in any preview finding (drawn with the red glow). */
export function flaggedItemIds(p: SpatialPreview): string[] {
  const ids = new Set<string>(p.out_of_bounds_item_ids)
  for (const c of p.collisions) ids.add(c.item_a).add(c.item_b)
  for (const d of p.blocked_doors) ids.add(d.blocked_by_item_id)
  return [...ids].sort()
}
