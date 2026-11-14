import {
  mockPlanDoors,
  mockPlanWindows,
  mockSegments,
  type RoomSegment,
} from '../../data/segments'
import { mockScene } from '../../data/mockScene'
import { useStore } from '../../store'
import { Button, Panel, StatusDot } from '../ui'

const M = 60 // px per metre
const PAD = 60

function PlanRoom({
  seg,
  selected,
  onSelect,
}: {
  seg: RoomSegment
  selected: boolean
  onSelect: () => void
}) {
  const w = seg.width * M,
    h = seg.depth * M
  const cx = seg.x * M + w / 2,
    cy = seg.z * M + h / 2
  const hall = !seg.selectable
  return (
    <g
      role={seg.selectable ? 'button' : undefined}
      aria-pressed={seg.selectable ? selected : undefined}
      tabIndex={seg.selectable ? 0 : -1}
      onClick={seg.selectable ? onSelect : undefined}
      onKeyDown={(e) =>
        seg.selectable && (e.key === 'Enter' || e.key === ' ') && onSelect()
      }
      className={
        seg.selectable
          ? 'cursor-pointer outline-none [&:hover>rect]:fill-paper-deep'
          : ''
      }
    >
      <rect
        x={seg.x * M}
        y={seg.z * M}
        width={w}
        height={h}
        className={selected ? 'fill-seal-vermilion/20' : 'fill-paper-card/65'}
        stroke={
          selected ? 'var(--color-seal-vermilion)' : 'var(--color-ink-primary)'
        }
        strokeWidth={3}
      />
      <text
        x={cx}
        y={cy - (hall ? -6 : 10)}
        textAnchor="middle"
        className={`font-serif text-[20px] font-semibold ${selected ? 'fill-seal-vermilion-dark' : 'fill-ink-primary'}`}
      >
        {seg.label}
      </text>
      {!hall && (
        <>
          <text
            x={cx}
            y={cy + 10}
            textAnchor="middle"
            className="mono fill-ink-medium text-[11px]"
          >
            {seg.width.toFixed(2)}m × {seg.depth.toFixed(2)}m
          </text>
          <text
            x={cx}
            y={cy + 28}
            textAnchor="middle"
            className="fill-ink-medium text-[11px] font-medium"
          >
            {(seg.width * seg.depth).toFixed(1)} m²
          </text>
        </>
      )}
    </g>
  )
}

export function FloorPlanScreen() {
  const { segmentId, selectSegment, openRoom } = useStore()
  const selected = mockSegments.find((s) => s.room_id === segmentId) ?? null
  // CLAUDE.md compass rule: only claim grounding when the scene has north_compass_deg.
  const grounded =
    selected?.scene_id === mockScene.scene_id &&
    mockScene.north_compass_deg != null
  const W = 11 * M,
    H = 9.6 * M
  // Draw the selected room last so its vermilion outline sits above its neighbours.
  const ordered = [...mockSegments].sort(
    (a, b) => Number(a.room_id === segmentId) - Number(b.room_id === segmentId),
  )

  return (
    <div className="relative flex h-full">
      <div className="relative flex-1">
        <Panel className="absolute top-6 left-6 flex flex-col gap-1 px-5 py-4">
          <h1 className="font-serif text-[20px] leading-[23px] font-semibold">
            Your home
          </h1>
          <p className="text-[11px] font-medium text-ink-medium">
            Floor plan segmented into 5 rooms · pick one to build
          </p>
        </Panel>

        <div className="grid h-full place-items-center">
          <svg
            viewBox={`${-PAD} ${-PAD} ${W + PAD * 2} ${H + PAD * 2}`}
            className="max-h-[80vh] w-auto max-w-[90%]"
          >
            {ordered.map((seg) => (
              <PlanRoom
                key={seg.room_id}
                seg={seg}
                selected={seg.room_id === segmentId}
                onSelect={() => selectSegment(seg.room_id)}
              />
            ))}
            <rect
              x={0}
              y={0}
              width={W}
              height={H}
              fill="none"
              stroke="var(--color-ink-primary)"
              strokeWidth={7}
            />
            {mockPlanDoors.map((d, i) => {
              const x = d.x * M,
                y = d.z * M,
                r = 0.85 * M,
                dir = d.into === 'down' ? 1 : -1
              return (
                <g key={i}>
                  <rect
                    x={x}
                    y={y - 4}
                    width={r}
                    height={8}
                    className="fill-paper-base"
                  />
                  <path
                    d={`M ${x} ${y} L ${x + r} ${y} A ${r} ${r} 0 0 ${dir > 0 ? 1 : 0} ${x} ${y + dir * r} Z`}
                    fill="none"
                    stroke="var(--color-ink-medium)"
                    strokeWidth={1}
                  />
                </g>
              )
            })}
            {mockPlanWindows.map((w, i) =>
              w.axis === 'x' ? (
                <rect
                  key={i}
                  x={w.x * M}
                  y={w.z * M - 3.5}
                  width={w.length * M}
                  height={7}
                  className="fill-paper-card"
                  stroke="var(--color-ink-primary)"
                  strokeWidth={1.5}
                />
              ) : (
                <rect
                  key={i}
                  x={w.x * M - 3.5}
                  y={w.z * M}
                  width={7}
                  height={w.length * M}
                  className="fill-paper-card"
                  stroke="var(--color-ink-primary)"
                  strokeWidth={1.5}
                />
              ),
            )}
            <g transform={`translate(${W + 22}, -10)`}>
              <text
                x={20}
                y={0}
                textAnchor="middle"
                className="mono fill-ink-primary text-[12px]"
              >
                N
              </text>
              <circle
                cx={20}
                cy={26}
                r={18}
                fill="none"
                stroke="var(--color-ink-primary)"
                strokeWidth={1.5}
              />
              <line
                x1={20}
                y1={14}
                x2={20}
                y2={38}
                stroke="var(--color-seal-vermilion)"
                strokeWidth={2}
              />
            </g>
            <g transform={`translate(0, ${H + 18})`}>
              <rect width={M} height={3} className="fill-ink-primary" />
              <text y={20} className="mono fill-ink-medium text-[11px]">
                1 m
              </text>
            </g>
          </svg>
        </div>

        {!selected && (
          <Panel className="absolute bottom-6 left-1/2 -translate-x-1/2 px-5 py-2.5 text-[13px] font-medium">
            Select a room to open its editor
          </Panel>
        )}
      </div>

      {selected && (
        <aside className="flex w-[380px] shrink-0 flex-col gap-4 border-l border-hairline-ink bg-scroll-panel p-6">
          <div className="flex flex-col gap-1">
            <h2 className="font-serif text-[20px] leading-[23px] font-semibold">
              {selected.label}
            </h2>
            <span className="mono text-[12px] text-ink-medium">
              {selected.width.toFixed(2)}m × {selected.depth.toFixed(2)}m ·{' '}
              {(selected.width * selected.depth).toFixed(1)} m²
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
              Doors and windows detected
            </span>
          </div>
          <p className="text-[14px] leading-[23px] text-ink-medium">
            Next, SpaceShift extracts this room&apos;s furniture from your
            walkthrough video and assembles it in 3D. Other rooms stay untouched
            until you pick them.
          </p>
          {!selected.scene_id && (
            <p className="text-[11px] font-medium text-accent-ochre">
              Demo data is only available for the Bedroom.
            </p>
          )}
          <div className="flex-1" />
          <Button
            variant="primary"
            size="lg"
            disabled={!selected.scene_id}
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
