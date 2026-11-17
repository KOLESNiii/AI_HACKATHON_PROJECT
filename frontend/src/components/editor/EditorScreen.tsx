import { useRef } from 'react'
import { useLiveAudit } from './useLiveAudit'
import { useStore } from '../../store'
import type { PlayControllerHandle } from '../play/controls'
import { PlayOverlay } from '../play/PlayOverlay'
import { Button } from '../ui'
import { isExtractingWarning } from '../../lib/spatial'
import { ExtractionProgress } from './ExtractionProgress'
import { RoomView } from './RoomView'
import { Sidebar } from './Sidebar'
import { VersionTree } from './VersionTree'
import { DEMO } from '../../demo/config'
import { isStartingLayout } from '../../demo/examples'

/** Room editor (edit mode): ink room view on the left, sidebar on the right. */
export function EditorScreen() {
  const setScreen = useStore((s) => s.setScreen)
  const play = useStore((s) => s.mode === 'play')
  const roomLoading = useStore((s) => s.roomLoading)
  const allWarnings = useStore((s) => s.roomWarnings)
  const extracting = useStore((s) => s.furnitureProgress !== null)
  // The progress panel says it better than the service's warning.
  const warnings = extracting
    ? allWarnings.filter((w) => !isExtractingWarning(w))
    : allWarnings
  const changed = useStore((s) => DEMO && !isStartingLayout(s.scene))
  const resetRoom = useStore((s) => s.resetRoom)
  const controller = useRef<PlayControllerHandle>(null)
  useLiveAudit()

  return (
    <div className="flex h-full">
      {!play && !DEMO && <VersionTree />}
      <div className="relative min-w-0 flex-1">
        <RoomView controller={controller} />
        {roomLoading && (
          <div
            role="status"
            className="absolute inset-0 z-40 flex items-center justify-center bg-paper-base/80 text-[14px]"
          >
            Loading room…
          </div>
        )}
        {!roomLoading && warnings.length > 0 && (
          <div
            role="status"
            className="absolute top-20 left-6 z-10 max-h-28 max-w-sm overflow-y-auto scroll-panel p-3 text-[11px] text-accent-ochre"
          >
            {warnings.map((warning, i) => (
              <p key={i}>{warning}</p>
            ))}
          </div>
        )}
        {!play && !roomLoading && <ExtractionProgress />}
        {!play && (
          <div className="absolute top-6 left-6 flex gap-2">
            <Button onClick={() => setScreen('floorplan')}>← Floor plan</Button>
            {changed && (
              <Button onClick={resetRoom} disabled={roomLoading}>
                Reset room
              </Button>
            )}
          </div>
        )}
        {!play && (
          <div className="pointer-events-none absolute bottom-6 left-6 scroll-panel max-w-[calc(100%-300px)] px-3 py-2 text-[11px] text-ink-medium">
            {DEMO
              ? 'Drag furniture to move it · Q/E rotate 90° · ←/→ rotate 5° · WASD pan'
              : 'WASD pan · Q/E rotate 90° · ←/→ rotate 5° · Select furniture to rotate'}
          </div>
        )}
        <PlayOverlay controller={controller} />
      </div>
      {!play && <Sidebar />}
    </div>
  )
}
