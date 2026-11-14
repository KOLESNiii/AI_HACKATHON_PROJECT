import { useRef, useState, type PointerEvent } from 'react'
import { requestOptimise } from '../../lib/api'
import { selectCurrentAudit, useStore, type Layer } from '../../store'
import { Button, Chip, Panel, ScoreRing, StatusDot } from '../ui'

/** Top-left: back to floor plan, room title, score ring (HUD/Score Pill). */
export function ScorePill() {
  const sceneId = useStore((s) => s.scene.scene_id)
  const audit = useStore(selectCurrentAudit)
  const setScreen = useStore((s) => s.setScreen)
  return (
    <Panel className="flex items-center gap-3.5 py-2.5 pr-3 pl-2">
      <Button onClick={() => setScreen('floorplan')}>← Floor plan</Button>
      <span className="h-5 w-px bg-hairline-ink" />
      <span className="font-serif text-[20px] leading-[23px] font-semibold">
        {sceneId}
      </span>
      <ScoreRing score={audit?.overall_score ?? null} />
    </Panel>
  )
}

const H0 = 8,
  H1 = 19
const A0 = 135,
  SPAN = 270 // degrees, clockwise from +x (screen)

function arcPath(cx: number, cy: number, r: number, from: number, to: number) {
  const p = (a: number) => [
    cx + r * Math.cos((a * Math.PI) / 180),
    cy + r * Math.sin((a * Math.PI) / 180),
  ]
  const [x0, y0] = p(from),
    [x1, y1] = p(to)
  return `M ${x0} ${y0} A ${r} ${r} 0 ${to - from > 180 ? 1 : 0} 1 ${x1} ${y1}`
}

/** Top-right: sun time scrubber + compass calibration (HUD/Sun & Compass). */
export function SunCompass() {
  const hour = useStore((s) => s.scene.sun_hour)
  const north = useStore((s) => s.scene.north_compass_deg)
  const { setSunHour, setNorth } = useStore.getState()
  const sunRef = useRef<SVGSVGElement>(null)
  const compRef = useRef<SVGSVGElement>(null)
  const [calibrating, setCalibrating] = useState(false)

  const clampedHour = Math.min(H1, Math.max(H0, hour))
  const angle = A0 + ((clampedHour - H0) / (H1 - H0)) * SPAN
  const knob = [
    56 + 49.5 * Math.cos((angle * Math.PI) / 180),
    56 + 49.5 * Math.sin((angle * Math.PI) / 180),
  ]

  const scrub = (e: PointerEvent<SVGSVGElement>) => {
    if (e.buttons !== 1 || !sunRef.current) return
    const r = sunRef.current.getBoundingClientRect()
    let a =
      (Math.atan2(
        e.clientY - r.top - r.height / 2,
        e.clientX - r.left - r.width / 2,
      ) *
        180) /
      Math.PI
    a = (a - A0 + 360) % 360
    if (a > SPAN) return
    setSunHour(H0 + (a / SPAN) * (H1 - H0))
  }
  const calibrate = (e: PointerEvent<SVGSVGElement>) => {
    if (!calibrating || e.buttons !== 1 || !compRef.current) return
    const r = compRef.current.getBoundingClientRect()
    // Plan bearing: clockwise from screen-up (-Z), matching north_compass_deg.
    setNorth(
      (Math.atan2(
        e.clientX - r.left - r.width / 2,
        -(e.clientY - r.top - r.height / 2),
      ) *
        180) /
        Math.PI,
    )
  }
  const grounded = north != null && !calibrating
  const hh = Math.floor(clampedHour),
    mm = Math.round((clampedHour - hh) * 60)

  return (
    <Panel className="flex items-center gap-5 px-4 py-3.5">
      <svg
        ref={sunRef}
        width={112}
        height={112}
        className="cursor-pointer touch-none"
        onPointerDown={scrub}
        onPointerMove={scrub}
        aria-label="Sun time"
      >
        <path
          d={arcPath(56, 56, 49.5, A0, A0 + SPAN)}
          stroke="var(--color-ink-medium)"
          strokeOpacity={0.3}
          strokeWidth={5}
          fill="none"
        />
        <path
          d={arcPath(56, 56, 49.5, A0, angle)}
          stroke="var(--color-sunbeam-wash)"
          strokeWidth={5}
          fill="none"
        />
        <circle
          cx={knob[0]}
          cy={knob[1]}
          r={7}
          fill="var(--color-sunbeam-wash)"
          stroke="var(--color-paper-base)"
          strokeWidth={2}
        />
        <text
          x={56}
          y={54}
          textAnchor="middle"
          className="mono fill-ink-primary text-[12px]"
        >
          {String(hh).padStart(2, '0')}:{String(mm).padStart(2, '0')}
        </text>
        <text
          x={56}
          y={70}
          textAnchor="middle"
          className="fill-ink-medium text-[11px] font-medium"
        >
          SUN
        </text>
        <text x={2} y={110} className="mono fill-ink-medium text-[10px]">
          08:00
        </text>
        <text
          x={110}
          y={110}
          textAnchor="end"
          className="mono fill-ink-medium text-[10px]"
        >
          19:00
        </text>
      </svg>
      <div className="flex flex-col items-center gap-2.5">
        <svg
          ref={compRef}
          width={72}
          height={72}
          className={calibrating ? 'cursor-grab touch-none' : ''}
          onPointerDown={calibrate}
          onPointerMove={calibrate}
          aria-label="Compass"
        >
          <circle
            cx={36}
            cy={36}
            r={32}
            fill="none"
            strokeWidth={2}
            stroke={
              grounded ? 'var(--color-ink-medium)' : 'var(--color-accent-ochre)'
            }
            strokeDasharray={grounded ? undefined : '4 4'}
            strokeOpacity={grounded ? 0.5 : 1}
          />
          <g transform={`rotate(${north ?? 0} 36 36)`}>
            <text
              x={36}
              y={22}
              textAnchor="middle"
              className={`mono text-[12px] ${grounded ? 'fill-accent-celadon' : 'fill-accent-ochre'}`}
            >
              N
            </text>
            <rect
              x={35}
              y={30}
              width={2}
              height={22}
              fill={
                grounded
                  ? 'var(--color-accent-celadon)'
                  : 'var(--color-accent-ochre)'
              }
            />
          </g>
        </svg>
        <button
          type="button"
          className="flex cursor-pointer items-center gap-1.5 text-[11px] font-medium"
          onClick={() => setCalibrating((c) => !c)}
        >
          <StatusDot status={grounded ? 'valid' : 'warning'} />
          {calibrating
            ? 'Drag ring · Done'
            : grounded
              ? 'North Grounded'
              : 'Calibrate North'}
        </button>
      </div>
    </Panel>
  )
}

