import { create } from 'zustand'
import { playCue, type SoundCue } from './audio/cues'
import type { CatalogItem } from './data/catalog'
import { roomScene } from './data/demoHome'
import {
  demoPlan,
  findPlanRoom,
  planFromParsed,
  type HomePlan,
} from './data/homePlan'
import type {
  AuditReport,
  FurnitureItem,
  LayoutProgress,
  Pose2D,
  RoomScene,
} from './lib/contracts'
import { MAX_LAYOUT_INSTRUCTION_CHARS } from './lib/contracts'
import {
  readProposal,
  streamAgentMessage,
  type EditorProposal,
} from './lib/agent'
import { errorMessage } from './lib/api'
import { uploadFloorPlan } from './lib/floorPlan'
import { layoutChanges, matchingAudit } from './lib/layoutDiff'
import { fetchAudit, fetchRoom, type FurnitureProgress } from './lib/spatial'
import {
  fetchFengShui,
  fetchFengShuiScore,
  type FengShuiResult,
  type FengShuiScore,
  type ScoreStatus,
} from './lib/fengShui'
import {
  initialRoomHistory,
  editRoomLayout,
  recordRoomVersion,
  type RoomVersion,
} from './lib/roomVersions'
import { bounds, clampToFloor, fitYaw, snapToNearestWall } from './lib/geometry'
import type { Pt } from './lib/geometry'
import { canStand, humanPoseAt } from './lib/walk'
import {
  freshItemId,
  importKey,
  loadLibrary,
  placeItem,
  saveLibrary,
  sharedImport,
  type LibraryEntry,
  type ProductOption,
} from './lib/products'
import { SpatialError } from './lib/spatial'
import {
  DEFAULT_PLAY_LIGHTING,
  type PlayLightingSettings,
} from './lib/lighting'

export type Screen =
  'home' | 'upload' | 'reading' | 'floorplan' | 'building' | 'editor'
export type Tab = 'chat' | 'stats' | 'library'
export type EditorMode = 'edit' | 'play'

export interface ChatMessage {
  role: 'user' | 'assistant'
  text: string
  proposal?: EditorProposal
  /** Immutable scene snapshot used to calculate and accept this proposal's diff. */
  baseScene?: RoomScene
  roomSession?: number
  baseVersionId?: string
  baseVersionLabel?: string
  baselineAudit?: AuditReport
  applied?: boolean
  rejected?: boolean
  progress?: LayoutProgress[]
  /** Real products found online, each offered with an Add to scene button. */
  products?: ProductOption[]
}
/** A room's working state, kept for the session so reopening it resumes where you left off. */
export interface SavedRoom {
  scene: RoomScene
  versions: RoomVersion[]
  currentVersionId: string
  hasUnsavedChanges: boolean
  chat: ChatMessage[]
  human: Pose2D | null
  playLighting: PlayLightingSettings
  roomWarnings: string[]
  /** Video furniture still being extracted when the room was left. */
  furnitureProgress: FurnitureProgress | null
}
export interface Toast {
  id: number
  text: string
}

export type PlanStatus = 'idle' | 'loading' | 'ready' | 'error'
export type UploadKind = 'plans' | 'videos'

interface State {
  screen: Screen
  /** The home in the room picker: the demo house, or the plan the user uploaded. */
  home: HomePlan
  /** Files chosen on the upload screen, kept so Back and Retry don't lose them. */
  uploadPlans: File[]
  uploadVideos: File[]
  /** The floor-plan upload and parse (`POST /floor-plans`). */
  planStatus: PlanStatus
  planError: string | null
  planAbort: AbortController | null
  /** A room of `home`, by `room_id`. */
  segmentId: string | null
  scene: RoomScene
  /** Incremented when a room is (re)opened; async results from older sessions are dropped. */
  roomSession: number
  versions: RoomVersion[]
  currentVersionId: string
  hasUnsavedChanges: boolean
  selectedId: string | null
  /** True while an item is being dragged or rotated. */
  interacting: boolean
  tab: Tab
  mode: EditorMode
  playPhase: 'walking' | 'lighting'
  playLighting: PlayLightingSettings
  /** Local preview actor, never included in RoomScene or its revision. */
  human: Pose2D | null
  placingHuman: boolean
  humanPreview: Pose2D | null
  roomLoading: boolean
  /** True once this room's canonical scene was loaded (or the local fallback kept). */
  roomReady: boolean
  /** Rooms opened this session, keyed by `roomKey`; restored instead of reloaded. */
  rooms: Record<string, SavedRoom>
  /** `<planId|demo>/<scene_id>` of the open room; null before any room is opened. */
  roomKey: string | null
  roomWarnings: string[]
  /** Furniture being extracted from the plan's videos; null when none is. */
  furnitureProgress: FurnitureProgress | null
  roomAbort: AbortController | null
  /** Audit of the current committed scene only; candidate reports stay in chat. */
  audit: AuditReport | null
  auditStatus: 'idle' | 'loading' | 'ready' | 'error'
  auditError: string | null
  auditAbort: AbortController | null
  /** Advisory `/feng-shui` assessment of the committed scene; cleared when the scene changes. */
  fengShui: FengShuiResult | null
  fengShuiStatus: 'idle' | 'loading' | 'ready' | 'error'
  fengShuiError: string | null
  fengShuiAbort: AbortController | null
  fengShuiScore: FengShuiScore | null
  fengShuiScoreStatus: ScoreStatus
  fengShuiScoreError: string | null
  fengShuiScoreAbort: AbortController | null
  chat: ChatMessage[]
  agentBusy: boolean
  agentProgress: LayoutProgress[]
  /** In-flight agent request, aborted when the room is reopened. */
  agentAbort: AbortController | null
  toasts: Toast[]
  /** Products imported through the reconstruction pipeline, newest first. */
  library: LibraryEntry[]
  /** Product URLs currently being imported or placed. */
  adding: string[]
  /** Background imports of found products, keyed by `importKey(product, scene_id)`. */
  prefetch: Record<string, 'pending' | 'ready'>

