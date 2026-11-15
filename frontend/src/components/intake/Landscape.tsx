/**
 * Endless Shan Shui landscape behind the front page and the processing screens.
 *
 * Each landscape is a pre-rendered panorama that wraps seamlessly (made by
 * scripts/generate-landscapes.ts from Lingdong Huang's Shan Shui Inf, MIT). Two
 * copies sit side by side and slide by one image width forever with a CSS transform
 * animation, so the compositor does all the work and nothing is generated at runtime.
 *
 * Mounted once for the whole app (see App.tsx) so every panorama is loaded before
 * it's needed. Hidden panoramas pause, so each one resumes where it left off.
 */
import { useState } from 'react'
import './ProgressScreen.css'

const LANDSCAPES = [1, 2, 3, 4].map(
  (n) => `${import.meta.env.BASE_URL}landscapes/landscape-${n}.webp`,
)

// Drift at the engine's own pace: 36 world units/s, rendered 1200px per 800/1.142
// units of height. Loops differ in length, so each one's duration follows its width.
const IMAGE_PX_PER_S = 36 * (1200 / (800 / 1.142))

/**
 * Where each panorama starts, as a fraction of its loop. Its wrap crossfade sits in
 * the first ~12%, so every landscape opens on clean scenery past it.
 */
const startAt = (i: number) => 0.15 + 0.12 * i

export function Landscape({ index }: { index: number | null }) {
  // Loop durations in seconds, known once each image has loaded.
  const [loops, setLoops] = useState<(number | null)[]>(() =>
    LANDSCAPES.map(() => null),
  )

  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 -z-10 overflow-hidden bg-paper-base transition-opacity duration-300 ease-out"
      style={{ opacity: index == null ? 0 : 1 }}
    >
      {LANDSCAPES.map((src, i) => {
        const active = i === index
        const loop = loops[i]
        return (
          <div
            key={src}
            className="absolute inset-0 transition-opacity duration-700 ease-out"
            style={{ opacity: active && loop ? 1 : 0 }}
          >
            <div
              className="landscape-strip flex h-full w-max will-change-transform"
              style={
                loop
                  ? {
                      animation: `landscape-drift ${loop}s linear ${-startAt(i) * loop}s infinite`,
                      animationPlayState: active ? 'running' : 'paused',
                    }
                  : undefined
              }
            >
              <img
                src={src}
                alt=""
                className="h-full max-w-none"
                onLoad={(e) => {
                  const s = e.currentTarget.naturalWidth / IMAGE_PX_PER_S
                  setLoops((l) => l.map((v, j) => (j === i ? s : v)))
                }}
              />
              <img src={src} alt="" className="h-full max-w-none" />
            </div>
          </div>
        )
      })}
    </div>
  )
}
