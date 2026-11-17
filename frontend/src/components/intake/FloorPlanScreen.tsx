import { AnimatePresence, motion } from 'framer-motion'
import { useMemo, useState } from 'react'
import type { RoomSegment } from '../../data/demoHome'
import { findPlanRoom } from '../../data/homePlan'
import type { RoomScene, Vec2 } from '../../lib/contracts'
import { bounds, doorSwing } from '../../lib/geometry'
import { useStore } from '../../store'
import { Button, Chip, Panel, StatusDot } from '../ui'
import { DEMO, DEVPOST_URL, REPO_URL } from '../../demo/config'
import { examplesFor } from '../../demo/examples'

const M = 60 // px per metre
const PAD = 40

const px = (p: Vec2) => `${p.x * M},${p.z * M}`
const points = (poly: Vec2[]) => poly.map(px).join(' ')

function PlanRoom({
  seg,
  selected,
  onSelect,
  onOpen,
}: {
  seg: RoomSegment
  selected: boolean
  onSelect: () => void
  onOpen: () => void
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
      onDoubleClick={seg.selectable ? onOpen : undefined}
      onKeyDown={(e) => {
        if (!seg.selectable) return
        // Enter on the already-selected room opens it; otherwise Enter/Space select.
        if (e.key === 'Enter' && selected) onOpen()
        else if (e.key === 'Enter' || e.key === ' ') onSelect()
      }}
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
        stroke="var(--color-seal-vermilion)"
        strokeOpacity={selected ? 1 : 0}
        strokeWidth={3}
        style={{ transition: 'fill 160ms ease, stroke-opacity 200ms ease' }}
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
          {DEMO && examplesFor(seg.room_id).length > 0 && (
            <tspan className="fill-seal-vermilion"> ✦</tspan>
          )}
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
function Openings({
  scene,
}: {
  scene: Pick<RoomScene, 'walls' | 'doors' | 'windows'>
}) {
  const { walls, doors, windows } = scene
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
  const { home, segmentId, selectSegment, openRoom, setScreen } = useStore()
  const selected = findPlanRoom(home, segmentId)
  const [floorId, setFloorId] = useState(
    selected?.floor_id ?? home.floors[0].id,
  )
  const floor = home.floors.find((f) => f.id === floorId) ?? home.floors[0]
  const room = useMemo(() => selected?.scene() ?? null, [selected])
  // CLAUDE.md compass rule: only claim grounding when the scene has north_compass_deg.
  const grounded = floor.grounded
  // The ink stroke around the wall mass reaches half its width past the outline.
  const b = bounds(floor.mass.flat())
  const pad = PAD + (floor.massStroke * M) / 2
  // Draw the selected room last so its vermilion outline sits above its neighbours.
  const ordered = [...floor.rooms].sort(
    (x, y) => Number(x.room_id === segmentId) - Number(y.room_id === segmentId),
  )
  const count = home.floors
    .flatMap((f) => f.rooms)
    .filter((r) => r.selectable).length
  const uploaded = home.planId !== null

  return (
    <div className="relative flex h-full">
      <div className="relative flex-1">
        <div className="absolute top-6 left-6 z-10 flex flex-col items-start gap-3">
          {/* Back to the upload step ("reading" is transient, so it is skipped). */}
          {!DEMO && (
            <Button
              onClick={() => {
                selectSegment(null)
                setScreen('upload')
              }}
            >
              ← Upload
            </Button>
          )}
          <Panel
            className={`flex flex-col gap-3 px-5 py-4 ${DEMO ? 'max-w-[236px]' : ''}`}
          >
            <div className="flex flex-col gap-1">
              <h1 className="font-serif text-[20px] leading-[23px] font-semibold">
                {DEMO ? 'A demo home' : 'Your home'}
              </h1>
              <p className="text-[11px] font-medium text-ink-medium">
                {plural(home.floors.length, 'floor')} segmented into{' '}
                {plural(count, 'room')} · pick one to build
              </p>
              {DEMO && (
                <p className="text-[11px] leading-[16px] text-ink-mist">
                  Read from a real estate-agent plan, with furniture rebuilt
                  from a phone walkthrough. Rooms marked{' '}
                  <span className="text-seal-vermilion">✦</span> have recorded
                  agent runs.
                </p>
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              {home.floors.map((f) => (
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
            {home.warnings.length > 0 && (
              <ul className="flex max-w-[280px] flex-col gap-1.5 border-t border-hairline-ink pt-3 text-[11px] leading-[16px] text-ink-medium">
                {home.warnings.map((w) => (
                  <li key={w} className="flex gap-2">
                    <StatusDot status="warning" />
                    <span>{w}</span>
                  </li>
                ))}
              </ul>
            )}
          </Panel>
        </div>

        <div
          className={`grid h-full place-items-center pr-[380px] ${DEMO ? 'pl-[260px]' : 'pl-[340px]'}`}
        >
          <AnimatePresence mode="wait" initial={false}>
            <motion.svg
              key={floor.id}
              initial={{ opacity: 0, scale: 0.985 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.985 }}
              transition={{ duration: 0.18, ease: 'easeOut' }}
              viewBox={`${b.minX * M - pad} ${b.minZ * M - pad} ${(b.maxX - b.minX) * M + pad * 2} ${(b.maxZ - b.minZ) * M + pad * 2}`}
              className="max-h-[84vh] w-auto max-w-[90%] select-none"
            >
              {/* Wall mass in ink, with the rooms laid over it. */}
              {floor.mass.map((poly, i) => (
                <polygon
                  key={i}
                  points={points(poly)}
                  className="fill-ink-primary"
                  stroke="var(--color-ink-primary)"
                  strokeWidth={floor.massStroke * M}
                  strokeLinejoin="miter"
                />
              ))}
              {ordered.map((seg) => (
                <PlanRoom
                  key={seg.room_id}
                  seg={seg}
                  selected={seg.room_id === segmentId}
                  onSelect={() => selectSegment(seg.room_id)}
                  onOpen={() => {
                    // Zustand's set is synchronous, so openRoom sees this segment.
                    selectSegment(seg.room_id)
                    openRoom()
                  }}
                />
              ))}
              {floor.openings.map((o, i) => (
                <Openings key={i} scene={o} />
              ))}
              <g
                transform={`translate(${b.minX * M}, ${b.maxZ * M + pad - 22})`}
              >
                <rect width={M} height={3} className="fill-ink-primary" />
                <text y={18} className="mono fill-ink-medium text-[11px]">
                  1 m
                </text>
              </g>
            </motion.svg>
          </AnimatePresence>
        </div>

        <AnimatePresence>
          {!selected && (
            <motion.div
              className="absolute bottom-6 left-[calc(50%-20px)] -translate-x-1/2"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 8 }}
              transition={{ duration: 0.2 }}
            >
              <Panel className="px-5 py-2.5 text-[13px] font-medium whitespace-nowrap">
                Click a room to inspect · double-click to open
              </Panel>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <AnimatePresence initial={false}>
        {selected && room && (
          <motion.aside
            key="room-panel"
            initial={{ x: 380, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 380, opacity: 0 }}
            transition={{ duration: 0.26, ease: 'easeOut' }}
            className="absolute inset-y-0 right-0 z-10 w-[380px] overflow-hidden border-l border-hairline-ink bg-scroll-panel"
          >
            <AnimatePresence mode="wait" initial={false}>
              <motion.div
                key={selected.room_id}
                initial={{ opacity: 0, x: 12 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -12 }}
                transition={{ duration: 0.16, ease: 'easeOut' }}
                className="flex h-full w-[380px] flex-col gap-4 p-6"
              >
                <div className="flex flex-col gap-1">
                  <h2 className="font-serif text-[20px] leading-[23px] font-semibold">
                    {selected.label}
                  </h2>
                  <span className="mono text-[12px] text-ink-medium">
                    {selected.width.toFixed(2)}m × {selected.depth.toFixed(2)}m
                    · {selected.area.toFixed(1)} m²
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
                  {selected.notes.map((note) => (
                    <span key={note} className="flex items-center gap-2">
                      <StatusDot status="warning" />
                      {note}
                    </span>
                  ))}
                </div>
                <p className="text-[14px] leading-[23px] text-ink-medium">
                  {DEMO
                    ? examplesFor(selected.room_id).length
                      ? `Open it in 3D: drag the furniture around, watch the checks update, add IKEA pieces and walk through it. ${examplesFor(selected.room_id).length === 1 ? 'One recorded agent run is' : `${examplesFor(selected.room_id).length} recorded agent runs are`} ready to replay here.`
                      : 'Open it in 3D: drag the furniture around, watch the checks update, add IKEA pieces and walk through it.'
                    : uploaded
                      ? 'Next, Refresh builds this room in 3D from your plan. Furniture found in your walkthrough videos is matched to its room automatically, and this room’s 3D models are built when you open it: allow a few minutes.'
                      : "Next, Refresh extracts this room's furniture from your walkthrough video and assembles it in 3D. Other rooms stay untouched until you pick them."}
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
                <span className="-mt-2 text-center text-[11px] font-medium text-ink-mist">
                  or double-click the room on the plan
                </span>
                {DEMO && (
                  <span className="flex justify-center gap-3 border-t border-hairline-ink pt-3 text-[11px] font-medium text-ink-medium">
                    <a
                      className="hover:text-seal-vermilion"
                      href={REPO_URL}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Source on GitHub
                    </a>
                    <span aria-hidden>·</span>
                    <a
                      className="hover:text-seal-vermilion"
                      href={DEVPOST_URL}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Devpost
                    </a>
                  </span>
                )}
              </motion.div>
            </AnimatePresence>
          </motion.aside>
        )}
      </AnimatePresence>
    </div>
  )
}

const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? '' : 's'}`
