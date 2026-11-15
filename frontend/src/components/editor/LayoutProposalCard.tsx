import { useEffect, useState } from 'react'
import type { AuditReport, RoomScene } from '../../lib/contracts'
import { errorMessage } from '../../lib/api'
import {
  fetchProposalFengShuiScores,
  type FengShuiScore,
  type ScoreStatus,
} from '../../lib/fengShui'
import { footprint } from '../../lib/geometry'
import { layoutChanges, type FurnitureChange } from '../../lib/layoutDiff'
import type { ChatMessage } from '../../store'
import { Button } from '../ui'
import type { EditorProposal } from '../../lib/agent'

const poseText = (p: FurnitureChange['before']) =>
  `(${p.x.toFixed(2)}, ${p.z.toFixed(2)}) m · ${(((p.yaw_deg % 360) + 360) % 360).toFixed(0)}°`

interface ScoreComparison {
  before: FengShuiScore | null
  after: FengShuiScore | null
  status: ScoreStatus
  error: string | null
}

function useProposalScores(
  scene: RoomScene | undefined,
  proposal: EditorProposal | undefined,
) {
  const [attempt, retry] = useState(0)
  const [saved, setSaved] = useState<
    | (ScoreComparison & {
        scene: RoomScene
        proposal: EditorProposal
        attempt: number
      })
    | null
  >(null)
  useEffect(() => {
    if (!scene || !proposal?.improved) return
    const controller = new AbortController()
    void fetchProposalFengShuiScores(scene, proposal, controller.signal).then(
      (scores) => {
        if (!controller.signal.aborted)
          setSaved({
            ...scores,
            scene,
            proposal,
            attempt,
            status: 'ready',
            error: null,
          })
      },
      (error) => {
        if (!controller.signal.aborted) {
          setSaved({
            before: null,
            after: null,
            scene,
            proposal,
            attempt,
            status: 'error',
            error: errorMessage(error),
          })
          controller.abort()
        }
      },
    )
    return () => controller.abort()
  }, [scene, proposal, attempt])
  const scores: ScoreComparison =
    saved?.scene === scene &&
    saved?.proposal === proposal &&
    saved?.attempt === attempt
      ? saved
      : { before: null, after: null, status: 'loading', error: null }
  return { scores, retry: () => retry((n) => n + 1) }
}

function PlanDiff({
  scene,
  changes,
}: {
  scene: RoomScene
  changes: FurnitureChange[]
}) {
  const xs = scene.floor_polygon.map((p) => p.x)
  const zs = scene.floor_polygon.map((p) => p.z)
  const size = Math.max(
    Math.max(...xs) - Math.min(...xs),
    Math.max(...zs) - Math.min(...zs),
    1,
  )
  const pad = size * 0.08
  const points = (ps: { x: number; z: number }[]) =>
    ps.map((p) => `${p.x},${p.z}`).join(' ')
  const changed = new Map(changes.map((c) => [c.id, c]))
  return (
    <figure>
      <svg
        viewBox={`${Math.min(...xs) - pad} ${Math.min(...zs) - pad} ${Math.max(...xs) - Math.min(...xs) + pad * 2} ${Math.max(...zs) - Math.min(...zs) + pad * 2}`}
        role="img"
        aria-label="Room diff floor plan. Dashed outlines show current positions; green outlines show proposed positions."
        className="h-44 w-full rounded-[2px] bg-paper-base"
      >
        <polygon
          points={points(scene.floor_polygon)}
          fill="none"
          stroke="var(--color-ink-medium)"
          strokeWidth={size * 0.006}
        />
        {scene.furniture.map((item) => {
          const change = changed.get(item.id)
          return (
            <g key={item.id}>
              <polygon
                points={points(footprint(item))}
                fill={change ? 'none' : 'var(--color-ink-mist)'}
                fillOpacity={0.12}
                stroke="var(--color-ink-mist)"
                strokeWidth={size * 0.004}
                strokeDasharray={
                  change ? `${size * 0.025} ${size * 0.015}` : undefined
                }
              />
              {change && (
                <polygon
                  points={points(footprint({ ...item, pose: change.after }))}
                  fill="var(--color-accent-celadon)"
                  fillOpacity={0.25}
                  stroke="var(--color-accent-celadon)"
                  strokeWidth={size * 0.006}
                />
              )}
            </g>
          )
        })}
        {changes
          .filter((c) => c.added)
          .map((c) => (
            <polygon
              key={`added-${c.id}`}
              points={points(
                footprint({
                  pose: c.after,
                  bbox_m: c.bbox,
                } as Parameters<typeof footprint>[0]),
              )}
              fill="var(--color-accent-celadon)"
              fillOpacity={0.25}
              stroke="var(--color-accent-celadon)"
              strokeWidth={size * 0.006}
            />
          ))}
        {changes.map((c, i) => (
          <g key={c.id}>
            <line
              x1={c.before.x}
              y1={c.before.z}
              x2={c.after.x}
              y2={c.after.z}
              stroke="var(--color-accent-celadon)"
              strokeWidth={size * 0.004}
            />
            <circle
              cx={c.after.x}
              cy={c.after.z}
              r={size * 0.035}
              fill="var(--color-ink-primary)"
            />
            <text
              x={c.after.x}
              y={c.after.z}
              textAnchor="middle"
              dominantBaseline="central"
              fontSize={size * 0.045}
              fill="var(--color-paper-base)"
            >
              {i + 1}
            </text>
          </g>
        ))}
      </svg>
      <figcaption className="mt-1 text-[11px] text-ink-medium">
        Dashed: current · Green: proposed
      </figcaption>
    </figure>
  )
}

