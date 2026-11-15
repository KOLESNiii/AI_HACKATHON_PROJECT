import { motion } from 'framer-motion'
import {
  useEffect,
  useMemo,
  useState,
  type DragEvent,
  type ReactNode,
} from 'react'
import { MAX_FLOOR_PLAN_IMAGES, MAX_ROOM_VIDEOS } from '../../lib/contracts'
import { addFiles, isPlanImage, isVideo } from '../../lib/uploadFiles'
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
  files,
  max,
  matches,
  kind,
  onFiles,
}: {
  step: string
  title: string
  hint: string
  accept: string
  glyph: ReactNode
  files: File[]
  max: number
  matches: (f: File) => boolean
  kind: string
  onFiles: (files: File[]) => void
}) {
  const [over, setOver] = useState(false)
  const [note, setNote] = useState<string | null>(null)
  const first = files[0] ?? null
  const url = usePreview(first)
  const preview = first?.type.startsWith('image/')
    ? 'image'
    : first?.type.startsWith('video/')
      ? 'video'
      : 'other'
  const add = (incoming: Iterable<File>) => {
    const { files: next, skipped } = addFiles(files, incoming, max, matches)
    setNote(
      skipped
        ? `${skipped} file${skipped === 1 ? '' : 's'} skipped: ${kind} only, ${max} at most`
        : null,
    )
    onFiles(next)
  }
  const remove = (i: number) => {
    setNote(null)
    onFiles(files.filter((_, j) => j !== i))
  }
  return (
    <label
      onDragOver={(e) => {
        e.preventDefault()
        setOver(true)
      }}
      onDragLeave={() => setOver(false)}
      onDrop={(e: DragEvent) => {
        e.preventDefault()
        setOver(false)
        add(e.dataTransfer.files)
      }}
      className={`scroll-panel drop-card group relative flex min-h-[230px] w-full max-w-[300px] cursor-pointer flex-col items-center justify-center gap-2 overflow-hidden px-6 py-4 text-center transition-colors sm:w-[300px] ${
        over ? 'is-over bg-seal-vermilion/6' : 'hover:bg-paper-card'
      }`}
    >
      <input
        type="file"
        accept={accept}
        multiple
        className="sr-only"
        onChange={(e) => {
          if (e.target.files) add(e.target.files)
          // Let the same file be chosen again after removing it.
          e.target.value = ''
        }}
      />
      <span className="mono absolute top-4 left-4 text-[10px] tracking-[0.24em] text-ink-mist uppercase">
        {step}
      </span>

      {files.length ? (
        <>
          <span className="seal-stamp" aria-hidden="true">
            已收
          </span>
          {url && preview === 'image' && (
            <img
              src={url}
              alt=""
              className="mt-6 h-[90px] w-full object-contain mix-blend-multiply"
            />
          )}
          {url && preview === 'video' && (
            <video
              src={`${url}#t=0.1`}
              muted
              playsInline
              preload="metadata"
              className="mt-6 h-[90px] w-full rounded-[2px] object-contain"
            />
          )}
          {preview === 'other' && (
            <span className="mt-4 text-ink-medium">{glyph}</span>
          )}
          <ul className="flex w-full flex-col gap-1">
            {files.map((f, i) => (
              <li
                key={`${f.name}-${f.size}-${f.lastModified}`}
                className="flex items-center gap-2"
              >
                <span className="mono min-w-0 flex-1 truncate text-left text-[11px] text-accent-celadon">
                  {f.name}
                </span>
                <button
                  type="button"
                  aria-label={`Remove ${f.name}`}
                  onClick={(e) => {
                    // Inside the label: don't open the file browser.
                    e.preventDefault()
                    e.stopPropagation()
                    remove(i)
                  }}
                  className="mono cursor-pointer px-1 text-[13px] leading-none text-ink-mist hover:text-seal-vermilion"
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
          <span className="mono text-[10px] tracking-[0.18em] text-ink-mist uppercase opacity-0 transition-opacity group-hover:opacity-100">
            {files.length < max
              ? `Click or drop to add (${files.length}/${max})`
              : `${max}/${max} · remove one to add another`}
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
            Drop files or click to browse
          </span>
          <span className="mono text-[10px] text-ink-mist">{hint}</span>
        </>
      )}
      {note && (
        <span role="status" className="text-[11px] text-seal-vermilion-dark">
          {note}
        </span>
      )}
    </label>
  )
}

export function UploadScreen() {
  const plans = useStore((s) => s.uploadPlans)
  const videos = useStore((s) => s.uploadVideos)
  const setUploadFiles = useStore((s) => s.setUploadFiles)
  const submitUpload = useStore((s) => s.submitUpload)
  const chooseDemoHome = useStore((s) => s.chooseDemoHome)
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
            A floor plan to read, and walkthroughs to furnish it.
          </motion.p>

          <motion.div
            variants={rise}
            className="mt-8 flex w-full flex-col items-center justify-center gap-5 sm:flex-row sm:items-stretch"
          >
            <DropCard
              step="壹 · Floor plan"
              title="Floor plan images"
              hint={`PNG · JPG · up to ${MAX_FLOOR_PLAN_IMAGES}`}
              accept="image/png,image/jpeg"
              glyph={PlanGlyph}
              files={plans}
              max={MAX_FLOOR_PLAN_IMAGES}
              matches={isPlanImage}
              kind="PNG or JPG images"
              onFiles={(f) => setUploadFiles('plans', f)}
            />
            <DropCard
              step="贰 · Walkthrough · optional"
              title="Walkthrough videos"
              hint={`MP4 · MOV · up to ${MAX_ROOM_VIDEOS}`}
              accept="video/*"
              glyph={VideoGlyph}
              files={videos}
              max={MAX_ROOM_VIDEOS}
              matches={isVideo}
              kind="videos"
              onFiles={(f) => setUploadFiles('videos', f)}
            />
          </motion.div>

          <motion.div variants={rise} className="mt-7 w-full max-w-[620px]">
            <hr className="ink-divider mb-5" />
            <div className="flex flex-wrap items-center justify-between gap-3">
              <Button size="lg" onClick={chooseDemoHome}>
                Skip with demo home
              </Button>
              <Button
                variant="primary"
                size="lg"
                disabled={!plans.length}
                onClick={() => void submitUpload()}
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
