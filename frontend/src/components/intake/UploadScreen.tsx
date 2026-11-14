import { useState, type DragEvent } from 'react'
import { useStore } from '../../store'
import { Button, Panel } from '../ui'

function DropZone({
  title,
  hint,
  accept,
  file,
  onFile,
}: {
  title: string
  hint: string
  accept: string
  file: File | null
  onFile: (f: File) => void
}) {
  const [over, setOver] = useState(false)
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
      className={`flex h-[180px] w-[260px] cursor-pointer flex-col items-center justify-center gap-1.5 rounded-[4px] border-[1.5px] border-dashed px-4 text-center transition-colors ${
        over
          ? 'border-seal-vermilion bg-seal-vermilion/6'
          : 'border-ink-medium/50 bg-ink-primary/6 hover:bg-ink-primary/10'
      }`}
    >
      <input
        type="file"
        accept={accept}
        className="hidden"
        onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])}
      />
      <span className="text-[13px] font-medium text-ink-primary">{title}</span>
      {file ? (
        <span className="mono max-w-full truncate text-[11px] text-accent-celadon">
          {file.name}
        </span>
      ) : (
        <span className="text-[11px] font-medium text-ink-medium">
          Drop file or click to browse
        </span>
      )}
      <span className="mono text-[11px] text-ink-medium">{hint}</span>
    </label>
  )
}

export function UploadScreen() {
  const setScreen = useStore((s) => s.setScreen)
  const [plan, setPlan] = useState<File | null>(null)
  const [video, setVideo] = useState<File | null>(null)
  return (
    <div className="grid h-full place-items-center">
      <Panel className="flex flex-col items-end gap-4 p-6">
        <div className="flex gap-4">
          <DropZone
            title="Floor plan image"
            hint="PNG · JPG · PDF"
            accept="image/*,application/pdf"
            file={plan}
            onFile={setPlan}
          />
          <DropZone
            title="Walkthrough video"
            hint="MP4 · MOV"
            accept="video/*"
            file={video}
            onFile={setVideo}
          />
        </div>
        <div className="flex w-full items-center justify-between gap-4">
          <button
            type="button"
            className="cursor-pointer text-[11px] font-medium text-ink-mist underline-offset-2 hover:underline"
            onClick={() => setScreen('reading')}
          >
            Skip with demo home
          </button>
          {/* Upload to the reconstruction service is not wired yet; files stay in the browser. */}
          <Button
            variant="primary"
            size="lg"
            disabled={!plan || !video}
            onClick={() => setScreen('reading')}
          >
            Build room
          </Button>
        </div>
      </Panel>
    </div>
  )
}
