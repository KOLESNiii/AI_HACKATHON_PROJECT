import { Html, Line, useGLTF } from '@react-three/drei'
import { useThree, type ThreeEvent } from '@react-three/fiber'
import {
  Component,
  memo,
  Suspense,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  type ReactNode,
} from 'react'
import {
  AdditiveBlending,
  Box3,
  BoxGeometry,
  EdgesGeometry,
  Plane,
  Vector3,
} from 'three'
import type { FurnitureItem } from '../../lib/contracts'
import { clampToFloor, DEG } from '../../lib/geometry'
import { useStore } from '../../store'
import { Tag } from '../ui'
import { categoryWash, disposeInk, inkify, inkLine } from './ink'
import { invalidatePlayShadows, preparePlayMaterials } from '../play/materials'

export const floorPlane = new Plane(new Vector3(0, 1, 0), 0)

/** Loads the .glb and fits it to bbox_m (never trust raw mesh scale), bottom-centre at origin. */
function Mesh({ item, play }: { item: FurnitureItem; play: boolean }) {
  const gltf = useGLTF(item.glb_url)
  const renderScene = useThree((s) => s.scene)
  const { object, scale, offset, dispose } = useMemo(() => {
    const clone = gltf.scene.clone(true)
    const dispose = play ? preparePlayMaterials(clone) : () => disposeInk(clone)
    if (!play) inkify(clone, () => categoryWash[item.category])
    const box = new Box3().setFromObject(clone)
    const size = box.getSize(new Vector3())
    const s = new Vector3(
      item.bbox_m.width / (size.x || 1),
      item.bbox_m.height / (size.y || 1),
      item.bbox_m.depth / (size.z || 1),
    )
    const centre = box.getCenter(new Vector3())
    return {
      object: clone,
      dispose,
      scale: s,
      offset: new Vector3(-centre.x * s.x, -box.min.y * s.y, -centre.z * s.z),
    }
  }, [
    gltf.scene,
    item.category,
    item.bbox_m.width,
    item.bbox_m.height,
    item.bbox_m.depth,
    play,
  ])
  useEffect(() => dispose, [dispose])
  useLayoutEffect(
    () => invalidatePlayShadows(renderScene),
    [renderScene, object],
  )
  return (
    <group position={offset} scale={scale}>
      <primitive object={object} dispose={null} />
    </group>
  )
}

/** Dimensioned, visibly labelled placeholder for is_proxy items or meshes that fail to load. */
function ProxyBox({
  item,
  showLabel,
}: {
  item: FurnitureItem
  showLabel: boolean
}) {
  const { width, height, depth } = item.bbox_m
  const renderScene = useThree((s) => s.scene)
  useLayoutEffect(
    () => invalidatePlayShadows(renderScene),
    [renderScene, width, height, depth, showLabel],
  )
  const edges = useMemo(() => {
    const box = new BoxGeometry(width, height, depth)
    const e = new EdgesGeometry(box)
    box.dispose()
    return e
  }, [width, height, depth])
  useEffect(() => () => edges.dispose(), [edges])
  return (
    <mesh
      position={[0, height / 2, 0]}
      castShadow={!showLabel}
      receiveShadow={!showLabel}
    >
      <boxGeometry args={[width, height, depth]} />
      {showLabel ? (
        <meshToonMaterial
          color={categoryWash[item.category]}
          transparent
          opacity={0.8}
        />
      ) : (
        <meshStandardMaterial
          color={categoryWash[item.category]}
          roughness={0.8}
        />
      )}
      {showLabel && (
        <lineSegments
          geometry={edges}
          material={inkLine}
          raycast={() => null}
        />
      )}
      <Html
        position={[0, height / 2 + 0.05, 0]}
        center
        zIndexRange={[10, 0]}
        style={{
          pointerEvents: 'none',
          display: showLabel ? undefined : 'none',
        }}
      >
        <span className="scroll-panel flex items-center gap-1.5 px-2 py-1 whitespace-nowrap">
          <span className="text-[11px] font-medium">{item.name}</span>
          <span className="mono text-[10px] text-ink-medium">
            {width.toFixed(2)} × {depth.toFixed(2)} m
          </span>
          <Tag>Proxy</Tag>
        </span>
      </Html>
    </mesh>
  )
}

/** Renders `fallback` instead of crashing the app when a .glb fails to load. */
export class MeshBoundary extends Component<
  { fallback: ReactNode; children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false }
  static getDerivedStateFromError() {
    return { failed: true }
  }
  render() {
    return this.state.failed ? this.props.fallback : this.props.children
  }
}

