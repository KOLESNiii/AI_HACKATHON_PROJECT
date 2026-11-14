/** Foundations components from the Figma file (page "0 Foundations"). */
import type { ButtonHTMLAttributes, HTMLAttributes, ReactNode } from 'react'

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary'
  size?: 'lg' | 'sm'
}

export function Button({
  variant = 'secondary',
  size = 'sm',
  className = '',
  ...rest
}: ButtonProps) {
  const base = variant === 'primary' ? 'chop-seal' : 'seal-outline'
  const pad =
    size === 'lg' ? 'px-5 py-3 text-[13px]' : 'px-2.5 py-1.5 text-[13px]'
  return (
    <button
      type="button"
      className={`${base} ${pad} font-medium leading-[18px] whitespace-nowrap cursor-pointer ${className}`}
      {...rest}
    />
  )
}

export function Chip({
  on,
  children,
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { on: boolean }) {
  return (
    <button
      type="button"
      aria-pressed={on}
      className={`inline-flex items-center gap-2 rounded-[2px] border px-3 py-2 text-[13px] font-medium leading-[18px] cursor-pointer transition-colors ${
        on
          ? 'border-ink-primary/50 bg-ink-primary/12 text-ink-primary'
          : 'border-hairline-ink text-ink-medium hover:bg-ink-primary/6'
      }`}
      {...rest}
    >
      <span
        className={`size-2 rounded-full ${on ? 'bg-accent-celadon' : 'bg-ink-medium/50'}`}
      />
      {children}
    </button>
  )
}

export type Status = 'valid' | 'warning' | 'danger' | 'pending'
const dotColor: Record<Status, string> = {
  valid: 'bg-accent-celadon',
  warning: 'bg-accent-ochre',
  danger: 'bg-seal-vermilion',
  pending: 'bg-ink-mist',
}
export function StatusDot({ status }: { status: Status }) {
  return (
    <span
      className={`inline-block size-2.5 shrink-0 rounded-full ${dotColor[status]}`}
    />
  )
}

export function Tag({ children }: { children: ReactNode }) {
  return (
    <span className="rounded-[2px] border border-accent-ochre/60 bg-accent-ochre/15 px-1.5 py-0.5 text-[11px] leading-[15px] font-medium text-accent-ochre">
      {children}
    </span>
  )
}

export function Panel({
  className = '',
  ...rest
}: HTMLAttributes<HTMLDivElement>) {
  return <div className={`scroll-panel ${className}`} {...rest} />
}

/** Circular 0–100 score ring; `null` renders the pending state. */
export function ScoreRing({
  score,
  size = 44,
}: {
  score: number | null
  size?: number
}) {
  const r = size / 2 - 4
  const c = 2 * Math.PI * r
  const tone =
    score == null
      ? 'var(--color-ink-mist)'
      : score >= 80
        ? 'var(--color-accent-celadon)'
        : score >= 50
          ? 'var(--color-accent-ochre)'
          : 'var(--color-seal-vermilion)'
  return (
    <div
      className="relative grid place-items-center"
      style={{ width: size, height: size }}
    >
      <svg width={size} height={size} className="absolute -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="var(--color-hairline-ink)"
          strokeWidth={4}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={tone}
          strokeWidth={4}
          strokeDasharray={`${score == null ? 0 : (c * score) / 100} ${c}`}
        />
      </svg>
      <span className="mono text-[12px] font-medium">
        {score == null ? '--' : Math.round(score)}
      </span>
    </div>
  )
}

export function Toasts({
  toasts,
  onDismiss,
}: {
  toasts: { id: number; text: string }[]
  onDismiss: (id: number) => void
}) {
  return (
    <div className="pointer-events-none fixed top-6 left-1/2 z-[60] flex -translate-x-1/2 flex-col items-center gap-2">
      {toasts.map((t) => (
        <button
          key={t.id}
          type="button"
          onClick={() => onDismiss(t.id)}
          className="pointer-events-auto max-w-[520px] cursor-pointer rounded-[4px] border-[1.5px] border-seal-vermilion bg-ink-primary px-4 py-2.5 text-left text-[13px] text-seal-paper shadow-[var(--shadow-scroll)]"
        >
          {t.text}
        </button>
      ))}
    </div>
  )
}
