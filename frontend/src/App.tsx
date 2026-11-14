import { useCallback } from 'react'
import { FloorPlanScreen } from './components/intake/FloorPlanScreen'
import { ProgressScreen } from './components/intake/ProgressScreen'
import { UploadScreen } from './components/intake/UploadScreen'
import { Button, Panel } from './components/ui'
import { mockSegments } from './data/segments'
import { useStore } from './store'

/** Flow: upload → read floor plan → pick a room → build that room → (editor: later PR). */
export default function App() {
  const screen = useStore((s) => s.screen)
  const segmentId = useStore((s) => s.segmentId)
  const setScreen = useStore((s) => s.setScreen)
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
      {screen === 'editor' && (
        <div className="grid h-full place-items-center">
          <Panel className="flex w-[360px] flex-col gap-3 p-6">
            <h2 className="font-serif text-[20px] leading-[23px] font-semibold">
              {roomLabel ?? 'Room'} is ready
            </h2>
            <p className="text-[14px] leading-[23px] text-ink-medium">
              The room editor arrives in a later PR.
            </p>
            <Button onClick={toFloorPlan} className="self-start">
              ← Floor plan
            </Button>
          </Panel>
        </div>
      )}
      <div className="aged-vignette" />
      <div className="paper-grain-overlay" />
    </div>
  )
}
