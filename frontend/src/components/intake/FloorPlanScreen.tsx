import { useMemo, useState } from 'react'
import {
  demoFloors,
  demoRooms,
  findRoom,
  roomScene,
  type DemoFloor,
  type RoomSegment,
} from '../../data/demoHome'
import type { Vec2 } from '../../lib/contracts'
import { bounds, doorSwing } from '../../lib/geometry'
import { useStore } from '../../store'
import { Button, Chip, Panel, StatusDot } from '../ui'

const M = 60 // px per metre
const PAD = 40

const px = (p: Vec2) => `${p.x * M},${p.z * M}`
const points = (poly: Vec2[]) => poly.map(px).join(' ')

function PlanRoom({
  seg,
  selected,
  onSelect,
}: {
  seg: RoomSegment
  selected: boolean
  onSelect: () => void
}) {
  const cx = seg.centre.x * M,
    cy = seg.centre.z * M
  // Label size follows the clear space around the label point.
  const size = seg.clear >= 1.3 ? 20 : seg.clear >= 0.6 ? 14 : 10
  const detail = seg.selectable && seg.clear >= 0.9
  return (
    <g
      role={seg.selectable ? 'button' : undefined}
      aria-label={seg.selectable ? seg.label : undefined}
      aria-pressed={seg.selectable ? selected : undefined}
      tabIndex={seg.selectable ? 0 : -1}
      onClick={seg.selectable ? onSelect : undefined}
      onKeyDown={(e) =>
        seg.selectable && (e.key === 'Enter' || e.key === ' ') && onSelect()
      }
      className={
        seg.selectable
          ? 'cursor-pointer outline-none [&:focus-visible>polygon]:fill-paper-deep [&:hover>polygon]:fill-paper-deep'
          : ''
      }
    >
      <polygon
        points={points(seg.outline)}
        className={
          selected
            ? 'fill-[#ecc9b6]!'
            : seg.selectable
              ? 'fill-paper-card'
              : 'fill-paper-base'
        }
        stroke={selected ? 'var(--color-seal-vermilion)' : 'none'}
        strokeWidth={3}
      />
      {seg.clear >= 0.2 && (
        <text
          x={cx}
          y={cy + (detail ? -8 : size * 0.35)}
          textAnchor="middle"
          style={{ fontSize: size }}
          className={`pointer-events-none font-serif font-semibold ${selected ? 'fill-seal-vermilion-dark' : seg.selectable ? 'fill-ink-primary' : 'fill-ink-mist'}`}
        >
          {seg.label}
        </text>
      )}
      {detail && (
        <>
          <text
            x={cx}
            y={cy + 10}
            textAnchor="middle"
            className="mono pointer-events-none fill-ink-medium text-[10px]"
          >
            {seg.width.toFixed(2)}m × {seg.depth.toFixed(2)}m
          </text>
          <text
            x={cx}
            y={cy + 26}
            textAnchor="middle"
            className="pointer-events-none fill-ink-medium text-[10px] font-medium"
          >
            {seg.area.toFixed(1)} m²
          </text>
        </>
      )}
    </g>
  )
}

/** Doors (gap in the wall plus the leaf's swing) and windows, straight from the scene. */
function Openings({ floor }: { floor: DemoFloor }) {
  const { walls, doors, windows } = floor.scene
  return (
    <g className="pointer-events-none">
      {windows.map((win) => {
        const w = walls.find((x) => x.id === win.wall_id)
        if (!w) return null
        const len = Math.hypot(w.end.x - w.start.x, w.end.z - w.start.z) || 1
        const dx = (w.end.x - w.start.x) / len,
          dz = (w.end.z - w.start.z) / len
        // Centre the glazing in the wall, which stands outward of its interior face (dz, -dx).
        const at = (t: number) => ({
          x: w.start.x + dx * t + (dz * w.thickness_m) / 2,
          z: w.start.z + dz * t - (dx * w.thickness_m) / 2,
        })
        const a = at(win.offset_along_wall_m),
          b = at(win.offset_along_wall_m + win.width_m)
        return (
          <g key={win.id}>
            <line
              x1={a.x * M}
              y1={a.z * M}
              x2={b.x * M}
              y2={b.z * M}
              stroke="var(--color-paper-card)"
              strokeWidth={7}
            />
            <line
              x1={a.x * M}
              y1={a.z * M}
              x2={b.x * M}
              y2={b.z * M}
              stroke="var(--color-ink-primary)"
              strokeWidth={1.25}
            />
          </g>
        )
      })}
      {doors.map((door) => {
        const fan = doorSwing(door, walls)
        const w = walls.find((x) => x.id === door.wall_id)
        if (!fan || !w) return null
        const [hinge, closed, ...arc] = fan
        // Clear this wall's full depth: it stands outward (dz, -dx) of its interior face, and
        // the room beyond clears its own half through its copy of the door.
        const len = Math.hypot(w.end.x - w.start.x, w.end.z - w.start.z) || 1
        const ox = ((w.end.z - w.start.z) / len) * w.thickness_m * M,
          oz = (-(w.end.x - w.start.x) / len) * w.thickness_m * M
        return (
          <g key={door.id}>
            <line
              x1={hinge.x * M + ox}
              y1={hinge.z * M + oz}
              x2={closed.x * M + ox}
              y2={closed.z * M + oz}
              stroke="var(--color-paper-base)"
              strokeWidth={w.thickness_m * M * 2 + 1}
            />
            {door.swings_into_room && (
              <polyline
                points={points([closed, ...arc, hinge])}
                fill="none"
                stroke="var(--color-ink-medium)"
                strokeWidth={1}
              />
            )}
          </g>
        )
      })}
    </g>
  )
}

