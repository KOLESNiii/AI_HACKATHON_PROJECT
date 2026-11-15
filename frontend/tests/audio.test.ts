import { afterEach, describe, expect, test } from 'bun:test'
import {
  AudioEngine,
  type AudioPlatform,
  type AudioStatus,
} from '../src/audio/engine'
import { onSoundCue, renderCue, type SoundCue } from '../src/audio/cues'
import {
  AUDIO_STORAGE_KEY,
  createAudioPreferences,
  DEFAULT_AUDIO,
} from '../src/audio/preferences'
import { useStore } from '../src/store'
import { handleItemKey } from '../src/components/editor/keyboard'

describe('audio preferences', () => {
  test('defaults on and restores independently muted channels and volumes', () => {
    const values = new Map<string, string>()
    const storage = {
      getItem: (key: string) => values.get(key) ?? null,
      setItem: (key: string, value: string) => {
        values.set(key, value)
      },
    }
    const prefs = createAudioPreferences(storage)
    expect(prefs.getState()).toMatchObject(DEFAULT_AUDIO)
    prefs
      .getState()
      .update({ musicVolume: 34, effectsVolume: 71, effectsEnabled: false })
    prefs.getState().toggleMute()
    const restored = createAudioPreferences(storage)
    expect(restored.getState()).toMatchObject({
      muted: true,
      musicVolume: 34,
      effectsVolume: 71,
      effectsEnabled: false,
    })
    restored.getState().toggleMute()
    expect(restored.getState()).toMatchObject({
      muted: false,
      musicVolume: 34,
      effectsVolume: 71,
      effectsEnabled: false,
    })
    expect(JSON.parse(values.get(AUDIO_STORAGE_KEY)!)).not.toHaveProperty(
      'update',
    )
  })

  test('malformed, unavailable and out-of-range storage never break controls', () => {
    for (const raw of [
      'broken json',
      'null',
      '[]',
      '{"muted":"yes","musicVolume":null}',
    ]) {
      expect(
        createAudioPreferences({
          getItem: () => raw,
          setItem: () => {},
        }).getState(),
      ).toMatchObject(DEFAULT_AUDIO)
    }
    const prefs = createAudioPreferences({
      getItem: () => {
        throw Error('denied')
      },
      setItem: () => {
        throw Error('full')
      },
    })
    expect(() => prefs.getState().toggleMute()).not.toThrow()
    prefs.getState().update({ musicVolume: -20, effectsVolume: 120 })
    expect(prefs.getState()).toMatchObject({
      musicVolume: 0,
      effectsVolume: 100,
    })
    prefs.getState().update({ effectsVolume: NaN })
    expect(prefs.getState().effectsVolume).toBe(DEFAULT_AUDIO.effectsVolume)
  })
})

class Param {
  value = 1
  curves: Float32Array[] = []
  cancelAndHoldAtTime() {}
  cancelScheduledValues() {}
  linearRampToValueAtTime(value: number) {
    this.value = value
  }
  setValueAtTime(value: number) {
    this.value = value
  }
  setValueCurveAtTime(curve: Float32Array) {
    this.curves.push(curve)
  }
}
class FakeNode {
  gain = new Param()
  playbackRate = new Param()
  buffer: unknown
  onended?: () => void
  started = false
  stopped = false
  connect() {}
  disconnect() {}
  start() {
    this.started = true
  }
  stop() {
    this.stopped = true
  }
}
class Media extends EventTarget {
  paused = true
  ended = false
  duration = 220.5
  currentTime = 0
  preload = ''
  calls = 0
  error?: Error
  pending?: Promise<void>
  play() {
    this.calls++
    if (this.error) return Promise.reject(this.error)
    if (this.pending)
      return this.pending.then(() => {
        this.paused = false
      })
    this.paused = false
    return Promise.resolve()
  }
  pause() {
    this.paused = true
  }
  removeAttribute() {}
  load() {}
}
class Context extends EventTarget {
  currentTime = 0
  sampleRate = 44100
  state = 'running'
  destination = new FakeNode()
  sources: FakeNode[] = []
  gains: FakeNode[] = []
  createGain() {
    const node = new FakeNode()
    this.gains.push(node)
    return node
  }
  createMediaElementSource() {
    return new FakeNode()
  }
  createBuffer(_channels: number, length: number) {
    return { length, copyToChannel() {} }
  }
  createBufferSource() {
    const node = new FakeNode()
    this.sources.push(node)
    return node
  }
  resume() {
    this.state = 'running'
    return Promise.resolve()
  }
  suspend() {
    this.state = 'suspended'
    return Promise.resolve()
  }
  close() {
    this.state = 'closed'
    return Promise.resolve()
  }
}

