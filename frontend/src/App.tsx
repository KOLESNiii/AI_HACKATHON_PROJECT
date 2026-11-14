import { useCallback } from 'react'
import { EditorScreen } from './components/editor/EditorScreen'
import { FloorPlanScreen } from './components/intake/FloorPlanScreen'
import { ProgressScreen } from './components/intake/ProgressScreen'
import { UploadScreen } from './components/intake/UploadScreen'
import { Toasts } from './components/ui'
import { mockSegments } from './data/segments'
import { useStore } from './store'

/** Flow: upload → read floor plan → pick a room → build that room → editor. */
export default function App() {
  const screen = useStore((s) => s.screen)
  const segmentId = useStore((s) => s.segmentId)
  const setScreen = useStore((s) => s.setScreen)
  const toasts = useStore((s) => s.toasts)
  const dismissToast = useStore((s) => s.dismissToast)
  const toFloorPlan = useCallback(() => setScreen('floorplan'), [setScreen])
  const toEditor = useCallback(() => setScreen('editor'), [setScreen])
  const roomLabel = mockSegments.find((s) => s.room_id === segmentId)?.label

  return (
    <div className="h-full">
      {screen === 'upload' && <UploadScreen />}
      {screen === 'reading' && (
        <ProgressScreen
          steps={['Parsing floor plan', 'Segmenting rooms']}
          onDone={toFloorPlan}
        />
      )}
      {screen === 'floorplan' && <FloorPlanScreen />}
      {screen === 'building' && (
        <ProgressScreen
          title={roomLabel}
          steps={['Extracting furniture from video', 'Assembling room']}
          onDone={toEditor}
        />
      )}
      {screen === 'editor' && <EditorScreen />}
      <Toasts toasts={toasts} onDismiss={dismissToast} />
      <div className="aged-vignette" />
      <div className="paper-grain-overlay" />
    </div>
  )
}