const layerLabels: [Layer, string][] = [
  ['clearance', 'Clearance & Doors'],
  ['glare', 'Solar Glare'],
  ['fengshui', 'Feng Shui Rays'],
]

/** Bottom dock: layer toggles + Auto-Fix / Photoreal, or Reject / Apply in preview (HUD/Bottom Dock). */
export function BottomDock() {
  const layers = useStore((s) => s.layers)
  const proposal = useStore((s) => s.proposal)
  const audit = useStore(selectCurrentAudit)
  const { toggleLayer, setProposal, applyProposal, toast } = useStore.getState()
  const [busy, setBusy] = useState(false)

  const autoFix = async () => {
    const { scene, roomSession } = useStore.getState()
    setBusy(true)
    try {
      const p = await requestOptimise({
        scene,
        locked_item_ids: scene.furniture
          .filter((i) => i.is_fixed)
          .map((i) => i.id),
        max_candidates: 200,
      })
      const now = useStore.getState()
      if (now.roomSession !== roomSession) return
      if (
        now.scene.scene_id !== p.report.scene_id ||
        now.scene.revision !== scene.revision ||
        p.report.scene_revision !== scene.revision
      )
        return toast('Layout changed while optimising. Try Auto-Fix again.')
      if (!p.improved)
        return toast(
          'No better layout found. The current one is already the best candidate.',
        )
      setProposal(p)
    } catch {
      toast(
        'Auto-Fix needs the spatial engine (port 8002) and its optimise endpoint. It is not reachable yet.',
      )
    } finally {
      setBusy(false)
    }
  }

  const onLayer = (l: Layer) => {
    if (!layers[l] && l !== 'clearance' && !audit)
      toast(
        `${l === 'glare' ? 'Solar glare' : 'Feng shui'} findings come from the spatial engine audit, which is not connected yet.`,
      )
    toggleLayer(l)
  }

  return (
    <Panel className="flex items-center gap-3 rounded-[4px] px-3 py-2.5">
      <div className="flex gap-2">
        {layerLabels.map(([l, label]) => (
          <Chip key={l} on={layers[l]} onClick={() => onLayer(l)}>
            {label}
          </Chip>
        ))}
      </div>
      <span className="h-7 w-px bg-hairline-ink" />
      {proposal ? (
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 px-1 text-[11px] font-medium text-ink-medium">
            Proposed
            <span className="mono text-[12px] text-accent-ochre">
              {audit ? Math.round(audit.overall_score) : '--'}
            </span>
            <span className="mono text-[12px] text-ink-mist">→</span>
            <span className="mono text-[12px] text-accent-celadon">
              {Math.round(proposal.report.overall_score)}
            </span>
          </span>
          <Button size="lg" onClick={() => setProposal(null)}>
            Reject
          </Button>
          <Button variant="primary" size="lg" onClick={applyProposal}>
            Apply
          </Button>
        </div>
      ) : (
        <div className="flex gap-2">
          <Button variant="primary" size="lg" disabled={busy} onClick={autoFix}>
            {busy ? 'Optimising…' : 'Auto-Fix Layout'}
          </Button>
          <Button
            variant="primary"
            size="lg"
            onClick={() =>
              toast(
                'Photoreal render comes later: it needs the RGB/depth/mask export (task #7) and the media service.',
              )
            }
          >
            Photoreal Render
          </Button>
        </div>
      )}
    </Panel>
  )
}
