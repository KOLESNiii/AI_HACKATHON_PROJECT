import type { AudioPreferences } from './preferences'
import { renderCue, type SoundCue } from './cues'

export type MusicStatus =
  'loading' | 'playing' | 'paused' | 'blocked' | 'unavailable'
export interface AudioStatus {
  supported: boolean
  music: MusicStatus
}
export interface AudioPlatform {
  createContext: () => AudioContext
  createMedia: () => HTMLAudioElement
}

const MUSIC_URL = `${import.meta.env.BASE_URL}audio/reverie.mp3`
const CROSSFADE_SECONDS = 5
const browserPlatform: AudioPlatform = {
  createContext: () => new AudioContext(),
  createMedia: () => new Audio(MUSIC_URL),
}

function ramp(param: AudioParam, value: number, now: number, seconds = 0.04) {
  // Firefox has no cancelAndHoldAtTime; pin the current value instead.
  if (typeof param.cancelAndHoldAtTime === 'function')
    param.cancelAndHoldAtTime(now)
  else {
    param.cancelScheduledValues(now)
    param.setValueAtTime(param.value, now)
  }
  param.linearRampToValueAtTime(value, now + seconds)
}

/** One app-lifetime mixer. Media streams avoid decoding the full song into memory. */
export class AudioEngine {
  private context?: AudioContext
  private master?: GainNode
  private music?: GainNode
  private effects?: GainNode
  private decks: {
    media: HTMLAudioElement
    gain: GainNode
    source: MediaElementAudioSourceNode
  }[] = []
  private buffers = new Map<SoundCue, AudioBuffer>()
  private voices = new Set<AudioBufferSourceNode>()
  private activeDeck = 0
  private crossfading = false
  private pending = new Set<HTMLAudioElement>()
  private lastRotation = -Infinity
  private disposed = false
  private hidden = false
  private playMode = false
  private musicFailed = false
  private status: AudioStatus = { supported: true, music: 'loading' }
  private timer?: ReturnType<typeof setInterval>
  private pauseTimer?: ReturnType<typeof setTimeout>
  private preferences: AudioPreferences
  private onStatus: (status: AudioStatus) => void

  constructor(
    preferences: AudioPreferences,
    onStatus: (status: AudioStatus) => void,
    platform = browserPlatform,
  ) {
    this.preferences = preferences
    this.onStatus = onStatus
    try {
      const ctx = platform.createContext()
      this.context = ctx
      this.master = ctx.createGain()
      this.music = ctx.createGain()
      this.effects = ctx.createGain()
      this.master.gain.value = 0
      this.music.gain.value = 0
      this.effects.gain.value = 0
      this.music.connect(this.master)
      this.effects.connect(this.master)
      this.master.connect(ctx.destination)
      for (const index of [0, 1]) {
        const media = platform.createMedia()
        media.preload = 'none'
        const source = ctx.createMediaElementSource(media)
        const gain = ctx.createGain()
        gain.gain.value = index === 0 ? 1 : 0
        source.connect(gain)
        gain.connect(this.music!)
        media.addEventListener('error', this.failMusic)
        media.addEventListener('ended', this.onEnded)
        this.decks.push({ media, gain, source })
      }
      ctx.addEventListener('statechange', this.onContextState)
      this.timer = setInterval(() => this.tick(), 100)
    } catch {
      this.status = { supported: false, music: 'unavailable' }
      // Dispose any partially initialized audio resources as well.
      this.dispose()
    }
    this.onStatus(this.status)
  }

  private report(music: MusicStatus) {
    if (this.disposed || this.status.music === music) return
    this.status = { ...this.status, music }
    this.onStatus(this.status)
  }

  private shouldPlayMusic() {
    const p = this.preferences
    return (
      !this.disposed &&
      !this.hidden &&
      !this.musicFailed &&
      !p.muted &&
      p.musicEnabled &&
      p.musicVolume > 0
    )
  }