  setScreen: (s: Screen) => void
  setUploadFiles: (kind: UploadKind, files: File[]) => void
  /** Uploads the chosen files and parses the plan; the reading screen waits on it. */
  submitUpload: () => Promise<void>
  /** Stops a running upload and returns to the upload screen. */
  cancelUpload: () => void
  /** Skips the upload: the room picker shows the demo house. */
  chooseDemoHome: () => void
  selectSegment: (id: string | null) => void
  openRoom: () => void
  selectVersion: (id: string) => void
  saveVersion: () => void
  discardChanges: () => void
  select: (id: string | null) => void
  setInteracting: (b: boolean) => void
  /** Live pose update while dragging/rotating; does not bump the revision. */
  setPose: (id: string, pose: Partial<Pose2D>) => void
  /** Ends a drag/rotate: bumps the revision once; null keeps cancelled/unchanged gestures silent. */
  commitEdit: (cue?: 'place' | 'rotate' | null) => void
  snapItem: (id: string) => void
  rotateItem: (id: string, degrees: number) => void
  /** Turns an item back to yaw 0 (front facing +Z), kept inside the floor. */
  resetRotation: (id: string) => void
  deleteItem: (id: string) => void
  addFromCatalog: (c: CatalogItem) => void
  /** Import a found product into the library, then place it in the room. */
  addProductToScene: (p: ProductOption) => Promise<void>
  /** Starts importing found products in parallel so Add to scene only has to place them. */
  prefetchProducts: (products: ProductOption[]) => void
  applyPoses: (messageIndex: number) => void
  rejectProposal: (messageIndex: number) => void
  sendChat: (text: string) => Promise<void>
  cancelAgent: () => void
  loadRoom: () => Promise<void>
  /** Keeps watching for video furniture in a room resumed from this session. */
  resumeRoomPoll: () => void
  refreshAudit: () => Promise<void>
  refreshFengShuiScore: () => Promise<void>
  assessFengShui: () => Promise<void>
  setTab: (t: Tab) => void
  beginHumanPlacement: () => boolean
  previewHuman: (p: Pt | null) => void
  finishHumanPlacement: (p: Pt | null) => boolean
  cancelHumanPlacement: () => void
  removeHuman: () => void
  startPlay: () => boolean
  finishPlay: (pose?: Pose2D) => void
  openLightingPanel: () => boolean
  resumeWalking: () => boolean
  setArtificialLight: (percent: number) => void
  setTimeOfDay: (hour: number) => void
  toast: (text: string) => void
  dismissToast: (id: number) => void
}

/** Results belong to a committed revision; uncommitted drag frames do not invalidate them. */
const sameRevision = (a: RoomScene, b: RoomScene) =>
  a.scene_id === b.scene_id && a.revision === b.revision

let toastSeq = 0
/** Background re-fetch of a room whose furniture is still being extracted from video. */
let roomPoll: ReturnType<typeof setTimeout> | undefined
export const ROOM_POLL_MS = 5_000
const ROOM_POLL_ATTEMPTS = 240 // 20 minutes: SAM 3D takes minutes per item
let itemSeq = 0

const bump = (
  scene: RoomScene,
  furniture: FurnitureItem[] = scene.furniture,
): RoomScene => ({ ...scene, furniture, revision: scene.revision + 1 })

const mapItem = (
  scene: RoomScene,
  id: string,
  f: (i: FurnitureItem) => FurnitureItem,
) => scene.furniture.map((i) => (i.id === id ? f(i) : i))

/** Restoring always gets a fresh audit revision and invalidates pending proposals. */
function restoreVersion(state: State, version: RoomVersion): Partial<State> {
  state.agentAbort?.abort()
  state.auditAbort?.abort()
  state.fengShuiScoreAbort?.abort()
  return {
    scene: {
      ...structuredClone(version.scene),
      revision: state.scene.revision + 1,
    },
    currentVersionId: version.id,
    hasUnsavedChanges: false,
    selectedId: null,
    audit: null,
    auditStatus: 'idle',
    auditError: null,
    auditAbort: null,
    fengShuiScore: null,
    fengShuiScoreStatus: 'idle',
    fengShuiScoreError: null,
    fengShuiScoreAbort: null,
    agentBusy: false,
    agentProgress: [],
    agentAbort: null,
    chat: state.agentBusy
      ? [
          ...state.chat,
          {
            role: 'assistant',
            text: 'Layout request cancelled. Ask again to branch from the selected version.',
            progress: state.agentProgress,
          },
        ]
      : state.chat,
  }
}

