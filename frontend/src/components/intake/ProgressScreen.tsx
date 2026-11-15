import { useEffect, useRef, useState, type CSSProperties } from 'react'
import { Button } from '../ui'
import './ProgressScreen.css'

/** Chinese proverbs shown while processing, with English glosses. */
const PROVERBS: [string, string][] = [
  [
    '千里之行，始于足下',
    'A journey of a thousand miles begins with a single step.',
  ],
  ['上善若水', 'The highest goodness is like water.'],
  ['水滴石穿', 'Dripping water wears through stone.'],
  ['山高水长', 'As enduring as mountains and flowing rivers.'],
  ['塞翁失马，焉知非福', 'What seems a misfortune may be a blessing.'],
  [
    '海纳百川，有容乃大',
    'The sea embraces all rivers; openness makes greatness.',
  ],
  ['静水流深', 'Still waters run deep.'],
  ['读万卷书，行万里路', 'Read ten thousand books; travel ten thousand miles.'],
  ['不积跬步，无以至千里', 'Great journeys are made of small steps.'],
  [
    '山不转路转，路不转人转',
    'When the mountain cannot turn, find another path.',
  ],
  ['知足常乐', 'Contentment brings lasting happiness.'],
  ['顺其自然', 'Let things follow their natural course.'],
]

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
 * a loading bar over the app-wide Shan Shui <Landscape>. Steps advance on a timer.
 *
 * When `pending` is given, the screen waits on real work: the last step holds until
 * `pending` is false, and an `error` stops it with Retry and Back.
 */
export function ProgressScreen({
  title,
  steps,
  onDone,
  stepMs = 900,
  pending,
  error,
  onRetry,
  onBack,
}: {
  title?: string
  steps: string[]
  onDone: () => void
  stepMs?: number
  pending?: boolean
  error?: string | null
  onRetry?: () => void
  onBack?: () => void
}) {
  const [done, setDone] = useState(0)
  const total = steps.length * stepMs
  const percent = useRef<HTMLSpanElement>(null)
  const gated = pending !== undefined
  const holding = !!pending && done >= steps.length - 1

  useEffect(() => {
    if (error) return
    if (done >= steps.length) {
      // Short beat on the full bar; the screen's exit animation covers the rest.
      const t = setTimeout(onDone, 200)
      return () => clearTimeout(t)
    }
    if (holding) return
    const t = setTimeout(() => setDone((d) => d + 1), stepMs)
    return () => clearTimeout(t)
  }, [done, steps.length, stepMs, onDone, holding, error])

  // Percentage readout tracks the bar's clock without re-rendering every frame.
  useEffect(() => {
    if (gated) return
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
  }, [total, gated])

  const finished = done >= steps.length
  const label = error ? 'Stopped' : finished ? 'Ready' : steps[done]
  const share = Math.min(done, steps.length) / steps.length

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
            {!finished && !error && (
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
              {gated ? `${Math.round(share * 100)}%` : '0%'}
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
          {gated ? (
            <div
              className="absolute inset-0 origin-left bg-seal-vermilion transition-transform duration-500 ease-out"
              style={{ transform: `scaleX(${share})` }}
            />
          ) : (
            <div
              className="mist-fill absolute inset-0 bg-seal-vermilion"
              style={{ '--mist-duration': `${total}ms` } as CSSProperties}
            />
          )}
          {/* Step boundaries, like brush-stroke joints. */}
          {steps.slice(1).map((s, i) => (
            <span
              key={s}
              className="absolute top-0 h-full w-[2px] bg-paper-base"
              style={{ left: `${((i + 1) / steps.length) * 100}%` }}
            />
          ))}
          {!finished && !error && <div className="mist-sweep" />}
        </div>
        {error ? (
          <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
            <p
              role="alert"
              className="max-w-[70ch] text-[13px] leading-[20px] text-seal-vermilion-dark"
            >
              {error}
            </p>
            <span className="flex gap-2">
              {onBack && <Button onClick={onBack}>← Back</Button>}
              {onRetry && (
                <Button variant="primary" onClick={onRetry}>
                  Try again
                </Button>
              )}
            </span>
          </div>
        ) : (
          holding &&
          onBack && (
            <div className="mt-4 flex justify-end">
              <Button onClick={onBack}>Cancel</Button>
            </div>
          )
        )}
      </footer>
    </div>
  )
}
