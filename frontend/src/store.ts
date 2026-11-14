import { create } from 'zustand'

/** Intake flow; the room editor arrives in a later PR. */
export type Screen = 'upload' | 'reading' | 'floorplan' | 'building' | 'editor'

interface State {
  screen: Screen
  segmentId: string | null
  setScreen: (s: Screen) => void
  selectSegment: (id: string | null) => void
  openRoom: () => void
}

export const useStore = create<State>((set) => ({
  screen: 'upload',
  segmentId: null,
  setScreen: (screen) => set({ screen }),
  selectSegment: (segmentId) => set({ segmentId }),
  openRoom: () => set({ screen: 'building' }),
}))
