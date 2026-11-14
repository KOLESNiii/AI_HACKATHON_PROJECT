import { create } from 'zustand'
import type { CatalogItem } from './data/catalog'
import { freshMockScene } from './data/mockScene'
import type {
  AuditReport,
  FurnitureItem,
  LayoutProposal,
  Pose2D,
  RoomScene,
} from './lib/contracts'
import { bounds, snapToNearestWall } from './lib/geometry'

export type Screen = 'upload' | 'reading' | 'floorplan' | 'building' | 'editor'
export type Tab = 'chat' | 'stats' | 'library'
export type Layer = 'clearance' | 'glare' | 'fengshui'
export type AuditStatus = 'idle' | 'pending' | 'ok' | 'unavailable'

export interface ChatMessage {
  role: 'user' | 'assistant'
  text: string
}
export interface Toast {
  id: number
  text: string
}

interface State {
  screen: Screen
  segmentId: string | null
  scene: RoomScene
  selectedId: string | null
  dragging: boolean
  layers: Record<Layer, boolean>
  tab: Tab
  replacingId: string | null
  audit: AuditReport | null
  auditStatus: AuditStatus
  /** Incremented whenever a room is (re)opened; async results from an older session are dropped. */
  roomSession: number
  proposal: LayoutProposal | null
  chat: ChatMessage[]
  toasts: Toast[]

  setScreen: (s: Screen) => void
  selectSegment: (id: string | null) => void
  openRoom: () => void
  select: (id: string | null) => void
  setDragging: (d: boolean) => void
  moveItem: (id: string, x: number, z: number) => void
  commitEdit: () => void
  rotateItem: (id: string, deltaDeg: number) => void
  snapItem: (id: string) => void
  deleteItem: (id: string) => void
  addFromCatalog: (c: CatalogItem) => void
  replaceWithCatalog: (id: string, c: CatalogItem) => void
  toggleLayer: (l: Layer) => void
  setTab: (t: Tab) => void
  startReplace: (id: string) => void
  cancelReplace: () => void
  setSunHour: (h: number) => void
  setNorth: (deg: number) => void
  setAudit: (a: AuditReport | null, status: AuditStatus) => void
  setProposal: (p: LayoutProposal | null) => void
  applyProposal: () => void
  sendChat: (text: string) => void
  toast: (text: string) => void
  dismissToast: (id: number) => void
}

let toastSeq = 0
let itemSeq = 0

const bump = (
  scene: RoomScene,
  furniture: FurnitureItem[] = scene.furniture,
): RoomScene => ({
  ...scene,
  furniture,
  revision: scene.revision + 1,
})

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

/** The audit only while it matches the current scene revision (stale reports are never shown). */
export const selectCurrentAudit = (s: State): AuditReport | null =>
  s.audit &&
  s.audit.scene_id === s.scene.scene_id &&
  s.audit.scene_revision === s.scene.revision
    ? s.audit
    : null

