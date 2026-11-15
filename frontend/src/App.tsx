import {
  AnimatePresence,
  MotionConfig,
  motion,
  type Variants,
} from 'framer-motion'
import { useCallback, useState } from 'react'
import { EditorScreen } from './components/editor/EditorScreen'
import { FloorPlanScreen } from './components/intake/FloorPlanScreen'
import { HomeScreen } from './components/intake/HomeScreen'
import { Landscape } from './components/intake/Landscape'
import { ProgressScreen } from './components/intake/ProgressScreen'
import { UploadScreen } from './components/intake/UploadScreen'
import { Toasts } from './components/ui'
import { SoundControls } from './components/SoundControls'
import { findPlanRoom } from './data/homePlan'
import { useStore, type Screen } from './store'

const ORDER: Screen[] = [
  'home',
  'upload',
  'reading',
  'floorplan',
  'building',
  'editor',
]

// `dir` is +1 moving forward through the flow, -1 going back (e.g. editor → floor plan).
// Opacity and transform only: a full-screen blur filter repaints the whole screen
// every frame and made the loader's proverb stutter.
const screenVariants: Variants = {
  enter: (dir: number) => ({ opacity: 0, y: 10 * dir }),
  center: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.28, ease: 'easeOut' },
  },
  exit: (dir: number) => ({
    opacity: 0,
    y: -10 * dir,
    transition: { duration: 0.18, ease: 'easeIn' },
  }),
}

/** Flow: home → upload → read floor plan → pick a room → build that room → editor. */
export default function App() {
  const screen = useStore((s) => s.screen)
  const segmentId = useStore((s) => s.segmentId)
  const setScreen = useStore((s) => s.setScreen)
  const toasts = useStore((s) => s.toasts)
  const dismissToast = useStore((s) => s.dismissToast)
  const toFloorPlan = useCallback(() => setScreen('floorplan'), [setScreen])
  const toEditor = useCallback(() => setScreen('editor'), [setScreen])
  const home = useStore((s) => s.home)
  const planStatus = useStore((s) => s.planStatus)
  const planError = useStore((s) => s.planError)
  const submitUpload = useStore((s) => s.submitUpload)
  const cancelUpload = useStore((s) => s.cancelUpload)
  const retryUpload = useCallback(() => void submitUpload(), [submitUpload])
  const roomLabel = findPlanRoom(home, segmentId)?.label
  const roomSession = useStore((s) => s.roomSession)
  // A different panorama per screen; room builds alternate between two.
  const landscape =
    screen === 'home' || screen === 'upload'
      ? 0
      : screen === 'reading'
        ? 1
        : screen === 'building'
          ? 2 + (roomSession % 2)
          : null

  // Direction of the latest screen change, derived during render (React's
  // "adjust state on prop change" pattern) so entering and exiting screens agree.
  const [prev, setPrev] = useState(screen)
  const [dir, setDir] = useState(1)
  if (prev !== screen) {
    setDir(ORDER.indexOf(screen) >= ORDER.indexOf(prev) ? 1 : -1)
    setPrev(screen)
  }

  const renderScreen = () => {
    switch (screen) {
      case 'home':
        return <HomeScreen />
      case 'upload':
        return <UploadScreen />
      case 'reading':
        // An upload waits on the service; the demo home only plays the steps.
        return planStatus === 'idle' ? (
          <ProgressScreen
            steps={['Parsing floor plan', 'Segmenting rooms']}
            onDone={toFloorPlan}
          />
        ) : (
          <ProgressScreen
            steps={['Sending your files', 'Reading floors and rooms']}
            onDone={toFloorPlan}
            pending={planStatus === 'loading'}
            error={planError}
            onRetry={retryUpload}
            onBack={cancelUpload}
          />
        )
      case 'floorplan':
        return <FloorPlanScreen />
      case 'building':
        return (
          <ProgressScreen
            title={roomLabel}
            steps={
              home.planId
                ? ['Raising walls and openings', 'Placing your furniture']
                : ['Extracting furniture from video', 'Assembling room']
            }
            onDone={toEditor}
          />
        )
      case 'editor':
        return <EditorScreen />
    }
  }

  return (
    <MotionConfig reducedMotion="user">
      <div className="h-full">
        {/* Mounted for the whole session so the loader opens on a drawn landscape. */}
        <Landscape index={landscape} />
        <AnimatePresence mode="wait" initial={false} custom={dir}>
          <motion.div
            key={screen}
            className="h-full"
            custom={dir}
            variants={screenVariants}
            initial="enter"
            animate="center"
            exit="exit"
          >
            {renderScreen()}
          </motion.div>
        </AnimatePresence>
        <Toasts toasts={toasts} onDismiss={dismissToast} />
        <SoundControls />
        <div className="aged-vignette" />
        <div className="paper-grain-overlay" />
      </div>
    </MotionConfig>
  )
}
