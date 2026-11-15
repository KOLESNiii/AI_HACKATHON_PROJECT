import { motion } from 'framer-motion'
import { useStore } from '../../store'
import { Button } from '../ui'
import './ProgressScreen.css'

const rise = {
  hidden: { opacity: 0, y: 14 },
  shown: { opacity: 1, y: 0, transition: { duration: 0.6, ease: 'easeOut' } },
} as const

/** Front page: title and call to action over the app-wide Shan Shui <Landscape>. */
export function HomeScreen() {
  const setScreen = useStore((s) => s.setScreen)
  return (
    <div className="relative h-full overflow-hidden">
      {/* Same pool of mist as the loader's proverb, so the text reads over the strokes. */}
      <motion.section
        className="mist-quote-zone"
        initial="hidden"
        animate="shown"
        transition={{ staggerChildren: 0.12, delayChildren: 0.1 }}
      >
        <div className="flex flex-col items-center">
          <motion.h1
            variants={rise}
            className="font-serif text-[clamp(56px,9vw,120px)] leading-none font-semibold tracking-[0.02em] text-ink-primary [text-shadow:0_0_24px_rgb(234_224_206/0.95)]"
          >
            Refresh
          </motion.h1>
          <motion.p
            variants={rise}
            className="mt-5 max-w-[34ch] font-serif text-[clamp(17px,1.8vw,24px)] leading-[1.45] text-ink-medium italic [text-shadow:0_0_16px_rgb(234_224_206/0.95)]"
          >
            Turn a floor plan and a walkthrough video into rooms you can
            rearrange in 3D.
          </motion.p>
          <motion.div variants={rise} className="mt-9">
            <Button
              variant="primary"
              size="lg"
              className="pointer-events-auto px-8"
              onClick={() => setScreen('upload')}
            >
              Redesign my home
            </Button>
          </motion.div>
        </div>
      </motion.section>
    </div>
  )
}