/** Red glow over an item the spatial preview flags (collision, outside the floor, blocking a door). */
function OverlapGlow({ item }: { item: FurnitureItem }) {
  const { width, height, depth } = item.bbox_m
  const edges = useMemo(() => {
    const box = new BoxGeometry(width + 0.04, height + 0.04, depth + 0.04)
    const e = new EdgesGeometry(box)
    box.dispose()
    return e
  }, [width, height, depth])
  useEffect(() => () => edges.dispose(), [edges])
  return (
    <group position={[0, height / 2, 0]} raycast={() => null}>
      <mesh raycast={() => null} renderOrder={2}>
        <boxGeometry args={[width + 0.04, height + 0.04, depth + 0.04]} />
        <meshBasicMaterial
          color="#c43a31"
          transparent
          opacity={0.28}
          depthWrite={false}
          blending={AdditiveBlending}
        />
      </mesh>
      <lineSegments geometry={edges} raycast={() => null} renderOrder={3}>
        <lineBasicMaterial color="#c43a31" transparent opacity={0.95} />
      </lineSegments>
    </group>
  )
}

/** One furniture item (selected by id so a drag only re-renders that item). */
export const Furniture = memo(function Furniture({
  id,
  flagged,
}: {
  id: string
  /** Flagged by the spatial preview (lib/spatialPreview.ts): draw it glowing red. */
  flagged: boolean
}) {
  const item = useStore((s) => s.scene.furniture.find((i) => i.id === id))
  const selected = useStore((s) => s.selectedId === id)
  const play = useStore((s) => s.mode === 'play')
  const { select, setPose, commitEdit, setInteracting } = useStore.getState()
  const controls = useThree((s) => s.controls) as { enabled: boolean } | null
  const drag = useRef<{
    dx: number
    dz: number
    moved: boolean
    startX: number
    startZ: number
  } | null>(null)

  // If the item disappears mid-drag (e.g. deleted), don't leave the camera locked.
  useEffect(
    () => () => {
      if (drag.current) {
        drag.current = null
        if (controls) controls.enabled = true
        setInteracting(false)
      }
    },
    [controls, setInteracting],
  )

  // Keyed on size only: the outline is drawn in local space, so a drag (which changes
  // only the pose) must not rebuild the line geometry on every pointer move.
  const bbox = item?.bbox_m
  const outline = useMemo(() => {
    if (!bbox) return []
    const w = bbox.width / 2
    const d = bbox.depth / 2
    return [
      [-w, 0.012, -d],
      [w, 0.012, -d],
      [w, 0.012, d],
      [-w, 0.012, d],
      [-w, 0.012, -d],
    ] as [number, number, number][]
  }, [bbox])

  if (!item) return null

  const hit = (e: ThreeEvent<PointerEvent>) =>
    e.ray.intersectPlane(floorPlane, new Vector3())

  const onDown = (e: ThreeEvent<PointerEvent>) => {
    if (useStore.getState().mode !== 'edit' || useStore.getState().placingHuman)
      return
    e.stopPropagation()
    select(id)
    if (item.is_fixed) return
    const p = hit(e)
    if (!p) return
    drag.current = {
      dx: item.pose.x - p.x,
      dz: item.pose.z - p.z,
      moved: false,
      startX: item.pose.x,
      startZ: item.pose.z,
    }
    ;(e.target as unknown as Element).setPointerCapture(e.pointerId)
    if (controls) controls.enabled = false
    setInteracting(true)
  }
  const onMove = (e: ThreeEvent<PointerEvent>) => {
    if (!drag.current) return
    const p = hit(e)
    if (!p) return
    const { scene } = useStore.getState()
    const live = scene.furniture.find((i) => i.id === id)
    if (!live) return
    const c = clampToFloor(
      scene.floor_polygon,
      live,
      p.x + drag.current.dx,
      p.z + drag.current.dz,
    )
    drag.current.moved = true
    setPose(id, { x: c.x, z: c.z })
  }
  const onUp = (e: ThreeEvent<PointerEvent>) => {
    if (!drag.current) return
    ;(e.target as unknown as Element).releasePointerCapture(e.pointerId)
    const live = useStore.getState().scene.furniture.find((i) => i.id === id)
    const changed =
      live &&
      (live.pose.x !== drag.current.startX ||
        live.pose.z !== drag.current.startZ)
    if (drag.current.moved)
      commitEdit(e.type !== 'pointercancel' && changed ? 'place' : null)
    drag.current = null
    if (controls) controls.enabled = true
    setInteracting(false)
  }

  return (
    <group
      position={[item.pose.x, 0, item.pose.z]}
      rotation={[0, item.pose.yaw_deg * DEG, 0]}
    >
      <group
        onPointerDown={onDown}
        onPointerMove={onMove}
        onPointerUp={onUp}
        onPointerCancel={onUp}
      >
        {item.glb_url && !item.is_proxy ? (
          <MeshBoundary fallback={<ProxyBox item={item} showLabel={!play} />}>
            <Suspense fallback={<ProxyBox item={item} showLabel={!play} />}>
              <Mesh item={item} play={play} />
            </Suspense>
          </MeshBoundary>
        ) : (
          <ProxyBox item={item} showLabel={!play} />
        )}
      </group>
      {!play && flagged && <OverlapGlow item={item} />}
      {!play && (selected || flagged) && (
        <Line
          points={outline}
          color={flagged ? '#c43a31' : '#1c1a17'}
          lineWidth={selected ? 2.5 : 1.5}
        />
      )}
    </group>
  )
})