const engines: AudioEngine[] = []
afterEach(() => {
  engines.splice(0).forEach((engine) => engine.dispose())
})

function fixture() {
  const context = new Context()
  const media = [new Media(), new Media()]
  const statuses: AudioStatus[] = []
  let index = 0
  const platform = {
    createContext: () => context,
    createMedia: () => media[index++],
  } as unknown as AudioPlatform
  const engine = new AudioEngine(
    { ...DEFAULT_AUDIO },
    (status) => statuses.push(status),
    platform,
  )
  engines.push(engine)
  return { engine, context, media, statuses }
}
const settle = async () => {
  await Promise.resolve()
  await Promise.resolve()
  await Promise.resolve()
}

describe('audio mixer lifecycle', () => {
  test('rate limits rotation, caps voices, and stops effects immediately on mute', () => {
    const { engine, context } = fixture()
    engine.update(DEFAULT_AUDIO)
    engine.play('rotate')
    context.currentTime = 0.05
    engine.play('rotate')
    expect(context.sources).toHaveLength(1)
    context.currentTime = 0.11
    engine.play('rotate')
    for (let i = 0; i < 10; i++) engine.play('place')
    expect(context.sources).toHaveLength(6)
    engine.update({ ...DEFAULT_AUDIO, muted: true })
    expect(context.sources.every((voice) => voice.stopped)).toBe(true)
    engine.play('place')
    expect(context.sources).toHaveLength(6)
    engine.update(DEFAULT_AUDIO)
    engine.play('place')
    expect(context.sources).toHaveLength(6)
    context.currentTime += 0.05
    for (const voice of context.sources) voice.onended?.()
    engine.play('place')
    expect(context.sources).toHaveLength(7)
  })

  test('drops blocked/hidden/disabled effects rather than replaying them', () => {
    const { engine, context } = fixture()
    context.state = 'suspended'
    engine.play('place')
    context.state = 'running'
    expect(context.sources).toHaveLength(0)
    engine.setHidden(true)
    engine.play('place')
    engine.setHidden(false)
    engine.update({ ...DEFAULT_AUDIO, effectsEnabled: false })
    engine.play('place')
    engine.update({ ...DEFAULT_AUDIO, effectsVolume: 0 })
    engine.play('place')
    expect(context.sources).toHaveLength(0)
  })

  test('autoplay rejection is recoverable and media failure keeps effects usable', async () => {
    const { engine, media, context, statuses } = fixture()
    media[0].error = new DOMException('gesture required', 'NotAllowedError')
    engine.activate()
    await settle()
    expect(statuses.at(-1)?.music).toBe('blocked')
    media[0].error = undefined
    engine.activate()
    await settle()
    expect(statuses.at(-1)?.music).toBe('playing')
    media[0].dispatchEvent(new Event('error'))
    expect(statuses.at(-1)?.music).toBe('unavailable')
    engine.play('place')
    expect(context.sources).toHaveLength(1)
    const attempts = media[0].calls
    engine.activate()
    await settle()
    expect(media[0].calls).toBe(attempts)
  })

  test('pauses hidden tabs, resumes position, and respects mute on return', async () => {
    const { engine, media } = fixture()
    engine.activate()
    await settle()
    media[0].currentTime = 82
    engine.setHidden(true)
    expect(media.every((deck) => deck.paused)).toBe(true)
    engine.setHidden(false)
    await settle()
    expect(media[0].currentTime).toBe(82)
    expect(media[0].paused).toBe(false)
    engine.update({ ...DEFAULT_AUDIO, muted: true })
    engine.setHidden(true)
    engine.setHidden(false)
    await settle()
    expect(media.every((deck) => deck.paused)).toBe(true)
  })

  test('crossfades twice, including when an ended deck is already paused', async () => {
    const { engine, media, context } = fixture()
    engine.activate()
    await settle()
    for (const [from, to] of [
      [0, 1],
      [1, 0],
    ]) {
      media[from].currentTime = media[from].duration - 4.9
      engine.tick()
      await settle()
      expect(media[to].paused).toBe(false)
      media[from].ended = true
      media[from].paused = true
      media[from].currentTime = media[from].duration
      engine.tick()
      media[from].ended = false
    }
    expect(context.gains[3].gain.curves).toHaveLength(2)
    expect(context.gains[4].gain.curves).toHaveLength(2)
    expect(media[0].paused).toBe(false)
  })

  test('late playback resolution after mute or disposal cannot restart music', async () => {
    const { engine, media } = fixture()
    let resolve!: () => void
    media[0].pending = new Promise<void>((done) => {
      resolve = done
    })
    engine.activate()
    engine.update({ ...DEFAULT_AUDIO, muted: true })
    resolve()
    await settle()
    expect(media[0].paused).toBe(true)
    engine.dispose()
    engine.activate()
    await settle()
    expect(media.every((deck) => deck.paused)).toBe(true)
  })

  test('a delayed incoming track starts normally if the outgoing track ends before its crossfade', async () => {
    const { engine, media, context } = fixture()
    engine.activate()
    await settle()
    let resolve!: () => void
    media[1].pending = new Promise<void>((done) => {
      resolve = done
    })
    media[0].currentTime = media[0].duration - 4
    engine.tick()
    media[0].currentTime = media[0].duration
    media[0].ended = true
    media[0].paused = true
    media[0].dispatchEvent(new Event('ended'))
    resolve()
    await settle()
    expect(media[1].paused).toBe(false)
    expect(context.gains[3].gain.curves).toHaveLength(0)
    expect(context.gains[4].gain.value).toBe(1)
  })

  test('unsupported browser audio does not throw', () => {
    const statuses: AudioStatus[] = []
    const engine = new AudioEngine(DEFAULT_AUDIO, (s) => statuses.push(s), {
      createContext: () => {
        throw Error('unsupported')
      },
      createMedia: () => {
        throw Error('unreachable')
      },
    })
    engines.push(engine)
    expect(() => {
      engine.activate()
      engine.play('place')
      engine.update(DEFAULT_AUDIO)
    }).not.toThrow()
    expect(statuses.at(-1)).toEqual({ supported: false, music: 'unavailable' })
  })
})

