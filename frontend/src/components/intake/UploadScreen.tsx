import { motion } from 'framer-motion'
import {
  useEffect,
  useMemo,
  useState,
  type DragEvent,
  type ReactNode,
} from 'react'
import { useStore } from '../../store'
import { Button } from '../ui'
import './ProgressScreen.css'
import './UploadScreen.css'

const rise = {
  hidden: { opacity: 0, y: 14 },
  shown: { opacity: 1, y: 0, transition: { duration: 0.6, ease: 'easeOut' } },
} as const

const glow = '[text-shadow:0_0_16px_rgb(234_224_206/0.95)]'

/** Ink glyph: a floor plan outline with a door swing. */
const PlanGlyph = (
  <svg
    viewBox="0 0 48 48"
    className="size-11"
    fill="none"
    stroke="currentColor"
    strokeWidth={1.6}
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
  >
    <path d="M6 8h36v32H6z" />
    <path d="M24 8v14M6 26h12M30 22h12M24 30v10" />
    <path d="M18 26a6 6 0 0 1 6 -6" strokeDasharray="2 2.5" />
  </svg>
)

/** Ink glyph: a strip of film. */
const VideoGlyph = (
  <svg
    viewBox="0 0 48 48"
    className="size-11"
    fill="none"
    stroke="currentColor"
    strokeWidth={1.6}
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
  >
    <path d="M8 10h32v28H8z" />
    <path d="M14 10v28M34 10v28" />
    <path d="M8 16h6M8 22h6M8 28h6M8 34h6M34 16h6M34 22h6M34 28h6M34 34h6" />
    <path d="M21 19.5v9l7-4.5z" />
  </svg>
)

/** Object URL for a file's preview, revoked when the file changes or the card unmounts. */
function usePreview(file: File | null) {
  const url = useMemo(() => (file ? URL.createObjectURL(file) : null), [file])
  useEffect(() => () => void (url && URL.revokeObjectURL(url)), [url])
  return url
}

function DropCard({
  step,
  title,
  hint,
  accept,
  glyph,
  file,
  onFile,
}: {
  step: string
  title: string
  hint: string
  accept: string
  glyph: ReactNode
  file: File | null
  onFile: (f: File) => void
}) {
  const [over, setOver] = useState(false)
  const url = usePreview(file)
  const kind = file?.type.startsWith('image/')
    ? 'image'
    : file?.type.startsWith('video/')
      ? 'video'
      : 'other'
  const onDrop = (e: DragEvent) => {
    e.preventDefault()
    setOver(false)
    const f = e.dataTransfer.files[0]
    if (f) onFile(f)
  }
  return (
    <label
      onDragOver={(e) => {
        e.preventDefault()
        setOver(true)
      }}
      onDragLeave={() => setOver(false)}
      onDrop={onDrop}
      className={`scroll-panel drop-card group relative flex h-[230px] w-full max-w-[300px] cursor-pointer flex-col items-center justify-center gap-2 overflow-hidden px-6 text-center transition-colors sm:w-[300px] ${
        over ? 'is-over bg-seal-vermilion/6' : 'hover:bg-paper-card'
      }`}
    >
      <input
        type="file"
        accept={accept}
        className="sr-only"
        onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])}
      />
      <span className="mono absolute top-4 left-4 text-[10px] tracking-[0.24em] text-ink-mist uppercase">
        {step}
      </span>

      {file ? (
        <>
          <span className="seal-stamp" aria-hidden="true">
            已收
          </span>
          {url && kind === 'image' && (
            <img
              src={url}
              alt=""
              className="mt-6 h-[130px] w-full object-contain mix-blend-multiply"
            />
          )}
          {url && kind === 'video' && (
            <video
              src={`${url}#t=0.1`}
              muted
              playsInline
              preload="metadata"
              className="mt-6 h-[130px] w-full rounded-[2px] object-contain"
            />
          )}
          {kind === 'other' && (
            <span className="mt-4 text-ink-medium">{glyph}</span>
          )}
          <span className="mono max-w-full truncate text-[11px] text-accent-celadon">
            {file.name}
          </span>
          <span className="mono text-[10px] tracking-[0.18em] text-ink-mist uppercase opacity-0 transition-opacity group-hover:opacity-100">
            Click or drop to replace
          </span>
        </>
      ) : (
        <>
          <span
            className={`mt-3 transition-colors ${over ? 'text-seal-vermilion' : 'text-ink-medium'}`}
          >
            {glyph}
          </span>
          <span className="font-serif text-[20px] leading-tight font-semibold text-ink-primary">
            {title}
          </span>
          <span className="text-[12px] text-ink-medium">
            Drop file or click to browse
          </span>
          <span className="mono text-[10px] text-ink-mist">{hint}</span>
        </>
      )}
    </label>
  )
}

export function UploadScreen() {
  const setScreen = useStore((s) => s.setScreen)
  const [plan, setPlan] = useState<File | null>(null)
  const [video, setVideo] = useState<File | null>(null)
  return (
    <div className="relative h-full overflow-hidden">
      <motion.section
        className="mist-quote-zone is-interactive"
        initial="hidden"
        animate="shown"
        transition={{ staggerChildren: 0.1, delayChildren: 0.05 }}
      >
        <div className="flex w-full flex-col items-center">
          <motion.div
            variants={rise}
            className="mb-3 font-serif text-[14px] text-seal-vermilion opacity-70"
          >
            ✦
          </motion.div>
          <motion.h1
            variants={rise}
            className={`font-serif text-[clamp(36px,5vw,60px)] leading-none font-semibold tracking-[0.02em] text-ink-primary ${glow}`}
          >
            Bring us your home
          </motion.h1>
          <motion.p
            variants={rise}
            className={`mt-3 max-w-[40ch] font-serif text-[clamp(15px,1.5vw,20px)] leading-[1.45] text-ink-medium italic ${glow}`}
          >
            A floor plan to read, and a walkthrough to furnish it.
          </motion.p>

          <motion.div
            variants={rise}
            className="mt-8 flex w-full flex-col items-center justify-center gap-5 sm:flex-row"
          >
            <DropCard
              step="壹 · Floor plan"
              title="Floor plan image"
              hint="PNG · JPG · PDF"
              accept="image/*,application/pdf"
              glyph={PlanGlyph}
              file={plan}
              onFile={setPlan}
            />
            <DropCard
              step="贰 · Walkthrough"
              title="Walkthrough video"
              hint="MP4 · MOV"
              accept="video/*"
              glyph={VideoGlyph}
              file={video}
              onFile={setVideo}
            />
          </motion.div>

          <motion.div variants={rise} className="mt-7 w-full max-w-[620px]">
            <hr className="ink-divider mb-5" />
            <div className="flex flex-wrap items-center justify-between gap-3">
              <Button size="lg" onClick={() => setScreen('reading')}>
                Skip with demo home
              </Button>
              {/* Upload to the reconstruction service is not wired yet; files stay in the browser. */}
              <Button
                variant="primary"
                size="lg"
                disabled={!plan || !video}
                onClick={() => setScreen('reading')}
              >
                Read floor plan
              </Button>
            </div>
          </motion.div>
        </div>
      </motion.section>
    </div>
  )
}
