import { Html, Line, useGLTF } from '@react-three/drei'
import { useThree, type ThreeEvent } from '@react-three/fiber'
import {
  Component,
  Suspense,
  useEffect,
  useMemo,
  useRef,
  type ReactNode,
} from 'react'
import {
  Box3,
  BoxGeometry,
  EdgesGeometry,
  Plane,
  Vector3,
  type Group,
} from 'three'
import type { FurnitureItem } from '../../lib/contracts'
import { clampToFloor, footprint } from '../../lib/geometry'
import { useStore } from '../../store'
import { categoryWash, disposeInk, inkify, inkLine } from './ink'
import { ObjectPill } from './ObjectPill'

const DEG = Math.PI / 180
const floorPlane = new Plane(new Vector3(0, 1, 0), 0)

/** Loads the .glb and fits it to bbox_m (never trust raw mesh scale), bottom-centre at origin. */
function Mesh({ item }: { item: FurnitureItem }) {
  const gltf = useGLTF(item.glb_url)
  const { object, scale, offset } = useMemo(() => {
    const clone = gltf.scene.clone(true)
    inkify(clone, () => categoryWash[item.category])
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
      scale: s,
      offset: new Vector3(-centre.x * s.x, -box.min.y * s.y, -centre.z * s.z),
    }
  }, [
    gltf.scene,
    item.category,
    item.bbox_m.width,
    item.bbox_m.height,
    item.bbox_m.depth,
  ])
  useEffect(() => () => disposeInk(object), [object])
  return (
    <group position={offset} scale={scale}>
      <primitive object={object} />
    </group>
  )
}

/** Dimensioned placeholder for items without a mesh (or while/if it fails to load). */
function ProxyBox({ item }: { item: FurnitureItem }) {
  const { width, height, depth } = item.bbox_m
  const edges = useMemo(() => {
    const box = new BoxGeometry(width, height, depth)
    const e = new EdgesGeometry(box)
    box.dispose()
    return e
  }, [width, height, depth])
  useEffect(() => () => edges.dispose(), [edges])
  return (
    <mesh position={[0, height / 2, 0]}>
      <boxGeometry args={[width, height, depth]} />
      <meshToonMaterial
        color={categoryWash[item.category]}
        transparent
        opacity={0.8}
      />
      <lineSegments geometry={edges} material={inkLine} raycast={() => null} />
    </mesh>
  )
}

class MeshBoundary extends Component<
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

export function Furniture({
  item,
  colliding,
}: {
  item: FurnitureItem
  colliding: boolean
}) {
  const selected = useStore((s) => s.selectedId === item.id)
  const showClearance = useStore((s) => s.layers.clearance)
  const { select, moveItem, commitEdit, setDragging } = useStore.getState()
  const controls = useThree((s) => s.controls) as { enabled: boolean } | null
  const drag = useRef<{ dx: number; dz: number; moved: boolean } | null>(null)
  const group = useRef<Group>(null)

  const hit = (e: ThreeEvent<PointerEvent>) =>
    e.ray.intersectPlane(floorPlane, new Vector3())

  const onDown = (e: ThreeEvent<PointerEvent>) => {
    e.stopPropagation()
    select(item.id)
    if (item.is_fixed) return
    const p = hit(e)
    if (!p) return
    drag.current = {
      dx: item.pose.x - p.x,
      dz: item.pose.z - p.z,
      moved: false,
    }
    ;(e.target as unknown as Element).setPointerCapture(e.pointerId)
    if (controls) controls.enabled = false
    setDragging(true)
  }
  const onMove = (e: ThreeEvent<PointerEvent>) => {
    if (!drag.current) return
    const p = hit(e)
    if (!p) return
    const { scene } = useStore.getState()
    const live = scene.furniture.find((i) => i.id === item.id)
    if (!live) return
    const c = clampToFloor(
      scene,
      live,
      p.x + drag.current.dx,
      p.z + drag.current.dz,
    )
    drag.current.moved = true
    moveItem(item.id, c.x, c.z)
  }
  const onUp = (e: ThreeEvent<PointerEvent>) => {
    if (!drag.current) return
    ;(e.target as unknown as Element).releasePointerCapture(e.pointerId)
    if (drag.current.moved) commitEdit()
    drag.current = null
    if (controls) controls.enabled = true
    setDragging(false)
  }

  const outline = useMemo(() => {
    const local = footprint({ ...item, pose: { x: 0, z: 0, yaw_deg: 0 } })
    return [...local, local[0]].map(
      (p) => [p.x, 0.012, p.z] as [number, number, number],
    )
  }, [item])

  const outlineColor =
    showClearance && colliding ? '#c43a31' : selected ? '#1c1a17' : null

  return (
    <group
      ref={group}
      position={[item.pose.x, 0, item.pose.z]}
      rotation={[0, item.pose.yaw_deg * DEG, 0]}
    >
      <group
        onPointerDown={onDown}
        onPointerMove={onMove}
        onPointerUp={onUp}
        onPointerCancel={onUp}
      >
        {item.glb_url ? (
          <MeshBoundary fallback={<ProxyBox item={item} />}>
            <Suspense fallback={<ProxyBox item={item} />}>
              <Mesh item={item} />
            </Suspense>
          </MeshBoundary>
        ) : (
          <ProxyBox item={item} />
        )}
      </group>
      {outlineColor && (
        <Line
          points={outline}
          color={outlineColor}
          lineWidth={selected ? 2.5 : 2}
        />
      )}
      {selected && (
        <Html
          position={[0, item.bbox_m.height + 0.3, 0]}
          center
          zIndexRange={[20, 0]}
          style={{ pointerEvents: 'auto' }}
        >
          <ObjectPill item={item} />
        </Html>
      )}
    </group>
  )
}
