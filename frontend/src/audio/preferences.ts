import { create } from 'zustand'

export interface AudioPreferences {
  muted: boolean
  musicEnabled: boolean
  effectsEnabled: boolean
  musicVolume: number
  effectsVolume: number
}

export const DEFAULT_AUDIO: AudioPreferences = {
  muted: false,
  musicEnabled: true,
  effectsEnabled: true,
  musicVolume: 20,
  effectsVolume: 55,
}
export const AUDIO_STORAGE_KEY = 'spaceshift.audio.v1'
type PreferenceStorage = Pick<Storage, 'getItem' | 'setItem'>

function preferences(value: unknown): AudioPreferences {
  const result = { ...DEFAULT_AUDIO }
  if (!value || typeof value !== 'object') return result
  const input = value as Record<string, unknown>
  for (const key of ['muted', 'musicEnabled', 'effectsEnabled'] as const) {
    if (typeof input[key] === 'boolean') result[key] = input[key]
  }
  for (const key of ['musicVolume', 'effectsVolume'] as const) {
    if (typeof input[key] === 'number' && Number.isFinite(input[key]))
      result[key] = Math.max(0, Math.min(100, input[key]))
  }
  return result
}

function browserStorage(): PreferenceStorage | undefined {
  try {
    return typeof window === 'undefined' ? undefined : window.localStorage
  } catch {
    return undefined
  }
}

export function createAudioPreferences(storage = browserStorage()) {
  let initial = { ...DEFAULT_AUDIO }
  try {
    initial = preferences(
      JSON.parse(storage?.getItem(AUDIO_STORAGE_KEY) ?? 'null'),
    )
  } catch {
    // Private browsing, disabled storage and old/corrupt preferences use defaults.
  }
  const store = create<
    AudioPreferences & {
      update: (patch: Partial<AudioPreferences>) => void
      toggleMute: () => void
    }
  >((set) => ({
    ...initial,
    update: (patch) => set((s) => preferences({ ...s, ...patch })),
    toggleMute: () => set((s) => ({ muted: !s.muted })),
  }))
  store.subscribe((state) => {
    try {
      storage?.setItem(AUDIO_STORAGE_KEY, JSON.stringify(preferences(state)))
    } catch {
      // Audio controls remain usable when persistence is unavailable.
    }
  })
  return store
}

export const useAudioPreferences = createAudioPreferences()
