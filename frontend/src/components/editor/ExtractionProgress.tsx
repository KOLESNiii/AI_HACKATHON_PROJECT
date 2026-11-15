import { useEffect, useState } from 'react'
import { useStore } from '../../store'
import '../intake/ProgressScreen.css'

const clock = (s: number) =>
  `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`

/**
 * Furniture extraction from the plan's walkthrough videos (fal.ai): which of the three
 * stages is running and for how long. The room stays editable meanwhile.
 */
export function ExtractionProgress() {
  const progress = useStore((s) => s.furnitureProgress)
  const [now, setNow] = useState(() => Date.now())
  useEffect(() => {
    if (!progress) return
    const t = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(t)
  }, [progress])
  if (!progress) return null

  const elapsed =
    progress.elapsedS + Math.max(0, (now - progress.receivedAt) / 1000)
  // Mid-way through the current stage: stages have no finer progress.
  const share = Math.max(0, progress.step - 0.5) / progress.steps
  return (
    <div
      role="status"
      aria-label="Extracting furniture from your videos"
      className="absolute top-6 left-1/2 z-20 w-[min(420px,calc(100%-240px))] -translate-x-1/2 scroll-panel px-4 py-3"
    >
      <div className="flex items-baseline justify-between gap-3">
        <span className="font-serif text-[15px] font-semibold text-ink-primary">
          Extracting furniture from your videos
        </span>
        <span className="mono text-[11px] text-ink-mist">{clock(elapsed)}</span>
      </div>
      <p className="mt-1 text-[12px] text-ink-medium">
        {progress.step > 0
          ? `Step ${progress.step} of ${progress.steps}: ${progress.stage}`
          : 'Starting'}
      </p>
      <div
        className="relative mt-2 h-[2px] overflow-hidden bg-ink-primary/12"
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={progress.steps}
        aria-valuenow={progress.step}
      >
        <div
          className="absolute inset-0 origin-left bg-seal-vermilion transition-transform duration-500 ease-out"
          style={{ transform: `scaleX(${share})` }}
        />
        <div className="mist-sweep" />
      </div>
      <p className="mt-2 text-[11px] text-ink-mist">
        The items appear in this room when ready. Edits you make meanwhile
        aren&apos;t overwritten.
      </p>
    </div>
  )
}
