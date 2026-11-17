import { findPlanRoom } from '../../data/homePlan'
import {
  examplesFor,
  isStartingLayout,
  roomsWithExamples,
} from '../../demo/examples'
import { matchingAudit } from '../../lib/layoutDiff'
import { useStore } from '../../store'
import { Button } from '../ui'

/**
 * The demo's stand-in for the chat box: real agent runs recorded on this room's starting
 * layout, replayed on request. They only run there, so after any change the room is reset first.
 */
export function ExamplePrompts({ compact }: { compact: boolean }) {
  const scene = useStore((s) => s.scene)
  const busy = useStore((s) => s.agentBusy)
  const blocked = useStore(
    (s) => s.interacting || s.roomLoading || s.mode !== 'edit',
  )
  const home = useStore((s) => s.home)
  // Proposals compare against the current audit, so wait for it before replaying.
  const audited = useStore((s) => matchingAudit(s.audit, s.scene))
  const { sendChat, resetRoom, selectSegment, openRoom } = useStore.getState()
  const examples = examplesFor(scene.scene_id)
  const pristine = isStartingLayout(scene)

  if (!examples.length) {
    const others = roomsWithExamples
      .map((id) => findPlanRoom(home, id))
      .filter((r) => r != null)
    return (
      <div className="flex flex-col gap-3 border-t border-hairline-ink pt-4">
        <p className="text-[13px] leading-[21px] text-ink-medium">
          No agent runs were recorded for this room. You can still move
          furniture, add from the Library and walk it. To see the agent work,
          open:
        </p>
        <div className="flex flex-wrap gap-2">
          {others.map((room) => (
            <Button
              key={room.room_id}
              onClick={() => {
                selectSegment(room.room_id)
                openRoom()
              }}
            >
              {room.label}
            </Button>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-2.5 border-t border-hairline-ink pt-4">
      <div className="flex items-baseline justify-between gap-2">
        <span className="text-[11px] font-medium tracking-[0.08em] text-ink-mist uppercase">
          Try asking
        </span>
        {!pristine && (
          <button
            type="button"
            onClick={resetRoom}
            disabled={busy || blocked}
            className="cursor-pointer text-[11px] font-medium text-seal-vermilion hover:underline disabled:cursor-default disabled:opacity-50"
          >
            Reset to starting layout
          </button>
        )}
      </div>
      {pristine && !audited && !busy && (
        <p role="status" className="text-[11px] leading-[17px] text-ink-medium">
          Checking the room first…
        </p>
      )}
      {!pristine && (
        <p className="text-[11px] leading-[17px] text-ink-medium">
          These runs were recorded on this room’s starting layout, so they
          replay only from there.
        </p>
      )}
      <ul className="flex flex-col gap-2">
        {examples.map((example) => (
          <li key={example.prompt}>
            <button
              type="button"
              disabled={busy || blocked || !pristine || !audited}
              onClick={() => void sendChat(example.prompt)}
              className="group flex w-full cursor-pointer flex-col gap-1 rounded-[2px] border border-hairline-ink bg-paper-card/65 px-3 py-2.5 text-left transition-colors hover:border-seal-vermilion/60 hover:bg-paper-card disabled:cursor-default disabled:opacity-55 disabled:hover:border-hairline-ink"
            >
              <span className="flex items-start justify-between gap-3">
                <em className="font-serif text-[15px] leading-[20px] text-ink-primary">
                  “{example.prompt}”
                </em>
                <span
                  aria-hidden
                  className="mt-0.5 text-[12px] text-seal-vermilion opacity-0 transition-opacity group-hover:opacity-100 group-disabled:opacity-0"
                >
                  ▸
                </span>
              </span>
              {!compact && (
                <span className="text-[11px] leading-[16px] text-ink-medium">
                  {example.blurb}
                </span>
              )}
            </button>
          </li>
        ))}
      </ul>
      <p className="text-[10px] leading-[15px] text-ink-mist">
        Real Claude runs, recorded and replayed so the demo needs no API key.
        The collision, door and Feng Shui checks run live in your browser.
      </p>
    </div>
  )
}