function savedRoom(s: State): SavedRoom {
  return {
    scene: s.scene,
    versions: s.versions,
    currentVersionId: s.currentVersionId,
    hasUnsavedChanges: s.hasUnsavedChanges,
    chat: s.agentBusy
      ? [
          ...s.chat,
          {
            role: 'assistant',
            text: 'Layout request cancelled when you left the room. Ask again to continue.',
            progress: s.agentProgress,
          },
        ]
      : s.chat,
    human: s.human,
    playLighting: { ...s.playLighting },
    roomWarnings: s.roomWarnings,
    furnitureProgress: s.furnitureProgress,
  }
}

function itemFromCatalog(c: CatalogItem, pose: Pose2D): FurnitureItem {
  itemSeq += 1
  const { sku, image_url: _image, ...asset } = c
  return {
    ...structuredClone(asset),
    id: `lib-${itemSeq}-${sku}`.slice(0, 64),
    pose,
    is_fixed: false,
  }
}

/** Successful semantic edits get one cue, regardless of button or keyboard input. */
function withEditCue(cue: SoundCue, change: () => void) {
  const before = useStore.getState().scene.furniture
  change()
  const after = useStore.getState().scene.furniture
  if (
    before.length !== after.length ||
    before.some(
      (item, i) =>
        item.id !== after[i].id ||
        item.pose.x !== after[i].pose.x ||
        item.pose.z !== after[i].pose.z ||
        item.pose.yaw_deg !== after[i].pose.yaw_deg,
    )
  )
    playCue(cue)
}

const initialScene = roomScene(null)

/**
 * Re-fetches `loaded` until its furniture arrives, without blocking the editor. The room
 * is replaced only if the user hasn't changed it since; otherwise they're told to reopen it.
 */
function pollRoom(session: number, loaded: RoomScene, attempt = 1) {
  clearTimeout(roomPoll)
  if (attempt > ROOM_POLL_ATTEMPTS) return
  roomPoll = setTimeout(async () => {
    const live = () =>
      useStore.getState().roomSession === session &&
      useStore.getState().screen === 'editor'
    if (!live()) return
    let result: Awaited<ReturnType<typeof fetchRoom>>
    try {
      result = await fetchRoom(loaded.scene_id)
    } catch {
      if (live()) pollRoom(session, loaded, attempt + 1)
      return
    }
    if (!live()) return
    if (result.pending) {
      useStore.setState({
        furnitureProgress: result.progress,
        ...(useStore.getState().scene === loaded
          ? { roomWarnings: result.warnings }
          : {}),
      })
      pollRoom(session, loaded, attempt + 1)
    } else if (useStore.getState().scene === loaded) {
      useStore.setState({
        scene: result.scene,
        ...initialRoomHistory(result.scene),
        roomWarnings: result.warnings,
        furnitureProgress: null,
      })
      useStore
        .getState()
        .toast(
          `Furniture from your videos is in: ${result.scene.furniture.length} items.`,
        )
    } else {
      // Not kept for the session, so reopening loads the furnished room.
      useStore.setState({
        furnitureProgress: null,
        roomReady: false,
        roomWarnings: [
          'Furniture from your videos is ready: open this room again to load it (your edits here are not carried over).',
        ],
      })
    }
  }, ROOM_POLL_MS)
}