export function FloorPlanScreen() {
  const { segmentId, selectSegment, openRoom } = useStore()
  const selected = findRoom(segmentId)
  const [floorId, setFloorId] = useState(selected?.floor_id ?? demoFloors[0].id)
  const floor = demoFloors.find((f) => f.id === floorId) ?? demoFloors[0]
  const room = useMemo(
    () => (selected ? roomScene(selected.room_id) : null),
    [selected],
  )
  // CLAUDE.md compass rule: only claim grounding when the scene has north_compass_deg.
  const grounded = floor.scene.north_compass_deg != null
  const b = bounds(floor.scene.floor_polygon)
  // Draw the selected room last so its vermilion outline sits above its neighbours.
  const ordered = [...floor.rooms].sort(
    (x, y) => Number(x.room_id === segmentId) - Number(y.room_id === segmentId),
  )
  const count = demoRooms.filter((r) => r.selectable).length

  return (
    <div className="relative flex h-full">
      <div className="relative flex-1">
        <Panel className="absolute top-6 left-6 z-10 flex flex-col gap-3 px-5 py-4">
          <div className="flex flex-col gap-1">
            <h1 className="font-serif text-[20px] leading-[23px] font-semibold">
              Your home
            </h1>
            <p className="text-[11px] font-medium text-ink-medium">
              {demoFloors.length} floors segmented into {count} rooms · pick one
              to build
            </p>
          </div>
          <div className="flex gap-2">
            {demoFloors.map((f) => (
              <Chip
                key={f.id}
                on={f.id === floor.id}
                onClick={() => {
                  setFloorId(f.id)
                  if (selected && selected.floor_id !== f.id)
                    selectSegment(null)
                }}
              >
                {f.label}
              </Chip>
            ))}
          </div>
        </Panel>
        <div className="grid h-full place-items-center">
          <svg
            viewBox={`${b.minX * M - PAD} ${b.minZ * M - PAD} ${(b.maxX - b.minX) * M + PAD * 2} ${(b.maxZ - b.minZ) * M + PAD * 2}`}
            className="max-h-[84vh] w-auto max-w-[90%]"
          >
            <polygon
              points={points(floor.scene.floor_polygon)}
              className="fill-ink-primary"
              stroke="var(--color-ink-primary)"
              strokeWidth={5}
              strokeLinejoin="miter"
            />
            {ordered.map((seg) => (
              <PlanRoom
                key={seg.room_id}
                seg={seg}
                selected={seg.room_id === segmentId}
                onSelect={() => selectSegment(seg.room_id)}
              />
            ))}
            <Openings floor={floor} />
            <g transform={`translate(${b.minX * M}, ${b.maxZ * M + PAD - 22})`}>
              <rect width={M} height={3} className="fill-ink-primary" />
              <text y={18} className="mono fill-ink-medium text-[11px]">
                1 m
              </text>
            </g>
          </svg>
        </div>
        {!selected && (
          <Panel className="absolute bottom-6 left-1/2 -translate-x-1/2 px-5 py-2.5 text-[13px] font-medium">
            Select a room to build
          </Panel>
        )}
      </div>
      {selected && room && (
        <aside className="flex w-[380px] shrink-0 flex-col gap-4 border-l border-hairline-ink bg-scroll-panel p-6">
          <div className="flex flex-col gap-1">
            <h2 className="font-serif text-[20px] leading-[23px] font-semibold">
              {selected.label}
            </h2>
            <span className="mono text-[12px] text-ink-medium">
              {selected.width.toFixed(2)}m × {selected.depth.toFixed(2)}m ·{' '}
              {selected.area.toFixed(1)} m²
            </span>
          </div>
          <div className="flex flex-col gap-2 text-[11px] font-medium text-ink-medium">
            <span className="flex items-center gap-2">
              <StatusDot status={grounded ? 'valid' : 'warning'} />
              {grounded
                ? 'North grounded from floor plan'
                : 'No compass on the plan: calibrate north in the editor'}
            </span>
            <span className="flex items-center gap-2">
              <StatusDot status="valid" />
              {plural(room.doors.length, 'door')} and{' '}
              {plural(room.windows.length, 'window')} detected
            </span>
          </div>
          <p className="text-[14px] leading-[23px] text-ink-medium">
            Next, SpaceShift extracts this room&apos;s furniture from your
            walkthrough video and assembles it in 3D. Other rooms stay untouched
            until you pick them.
          </p>
          <div className="flex-1" />
          <Button
            variant="primary"
            size="lg"
            onClick={openRoom}
            className="w-full"
          >
            Build this room
          </Button>
        </aside>
      )}
    </div>
  )
}

const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? '' : 's'}`
