import { create } from 'zustand'
import type { CatalogItem } from './data/catalog'
import { freshMockScene } from './data/mockScene'
import type {
  AuditReport,
  FurnitureItem,
  Pose2D,
  RoomScene,
} from './lib/contracts'
import { bounds, clampToFloor, fitYaw, snapToNearestWall } from './lib/geometry'

export type Screen = 'upload' | 'reading' | 'floorplan' | 'building' | 'editor'
export type Tab = 'chat' | 'stats' | 'library'

export interface ChatMessage {
  role: 'user' | 'assistant'
  text: string
  /** Proposed poses attached to an agent reply (item_id -> pose). */
  poses?: Record<string, Pose2D>
  /** Scene revision the agent saw; poses only apply while the scene is still at it. */
  baseRevision?: number
  applied?: boolean
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
  selectedId: string | null
  /** True while an item is being dragged or rotated. */
  interacting: boolean
  tab: Tab
  /** Latest AuditReport from the spatial engine (hooked up in a later PR). */
  audit: AuditReport | null
  chat: ChatMessage[]
  agentBusy: boolean
  /** In-flight agent request, aborted when the room is reopened. */
  agentAbort: AbortController | null
  toasts: Toast[]

  setScreen: (s: Screen) => void
  selectSegment: (id: string | null) => void
  openRoom: () => void
  select: (id: string | null) => void
  setInteracting: (b: boolean) => void
  /** Live pose update while dragging/rotating; does not bump the revision. */
  setPose: (id: string, pose: Partial<Pose2D>) => void
  /** Ends a drag/rotate: bumps the revision once. */
  commitEdit: () => void
  snapItem: (id: string) => void
  /** Turns an item back to yaw 0 (front facing +Z), kept inside the floor. */
  resetRotation: (id: string) => void
  deleteItem: (id: string) => void
  addFromCatalog: (c: CatalogItem) => void
  applyPoses: (messageIndex: number) => void
  setTab: (t: Tab) => void
  pushChat: (m: ChatMessage) => void
  setAgentBusy: (b: boolean, abort?: AbortController | null) => void
  toast: (text: string) => void
  dismissToast: (id: number) => void
}

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

function itemFromCatalog(c: CatalogItem, pose: Pose2D): FurnitureItem {
  itemSeq += 1
  return {
    id: `lib-${c.sku}-${itemSeq}`.slice(0, 64),
    name: c.name,
    category: c.category,
    source: 'catalog_search',
    glb_url: '', // no reconstructed mesh yet: rendered as a labelled proxy box
    price_gbp: c.price_gbp,
    product_url: c.product_url ?? null,
    bbox_m: { ...c.bbox_m },
    pose,
    has_screen: false,
    requires_front_clear_m: 0.6,
    wall_flush_preferred: true,
    is_proxy: true,
    dimension_source: 'catalog',
    correction_needed: [],
    collision_parts: [],
    collision_source: 'template',
    is_fixed: false,
  }
}

export const useStore = create<State>((set, get) => ({
  screen: 'upload',
  segmentId: null,
  scene: freshMockScene(),
  roomSession: 0,
  selectedId: null,
  interacting: false,
  tab: 'chat',
  audit: null,
  chat: [],
  agentBusy: false,
  agentAbort: null,
  toasts: [],

  setScreen: (screen) => set({ screen }),
  selectSegment: (segmentId) => set({ segmentId }),
  openRoom: () => {
    get().agentAbort?.abort()
    set((s) => ({
      screen: 'building',
      scene: freshMockScene(),
      roomSession: s.roomSession + 1,
      selectedId: null,
      tab: 'chat',
      audit: null,
      interacting: false,
      chat: [],
      agentBusy: false,
      agentAbort: null,
    }))
  },
  select: (selectedId) => set({ selectedId }),
  setInteracting: (interacting) => set({ interacting }),
  setPose: (id, pose) =>
    set((s) => ({
      scene: {
        ...s.scene,
        furniture: mapItem(s.scene, id, (i) => ({
          ...i,
          pose: { ...i.pose, ...pose },
        })),
      },
    })),
  commitEdit: () => set((s) => ({ scene: bump(s.scene) })),
  snapItem: (id) =>
    set((s) => {
      const item = s.scene.furniture.find((i) => i.id === id)
      if (!item || item.is_fixed) return {}
      return {
        scene: bump(
          s.scene,
          mapItem(s.scene, id, (i) => ({
            ...i,
            pose: snapToNearestWall(s.scene.walls, s.scene.floor_polygon, i),
          })),
        ),
      }
    }),
  resetRotation: (id) =>
    set((s) => {
      const item = s.scene.furniture.find((i) => i.id === id)
      if (!item || item.is_fixed || item.pose.yaw_deg === 0) return {}
      const upright = { ...item, pose: { ...item.pose, yaw_deg: 0 } }
      const c = clampToFloor(
        s.scene.floor_polygon,
        upright,
        item.pose.x,
        item.pose.z,
      )
      return {
        scene: bump(
          s.scene,
          mapItem(s.scene, id, (i) => ({
            ...i,
            pose: { x: c.x, z: c.z, yaw_deg: 0 },
          })),
        ),
      }
    }),
  deleteItem: (id) =>
    set((s) => {
      const item = s.scene.furniture.find((i) => i.id === id)
      if (!item || item.is_fixed) return {}
      return {
        scene: bump(
          s.scene,
          s.scene.furniture.filter((i) => i.id !== id),
        ),
        selectedId: s.selectedId === id ? null : s.selectedId,
      }
    }),
  addFromCatalog: (c) => {
    const { scene } = get()
    const yaw = fitYaw(scene.floor_polygon, c.bbox_m.width, c.bbox_m.depth)
    if (yaw == null) return get().toast(`${c.name} doesn't fit this room.`)
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
      scene: bump(scene, [...scene.furniture, item]),
      selectedId: item.id,
    })
    get().toast(`Added ${c.name} as a proxy box. Drag it into place.`)
  },
  applyPoses: (index) => {
    const { chat, scene } = get()
    const msg = chat[index]
    if (!msg?.poses || msg.applied) return
    if (msg.baseRevision !== scene.revision)
      return get().toast(
        'The room changed since this suggestion. Ask the agent again.',
      )
    // Fixed items (fixtures) are never moved by the agent or solver.
    const poses = msg.poses
    const furniture = scene.furniture.map((i) =>
      poses[i.id] && !i.is_fixed ? { ...i, pose: { ...poses[i.id] } } : i,
    )
    set({
      scene: bump(scene, furniture),
      chat: chat.map((m, i) => (i === index ? { ...m, applied: true } : m)),
    })
  },
  setTab: (tab) => set({ tab }),
  pushChat: (m) => set((s) => ({ chat: [...s.chat, m] })),
  setAgentBusy: (agentBusy, agentAbort = null) =>
    set({ agentBusy, agentAbort }),
  toast: (text) => {
    const id = ++toastSeq
    set((s) => ({ toasts: [...s.toasts, { id, text }] }))
    setTimeout(() => get().dismissToast(id), 4500)
  },
  dismissToast: (id) =>
    set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}))