  /** Called on load and from real input events; blocked playback never queues effects. */
  activate() {
    const ctx = this.context
    if (this.disposed || this.hidden || !ctx) return
    if (
      this.preferences.muted ||
      (!this.preferences.musicEnabled && !this.preferences.effectsEnabled)
    )
      return
    if (ctx.state === 'running') {
      if (this.decks[this.activeDeck]?.media.paused)
        this.update(this.preferences)
      return
    }
    // Invoke both in the gesture's synchronous stack (important on Safari).
    void ctx
      .resume()
      .then(() => {
        if (!this.disposed && !this.hidden)
          this.update(this.preferences, this.playMode)
      })
      .catch(() => {
        if (!this.disposed && !this.musicFailed) this.report('blocked')
      })
    this.update(this.preferences, this.playMode)
  }

  update(preferences: AudioPreferences, playMode = this.playMode) {
    this.preferences = preferences
    this.playMode = playMode
    const ctx = this.context
    if (!ctx || this.disposed) return
    ramp(
      this.master!.gain,
      preferences.muted || this.hidden ? 0 : 1,
      ctx.currentTime,
    )
    ramp(
      this.effects!.gain,
      preferences.effectsEnabled ? (preferences.effectsVolume / 100) * 1.95 : 0,
      ctx.currentTime,
    )
    ramp(
      this.music!.gain,
      this.shouldPlayMusic()
        ? (preferences.musicVolume / 100) * (playMode ? 0.75 : 1)
        : 0,
      ctx.currentTime,
      this.shouldPlayMusic() ? 2 : 0.04,
    )
    if (preferences.muted || this.hidden || !preferences.effectsEnabled)
      this.stopEffects(true)
    if (this.shouldPlayMusic()) {
      clearTimeout(this.pauseTimer)
      this.pauseTimer = undefined
      this.playDeck(this.activeDeck)
    } else {
      if (this.hidden || this.musicFailed) this.pauseMusic()
      else if (!this.pauseTimer) {
        // Let the gain ramp finish before pausing a stream at an arbitrary sample.
        this.pauseTimer = setTimeout(() => {
          this.pauseTimer = undefined
          if (!this.shouldPlayMusic()) this.pauseMusic()
        }, 45)
      }
      if (!this.musicFailed) this.report('paused')
    }
  }

  private playDeck(index: number, onPlaying?: () => void) {
    const deck = this.decks[index]
    if (!deck || !this.shouldPlayMusic() || this.pending.has(deck.media)) return
    if (!deck.media.paused) return
    this.pending.add(deck.media)
    void deck.media
      .play()
      .then(() => {
        this.pending.delete(deck.media)
        if (!this.shouldPlayMusic()) {
          deck.media.pause()
          return
        }
        if (this.context?.state === 'running') this.report('playing')
        onPlaying?.()
      })
      .catch((error: unknown) => {
        this.pending.delete(deck.media)
        if (this.disposed || !this.shouldPlayMusic()) return
        if (error instanceof Error && error.name === 'NotAllowedError')
          this.report('blocked')
        else if (!(error instanceof Error && error.name === 'AbortError'))
          this.failMusic()
      })
  }

  private pauseMusic() {
    // Preserve the incoming deck if a crossfade was interrupted. Do not restart the song.
    if (this.crossfading) this.activeDeck = 1 - this.activeDeck
    this.crossfading = false
    for (const [index, deck] of this.decks.entries()) {
      deck.media.pause()
      if (this.context) {
        deck.gain.gain.cancelScheduledValues(this.context.currentTime)
        deck.gain.gain.setValueAtTime(
          index === this.activeDeck ? 1 : 0,
          this.context.currentTime,
        )
      }
    }
  }

  private failMusic = () => {
    if (this.disposed) return
    this.musicFailed = true
    this.pauseMusic()
    this.report('unavailable')
  }

  private onEnded = () => {
    if (!this.shouldPlayMusic() || this.crossfading) return
    const next = 1 - this.activeDeck
    const deck = this.decks[next]
    deck.media.currentTime = 0
    this.activeDeck = next
    for (const [i, d] of this.decks.entries())
      d.gain.gain.setValueAtTime(i === next ? 1 : 0, this.context!.currentTime)
    this.playDeck(next)
  }

  private onContextState = () => {
    if (this.disposed) return
    if (this.context?.state === 'running') {
      if (this.shouldPlayMusic() && !this.decks[this.activeDeck]?.media.paused)
        this.report('playing')
    } else if (this.shouldPlayMusic()) this.report('blocked')
  }