export const useStore = create<State>((set, get) => ({
  screen: 'upload',
  segmentId: null,
  scene: freshMockScene(),
  selectedId: null,
  dragging: false,
  layers: { clearance: false, glare: false, fengshui: false },
  tab: 'chat',
  replacingId: null,
  audit: null,
  auditStatus: 'idle',
  roomSession: 0,
  proposal: null,
  chat: [],
  toasts: [],

  setScreen: (screen) => set({ screen }),
  selectSegment: (segmentId) => set({ segmentId }),
  openRoom: () =>
    set((s) => ({
      roomSession: s.roomSession + 1,
      screen: 'building',
      scene: freshMockScene(),
      selectedId: null,
      dragging: false,
      layers: { clearance: false, glare: false, fengshui: false },
      tab: 'chat',
      replacingId: null,
      audit: null,
      auditStatus: 'idle',
      proposal: null,
      chat: [],
    })),
  select: (selectedId) => set({ selectedId }),
  setDragging: (dragging) => set({ dragging }),
  moveItem: (id, x, z) =>
    set((s) => ({
      scene: {
        ...s.scene,
        furniture: mapItem(s.scene, id, (i) => ({
          ...i,
          pose: { ...i.pose, x, z },
        })),
      },
    })),
  commitEdit: () => set((s) => ({ scene: bump(s.scene), proposal: null })),
  rotateItem: (id, d) =>
    set((s) => ({
      scene: bump(
        s.scene,
        mapItem(s.scene, id, (i) => ({
          ...i,
          pose: {
            ...i.pose,
            yaw_deg: (((i.pose.yaw_deg + d) % 360) + 360) % 360,
          },
        })),
      ),
      proposal: null,
    })),
  snapItem: (id) =>
    set((s) => ({
      scene: bump(
        s.scene,
        mapItem(s.scene, id, (i) => ({
          ...i,
          pose: snapToNearestWall(s.scene, i),
        })),
      ),
      proposal: null,
    })),
  deleteItem: (id) =>
    set((s) => ({
      scene: bump(
        s.scene,
        s.scene.furniture.filter((i) => i.id !== id),
      ),
      selectedId: null,
      proposal: null,
    })),
  addFromCatalog: (c) => {
    const { scene } = get()
    const b = bounds(scene.floor_polygon)
    const pose = {
      x: (b.minX + b.maxX) / 2,
      z: (b.minZ + b.maxZ) / 2,
      yaw_deg: 0,
    }
    const item = itemFromCatalog(c, pose)
    set({
      scene: bump(scene, [...scene.furniture, item]),
      selectedId: item.id,
      proposal: null,
    })
    get().toast(`Added ${c.name} as a proxy box. Drag it into place.`)
  },
  replaceWithCatalog: (id, c) => {
    const { scene } = get()
    const old = scene.furniture.find((i) => i.id === id)
    if (!old) return
    const item = itemFromCatalog(c, { ...old.pose })
    set({
      scene: bump(
        scene,
        scene.furniture.map((i) => (i.id === id ? item : i)),
      ),
      selectedId: item.id,
      replacingId: null,
      proposal: null,
    })
  },
  toggleLayer: (l) =>
    set((s) => ({ layers: { ...s.layers, [l]: !s.layers[l] } })),
  setTab: (tab) => set({ tab }),
  startReplace: (id) => set({ replacingId: id, tab: 'library' }),
  cancelReplace: () => set({ replacingId: null }),
  setSunHour: (h) =>
    set((s) => ({ scene: { ...s.scene, sun_hour: Math.round(h * 4) / 4 } })),
  setNorth: (deg) =>
    set((s) => ({
      scene: {
        ...s.scene,
        north_compass_deg: ((Math.round(deg) % 360) + 360) % 360,
      },
    })),
  setAudit: (audit, auditStatus) => set({ audit, auditStatus }),
  setProposal: (proposal) => set({ proposal }),
  applyProposal: () => {
    const { proposal, scene } = get()
    if (!proposal) return
    const furniture = scene.furniture.map((i) =>
      proposal.poses[i.id] ? { ...i, pose: { ...proposal.poses[i.id] } } : i,
    )
    set({ scene: bump(scene, furniture), proposal: null })
  },
  sendChat: (text) =>
    set((s) => ({
      chat: [
        ...s.chat,
        { role: 'user', text },
        {
          role: 'assistant',
          text: 'Chat redesign is not connected yet. It needs a chat → LayoutProposal endpoint (see FIGMA_DESIGN_SPEC.md). Meanwhile, try Auto-Fix Layout in the dock.',
        },
      ],
    })),
  toast: (text) => {
    const id = ++toastSeq
    set((s) => ({ toasts: [...s.toasts, { id, text }] }))
    setTimeout(() => get().dismissToast(id), 4500)
  },
  dismissToast: (id) =>
    set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}))