export function AuditDiff({
  before,
  after,
  fengShui,
}: {
  before?: AuditReport
  after: AuditReport
  fengShui?: ScoreComparison
}) {
  const percent = (n: number | null) =>
    n == null ? 'Not checked' : `${Math.round(n * 100)}%`
  const critical = (r: AuditReport) =>
    r.collisions.length +
    r.blocked_doors.length +
    r.out_of_bounds_item_ids.length
  const score = (value: FengShuiScore | null) =>
    value
      ? value.score === null
        ? 'Not assessable'
        : `${value.score} / 100${value.capped_by_audit ? ' · capped' : ''}`
      : fengShui?.status === 'error'
        ? 'Unavailable'
        : 'Checking…'
  const rows = [
    [
      'Fit / door findings',
      before ? String(critical(before)) : '—',
      String(critical(after)),
    ],
    [
      'Front access issues',
      before ? String(before.clearance_issues.length) : '—',
      String(after.clearance_issues.length),
    ],
    [
      'Walkable floor',
      before ? percent(before.walkable_floor_ratio) : '—',
      percent(after.walkable_floor_ratio),
    ],
    [
      'Feng shui',
      fengShui
        ? score(fengShui.before)
        : before?.feng_shui
          ? String(before.feng_shui.score)
          : 'Not checked',
      fengShui
        ? score(fengShui.after)
        : after.feng_shui
          ? String(after.feng_shui.score)
          : 'Not checked',
    ],
  ]
  if (fengShui)
    rows.push([
      'Feng shui rule coverage',
      fengShui.before ? percent(fengShui.before.coverage) : '—',
      fengShui.after ? percent(fengShui.after.coverage) : '—',
    ])
  if (before?.overall_score != null || after.overall_score != null)
    rows.push([
      'Overall score',
      before?.overall_score == null
        ? 'Not checked'
        : String(before.overall_score),
      after.overall_score == null ? 'Not checked' : String(after.overall_score),
    ])
  return (
    <table className="w-full text-left text-[11px]">
      <caption className="mb-1 text-left font-medium">
        Measured findings{before ? '' : ' · no baseline audit'}
      </caption>
      <thead>
        <tr className="text-ink-mist">
          <th scope="col">Metric</th>
          <th scope="col">Before</th>
          <th scope="col">Proposed</th>
        </tr>
      </thead>
      <tbody>
        {rows.map(([label, a, b]) => (
          <tr key={label} className="border-t border-hairline-ink">
            <th scope="row" className="py-1 font-normal">
              {label}
            </th>
            <td>{a}</td>
            <td>{b}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export function LayoutProposalCard({
  message,
  stale,
  blocked,
  onAccept,
  onReject,
}: {
  message: ChatMessage
  stale: boolean
  blocked: boolean
  onAccept: () => void
  onReject: () => void
}) {
  const proposal = message.proposal
  const { scores, retry } = useProposalScores(message.baseScene, proposal)
  if (!proposal || !message.baseScene) return null
  const changes = layoutChanges(message.baseScene, proposal)
  const actionable = proposal.improved && changes.length > 0
  const status = message.applied
    ? 'Accepted'
    : message.rejected
      ? 'Rejected'
      : stale
        ? 'Outdated · ask again for this room'
        : null
  return (
    <section
      aria-label="Layout proposal"
      className="flex w-full flex-col gap-3 rounded-[2px] border border-hairline-ink bg-paper-deep p-3"
    >
      <div className="text-[13px] font-medium">
        {actionable
          ? `Room diff · ${changes.length} item${changes.length === 1 ? '' : 's'}`
          : proposal.outcome === 'assistant_unavailable'
            ? 'Layout agent unavailable'
            : proposal.outcome === 'stopped_early'
              ? 'Search stopped before finding an improvement'
              : 'No improved layout found'}
      </div>
      {proposal.goal && (
        <p className="text-[11px] text-ink-medium">
          {proposal.goal === 'custom'
            ? 'Goal: your request · only fit, doors and access were checked, so judge the rest in the preview'
            : `Goal: ${proposal.goal.replaceAll('_', ' ')}`}
        </p>
      )}
      {message.baseVersionLabel && (
        <p className="text-[11px] text-ink-medium">
          Based on {message.baseVersionLabel}
        </p>
      )}
      {proposal.outcome === 'stopped_early' && actionable && (
        <p role="status" className="text-[11px] text-accent-ochre">
          Search stopped early. This proposal passed the backend checks.
        </p>
      )}
      {actionable && (
        <>
          <PlanDiff scene={message.baseScene} changes={changes} />
          <ol className="flex flex-col gap-2 text-[12px]">
            {changes.map((c, i) => (
              <li key={c.id}>
                <span className="font-medium">
                  {i + 1}. {c.name}
                </span>
                <p className="text-ink-medium">
                  {c.added
                    ? 'Add new item'
                    : c.distance > 1e-9
                      ? `Move ${c.distance.toFixed(2)} m`
                      : 'Keep position'}
                  {Math.abs(c.turn) > 1e-9
                    ? ` · turn ${Math.abs(c.turn).toFixed(0)}° ${c.turn > 0 ? 'counterclockwise' : 'clockwise'}`
                    : ''}
                </p>
                <details className="mt-0.5 text-[11px] text-ink-mist">
                  <summary className="cursor-pointer">
                    Position and rotation
                  </summary>
                  {!c.added && <p>Before: {poseText(c.before)}</p>}
                  <p>Proposed: {poseText(c.after)}</p>
                </details>
              </li>
            ))}
          </ol>
          <AuditDiff
            before={message.baselineAudit}
            after={proposal.report}
            fengShui={scores}
          />
          <p className="text-[11px] text-ink-medium">
            {proposal.goal === 'feng_shui'
              ? 'This goal uses the full Feng shui score shown in Stats, with its coverage and assumptions.'
              : 'Feng shui scores describe traditional placement rules; they do not rank this proposal.'}
          </p>
          {scores.error && (
            <div className="flex flex-col gap-1 text-[11px] text-ink-medium">
              <p role="alert">{scores.error}</p>
              <Button onClick={retry}>Retry Feng shui scores</Button>
            </div>
          )}
          {status ? (
            <p role="status" className="text-[12px] font-medium">
              {status}
            </p>
          ) : (
            <>
              <p className="text-[11px] text-ink-medium">
                Your room stays as it is until you accept.
              </p>
              <div className="flex gap-2">
                <Button variant="primary" disabled={blocked} onClick={onAccept}>
                  Accept layout
                </Button>
                <Button onClick={onReject}>Reject</Button>
              </div>
            </>
          )}
        </>
      )}
    </section>
  )
}
