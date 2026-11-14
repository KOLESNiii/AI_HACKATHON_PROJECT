import { useEffect, type RefObject } from 'react'
import { canStand } from '../../lib/walk'
import { useStore } from '../../store'
import { Button } from '../ui'
import type { PlayControllerHandle } from './controls'

export function PlayOverlay({
  controller,
}: {
  controller: RefObject<PlayControllerHandle | null>
}) {
  const play = useStore((s) => s.mode === 'play')
  const human = useStore((s) => s.human)
  const scene = useStore((s) => s.scene)
  const placing = useStore((s) => s.placingHuman)
  const interacting = useStore((s) => s.interacting)
  const valid = human != null && canStand(human, scene)

  useEffect(() => {
    const cancel = () => useStore.getState().cancelHumanPlacement()
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') cancel()
    }
    window.addEventListener('blur', cancel)
    window.addEventListener('keydown', onKey)
    document.addEventListener('visibilitychange', cancel)
    return () => {
      cancel()
      window.removeEventListener('blur', cancel)
      window.removeEventListener('keydown', onKey)
      document.removeEventListener('visibilitychange', cancel)
    }
  }, [])

  if (play)
    return (
      <div className="pointer-events-none absolute inset-0 select-none">
        <div className="scroll-panel absolute top-6 left-6 px-3 py-2 text-[12px]">
          WASD walk · Mouse look · Esc return to editor
        </div>
        <div className="absolute top-1/2 left-1/2 size-1.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-seal-paper shadow" />
      </div>
    )

  return (
    <div
      className="scroll-panel absolute right-6 bottom-6 flex max-w-[240px] flex-col items-end gap-2 p-3 select-none"
      aria-label="Human placement"
    >
      <button
        type="button"
        aria-label="Drag human into room"
        disabled={interacting && !placing}
        className="flex touch-none cursor-grab items-center gap-2 text-[13px] font-medium text-accent-ochre active:cursor-grabbing"
        onPointerDown={(e) => {
          if (e.button !== 0 || !useStore.getState().beginHumanPlacement())
            return
          e.preventDefault()
          e.currentTarget.setPointerCapture(e.pointerId)
        }}
        onPointerMove={(e) => {
          if (useStore.getState().placingHuman)
            useStore
              .getState()
              .previewHuman(
                controller.current?.floorPoint(e.clientX, e.clientY) ?? null,
              )
        }}
        onPointerUp={(e) => {
          if (!useStore.getState().placingHuman) return
          const placed = useStore
            .getState()
            .finishHumanPlacement(
              controller.current?.floorPoint(e.clientX, e.clientY) ?? null,
            )
          e.currentTarget.releasePointerCapture(e.pointerId)
          if (!placed)
            useStore
              .getState()
              .toast('Drop the human on clear floor inside the room.')
        }}
        onPointerCancel={() => useStore.getState().cancelHumanPlacement()}
        onLostPointerCapture={() => useStore.getState().cancelHumanPlacement()}
      >
        <svg
          width="22"
          height="32"
          viewBox="0 0 22 32"
          fill="currentColor"
          aria-hidden="true"
        >
          <circle cx="11" cy="5" r="4" />
          <path d="M6 11h10l4 11-3 1-3-8v15h-3V21h-1v9H7V15l-3 8-3-1z" />
        </svg>
        {placing
          ? 'Drop onto clear floor'
          : human
            ? 'Drag to relocate'
            : 'Drag human into room'}
      </button>
      {human && (
        <div className="flex gap-2">
          <Button
            variant="primary"
            disabled={!valid || interacting}
            onClick={() => controller.current?.requestPlay()}
          >
            ▶ Play
          </Button>
          <Button
            disabled={interacting}
            onClick={() => useStore.getState().removeHuman()}
          >
            Remove human
          </Button>
        </div>
      )}
      {human && !valid && (
        <p className="text-[11px] text-seal-vermilion">
          Position blocked. Drag the human to clear floor.
        </p>
      )}
      {!human && (
        <p className="text-[11px] text-ink-medium">
          Place a human, then Play to explore.
        </p>
      )}
    </div>
  )
}