describe('semantic editor cues', () => {
  const initial = useStore.getState()
  afterEach(() => useStore.setState(initial))

  test('keyboard and button rotations, selection and deletion produce one cue per successful action', () => {
    const scene = structuredClone(initial.scene)
    scene.floor_polygon = [
      { x: 0, z: 0 },
      { x: 10, z: 0 },
      { x: 10, z: 10 },
      { x: 0, z: 10 },
    ]
    scene.furniture = [
      {
        ...scene.furniture[0],
        id: 'item',
        is_fixed: false,
        pose: { x: 5, z: 5, yaw_deg: 0 },
      },
    ]
    useStore.setState({ ...initial, scene })
    const cues: SoundCue[] = []
    const stop = onSoundCue((cue) => cues.push(cue))
    try {
      const s = useStore.getState()
      s.select('item')
      s.select('item')
      s.rotateItem('item', 90)
      handleItemKey({ key: 'e', preventDefault() {} } as KeyboardEvent)
      s.resetRotation('item') // Already reset by E.
      s.rotateItem('missing', 90)
      s.setTab('stats')
      s.setTab('stats')
      s.deleteItem('item')
      s.deleteItem('item')
      expect(cues).toEqual(['select', 'rotate', 'rotate', 'select', 'delete'])
    } finally {
      stop()
    }
  })

  test('fixed items, cancelled edits and live pose updates stay quiet', () => {
    const scene = structuredClone(initial.scene)
    scene.furniture = [{ ...scene.furniture[0], id: 'fixed', is_fixed: true }]
    useStore.setState({ ...initial, scene })
    const cues: SoundCue[] = []
    const stop = onSoundCue((cue) => cues.push(cue))
    try {
      const s = useStore.getState()
      s.select('fixed')
      s.rotateItem('fixed', 90)
      s.snapItem('fixed')
      s.deleteItem('fixed')
      s.setPose('fixed', { x: 3 })
      s.commitEdit(null)
      s.cancelHumanPlacement()
      expect(cues).toEqual([])
      s.commitEdit('rotate')
      expect(cues).toEqual(['rotate'])
    } finally {
      stop()
    }
  })
})

test('procedural cues have softened edges, finite samples and ample headroom', () => {
  for (const cue of [
    'select',
    'place',
    'rotate',
    'snap',
    'add',
    'delete',
    'apply',
    'ready',
    'transition',
    'reject',
  ] as SoundCue[]) {
    const samples = renderCue(cue, 44100)
    expect(samples.length).toBeLessThanOrEqual(44100)
    expect(samples[0]).toBe(0)
    expect(Math.abs(samples.at(-1)!)).toBeLessThan(0.001)
    expect(samples.every((v) => Number.isFinite(v) && Math.abs(v) < 0.7)).toBe(
      true,
    )
    expect(samples.some((v) => Math.abs(v) > 0.001)).toBe(true)
  }
})
