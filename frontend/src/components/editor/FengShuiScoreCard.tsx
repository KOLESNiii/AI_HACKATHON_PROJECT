import type { RoomScene } from '../../lib/contracts'
import {
  matchingFengShuiScore,
  type FengShuiScore,
  type ScoreStatus,
} from '../../lib/fengShui'
import { Button } from '../ui'

/** The deterministic score has its own lifecycle, independent of audit and AI advice. */
export function FengShuiScoreCard({
  scene,
  score,
  status,
  error,
  blocked,
  onRetry,
}: {
  scene: RoomScene
  score: FengShuiScore | null
  status: ScoreStatus
  error: string | null
  blocked: boolean
  onRetry: () => void
}) {
  const result = !blocked && matchingFengShuiScore(score, scene) ? score : null
  const name = (id: string) =>
    scene.furniture.find((i) => i.id === id)?.name ?? id
  return (
    <section aria-label="Feng shui score" className="flex flex-col gap-3">
      <h3 className="font-serif text-[20px] leading-[23px] font-semibold">
        Feng shui score
      </h3>
      {blocked ? (
        <p role="status" className="text-[13px] text-ink-medium">
          Finish editing to update the score.
        </p>
      ) : status === 'loading' ? (
        <p role="status" className="text-[13px] text-ink-medium">
          Checking Feng shui placement…
        </p>
      ) : status === 'error' ? (
        <>
          <p role="alert" className="text-[13px] text-ink-medium">
            {error ?? 'The Feng shui score is unavailable.'}
          </p>
          <Button onClick={onRetry}>Retry score</Button>
        </>
      ) : !result ? (
        <>
          <p className="text-[13px] text-ink-medium">Not checked yet.</p>
          <Button onClick={onRetry}>Check score</Button>
        </>
      ) : (
        <>
          <div className="flex items-baseline justify-between gap-3">
            <span className="mono text-[24px] font-bold">
              {result.score === null
                ? 'Not assessable'
                : `${result.score} / 100`}
            </span>
            <span className="text-[11px] text-ink-medium">
              Rule coverage: {Math.round(result.coverage * 100)}%
            </span>
          </div>
          <p className="text-[11px] text-ink-medium">
            Coverage is the assessed share of applicable rule weights.
          </p>
          {result.capped_by_audit && (
            <p className="text-[12px] text-ink-medium">
              Score capped because fit or door findings remain.
            </p>
          )}
          {result.rules.length > 0 && (
            <details className="text-[12px] leading-5">
              <summary className="cursor-pointer font-medium">
                Rule breakdown · {result.rules.length}
              </summary>
              <ul className="mt-2 flex flex-col gap-2">
                {result.rules.map((r, i) => (
                  <li key={i} className="border-b border-hairline-ink pb-2">
                    <span className="font-medium capitalize">
                      {r.rule.replaceAll('_', ' ')} ·{' '}
                      {Math.round(r.score * 100)}%
                    </span>
                    <p className="text-ink-medium">{r.detail}</p>
                    <p className="text-[11px] text-ink-mist">
                      {r.object_ids.map(name).join(', ')} · Weight {r.weight}
                    </p>
                  </li>
                ))}
              </ul>
            </details>
          )}
          {result.sightlines.map((s, i) => (
            <p key={i} className="text-[12px] leading-5 text-ink-medium">
              {name(s.from_item_id)} · {s.status.replaceAll('_', ' ')}:{' '}
              {s.reason}
            </p>
          ))}
          {result.unassessed.length > 0 && (
            <div className="text-[11px] leading-5 text-ink-medium">
              <p className="font-medium">Unassessed and assumptions</p>
              <ul className="list-disc pl-4">
                {result.unassessed.map((reason, i) => (
                  <li key={i}>{reason}</li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}
      <p className="text-[11px] text-ink-mist">
        Traditional placement guide based on room geometry.
      </p>
    </section>
  )
}
