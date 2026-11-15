import { useRef } from 'react'
import { useStore } from '../../store'
import type { PlayControllerHandle } from '../play/controls'
import { PlayOverlay } from '../play/PlayOverlay'
import { Button } from '../ui'
import { RoomView } from './RoomView'
import { Sidebar } from './Sidebar'
import { useLiveAudit } from './useLiveAudit'

/** Room editor (edit mode): ink room view on the left, sidebar on the right. */
export function EditorScreen() {
  const setScreen = useStore((s) => s.setScreen)
  const play = useStore((s) => s.mode === 'play')
  const controller = useRef<PlayControllerHandle>(null)
  useLiveAudit()

  return (
    <div className="flex h-full">
      <div className="relative min-w-0 flex-1">
        <RoomView controller={controller} />
        {!play && (
          <div className="absolute top-6 left-6">
            <Button onClick={() => setScreen('floorplan')}>← Floor plan</Button>
          </div>
        )}
        {!play && (
          <div className="pointer-events-none absolute bottom-6 left-6 scroll-panel max-w-[calc(100%-300px)] px-3 py-2 text-[11px] text-ink-medium">
            WASD pan · Q/E rotate 90° · ←/→ rotate 5° · Select furniture to
            rotate
          </div>
        )}
        <PlayOverlay controller={controller} />
      </div>
      {!play && <Sidebar />}
    </div>
  )
}
