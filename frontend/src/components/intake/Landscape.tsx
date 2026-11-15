import { useEffect, useRef, useState } from 'react'
import './ProgressScreen.css'
import {
  SHAN_SHUI_READY,
  SHAN_SHUI_RUN,
  adaptShanShui,
  loadShanShui,
  paintFallback,
} from './shanShui'

/**
 * Endless Shan Shui landscape behind the processing screens.
 *
 * Mounted once for the whole app (see App.tsx) so the engine boots while the user is
 * still on the upload screen. A fresh engine per screen needs about a second to draw,
 * which is longer than a short processing step. While hidden, the engine is paused
 * with its last frame kept, so each wait opens on a drawn landscape that carries on
 * drifting from where the previous wait left it. The procedural fallback only paints
 * while the landscape is visible and the engine isn't ready (still booting, or failed).
 */
export function Landscape({ visible }: { visible: boolean }) {
  const canvas = useRef<HTMLCanvasElement>(null)
  const frame = useRef<HTMLIFrameElement>(null)
  const [srcDoc, setSrcDoc] = useState<string>()
  const [ready, setReady] = useState(false)

  // Boot the engine once the app is idle, so it doesn't compete with first paint.
  useEffect(() => {
    let live = true
    const boot = () =>
      loadShanShui().then((src) => {
        const doc = src && adaptShanShui(src)
        if (live && doc) setSrcDoc(doc)
      })
    const idle = window.requestIdleCallback
      ? window.requestIdleCallback(boot, { timeout: 1500 })
      : window.setTimeout(boot, 300)
    const onMessage = (e: MessageEvent) => {
      if (
        e.source === frame.current?.contentWindow &&
        e.data?.type === SHAN_SHUI_READY
      )
        setReady(true)
    }
    window.addEventListener('message', onMessage)
    return () => {
      live = false
      if (window.cancelIdleCallback) window.cancelIdleCallback(idle)
      else clearTimeout(idle)
      window.removeEventListener('message', onMessage)
    }
  }, [])

  // Drift only while shown.
  useEffect(() => {
    if (!ready) return
    frame.current?.contentWindow?.postMessage(
      { type: SHAN_SHUI_RUN, run: visible },
      '*',
    )
  }, [ready, visible])

  // Fallback painting while shown and the engine isn't up yet. It stays a little
  // after the engine is ready, so the engine can fade in over it.
  const [engineIn, setEngineIn] = useState(false)
  useEffect(() => {
    if (!ready) return
    const t = setTimeout(() => setEngineIn(true), 1800)
    return () => clearTimeout(t)
  }, [ready])
  useEffect(() => {
    if (!visible || engineIn || !canvas.current) return
    return paintFallback(canvas.current)
  }, [visible, engineIn])

  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 -z-10 isolate bg-paper-base transition-opacity duration-300 ease-out"
      style={{ opacity: visible ? 1 : 0 }}
    >
      {/* Fades out as the engine fades in, so its frozen last frame never shows through. */}
      <canvas
        ref={canvas}
        className="mist-art transition-opacity duration-[1600ms]"
        style={{ opacity: ready ? 0 : 1 }}
      />
      {srcDoc && (
        <iframe
          ref={frame}
          srcDoc={srcDoc}
          sandbox="allow-scripts"
          tabIndex={-1}
          title="Endlessly generated Chinese landscape"
          className={`mist-art mist-art--engine ${ready ? 'is-ready' : ''}`}
        />
      )}
    </div>
  )
}
