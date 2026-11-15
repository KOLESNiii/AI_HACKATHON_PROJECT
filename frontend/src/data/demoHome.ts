/**
 * Demo home for the room picker and editor: Dev 1's three-floor house fixture
 * (contracts/mock_room/three_floor_*_scene.json, traced from examples/three_floor.png).
 *
 * Each fixture file is a whole floor in one RoomScene. The editor works on one room, so a
 * floor is split into rooms here: a room is the closed loop of walls sharing an id prefix
 * (`g-master-w00` -> `g-master`), its outline is that loop, and it takes the openings on
 * those walls plus the furniture standing inside the outline. Rooms keep floor coordinates.
 *
 * The reconstruction backend serves the canonical furniture fixtures and generates each
 * room's shell on demand. The frontend holds no copies of the demo GLBs.
 */
import firstJson from '../../../contracts/mock_room/three_floor_first_scene.json'
import groundJson from '../../../contracts/mock_room/three_floor_ground_scene.json'
import secondJson from '../../../contracts/mock_room/three_floor_second_scene.json'
import type { RoomScene, Vec2 } from '../lib/contracts'
import { bounds } from '../lib/geometry'

const ASSET_ROOT = '/api/reconstruction/mock-room'

export interface RoomSegment {
  room_id: string
  floor_id: string
  label: string
  /** Interior outline in floor-plan metres (+X right, +Z down the page). */
  outline: Vec2[]
  /** Bounding size of the outline. */
  width: number
  depth: number
  area: number
  /** Interior point furthest from the walls: where the label goes. */
  centre: Vec2
  /** Clear radius around `centre`, to size the label. */
  clear: number
  /** Halls and stairs are drawn but can't be opened in the editor. */
  selectable: boolean
}

export interface DemoFloor {
  id: string
  label: string
  /** The whole floor, as authored. */
  scene: RoomScene
  rooms: RoomSegment[]
}

const ROOM_LABELS: Record<string, string> = {
  'g-master': 'Master bedroom',
  'g-reception': 'Reception room',
  'g-kitchen': 'Kitchen',
  'g-bed2': 'Bedroom 2',
  'g-bed3': 'Bedroom 3',
  'g-utility': 'Utility room',
  'g-shower': 'Shower room',
  'g-bath': 'Bathroom',
  'g-entry2': 'Rear entry',
  'g-stair': 'Stairs',
  'g-hall': 'Hall',
  'f-bed4': 'Bedroom 4',
  'f-bed5': 'Bedroom 5',
  'f-bed6': 'Bedroom 6',
  'f-bath': 'Shower room',
  'f-kitchen': 'Kitchen 2',
  'f-stair': 'Stairs',
  'f-hall': 'Landing',
  's-bed7': 'Bedroom 7',
  's-bed8': 'Bedroom 8',
  's-bath': 'Shower room',
  's-store': 'Eaves store',
  's-cupboard': 'Cupboard',
  's-stair': 'Stairs',
  's-hall': 'Landing',
}
const CIRCULATION = /-(hall|stair|entry\d*)$/

const roomOf = (wallId: string) => wallId.replace(/-w\d+$/, '')

function inside(p: Vec2, poly: Vec2[]): boolean {
  let hit = false
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const a = poly[i],
      b = poly[j]
    if (
      a.z > p.z !== b.z > p.z &&
      p.x < ((b.x - a.x) * (p.z - a.z)) / (b.z - a.z) + a.x
    )
      hit = !hit
  }
  return hit
}

function edgeDistance(p: Vec2, a: Vec2, b: Vec2): number {
  const dx = b.x - a.x,
    dz = b.z - a.z
  const t = Math.max(
    0,
    Math.min(
      1,
      ((p.x - a.x) * dx + (p.z - a.z) * dz) / (dx * dx + dz * dz || 1),
    ),
  )
  return Math.hypot(p.x - a.x - t * dx, p.z - a.z - t * dz)
}

/** Grid search for the interior point furthest from every edge (halls are L-shaped). */
export function labelPoint(poly: Vec2[]): { centre: Vec2; clear: number } {
  const b = bounds(poly)
  const N = 24
  let centre = { x: (b.minX + b.maxX) / 2, z: (b.minZ + b.maxZ) / 2 }
  let clear = 0
  for (let i = 0; i < N; i++)
    for (let j = 0; j < N; j++) {
      const p = {
        x: b.minX + ((i + 0.5) / N) * (b.maxX - b.minX),
        z: b.minZ + ((j + 0.5) / N) * (b.maxZ - b.minZ),
      }
      if (!inside(p, poly)) continue
      const d = Math.min(
        ...poly.map((a, k) => edgeDistance(p, a, poly[(k + 1) % poly.length])),
      )
      if (d > clear) [centre, clear] = [p, d]
    }
  return { centre, clear }
}

export function area(poly: Vec2[]): number {
  let sum = 0
  for (let i = 0; i < poly.length; i++) {
    const a = poly[i],
      b = poly[(i + 1) % poly.length]
    sum += a.x * b.z - b.x * a.z
  }
  return Math.abs(sum) / 2
}

function floor(id: string, label: string, json: unknown): DemoFloor {
  const scene = json as RoomScene
  const outlines = new Map<string, Vec2[]>()
  for (const w of scene.walls) {
    const room = roomOf(w.id)
    outlines.set(room, [...(outlines.get(room) ?? []), w.start])
  }
  const rooms = [...outlines].map(([room_id, outline]): RoomSegment => {
    const b = bounds(outline)
    return {
      room_id,
      floor_id: id,
      label: ROOM_LABELS[room_id] ?? room_id,
      outline,
      width: b.maxX - b.minX,
      depth: b.maxZ - b.minZ,
      area: area(outline),
      ...labelPoint(outline),
      selectable: !CIRCULATION.test(room_id),
    }
  })
  return { id, label, scene, rooms }
}

export const demoFloors: DemoFloor[] = [
  floor('ground', 'Ground', groundJson),
  floor('first', 'First', firstJson),
  floor('second', 'Second', secondJson),
]

export const demoRooms: RoomSegment[] = demoFloors.flatMap((f) => f.rooms)

export const findRoom = (roomId: string | null) =>
  demoRooms.find((r) => r.room_id === roomId) ?? null

/** Room opened when the flow starts or no room was picked. */
export const DEFAULT_ROOM_ID = 'g-master'

/** A fresh, editable RoomScene for one room of the demo home. */
export function roomScene(roomId: string | null): RoomScene {
  const room = findRoom(roomId) ?? findRoom(DEFAULT_ROOM_ID)!
  const scene = demoFloors.find((f) => f.id === room.floor_id)!.scene
  const walls = scene.walls.filter((w) => roomOf(w.id) === room.room_id)
  const onWall = (o: { wall_id: string }) =>
    walls.some((w) => w.id === o.wall_id)
  return structuredClone({
    ...scene,
    scene_id: room.room_id,
    shell_glb_url: `${ASSET_ROOT}/shells/${room.room_id}.glb`,
    floor_polygon: room.outline,
    walls,
    windows: scene.windows.filter(onWall),
    doors: scene.doors.filter(onWall),
    furniture: scene.furniture
      .filter((i) => inside(i.pose, room.outline))
      .map((i) => ({
        ...i,
        glb_url: i.glb_url.startsWith('/assets/')
          ? ASSET_ROOT + i.glb_url
          : i.glb_url,
      })),
  })
}
