import { useEffect, useRef, useState } from 'react'
import { AudioEngine, type AudioStatus } from '../audio/engine'
import { onSoundCue, playCue } from '../audio/cues'
import { useAudioPreferences } from '../audio/preferences'
import { useStore } from '../store'
import { editorKey } from './editor/keyboard'

function Speaker({ muted }: { muted: boolean }) {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      aria-hidden="true"
    >
      <path d="M11 4 6 8H3v8h3l5 4V4Z" strokeLinejoin="round" />
      {muted ? (
        <path d="m16 9 6 6m0-6-6 6" strokeLinecap="round" />
      ) : (
        <>
          <path
            d="M15 8a6 6 0 0 1 0 8M18 5a10 10 0 0 1 0 14"
            strokeLinecap="round"
          />
        </>
      )}
    </svg>
  )
}

/** App-wide lifetime: screen animations never recreate the mixer or restart music. */
export function SoundControls() {
  const preferences = useAudioPreferences()
  const [open, setOpen] = useState(false)
  const [status, setStatus] = useState<AudioStatus>({
    supported: true,
    music: 'loading',
  })
  const mode = useStore((s) => s.mode)
  const screen = useStore((s) => s.screen)
  const phase = useStore((s) => s.playPhase)
  const walking = mode === 'play' && phase === 'walking'
  const panel = useRef<HTMLDivElement>(null)
  const settingsButton = useRef<HTMLButtonElement>(null)
  const musicToggle = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const engine = new AudioEngine(useAudioPreferences.getState(), setStatus)
    engine.update(
      useAudioPreferences.getState(),
      useStore.getState().mode === 'play',
    )
    const stopCues = onSoundCue((cue) => engine.play(cue))
    const stopPreferences = useAudioPreferences.subscribe((p) => {
      engine.update(p)
      engine.activate()
    })
    const stopScene = useStore.subscribe((next, prev) => {
      if (next.mode !== prev.mode) {
        engine.update(useAudioPreferences.getState(), next.mode === 'play')
        playCue('transition')
      }
      if (
        (prev.screen === 'reading' && next.screen === 'floorplan') ||
        (prev.screen === 'building' && next.screen === 'editor')
      )
        playCue('ready')
    })
    const gesture = () => engine.activate()
    const key = (event: KeyboardEvent) => {
      if (editorKey(event) === 'm' && !event.repeat) {
        event.preventDefault()
        useAudioPreferences.getState().toggleMute()
      }
    }
    const visibility = () => engine.setHidden(document.hidden)
    window.addEventListener('pointerdown', gesture, true)
    window.addEventListener('keydown', gesture, true)
    window.addEventListener('keydown', key)
    document.addEventListener('visibilitychange', visibility)
    engine.setHidden(document.hidden)
    return () => {
      stopCues()
      stopPreferences()
      stopScene()
      window.removeEventListener('pointerdown', gesture, true)
      window.removeEventListener('keydown', gesture, true)
      window.removeEventListener('keydown', key)
      document.removeEventListener('visibilitychange', visibility)
      engine.dispose()
    }
  }, [])

  useEffect(() => {
    if (!open || walking) return
    musicToggle.current?.focus()
    const outside = (e: PointerEvent) => {
      if (!panel.current?.contains(e.target as Node)) setOpen(false)
    }
    const escape = (e: KeyboardEvent) => {
      if (e.key !== 'Escape') return
      e.stopPropagation()
      setOpen(false)
      settingsButton.current?.focus()
    }
    window.addEventListener('pointerdown', outside)
    panel.current?.addEventListener('keydown', escape)
    const node = panel.current
    return () => {
      window.removeEventListener('pointerdown', outside)
      node?.removeEventListener('keydown', escape)
    }
  }, [open, walking])

  const silent =
    preferences.muted ||
    ((!preferences.musicEnabled || preferences.musicVolume === 0) &&
      (!preferences.effectsEnabled || preferences.effectsVolume === 0))
  const musicLabel = {
    loading: 'Music is loading…',
    playing: 'Piano for a little breathing room.',
    paused: 'Music is paused.',
    blocked: 'Click or press a key to begin audio.',
    unavailable: 'Music unavailable. Editor sounds can still play.',
  }[status.music]

  return (
    <div
      ref={panel}
      className={`fixed right-4 z-[65] ${screen === 'editor' && mode === 'edit' ? 'top-[68px]' : 'top-4'}`}
    >
      <div className="scroll-panel ml-auto flex w-fit items-center overflow-hidden text-ink-medium">
        <button
          type="button"
          aria-label={preferences.muted ? 'Unmute sound (M)' : 'Mute sound (M)'}
          aria-pressed={preferences.muted}
          title={`${preferences.muted ? 'Unmute' : 'Mute'} sound · M${walking ? ' · L pauses walking' : ''}`}
          className="flex size-10 items-center justify-center cursor-pointer hover:bg-paper-deep focus-visible:outline-2 focus-visible:outline-accent-ochre"
          onClick={preferences.toggleMute}
          disabled={walking}
        >
          <Speaker muted={silent} />
        </button>
        <button
          ref={settingsButton}
          type="button"
          aria-label="Sound settings"
          aria-expanded={open && !walking}
          aria-controls="sound-settings"
          disabled={walking}
          title={walking ? 'Press L or Esc to adjust sound' : 'Sound settings'}
          className="flex h-10 items-center gap-2 border-l border-hairline-ink px-3 text-xs cursor-pointer hover:bg-paper-deep focus-visible:outline-2 focus-visible:outline-accent-ochre"
          onClick={() => setOpen(!open)}
        >
          Sound <span aria-hidden="true">{open && !walking ? '⌃' : '⌄'}</span>
        </button>
      </div>
      {open && !walking && (
        <section
          id="sound-settings"
          aria-label="Sound settings"
          className="scroll-panel mt-2 max-h-[calc(100dvh-140px)] w-[min(300px,calc(100vw-32px))] space-y-5 overflow-y-auto p-5 text-sm"
        >
          <div className="flex items-center justify-between">
            <h2 className="font-serif text-xl">A quieter kind of focus</h2>
            <button
              type="button"
              aria-label="Close sound settings"
              className="cursor-pointer px-2"
              onClick={() => {
                setOpen(false)
                settingsButton.current?.focus()
              }}
            >
              ×
            </button>
          </div>
          {(['music', 'effects'] as const).map((channel) => {
            const enabled =
              channel === 'music' ? 'musicEnabled' : 'effectsEnabled'
            const volume = channel === 'music' ? 'musicVolume' : 'effectsVolume'
            const label = channel === 'music' ? 'Music' : 'Editor sounds'
            return (
              <div key={channel} className="space-y-2">
                <label className="flex items-center justify-between">
                  {label}
                  <input
                    ref={channel === 'music' ? musicToggle : undefined}
                    type="checkbox"
                    checked={preferences[enabled]}
                    className="size-4 accent-accent-celadon"
                    onChange={(e) =>
                      preferences.update({ [enabled]: e.currentTarget.checked })
                    }
                  />
                </label>
                <label
                  htmlFor={`${channel}-volume`}
                  className="flex items-center justify-between text-xs text-ink-medium"
                >
                  Volume <output>{preferences[volume]}%</output>
                </label>
                <input
                  id={`${channel}-volume`}
                  aria-label={`${label} volume`}
                  type="range"
                  min="0"
                  max="100"
                  value={preferences[volume]}
                  className="w-full accent-accent-ochre"
                  onChange={(e) =>
                    preferences.update({
                      [volume]: e.currentTarget.valueAsNumber,
                    })
                  }
                />
              </div>
            )
          })}
          <p className="text-xs text-ink-medium" role="status">
            {!status.supported
              ? 'Audio is unavailable in this browser.'
              : preferences.muted
                ? 'All sound muted · press M to restore.'
                : musicLabel}
          </p>
          <p className="border-t border-hairline-ink pt-3 text-[11px] leading-relaxed text-ink-medium">
            <a
              className="underline"
              href="https://www.scottbuckley.com.au/library/reverie/"
              target="_blank"
              rel="noreferrer"
            >
              “Reverie” by Scott Buckley
            </a>{' '}
            ·{' '}
            <a
              className="underline"
              href="https://creativecommons.org/licenses/by/4.0/"
              target="_blank"
              rel="noreferrer"
            >
              CC BY 4.0
            </a>
            . Trimmed and re-encoded for a continuous background loop.
          </p>
        </section>
      )}
    </div>
  )
}
