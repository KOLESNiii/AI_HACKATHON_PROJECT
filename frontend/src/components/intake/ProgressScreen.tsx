import { useEffect, useState } from 'react'
import { Panel, StatusDot } from '../ui'

/**
 * Step list used for "Reading floor plan" and "Building room".
 * Steps advance on a timer until the reconstruction service exposes progress.
 */
export function ProgressScreen({
  title,
  steps,
  onDone,
  stepMs = 900,
}: {
  title?: string
  steps: string[]
  onDone: () => void
  stepMs?: number
}) {
  const [done, setDone] = useState(0)
  useEffect(() => {
    if (done >= steps.length) {
      const t = setTimeout(onDone, 300)
      return () => clearTimeout(t)
    }
    const t = setTimeout(() => setDone((d) => d + 1), stepMs)
    return () => clearTimeout(t)
  }, [done, steps.length, stepMs, onDone])

  return (
    <div className="grid h-full place-items-center">
      <Panel className="flex w-[360px] flex-col gap-3.5 p-6">
        {title && (
          <h2 className="font-serif text-[20px] leading-[23px] font-semibold">
            {title}
          </h2>
        )}
        {steps.map((s, i) => (
          <div key={s} className="flex items-center gap-2.5">
            <StatusDot status={i < done ? 'valid' : 'pending'} />
            <span
              className={`text-[14px] leading-[23px] ${i <= done ? 'text-ink-primary' : 'text-ink-mist'}`}
            >
              {s}
              {i === done ? '…' : ''}
            </span>
          </div>
        ))}
      </Panel>
    </div>
  )
}
