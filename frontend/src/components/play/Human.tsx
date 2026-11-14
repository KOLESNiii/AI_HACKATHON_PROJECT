import { type ThreeEvent } from '@react-three/fiber'
import { useRef, type RefObject } from 'react'
import type { Pose2D } from '../../lib/contracts'
import { DEG } from '../../lib/geometry'
import { BODY_RADIUS_M, canStand } from '../../lib/walk'
import { useStore } from '../../store'
import type { PlayControllerHandle } from './controls'

/** A lightweight human-shaped scale reference; no downloaded character assets. */
function Mannequin({
  pose,
  valid,
  preview,
}: {
  pose: Pose2D
  valid: boolean
  preview: boolean
}) {
  const color = valid ? '#4e6352' : '#c43a31'
  const material = (
    <meshToonMaterial
      color={color}
      transparent
      opacity={preview ? 0.5 : 0.95}
    />
  )
  return (
    <group position={[pose.x, 0, pose.z]} rotation={[0, pose.yaw_deg * DEG, 0]}>
      <mesh position={[0, 1.64, 0]}>
        <sphereGeometry args={[0.16, 16, 12]} />
        {material}
      </mesh>
      <mesh position={[0, 1.15, 0]}>
        <capsuleGeometry args={[0.17, 0.42, 4, 12]} />
        {material}
      </mesh>
      {[-1, 1].map((side) => (
        <group key={side}>
          <mesh position={[side * 0.105, 0.44, 0]}>
            <capsuleGeometry args={[0.075, 0.72, 4, 8]} />
            {material}
          </mesh>
          <mesh
            position={[side * 0.25, 1.13, 0]}
            rotation={[0, 0, side * 0.12]}
          >
            <capsuleGeometry args={[0.055, 0.48, 4, 8]} />
            {material}
          </mesh>
        </group>
      ))}
      <mesh position={[0, 1.65, 0.145]} raycast={() => null}>
        <boxGeometry args={[0.15, 0.045, 0.035]} />
        <meshBasicMaterial color="#f7efe2" />
      </mesh>
      <mesh
        position={[0, 0.012, 0]}
        rotation={[-Math.PI / 2, 0, 0]}
        raycast={() => null}
      >
        <ringGeometry
          args={[BODY_RADIUS_M - 0.015, BODY_RADIUS_M + 0.015, 48]}
        />
        <meshBasicMaterial color={color} transparent opacity={0.8} />
      </mesh>
    </group>
  )
}

export function Human({
  controller,
}: {
  controller: RefObject<PlayControllerHandle | null>
}) {
  const human = useStore((s) => s.human)
  const placing = useStore((s) => s.placingHuman)
  const preview = useStore((s) => s.humanPreview)
  const scene = useStore((s) => s.scene)
  const drag = useRef<{ dx: number; dz: number } | null>(null)
  const pose = placing ? (preview ?? human) : human
  if (!pose) return null
  const point = (e: ThreeEvent<PointerEvent>) => {
    const p = controller.current?.floorPoint(e.clientX, e.clientY)
    return p
      ? { x: p.x + (drag.current?.dx ?? 0), z: p.z + (drag.current?.dz ?? 0) }
      : null
  }
  return (
    <group
      onPointerDown={(e) => {
        e.stopPropagation()
        const p = controller.current?.floorPoint(e.clientX, e.clientY)
        if (!p || !human) return
        if (e.button !== 0 || !useStore.getState().beginHumanPlacement()) return
        drag.current = { dx: human.x - p.x, dz: human.z - p.z }
        ;(e.target as unknown as Element).setPointerCapture(e.pointerId)
        useStore.getState().previewHuman(point(e))
      }}
      onPointerMove={(e) => {
        if (!useStore.getState().placingHuman) return
        e.stopPropagation()
        useStore.getState().previewHuman(point(e))
      }}
      onPointerUp={(e) => {
        if (!useStore.getState().placingHuman) return
        e.stopPropagation()
        useStore.getState().finishHumanPlacement(point(e))
        drag.current = null
        ;(e.target as unknown as Element).releasePointerCapture(e.pointerId)
      }}
      onPointerCancel={() => {
        drag.current = null
        useStore.getState().cancelHumanPlacement()
      }}
    >
      <Mannequin
        pose={pose}
        valid={(!placing || preview != null) && canStand(pose, scene)}
        preview={placing}
      />
    </group>
  )
}