export const useStore = create<State>((set, get) => ({
  screen: 'home',
  home: demoPlan,
  uploadPlans: [],
  uploadVideos: [],
  planStatus: 'idle',
  planError: null,
  planAbort: null,
  segmentId: null,
  scene: initialScene,
  ...initialRoomHistory(initialScene),
  roomSession: 0,
  selectedId: null,
  interacting: false,
  tab: 'chat',
  mode: 'edit',
  playPhase: 'walking',
  playLighting: { ...DEFAULT_PLAY_LIGHTING },
  human: null,
  placingHuman: false,
  humanPreview: null,
  roomLoading: false,
  roomReady: false,
  rooms: {},
  roomKey: null,
  roomWarnings: [],
  furnitureProgress: null,
  roomAbort: null,
  audit: null,
  auditStatus: 'idle',
  auditError: null,
  auditAbort: null,
  fengShui: null,
  fengShuiStatus: 'idle',
  fengShuiError: null,
  fengShuiAbort: null,
  fengShuiScore: null,
  fengShuiScoreStatus: 'idle',
  fengShuiScoreError: null,
  fengShuiScoreAbort: null,
  chat: [],
  agentBusy: false,
  agentProgress: [],
  agentAbort: null,
  toasts: [],
  library: loadLibrary(),
  adding: [],
  prefetch: {},

  setScreen: (screen) =>
    set({
      screen,
      mode: 'edit',
      playPhase: 'walking',
      placingHuman: false,
      humanPreview: null,
      interacting: false,
    }),
  setUploadFiles: (kind, files) =>
    set(kind === 'plans' ? { uploadPlans: files } : { uploadVideos: files }),
  submitUpload: async () => {
    get().planAbort?.abort()
    const { uploadPlans, uploadVideos } = get()
    if (!uploadPlans.length) return
    const controller = new AbortController()
    set({
      screen: 'reading',
      segmentId: null,
      planStatus: 'loading',
      planError: null,
      planAbort: controller,
    })
    try {
      const parsed = await uploadFloorPlan(
        uploadPlans,
        uploadVideos,
        controller.signal,
      )
      if (get().planAbort !== controller) return
      const home = planFromParsed(parsed)
      if (!home.floors.some((f) => f.rooms.length))
        throw new Error(
          'No rooms were found on this floor plan. Try a clearer image.',
        )
      set({ home, planStatus: 'ready', planAbort: null })
    } catch (error) {
      // Superseded by another upload, the demo home or a cancel. A timeout is still ours.
      if (get().planAbort !== controller) return
      set({
        planStatus: 'error',
        planError: errorMessage(error),
        planAbort: null,
      })
    }
  },
  cancelUpload: () => {
    get().planAbort?.abort()
    set({
      planStatus: 'idle',
      planError: null,
      planAbort: null,
      screen: 'upload',
    })
  },
  chooseDemoHome: () => {
    get().planAbort?.abort()
    set({
      home: demoPlan,
      segmentId: null,
      planStatus: 'idle',
      planError: null,
      planAbort: null,
      screen: 'reading',
    })
  },
  selectSegment: (segmentId) => set({ segmentId }),
  openRoom: () => {
    get().agentAbort?.abort()
    get().roomAbort?.abort()
    get().auditAbort?.abort()
    get().fengShuiAbort?.abort()
    get().fengShuiScoreAbort?.abort()
    set((s) => {
      const plan =
        findPlanRoom(s.home, s.segmentId) ??
        s.home.floors.flatMap((f) => f.rooms).find((r) => r.selectable)
      const fresh = plan ? plan.scene() : roomScene(null)
      const roomKey = `${s.home.planId ?? 'demo'}/${fresh.scene_id}`
      // Keep the room being left once it finished loading; forget one that didn't.
      const rooms = { ...s.rooms }
      if (s.roomKey && s.roomReady) rooms[s.roomKey] = savedRoom(s)
      else if (s.roomKey) delete rooms[s.roomKey]
      // An untouched room still waiting on video furniture simply loads again.
      let saved: SavedRoom | undefined = rooms[roomKey]
      if (
        saved?.furnitureProgress &&
        saved.versions.length === 1 &&
        !saved.hasUnsavedChanges
      ) {
        delete rooms[roomKey]
        saved = undefined
      }
      const roomSession = s.roomSession + 1
      const room = saved
        ? {
            ...saved,
            // Proposals stay usable: their base scene and version are unchanged.
            chat: saved.chat.map((m) =>
              m.roomSession == null ? m : { ...m, roomSession },
            ),
            playLighting: { ...saved.playLighting },
            roomReady: true,
          }
        : {
            scene: fresh,
            ...initialRoomHistory(fresh),
            chat: [],
            human: null,
            playLighting: { ...DEFAULT_PLAY_LIGHTING },
            roomWarnings: [],
            furnitureProgress: null,
            roomReady: false,
          }
      return {
        screen: 'building',
        rooms,
        roomKey,
        ...room,
        roomSession,
        selectedId: null,
        tab: 'chat',
        mode: 'edit',
        playPhase: 'walking',
        placingHuman: false,
        humanPreview: null,
        audit: null,
        auditStatus: 'idle',
        auditError: null,
        auditAbort: null,
        fengShui: null,
        fengShuiStatus: 'idle',
        fengShuiError: null,
        fengShuiAbort: null,
        fengShuiScore: null,
        fengShuiScoreStatus: 'idle',
        fengShuiScoreError: null,
        fengShuiScoreAbort: null,
        roomLoading: false,
        roomAbort: null,
        interacting: false,
        agentBusy: false,
        agentProgress: [],
        agentAbort: null,
      }
    })
  },
  selectVersion: (id) => {
    const s = get()
    if (
      s.currentVersionId === id ||
      s.roomLoading ||
      s.interacting ||
      s.mode !== 'edit'
    )
      return
    const version = s.versions.find((v) => v.id === id)
    if (!version || version.scene.scene_id !== s.scene.scene_id) return
    if (s.hasUnsavedChanges)
      return get().toast(
        'Save with Ctrl+S or discard your changes before switching versions.',
      )
    set(restoreVersion(s, version))
    playCue('select')
  },
  saveVersion: () => {
    const s = get()
    if (
      s.screen !== 'editor' ||
      s.mode !== 'edit' ||
      s.roomLoading ||
      s.interacting ||
      !s.hasUnsavedChanges
    )
      return
    const saved = recordRoomVersion(
      s,
      s.scene,
      'Saved manual changes',
      'manual',
    )
    if (saved.currentVersionId === s.currentVersionId) {
      set(saved)
      return
    }
    s.agentAbort?.abort()
    set({
      ...saved,
      agentBusy: false,
      agentProgress: [],
      agentAbort: null,
      chat: s.agentBusy
        ? [
            ...s.chat,
            {
              role: 'assistant',
              text: 'Layout request cancelled because a new version was saved. Ask again from this version.',
              progress: s.agentProgress,
            },
          ]
        : s.chat,
    })
    playCue('ready')
  },
  discardChanges: () => {
    const s = get()
    if (
      s.screen !== 'editor' ||
      s.mode !== 'edit' ||
      s.roomLoading ||
      s.interacting ||
      !s.hasUnsavedChanges
    )
      return
    const version = s.versions.find((v) => v.id === s.currentVersionId)
    if (version) set(restoreVersion(s, version))
  },
  select: (selectedId) => {
    const s = get()
    if (s.selectedId === selectedId) return
    set({ selectedId })
    if (
      selectedId &&
      s.scene.furniture.some((i) => i.id === selectedId && !i.is_fixed)
    )
      playCue('select')
  },
  setInteracting: (interacting) => set({ interacting }),
  setPose: (id, pose) =>
    set((s) =>
      s.roomLoading
        ? {}
        : {
            scene: {
              ...s.scene,
              furniture: mapItem(s.scene, id, (i) => ({
                ...i,
                pose: { ...i.pose, ...pose },
              })),
            },
          },
    ),
  commitEdit: (cue = 'place') => {
    if (get().roomLoading) return
    set((s) => editRoomLayout(s, bump(s.scene)))
    if (cue) playCue(cue)
  },
  snapItem: (id) =>
    withEditCue('snap', () =>
      set((s) => {
        const item = s.scene.furniture.find((i) => i.id === id)
        if (!item || item.is_fixed || s.roomLoading) return {}
        return editRoomLayout(
          s,
          bump(
            s.scene,
            mapItem(s.scene, id, (i) => ({
              ...i,
              pose: snapToNearestWall(s.scene.walls, s.scene.floor_polygon, i),
            })),
          ),
        )
      }),
    ),
  rotateItem: (id, degrees) =>
    withEditCue('rotate', () =>
      set((s) => {
        const item = s.scene.furniture.find((i) => i.id === id)
        if (
          !item ||
          item.is_fixed ||
          s.roomLoading ||
          s.interacting ||
          !Number.isFinite(degrees)
        )
          return {}
        const yaw = (((item.pose.yaw_deg + degrees) % 360) + 360) % 360
        if (yaw === item.pose.yaw_deg) return {}
        const rotated = { ...item, pose: { ...item.pose, yaw_deg: yaw } }
        const p = clampToFloor(
          s.scene.floor_polygon,
          rotated,
          item.pose.x,
          item.pose.z,
        )
        return editRoomLayout(
          s,
          bump(
            s.scene,
            mapItem(s.scene, id, (i) => ({
              ...i,
              pose: { x: p.x, z: p.z, yaw_deg: yaw },
            })),
          ),
        )
      }),
    ),
  resetRotation: (id) =>
    withEditCue('rotate', () =>
      set((s) => {
        const item = s.scene.furniture.find((i) => i.id === id)
        if (!item || item.is_fixed || s.roomLoading || item.pose.yaw_deg === 0)
          return {}
        const upright = { ...item, pose: { ...item.pose, yaw_deg: 0 } }
        const c = clampToFloor(
          s.scene.floor_polygon,
          upright,
          item.pose.x,
          item.pose.z,
        )
        return editRoomLayout(
          s,
          bump(
            s.scene,
            mapItem(s.scene, id, (i) => ({
              ...i,
              pose: { x: c.x, z: c.z, yaw_deg: 0 },
            })),
          ),
        )
      }),
    ),
  deleteItem: (id) =>
    withEditCue('delete', () =>
      set((s) => {
        const item = s.scene.furniture.find((i) => i.id === id)
        if (!item || item.is_fixed || s.roomLoading) return {}
        return {
          ...editRoomLayout(
            s,
            bump(
              s.scene,
              s.scene.furniture.filter((i) => i.id !== id),
            ),
          ),
          selectedId: s.selectedId === id ? null : s.selectedId,
        }
      }),
    ),
  addFromCatalog: (c) => {
    if (get().roomLoading) return
    const { scene } = get()
    const yaw = fitYaw(scene.floor_polygon, c.bbox_m.width, c.bbox_m.depth)
    if (yaw == null) {
      playCue('reject')
      return get().toast(`${c.name} doesn't fit this room.`)
    }
    const b = bounds(scene.floor_polygon)
    const draft = itemFromCatalog(c, { x: 0, z: 0, yaw_deg: yaw })
    const p = clampToFloor(
      scene.floor_polygon,
      draft,
      (b.minX + b.maxX) / 2,
      (b.minZ + b.maxZ) / 2,
    )
    const item = { ...draft, pose: { x: p.x, z: p.z, yaw_deg: yaw } }
    set({
      ...editRoomLayout(get(), bump(scene, [...scene.furniture, item])),
      selectedId: item.id,
    })
    get().toast(
      `Added ${c.name}${item.is_proxy ? ' as a proxy box' : ''}. Drag it into place.`,
    )
    playCue('add')
  },
  addProductToScene: async (product) => {
    const url = product.product_url
    if (get().adding.includes(url)) return
    const session = get().roomSession
    const current = () => get().roomSession === session
    set((s) => ({ adding: [...s.adding, url] }))
    try {
      // 1. The library: imported once per product, reused after that.
      let entry = get().library.find((e) => e.product.product_url === url)
      if (!entry) {
        // Usually already running, or done, since the chat reply prefetched it.
        const item = await sharedImport(product, get().scene.scene_id)
        entry = { product, item }
        const library = [
          entry,
          ...get().library.filter((e) => e.product.product_url !== url),
        ]
        set({ library })
        saveLibrary(library)
      }
      if (!current()) return
      // 2. Placement against the room as it is now, then 3. into the scene.
      const before = get().scene
      const taken = new Set(before.furniture.map((i) => i.id))
      const draft = { ...entry.item, id: freshItemId(entry.item.id, taken) }
      const placed = await placeItem(before, draft)
      const scene = get().scene
      if (!current()) return
      if (
        scene.revision !== before.revision ||
        get().mode !== 'edit' ||
        get().roomLoading
      ) {
        playCue('reject')
        return get().toast(
          `The room changed while placing ${product.name}. Add it again from the Library.`,
        )
      }
      const audit =
        placed.report?.scene_id === scene.scene_id &&
        placed.report.scene_revision === scene.revision
          ? { ...placed.report, scene_revision: scene.revision + 1 }
          : null
      set({
        ...editRoomLayout(
          get(),
          bump(scene, [...scene.furniture, placed.item]),
        ),
        selectedId: placed.item.id,
        audit,
        auditStatus: audit ? 'ready' : 'idle',
        auditError: null,
      })
      get().toast(
        placed.item.is_proxy
          ? `${placed.text} No 3D model was available, so it is a labelled box.`
          : placed.text,
      )
      playCue('add')
    } catch (error) {
      if (!current()) return
      playCue('reject')
      get().toast(
        error instanceof SpatialError
          ? error.message
          : `${product.name} could not be added. Try again.`,
      )
    } finally {
      set((s) => ({ adding: s.adding.filter((u) => u !== url) }))
    }
  },
  prefetchProducts: (products) => {
    const sceneId = get().scene.scene_id
    const mark = (key: string, status: 'pending' | 'ready' | null) =>
      set((s) => {
        const prefetch = { ...s.prefetch }
        if (status) prefetch[key] = status
        else delete prefetch[key]
        return { prefetch }
      })
    for (const product of products) {
      const url = product.product_url
      const key = importKey(product, sceneId)
      if (get().library.some((e) => e.product.product_url === url)) continue
      if (get().prefetch[key]) continue
      mark(key, 'pending')
      // A failure stays quiet here: Add to scene retries the import and reports it.
      sharedImport(product, sceneId).then(
        () => mark(key, 'ready'),
        () => mark(key, null),
      )
    }
  },
  applyPoses: (index) => {
    const {
      chat,
      scene,
      roomSession,
      currentVersionId,
      interacting,
      mode,
      roomLoading,
    } = get()
    const msg = chat[index]
    if (
      !msg?.proposal ||
      !msg.baseScene ||
      msg.applied ||
      msg.rejected ||
      interacting ||
      mode !== 'edit' ||
      roomLoading
    )
      return
    if (
      msg.roomSession !== roomSession ||
      scene !== msg.baseScene ||
      msg.baseVersionId !== currentVersionId
    ) {
      playCue('reject')
      return get().toast(
        'The room changed since this suggestion. Ask the agent again.',
      )
    }
    let proposal: EditorProposal
    try {
      proposal = readProposal(msg.proposal, scene, msg.baselineAudit)
      if (!proposal.improved || layoutChanges(scene, proposal).length === 0)
        return
    } catch (error) {
      return get().toast(errorMessage(error))
    }
    const poses = proposal.poses
    const removed = new Set(proposal.removals ?? [])
    const furniture = scene.furniture
      .filter((i) => !removed.has(i.id))
      .map((i) =>
        Object.hasOwn(poses, i.id) ? { ...i, pose: { ...poses[i.id] } } : i,
      )
    withEditCue('apply', () =>
      set({
        ...recordRoomVersion(
          get(),
          bump(scene, [
            ...furniture,
            ...structuredClone(proposal.additions ?? []),
          ]),
          `Agent: ${proposal.explanation}`,
          'agent',
        ),
        audit: null,
        auditStatus: 'idle',
        ...(removed.has(get().selectedId ?? '') ? { selectedId: null } : {}),
        chat: chat.map((m, i) => (i === index ? { ...m, applied: true } : m)),
      }),
    )
  },
  rejectProposal: (index) =>
    set((s) => ({
      chat: s.chat.map((m, i) =>
        i === index && m.proposal && !m.applied ? { ...m, rejected: true } : m,
      ),
    })),
  sendChat: async (text) => {
    const instruction = text.trim()
    const {
      scene,
      roomSession,
      currentVersionId,
      audit,
      agentBusy,
      interacting,
      mode,
      roomLoading,
    } = get()
    if (
      agentBusy ||
      interacting ||
      mode !== 'edit' ||
      roomLoading ||
      !instruction
    )
      return
    if ([...instruction].length > MAX_LAYOUT_INSTRUCTION_CHARS) {
      get().toast(
        `Keep your request within ${MAX_LAYOUT_INSTRUCTION_CHARS} characters.`,
      )
      return
    }
    const controller = new AbortController()
    const current = () =>
      get().roomSession === roomSession && get().agentAbort === controller
    set((s) => ({
      agentBusy: true,
      agentProgress: [],
      agentAbort: controller,
      chat: [...s.chat, { role: 'user', text: instruction }],
    }))
    try {
      const reply = await streamAgentMessage(
        scene,
        instruction,
        controller.signal,
        (update) => {
          if (current())
            set((s) => ({
              agentProgress: [...s.agentProgress, update].slice(-200),
            }))
        },
        matchingAudit(audit, scene) ? audit : undefined,
      )
      if (!current()) return
      set((s) => ({
        chat: [
          ...s.chat,
          {
            role: 'assistant',
            text: reply.text,
            proposal: reply.proposal,
            products: reply.products,
            progress: s.agentProgress,
            baseScene: scene,
            roomSession,
            baseVersionId: currentVersionId,
            baseVersionLabel: get().versions.find(
              (v) => v.id === currentVersionId,
            )?.label,
            baselineAudit: matchingAudit(audit, scene) ? audit : undefined,
          },
        ],
      }))
      if (reply.products?.length) get().prefetchProducts(reply.products)
    } catch (error) {
      if (current() && !controller.signal.aborted)
        set((s) => ({
          chat: [
            ...s.chat,
            {
              role: 'assistant',
              text: errorMessage(error),
              progress: s.agentProgress,
            },
          ],
        }))
    } finally {
      if (current())
        set({ agentBusy: false, agentAbort: null, agentProgress: [] })
    }
  },
  cancelAgent: () => {
    if (!get().agentBusy) return
    get().agentAbort?.abort()
    set((s) => ({
      agentBusy: false,
      agentProgress: [],
      agentAbort: null,
      chat: [
        ...s.chat,
        {
          role: 'assistant',
          text: 'Request cancelled. Your room has not changed.',
          progress: s.agentProgress,
        },
      ],
    }))
  },
  loadRoom: async () => {
    get().roomAbort?.abort()
    clearTimeout(roomPoll)
    const { scene, roomSession } = get()
    const controller = new AbortController()
    const current = () =>
      get().roomSession === roomSession && get().roomAbort === controller
    set({
      roomLoading: true,
      roomAbort: controller,
      roomWarnings: [],
      furnitureProgress: null,
      audit: null,
    })
    try {
      const result = await fetchRoom(scene.scene_id, controller.signal)
      if (current() && get().scene === scene) {
        set({
          scene: result.scene,
          ...initialRoomHistory(result.scene),
          roomWarnings: result.warnings,
          furnitureProgress: result.progress,
        })
        if (result.pending) pollRoom(roomSession, result.scene)
      }
    } catch (error) {
      if (current() && !controller.signal.aborted)
        set({
          roomWarnings: [
            get().home.planId
              ? `Showing the room as parsed, without furniture. ${errorMessage(error)}`
              : `Using the local demo room. ${errorMessage(error)}`,
          ],
        })
    } finally {
      if (current())
        set({ roomLoading: false, roomAbort: null, roomReady: true })
    }
  },
  resumeRoomPoll: () => {
    const s = get()
    // The saved original never matches the edited scene, so the user is told to
    // reopen the room rather than having their edits replaced.
    if (s.roomReady && s.furnitureProgress)
      pollRoom(s.roomSession, s.versions[0].scene)
  },
  refreshAudit: async () => {
    const { scene, roomSession, interacting, roomLoading } = get()
    if (interacting || roomLoading) return
    get().auditAbort?.abort()
    const controller = new AbortController()
    const current = () =>
      get().roomSession === roomSession &&
      sameRevision(get().scene, scene) &&
      !get().interacting &&
      get().auditAbort === controller
    set({
      audit: null,
      auditStatus: 'loading',
      auditError: null,
      auditAbort: controller,
    })
    try {
      const audit = await fetchAudit(scene, controller.signal)
      if (current()) set({ audit, auditStatus: 'ready' })
    } catch (error) {
      if (current() && !controller.signal.aborted)
        set({ auditStatus: 'error', auditError: errorMessage(error) })
    } finally {
      if (get().auditAbort === controller) set({ auditAbort: null })
    }
  },
  refreshFengShuiScore: async () => {
    const { scene, roomSession, interacting, roomLoading } = get()
    if (interacting || roomLoading) return
    get().fengShuiScoreAbort?.abort()
    const controller = new AbortController()
    const current = () =>
      get().roomSession === roomSession &&
      sameRevision(get().scene, scene) &&
      !get().interacting &&
      get().fengShuiScoreAbort === controller
    set({
      fengShuiScore: null,
      fengShuiScoreStatus: 'loading',
      fengShuiScoreError: null,
      fengShuiScoreAbort: controller,
    })
    try {
      const score = await fetchFengShuiScore(scene, controller.signal)
      if (current()) set({ fengShuiScore: score, fengShuiScoreStatus: 'ready' })
    } catch (error) {
      if (current() && !controller.signal.aborted)
        set({
          fengShuiScoreStatus: 'error',
          fengShuiScoreError: errorMessage(error),
        })
    } finally {
      if (get().fengShuiScoreAbort === controller)
        set({ fengShuiScoreAbort: null })
    }
  },
  assessFengShui: async () => {
    const { scene, roomSession, interacting, roomLoading } = get()
    if (interacting || roomLoading || get().fengShuiStatus === 'loading') return
    const controller = new AbortController()
    const current = () =>
      get().roomSession === roomSession &&
      sameRevision(get().scene, scene) &&
      get().fengShuiAbort === controller
    set({
      fengShui: null,
      fengShuiStatus: 'loading',
      fengShuiError: null,
      fengShuiAbort: controller,
    })
    try {
      const fengShui = await fetchFengShui(scene, controller.signal)
      if (current()) set({ fengShui, fengShuiStatus: 'ready' })
    } catch (error) {
      if (current() && !controller.signal.aborted)
        set({ fengShuiStatus: 'error', fengShuiError: errorMessage(error) })
    } finally {
      if (get().fengShuiAbort === controller) set({ fengShuiAbort: null })
    }
  },
  setTab: (tab) => {
    if (get().tab === tab) return
    set({ tab })
    playCue('select')
  },
  beginHumanPlacement: () => {
    const s = get()
    if (s.mode !== 'edit' || s.interacting || s.roomLoading) return false
    set({
      placingHuman: true,
      humanPreview: null,
      interacting: true,
      selectedId: null,
    })
    return true
  },
  previewHuman: (p) => {
    const s = get()
    if (s.placingHuman)
      set({ humanPreview: p ? humanPoseAt(p, s.scene, s.human) : null })
  },
  finishHumanPlacement: (p) => {
    const s = get()
    if (!s.placingHuman) return false
    const valid = p != null && canStand(p, s.scene)
    set({
      human: valid ? humanPoseAt(p, s.scene, s.human) : s.human,
      placingHuman: false,
      humanPreview: null,
      interacting: false,
    })
    if (!valid) playCue('reject')
    else if (!s.human || p!.x !== s.human.x || p!.z !== s.human.z)
      playCue('place')
    return valid
  },
  cancelHumanPlacement: () => {
    if (get().placingHuman)
      set({ placingHuman: false, humanPreview: null, interacting: false })
  },
  removeHuman: () => {
    if (get().mode === 'edit' && !get().interacting) set({ human: null })
  },
  startPlay: () => {
    const s = get()
    if (
      s.screen !== 'editor' ||
      s.mode !== 'edit' ||
      s.interacting ||
      !s.human ||
      !canStand(s.human, s.scene)
    )
      return false
    set({ mode: 'play', playPhase: 'walking', selectedId: null })
    return true
  },
  finishPlay: (pose) => {
    const s = get()
    if (s.mode !== 'play') return
    const valid =
      pose &&
      Number.isFinite(pose.x) &&
      Number.isFinite(pose.z) &&
      Number.isFinite(pose.yaw_deg)
    set({
      mode: 'edit',
      playPhase: 'walking',
      human: valid && s.human ? { ...pose } : s.human,
    })
  },
  openLightingPanel: () => {
    if (get().mode !== 'play') return false
    set({ playPhase: 'lighting' })
    return true
  },
  resumeWalking: () => {
    if (get().mode !== 'play' || get().playPhase !== 'lighting') return false
    set({ playPhase: 'walking' })
    return true
  },
  setArtificialLight: (percent) => {
    if (Number.isFinite(percent))
      set((s) => ({
        playLighting: {
          ...s.playLighting,
          artificialPercent: Math.max(0, Math.min(100, percent)),
        },
      }))
  },
  setTimeOfDay: (hour) => {
    if (Number.isFinite(hour))
      set((s) => ({
        playLighting: {
          ...s.playLighting,
          timeOfDay: Math.round(Math.max(0, Math.min(24, hour)) * 4) / 4,
        },
      }))
  },
  toast: (text) => {
    const id = ++toastSeq
    set((s) => ({ toasts: [...s.toasts, { id, text }] }))
    setTimeout(() => get().dismissToast(id), 4500)
  },
  dismissToast: (id) =>
    set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}))
