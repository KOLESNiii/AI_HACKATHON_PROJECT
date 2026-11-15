/**
 * The home shown in the room picker: either the built-in demo house or a floor plan the user
 * uploaded and the reconstruction service parsed (`ParsedFloorPlan`). Both become floors of
 * pickable rooms in floor-plan metres (+X right, +Z down the page), so the picker and the
 * editor don't care which one they have.
 */
import type {
  ParsedFloorPlan,
  ParsedRoom,
  RoomScene,
  Vec2,
} from '../lib/contracts'
import { bounds } from '../lib/geometry'
import {
  area,
  demoFloors,
  labelPoint,
  roomScene,
  type RoomSegment,
} from './demoHome'

export interface PlanRoom extends RoomSegment {
  /** A fresh, editable scene for the editor (furniture is fetched when it opens). */
  scene: () => RoomScene
  /** What the parse asks the user to check, in plain words. */
  notes: string[]
}

type Openings = Pick<RoomScene, 'walls' | 'doors' | 'windows'>

export interface PlanFloor {
  id: string
  label: string
  rooms: PlanRoom[]
  /** Wall mass drawn in ink under the rooms. */
  mass: Vec2[][]
  /** Width of the ink stroke around `mass`, in metres. */
  massStroke: number
  /** Doors and windows, each set against its own walls. */
  openings: Openings[]
  /** CLAUDE.md compass rule: only claim north when the plan states it. */
  grounded: boolean
}

export interface HomePlan {
  /** The parsed plan's ID; null for the demo home. */
  planId: string | null
  floors: PlanFloor[]
  warnings: string[]
}

export const demoPlan: HomePlan = {
  planId: null,
  warnings: [],
  floors: demoFloors.map((f) => ({
    id: f.id,
    label: f.label,
    rooms: f.rooms.map((r) => ({
      ...r,
      scene: () => roomScene(r.room_id),
      notes: [],
    })),
    // The demo floor outline already runs around the outside of the walls.
    mass: [f.scene.floor_polygon],
    massStroke: 5 / 60,
    openings: [f.scene],
    grounded: f.scene.north_compass_deg != null,
  })),
}

const CIRCULATION = /\b(stairs?|staircase|hall(way)?|landing|corridor)\b/i
const DEFAULT_WALL_M = 0.15

function notesFor(room: ParsedRoom): string[] {
  const notes: string[] = []
  if (room.correction_needed.includes('dimensions'))
    notes.push('Sizes are estimated: no dimension label was read for them')
  if (room.correction_needed.includes('openings'))
    notes.push('Check the doors and windows: some may be missed')
  return notes
}

function median(values: number[]): number {
  if (!values.length) return DEFAULT_WALL_M
  const sorted = [...values].sort((a, b) => a - b)
  return sorted[Math.floor(sorted.length / 2)]
}

/** The room picker's view of a parsed plan. Rooms keep their floor's shared frame. */
export function planFromParsed(plan: ParsedFloorPlan): HomePlan {
  return {
    planId: plan.plan_id,
    warnings: plan.warnings,
    floors: plan.floors
      .filter((f) => f.rooms.length > 0)
      .map((f) => {
        const walls = f.rooms.flatMap((r) => r.scene.walls)
        return {
          id: f.floor_id,
          label: f.name,
          rooms: f.rooms.map((r): PlanRoom => {
            const outline = r.scene.floor_polygon
            const b = bounds(outline)
            return {
              room_id: r.room_id,
              floor_id: f.floor_id,
              label: r.name,
              outline,
              width: b.maxX - b.minX,
              depth: b.maxZ - b.minZ,
              area: area(outline),
              ...labelPoint(outline),
              selectable: !CIRCULATION.test(r.name),
              scene: () => structuredClone(r.scene),
              notes: notesFor(r),
            }
          }),
          // Room outlines are interior faces: a stroke twice the wall thickness fills the
          // walls between neighbouring rooms and stands the outer walls outside them.
          mass: f.rooms.map((r) => r.scene.floor_polygon),
          massStroke: 2 * median(walls.map((w) => w.thickness_m)),
          openings: f.rooms.map((r) => r.scene),
          grounded: f.rooms.some((r) => r.scene.north_compass_deg != null),
        }
      }),
  }
}

export function findPlanRoom(
  home: HomePlan,
  roomId: string | null,
): PlanRoom | null {
  if (roomId == null) return null
  for (const f of home.floors)
    for (const r of f.rooms) if (r.room_id === roomId) return r
  return null
}