  /** Poll media time, but schedule the actual crossfade on the audio clock. */
  tick() {
    const ctx = this.context
    const from = this.decks[this.activeDeck]
    if (!ctx || ctx.state !== 'running' || !this.shouldPlayMusic() || !from)
      return
    if (this.crossfading) {
      if (
        from.media.ended ||
        from.media.currentTime >= from.media.duration - 0.05
      ) {
        from.media.pause()
        this.activeDeck = 1 - this.activeDeck
        this.crossfading = false
      }
      return
    }
    if (from.media.paused) return
    const remaining = from.media.duration - from.media.currentTime
    if (
      !Number.isFinite(remaining) ||
      remaining > CROSSFADE_SECONDS ||
      from.media.duration < CROSSFADE_SECONDS * 2
    )
      return
    const to = this.decks[1 - this.activeDeck]
    if (this.pending.has(to.media)) return
    to.media.currentTime = 0
    const fromIndex = this.activeDeck
    this.playDeck(1 - fromIndex, () => {
      // A slow media load can complete after the outgoing deck has already ended
      // or after mute/visibility changes picked a different active deck.
      if (
        !this.shouldPlayMusic() ||
        this.crossfading ||
        this.activeDeck !== fromIndex
      )
        return
      this.crossfading = true
      const duration = Math.max(
        0.05,
        Math.min(
          CROSSFADE_SECONDS,
          from.media.duration - from.media.currentTime,
        ),
      )
      for (const [deck, incoming] of [
        [from, false],
        [to, true],
      ] as const) {
        const curve = Float32Array.from({ length: 65 }, (_, i) =>
          incoming
            ? Math.sin(((i / 64) * Math.PI) / 2)
            : Math.cos(((i / 64) * Math.PI) / 2),
        )
        deck.gain.gain.cancelScheduledValues(ctx.currentTime)
        deck.gain.gain.setValueCurveAtTime(curve, ctx.currentTime, duration)
      }
    })
  }

  setHidden(hidden: boolean) {
    this.hidden = hidden
    this.update(this.preferences)
    if (hidden) void this.context?.suspend().catch(() => {})
    else this.activate()
  }

  play(cue: SoundCue) {
    const ctx = this.context
    const p = this.preferences
    if (
      !ctx ||
      this.disposed ||
      this.hidden ||
      ctx.state !== 'running' ||
      p.muted ||
      !p.effectsEnabled ||
      p.effectsVolume <= 0 ||
      this.voices.size >= 6
    )
      return
    if (cue === 'rotate' && ctx.currentTime - this.lastRotation < 0.1) return
    if (cue === 'rotate') this.lastRotation = ctx.currentTime
    let buffer = this.buffers.get(cue)
    if (!buffer) {
      const samples = renderCue(cue, ctx.sampleRate)
      buffer = ctx.createBuffer(1, samples.length, ctx.sampleRate)
      buffer.copyToChannel(samples as Float32Array<ArrayBuffer>, 0)
      this.buffers.set(cue, buffer)
    }
    const source = ctx.createBufferSource()
    source.buffer = buffer
    source.playbackRate.value = 0.97 + Math.random() * 0.06
    source.connect(this.effects!)
    this.voices.add(source)
    source.onended = () => {
      this.voices.delete(source)
      source.disconnect()
    }
    source.start()
  }

  private stopEffects(fade = false) {
    for (const voice of this.voices) {
      voice.stop(fade ? this.context!.currentTime + 0.04 : 0)
      if (!fade) voice.disconnect()
    }
    // Fading voices still count toward the cap until their ended event fires.
    if (!fade) this.voices.clear()
  }

  dispose() {
    this.disposed = true
    clearInterval(this.timer)
    clearTimeout(this.pauseTimer)
    this.stopEffects()
    for (const { media, gain, source } of this.decks) {
      media.removeEventListener('error', this.failMusic)
      media.removeEventListener('ended', this.onEnded)
      media.pause()
      media.removeAttribute('src')
      media.load()
      gain.disconnect()
      source.disconnect()
    }
    this.context?.removeEventListener('statechange', this.onContextState)
    void this.context?.close().catch(() => {})
  }
}
