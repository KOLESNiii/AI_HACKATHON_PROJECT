/**
 * Floor-plan segmentation result used by the room picker.
 *
 * Not in contracts/schema.py yet: proposed as `RoomSegment { room_id, label, outline_plan }`
 * for Dev 1's floor-plan parser. Outlines are in floor-plan metres (+X right, +Z down the page).
 * Until that endpoint exists the picker uses this mock home; only the bedroom has scene data
 * (the shared mock_room fixture, 4.2 m × 3.6 m).
 */
export interface RoomSegment {
  room_id: string
  label: string
  /** Axis-aligned for the mock; real segments may be any simple polygon. */
  x: number
  z: number
  width: number
  depth: number
  selectable: boolean
  /** scene_id of a buildable RoomScene, when one exists. */
  scene_id: string | null
}

export const mockSegments: RoomSegment[] = [
  {
    room_id: 'living',
    label: 'Living room',
    x: 0,
    z: 0,
    width: 7,
    depth: 5,
    selectable: true,
    scene_id: null,
  },
  {
    room_id: 'kitchen',
    label: 'Kitchen',
    x: 7,
    z: 0,
    width: 4,
    depth: 5,
    selectable: true,
    scene_id: null,
  },
  {
    room_id: 'hall',
    label: 'Hall',
    x: 0,
    z: 5,
    width: 11,
    depth: 1,
    selectable: false,
    scene_id: null,
  },
  {
    room_id: 'bedroom',
    label: 'Bedroom',
    x: 0,
    z: 6,
    width: 4.2,
    depth: 3.6,
    selectable: true,
    scene_id: 'demo_studio_01',
  },
  {
    room_id: 'bathroom',
    label: 'Bathroom',
    x: 4.2,
    z: 6,
    width: 2.8,
    depth: 3.6,
    selectable: true,
    scene_id: null,
  },
  {
    room_id: 'study',
    label: 'Study',
    x: 7,
    z: 6,
    width: 4,
    depth: 3.6,
    selectable: true,
    scene_id: null,
  },
]

/** Door hinges on the mock plan (metres), drawn as quarter swings into the room below the hall. */
export const mockPlanDoors = [
  { x: 3, z: 5, into: 'up' as const },
  { x: 8, z: 5, into: 'up' as const },
  { x: 0.4, z: 6, into: 'down' as const },
  { x: 5.2, z: 6, into: 'down' as const },
  { x: 8.6, z: 6, into: 'down' as const },
]

export const mockPlanWindows = [
  { x: 2, z: 0, length: 2, axis: 'x' as const },
  { x: 8.5, z: 0, length: 1.5, axis: 'x' as const },
  { x: 1.1, z: 9.6, length: 1.8, axis: 'x' as const },
  { x: 8.6, z: 9.6, length: 1.2, axis: 'x' as const },
  { x: 11, z: 1.5, length: 2, axis: 'z' as const },
]
