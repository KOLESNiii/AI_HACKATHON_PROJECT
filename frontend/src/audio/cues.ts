export type SoundCue =
  | 'select'
  | 'place'
  | 'rotate'
  | 'snap'
  | 'add'
  | 'delete'
  | 'apply'
  | 'ready'
  | 'transition'
  | 'reject'

const listeners = new Set<(cue: SoundCue) => void>()

/** Semantic actions stay independent of browser audio and never queue old sounds. */
export function playCue(cue: SoundCue) {
  for (const listener of listeners) listener(cue)
}

export function onSoundCue(listener: (cue: SoundCue) => void) {
  listeners.add(listener)
  return () => {
    listeners.delete(listener)
  }
}

// frequency, delay, duration, level, noise amount. Original, synthesized effects.
type PartialTone = readonly [number, number, number, number, number]
const tones: Record<SoundCue, readonly PartialTone[]> = {
  select: [[760, 0, 0.065, 0.3, 0.12]],
  place: [
    [145, 0, 0.16, 0.45, 0.08],
    [310, 0, 0.1, 0.12, 0],
  ],
  rotate: [[1050, 0, 0.055, 0.22, 0.1]],
  snap: [
    [820, 0, 0.055, 0.26, 0.1],
    [1100, 0.055, 0.065, 0.23, 0.06],
  ],
  add: [
    [145, 0, 0.16, 0.38, 0.05],
    [440, 0.025, 0.17, 0.12, 0],
  ],
  delete: [[210, 0, 0.14, 0.12, 0.65]],
  apply: [
    [440, 0, 0.45, 0.16, 0],
    [660, 0.12, 0.5, 0.13, 0],
  ],
  ready: [
    [440, 0, 0.65, 0.14, 0],
    [660, 0.15, 0.7, 0.11, 0],
  ],
  transition: [[180, 0, 0.25, 0.05, 0.75]],
  reject: [[130, 0, 0.12, 0.24, 0.05]],
}

/** Render once per cue; warmed resonances and filtered noise avoid sharp transients. */
export function renderCue(cue: SoundCue, sampleRate: number): Float32Array {
  const layers = tones[cue]
  const duration = Math.max(
    ...layers.map(([, delay, length]) => delay + length),
  )
  const samples = new Float32Array(Math.ceil(duration * sampleRate))
  let seed = 7381
  for (const [hz, delay, length, level, noise] of layers) {
    let filtered = 0
    const start = Math.round(delay * sampleRate)
    for (let i = 0; i < Math.floor(length * sampleRate); i++) {
      const t = i / sampleRate
      seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0
      filtered += ((seed / 0xffffffff) * 2 - 1 - filtered) * 0.12
      const envelope =
        Math.min(t / 0.006, 1) *
        Math.exp((-6 * t) / length) *
        Math.min((length - t) / 0.012, 1)
      const tone =
        Math.sin(2 * Math.PI * hz * t) +
        0.18 * Math.sin(2 * Math.PI * hz * 2.73 * t)
      samples[start + i] +=
        level * envelope * (tone * (1 - noise) + filtered * noise)
    }
  }
  return samples
}
