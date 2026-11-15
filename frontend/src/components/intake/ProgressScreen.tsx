import { useEffect, useRef, useState, type CSSProperties } from 'react'
import './ProgressScreen.css'
import { PROVERBS } from './shanShui'

const PROVERB_MS = 11500 // ~0.5s dissolve, ~0.8s reveal, the rest held
const DISSOLVE_MS = 550

function QuoteText({ cn, en }: { cn: string; en: string }) {
  return (
    <>
      <div className="mb-5 font-serif text-[14px] text-seal-vermilion opacity-70">
        ✦
      </div>
      <p className="mist-quote-cn" lang="zh-Hans">
        {cn}
      </p>
      <p className="mist-quote-en" lang="en">
        {en}
      </p>
    </>
  )
}

function Proverb() {
  const [index, setIndex] = useState(() =>
    Math.floor(Math.random() * PROVERBS.length),
  )
  const [visible, setVisible] = useState(false)
  useEffect(() => {
    // Reveal the first proverb straight away; processing steps are short.
    const first = setTimeout(() => setVisible(true), 30)
    let swap: ReturnType<typeof setTimeout>
    const cycle = setInterval(() => {
      setVisible(false)
      swap = setTimeout(() => {
        setIndex((i) => (i + 1) % PROVERBS.length)
        setVisible(true)
      }, DISSOLVE_MS)
    }, PROVERB_MS)
    return () => {
      clearTimeout(first)
      clearTimeout(swap)
      clearInterval(cycle)
    }
  }, [])
  const [cn, en] = PROVERBS[index]
  return (
    <section className="mist-quote-zone" aria-hidden="true">
      {/* Toggling is-visible restarts the ghost's animation for each proverb. */}
      <div className={`mist-quote ${visible ? 'is-visible' : ''}`}>
        <div className="mist-quote-layer mist-quote-ghost">
          <QuoteText cn={cn} en={en} />
        </div>
        <div className="mist-quote-layer mist-quote-sharp">
          <QuoteText cn={cn} en={en} />
        </div>
      </div>
    </section>
  )
}

/**
 * Processing screen used for "Reading floor plan" and "Building room": a proverb and
 * a loading bar over the app-wide Shan Shui <Landscape>. Steps advance on a timer until the
 * reconstruction service exposes progress.
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
  const total = steps.length * stepMs
  const percent = useRef<HTMLSpanElement>(null)

  useEffect(() => {
    if (done >= steps.length) {
      // Short beat on the full bar; the screen's exit animation covers the rest.
      const t = setTimeout(onDone, 200)
      return () => clearTimeout(t)
    }
    const t = setTimeout(() => setDone((d) => d + 1), stepMs)
    return () => clearTimeout(t)
  }, [done, steps.length, stepMs, onDone])

  // Percentage readout tracks the bar's clock without re-rendering every frame.
  useEffect(() => {
    const start = performance.now()
    let raf = 0
    const tick = (now: number) => {
      const p = Math.min(1, (now - start) / total)
      if (percent.current)
        percent.current.textContent = `${Math.round(p * 100)}%`
      if (p < 1) raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [total])

  const finished = done >= steps.length
  const label = finished ? 'Ready' : steps[done]

  return (
    // Transparent: the app-wide <Landscape> shows through from behind.
    <div className="relative h-full overflow-hidden">
      <Proverb />

      <footer className="absolute inset-x-[clamp(24px,5vw,80px)] bottom-[clamp(27px,5.5vh,56px)]">
        {title && (
          <h2 className="mb-2 font-serif text-[22px] leading-[26px] font-semibold text-ink-primary">
            {title}
          </h2>
        )}
        <div className="mb-3 flex items-end justify-between gap-4">
          <span
            className="mono text-[10px] tracking-[0.24em] whitespace-nowrap text-ink-medium uppercase"
            role="status"
          >
            {label}
            {!finished && (
              <span className="mist-dots tracking-normal">...</span>
            )}
          </span>
          <span className="flex items-baseline gap-3">
            <span className="mono text-[10px] tracking-[0.18em] text-ink-mist">
              {Math.min(done + 1, steps.length)}/{steps.length}
            </span>
            <span
              ref={percent}
              className="mono w-[4ch] text-right text-[13px] text-seal-vermilion"
            >
              0%
            </span>
          </span>
        </div>
        <div
          className="relative h-[2px] overflow-hidden bg-ink-primary/12"
          role="progressbar"
          aria-label={title ? `Building ${title}` : 'Processing'}
          aria-valuemin={0}
          aria-valuemax={steps.length}
          aria-valuenow={done}
          aria-valuetext={label}
        >
          <div
            className="mist-fill absolute inset-0 bg-seal-vermilion"
            style={{ '--mist-duration': `${total}ms` } as CSSProperties}
          />
          {/* Step boundaries, like brush-stroke joints. */}
          {steps.slice(1).map((s, i) => (
            <span
              key={s}
              className="absolute top-0 h-full w-[2px] bg-paper-base"
              style={{ left: `${((i + 1) / steps.length) * 100}%` }}
            />
          ))}
          {!finished && <div className="mist-sweep" />}
        </div>
      </footer>
    </div>
  )
}
