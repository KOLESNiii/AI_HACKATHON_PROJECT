/** Foundations components from the Figma file (page "0 Foundations"). */
import type { ButtonHTMLAttributes, HTMLAttributes } from 'react'

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

export function Panel({
  className = '',
  ...rest
}: HTMLAttributes<HTMLDivElement>) {
  return <div className={`scroll-panel ${className}`} {...rest} />
}
