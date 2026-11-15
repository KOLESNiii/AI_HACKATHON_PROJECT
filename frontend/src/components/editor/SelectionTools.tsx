import { Html } from '@react-three/drei'
import { useThree, type ThreeEvent } from '@react-three/fiber'
import { useEffect, useRef, useState } from 'react'
import { DoubleSide, Vector3 } from 'three'
import type { FurnitureItem } from '../../lib/contracts'
import { DEG, planAngle } from '../../lib/geometry'
import { useStore } from '../../store'
import { Button } from '../ui'
import { floorPlane } from './Furniture'

const Y = 0.015

/**
 * Rotation ring on the floor around the selected item. Drag it to rotate in 1° steps;
 * the vermilion handle marks the item's front.
 */
function RotationRing({ item }: { item: FurnitureItem }) {
  const { setPose, commitEdit, setInteracting } = useStore.getState()
  const controls = useThree((s) => s.controls) as { enabled: boolean } | null
  const drag = useRef<{ startYaw: number; startAngle: number } | null>(null)
  const [active, setActive] = useState(false)
  // Reset the grab cursor if the ring disappears while hovered (e.g. item deleted).
  useEffect(
    () => () => {
      document.body.style.cursor = ''
      if (drag.current) {
        drag.current = null
        if (controls) controls.enabled = true
        setInteracting(false)
      }
    },
    [controls, setInteracting],
  )
  const r = Math.hypot(item.bbox_m.width, item.bbox_m.depth) / 2 + 0.2
  const yaw = item.pose.yaw_deg * DEG

  const angleAt = (e: ThreeEvent<PointerEvent>) => {
    const p = e.ray.intersectPlane(floorPlane, new Vector3())
    return p ? planAngle(p.x - item.pose.x, p.z - item.pose.z) : null
  }
  const onDown = (e: ThreeEvent<PointerEvent>) => {
    e.stopPropagation()
    const a = angleAt(e)
    if (a == null || item.is_fixed) return
    drag.current = { startYaw: item.pose.yaw_deg, startAngle: a }
    ;(e.target as unknown as Element).setPointerCapture(e.pointerId)
    if (controls) controls.enabled = false
    setInteracting(true)
    setActive(true)
  }
  const onMove = (e: ThreeEvent<PointerEvent>) => {
    if (!drag.current) return
    const a = angleAt(e)
    if (a == null) return
    const next = Math.round(drag.current.startYaw + a - drag.current.startAngle)
    setPose(item.id, { yaw_deg: ((next % 360) + 360) % 360 })
  }
  const onUp = (e: ThreeEvent<PointerEvent>) => {
    if (!drag.current) return
    ;(e.target as unknown as Element).releasePointerCapture(e.pointerId)
    const changed =
      useStore.getState().scene.furniture.find((i) => i.id === item.id)?.pose
        .yaw_deg !== drag.current.startYaw
    drag.current = null
    if (controls) controls.enabled = true
    setInteracting(false)
    setActive(false)
    if (changed) commitEdit(e.type === 'pointercancel' ? null : 'rotate')
  }

  if (item.is_fixed) return null
  return (
    <group position={[item.pose.x, Y, item.pose.z]}>
      {/* Visible ink ring */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} raycast={() => null}>
        <ringGeometry args={[r - 0.012, r + 0.012, 96]} />
        <meshBasicMaterial
          color={active ? '#c43a31' : '#1c1a17'}
          transparent
          opacity={active ? 0.9 : 0.6}
          side={DoubleSide}
          depthWrite={false}
        />
      </mesh>
      {/* Wider invisible band that is easy to grab */}
      <mesh
        rotation={[-Math.PI / 2, 0, 0]}
        onPointerDown={onDown}
        onPointerMove={onMove}
        onPointerUp={onUp}
        onPointerCancel={onUp}
        onPointerOver={() => (document.body.style.cursor = 'grab')}
        onPointerOut={() => (document.body.style.cursor = '')}
      >
        <ringGeometry args={[r - 0.12, r + 0.12, 96]} />
        <meshBasicMaterial
          transparent
          opacity={0}
          depthWrite={false}
          side={DoubleSide}
        />
      </mesh>
      {/* Front handle */}
      <mesh
        position={[Math.sin(yaw) * r, 0.01, Math.cos(yaw) * r]}
        raycast={() => null}
      >
        <cylinderGeometry args={[0.06, 0.06, 0.02, 24]} />
        <meshBasicMaterial color="#c43a31" />
      </mesh>
      {active && (
        <Html position={[0, 0.05, 0]} center style={{ pointerEvents: 'none' }}>
          <span className="scroll-panel mono px-2 py-1 text-[12px]">
            {Math.round(item.pose.yaw_deg)}°
          </span>
        </Html>
      )}
    </group>
  )
}

/** Action bar above the selected item. */
function SelectionBar({ item }: { item: FurnitureItem }) {
  const { snapItem, rotateItem, resetRotation, deleteItem } =
    useStore.getState()
  if (item.is_fixed) return null
  return (
    <Html
      position={[item.pose.x, item.bbox_m.height + 0.35, item.pose.z]}
      center
      zIndexRange={[20, 0]}
    >
      <div
        className="scroll-panel flex items-center gap-1.5 p-1.5 whitespace-nowrap select-none"
        onPointerDown={(e) => e.stopPropagation()}
      >
        <Button onClick={() => snapItem(item.id)}>Snap to wall</Button>
        <Button
          title="Rotate counterclockwise 90° (Q)"
          onClick={() => rotateItem(item.id, 90)}
        >
          ↶ 90°
        </Button>
        <Button
          title="Rotate clockwise 90° (E)"
          onClick={() => rotateItem(item.id, -90)}
        >
          ↷ 90°
        </Button>
        <Button
          onClick={() => resetRotation(item.id)}
          disabled={item.pose.yaw_deg === 0}
        >
          Reset rotation
        </Button>
        <Button onClick={() => deleteItem(item.id)}>Delete</Button>
      </div>
    </Html>
  )
}

export function SelectionTools() {
  const item = useStore((s) =>
    s.scene.furniture.find((i) => i.id === s.selectedId),
  )
  if (!item) return null
  return (
    <>
      <RotationRing item={item} />
      <SelectionBar item={item} />
    </>
  )
}
