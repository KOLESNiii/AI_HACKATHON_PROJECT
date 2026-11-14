import { useStore } from '../../store'
import { Button } from '../ui'
import { RoomView } from './RoomView'
import { Sidebar } from './Sidebar'

/** Room editor (edit mode): ink room view on the left, sidebar on the right. */
export function EditorScreen() {
  const setScreen = useStore((s) => s.setScreen)

  return (
    <div className="flex h-full">
      <div className="relative min-w-0 flex-1">
        <RoomView />
        <div className="absolute top-6 left-6">
          <Button onClick={() => setScreen('floorplan')}>← Floor plan</Button>
        </div>
        <div className="pointer-events-none absolute bottom-6 left-6 scroll-panel px-3 py-2 text-[11px] text-ink-medium">
          WASD pan · Q/E rotate 90° · ←/→ rotate 5° · Select furniture to rotate
        </div>
      </div>
      <Sidebar />
    </div>
  )
}
