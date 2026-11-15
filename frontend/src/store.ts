import { create } from 'zustand'
import { playCue, type SoundCue } from './audio/cues'
import type { CatalogItem } from './data/catalog'
import { roomScene } from './data/demoHome'
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
import { layoutChanges, matchingAudit } from './lib/layoutDiff'
import { fetchAudit, fetchRoom } from './lib/spatial'
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
  importProduct,
  loadLibrary,
  placeItem,
  saveLibrary,
  type LibraryEntry,
  type ProductOption,
} from './lib/products'
import { SpatialError } from './lib/spatial'
import {
  DEFAULT_PLAY_LIGHTING,
  artificialSources,
  MAX_LIGHT_SOURCES,
  validLightPosition,
  type LightPosition,
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
export interface Toast {
  id: number
  text: string
}

interface State {
  screen: Screen
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
  playLightTool: 'none' | 'add' | 'remove'
  playLighting: PlayLightingSettings
  /** Local preview actor, never included in RoomScene or its revision. */
  human: Pose2D | null
  placingHuman: boolean
  humanPreview: Pose2D | null
  roomLoading: boolean
  roomWarnings: string[]
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

  setScreen: (s: Screen) => void
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
  applyPoses: (messageIndex: number) => void
  rejectProposal: (messageIndex: number) => void
  sendChat: (text: string) => Promise<void>
  cancelAgent: () => void
  loadRoom: () => Promise<void>
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
  setLightWarmth: (kelvin: number) => void
  setLightTool: (tool: 'none' | 'add' | 'remove') => void
  addLightSource: (position: LightPosition) => boolean
  removeLightSource: (id: string) => boolean
  toast: (text: string) => void
  dismissToast: (id: number) => void
}

/** Results belong to a committed revision; uncommitted drag frames do not invalidate them. */
const sameRevision = (a: RoomScene, b: RoomScene) =>
  a.scene_id === b.scene_id && a.revision === b.revision

let lightSeq = 0
let toastSeq = 0
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

export const useStore = create<State>((set, get) => ({
  screen: 'home',
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
  playLightTool: 'none',
  human: null,
  placingHuman: false,
  humanPreview: null,
  roomLoading: false,
  roomWarnings: [],
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

  setScreen: (screen) =>
    set({
      screen,
      mode: 'edit',
      playPhase: 'walking',
      placingHuman: false,
      humanPreview: null,
      interacting: false,
    }),
  selectSegment: (segmentId) => set({ segmentId }),
  openRoom: () => {
    get().agentAbort?.abort()
    get().roomAbort?.abort()
    get().auditAbort?.abort()
    get().fengShuiAbort?.abort()
    get().fengShuiScoreAbort?.abort()
    set((s) => {
      const scene = roomScene(s.segmentId)
      return {
        screen: 'building',
        scene,
        ...initialRoomHistory(scene),
        roomSession: s.roomSession + 1,
        selectedId: null,
        tab: 'chat',
        mode: 'edit',
        playPhase: 'walking',
        playLighting: { ...DEFAULT_PLAY_LIGHTING },
        playLightTool: 'none',
        human: null,
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
        roomWarnings: [],
        roomAbort: null,
        interacting: false,
        chat: [],
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
        const item = await importProduct(product, get().scene.scene_id)
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
    const furniture = scene.furniture.map((i) =>
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
    const { scene, roomSession } = get()
    const controller = new AbortController()
    const current = () =>
      get().roomSession === roomSession && get().roomAbort === controller
    set({
      roomLoading: true,
      roomAbort: controller,
      roomWarnings: [],
      audit: null,
    })
    try {
      const result = await fetchRoom(scene.scene_id, controller.signal)
      if (current() && get().scene === scene)
        set({
          scene: result.scene,
          ...initialRoomHistory(result.scene),
          roomWarnings: result.warnings,
        })
    } catch (error) {
      if (current() && !controller.signal.aborted)
        set({
          roomWarnings: [`Using the local demo room. ${errorMessage(error)}`],
        })
    } finally {
      if (current()) set({ roomLoading: false, roomAbort: null })
    }
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
      playLightTool: 'none',
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
    set({ playPhase: 'walking', playLightTool: 'none' })
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
  setLightWarmth: (kelvin) => {
    if (Number.isFinite(kelvin))
      set((s) => ({
        playLighting: {
          ...s.playLighting,
          warmthKelvin:
            Math.round(Math.max(2200, Math.min(6500, kelvin)) / 100) * 100,
        },
      }))
  },
  setLightTool: (tool) => {
    if (get().mode === 'play' && get().playPhase === 'lighting')
      set({ playLightTool: tool })
  },
  addLightSource: (position) => {
    const s = get()
    const sources = artificialSources(s.scene, s.playLighting)
    if (
      s.mode !== 'play' ||
      s.playPhase !== 'lighting' ||
      sources.length >= MAX_LIGHT_SOURCES ||
      !validLightPosition(s.scene, position)
    )
      return false
    set({
      playLighting: {
        ...s.playLighting,
        sources: [
          ...sources,
          {
            id: `point-${++lightSeq}`,
            position: [...position],
            kind: 'point',
          },
        ],
      },
    })
    return true
  },
  removeLightSource: (id) => {
    const s = get()
    const sources = artificialSources(s.scene, s.playLighting)
    if (
      s.mode !== 'play' ||
      s.playPhase !== 'lighting' ||
      !sources.some((light) => light.id === id)
    )
      return false
    set({
      playLighting: {
        ...s.playLighting,
        sources: sources.filter((light) => light.id !== id),
      },
    })
    return true
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
