import { useEffect } from 'react'
import { useStore } from '../../store'
import { Button } from '../ui'
import { RoomView } from './RoomView'
import { Sidebar } from './Sidebar'

/** Room editor (edit mode): ink room view on the left, sidebar on the right. */
export function EditorScreen() {
  const setScreen = useStore((s) => s.setScreen)

  // Delete / Backspace removes the selected item (not while typing).
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== 'Delete' && e.key !== 'Backspace') return
      const el = e.target as HTMLElement | null
      if (
        el &&
        (el.tagName === 'INPUT' ||
          el.tagName === 'TEXTAREA' ||
          el.isContentEditable)
      )
        return
      const { selectedId, interacting, deleteItem } = useStore.getState()
      if (selectedId && !interacting) deleteItem(selectedId)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  return (
    <div className="flex h-full">
      <div className="relative min-w-0 flex-1">
        <RoomView />
        <div className="absolute top-6 left-6">
          <Button onClick={() => setScreen('floorplan')}>← Floor plan</Button>
        </div>
      </div>
      <Sidebar />
    </div>
  )
}
