import { useEffect, useRef, type RefObject } from 'react'
import {
  artificialSources,
  formatTimeOfDay,
  MAX_LIGHT_SOURCES,
} from '../../lib/lighting'
import { useStore } from '../../store'
import { Button } from '../ui'
import type { PlayControllerHandle } from './controls'

export function LightingPanel({
  controller,
}: {
  controller: RefObject<PlayControllerHandle | null>
}) {
  const settings = useStore((s) => s.playLighting)
  const tool = useStore((s) => s.playLightTool)
  const scene = useStore((s) => s.scene)
  const sourceCount = artificialSources(scene, settings).length
  const north = useStore((s) => s.scene.north_compass_deg)
  const firstSlider = useRef<HTMLInputElement>(null)
  useEffect(() => {
    firstSlider.current?.focus()
  }, [])

  return (
    <section
      aria-label="Room lighting"
      className="pointer-events-auto scroll-panel absolute top-20 right-6 w-[min(320px,calc(100%-48px))] max-h-[calc(100%-100px)] overflow-y-auto space-y-5 p-5 text-ink-primary"
    >
      <div>
        <h2 className="font-serif text-xl">Room lighting</h2>
        <p className="mt-1 text-xs text-ink-medium">
          Walking paused · adjust the room from this view
        </p>
      </div>
      <div>
        <label
          htmlFor="artificial-light"
          className="flex justify-between text-sm"
        >
          Artificial light{' '}
          <output htmlFor="artificial-light">
            {settings.artificialPercent}%
          </output>
        </label>
        <input
          ref={firstSlider}
          id="artificial-light"
          type="range"
          min="0"
          max="100"
          step="1"
          value={settings.artificialPercent}
          className="mt-3 w-full accent-accent-ochre"
          onChange={(e) =>
            useStore
              .getState()
              .setArtificialLight(e.currentTarget.valueAsNumber)
          }
        />
      </div>
      <div>
        <label htmlFor="light-warmth" className="flex justify-between text-sm">
          Light warmth{' '}
          <output htmlFor="light-warmth">{settings.warmthKelvin} K</output>
        </label>
        <input
          id="light-warmth"
          type="range"
          min="2200"
          max="6500"
          step="100"
          value={settings.warmthKelvin}
          className="mt-3 w-full accent-accent-ochre"
          onChange={(e) =>
            useStore.getState().setLightWarmth(e.currentTarget.valueAsNumber)
          }
        />
        <div className="flex justify-between text-xs text-ink-medium">
          <span>Warm</span>
          <span>Cool</span>
        </div>
      </div>
      <div className="space-y-2">
        <p className="text-sm">
          Light sources · {sourceCount}/{MAX_LIGHT_SOURCES}
        </p>
        <div className="flex gap-2">
          <Button
            aria-pressed={tool === 'add'}
            variant={tool === 'add' ? 'primary' : 'secondary'}
            disabled={sourceCount >= MAX_LIGHT_SOURCES}
            onClick={() =>
              useStore.getState().setLightTool(tool === 'add' ? 'none' : 'add')
            }
          >
            Add light point
          </Button>
          <Button
            aria-pressed={tool === 'remove'}
            variant={tool === 'remove' ? 'primary' : 'secondary'}
            disabled={!sourceCount}
            onClick={() =>
              useStore
                .getState()
                .setLightTool(tool === 'remove' ? 'none' : 'remove')
            }
          >
            Remove light
          </Button>
        </div>
        <p className="text-xs text-ink-medium" role="status">
          {tool === 'add'
            ? 'Click a room surface to place a light just in front of it.'
            : tool === 'remove'
              ? 'Click an amber light marker to remove that source.'
              : 'Choose a tool, then click in the room. Press Resume to walk to another view.'}{' '}
          Changes last while this room is open.
        </p>
      </div>
      <div>
        <label htmlFor="time-of-day" className="flex justify-between text-sm">
          Time of day{' '}
          <output htmlFor="time-of-day">
            {formatTimeOfDay(settings.timeOfDay)}
          </output>
        </label>
        <input
          id="time-of-day"
          type="range"
          min="0"
          max="24"
          step="0.25"
          value={settings.timeOfDay}
          aria-valuetext={formatTimeOfDay(settings.timeOfDay)}
          className="mt-3 w-full accent-accent-ochre"
          onChange={(e) =>
            useStore.getState().setTimeOfDay(e.currentTarget.valueAsNumber)
          }
        />
        <p className="mt-2 text-xs text-ink-medium">
          Illustrative daylight ·{' '}
          {north == null
            ? 'North assumed toward the top of the floor plan'
            : 'Uses floor-plan north'}
        </p>
      </div>
      <div className="flex gap-2">
        <Button
          variant="primary"
          onClick={() => controller.current?.resumePlay()}
        >
          Resume
        </Button>
        <Button onClick={() => controller.current?.exitPlay()}>
          Return to editor
        </Button>
      </div>
    </section>
  )
}
