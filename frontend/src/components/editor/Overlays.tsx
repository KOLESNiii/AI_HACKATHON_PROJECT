import { Line } from '@react-three/drei'
import { useMemo } from 'react'
import { DoubleSide, Shape } from 'three'
import type { Pose2D, RoomScene } from '../../lib/contracts'
import { doorSector, footprint, type Pt } from '../../lib/geometry'

const Y = 0.01

/** Flat filled polygon on the floor plane (shape XY rotated onto XZ). */
function FloorFill({
  pts,
  color,
  opacity,
}: {
  pts: Pt[]
  color: string
  opacity: number
}) {
  const shape = useMemo(() => {
    const s = new Shape()
    pts.forEach((p, i) => (i ? s.lineTo(p.x, -p.z) : s.moveTo(p.x, -p.z)))
    return s
  }, [pts])
  return (
    <mesh
      rotation={[-Math.PI / 2, 0, 0]}
      position={[0, Y, 0]}
      raycast={() => null}
    >
      <shapeGeometry args={[shape]} />
      <meshBasicMaterial
        color={color}
        transparent
        opacity={opacity}
        side={DoubleSide}
        depthWrite={false}
      />
    </mesh>
  )
}

const loop = (pts: Pt[]) =>
  [...pts, pts[0]].map((p) => [p.x, Y + 0.004, p.z] as [number, number, number])

/** Clearance & Doors layer: door swings, green when clear and vermilion when blocked. */
export function DoorSwings({
  scene,
  blockedDoorIds,
}: {
  scene: RoomScene
  blockedDoorIds: Set<string>
}) {
  return (
    <>
      {scene.doors.map((d) => {
        const pts = doorSector(d, scene.walls)
        if (pts.length < 3) return null
        const color = blockedDoorIds.has(d.id) ? '#c43a31' : '#4e6352'
        return (
          <group key={d.id}>
            <FloorFill pts={pts} color={color} opacity={0.18} />
            <Line points={loop(pts)} color={color} lineWidth={1.5} />
          </group>
        )
      })}
    </>
  )
}

/** Auto-Fix preview: dashed outlines of proposed poses. */
export function ProposedPoses({
  scene,
  poses,
}: {
  scene: RoomScene
  poses: Record<string, Pose2D>
}) {
  return (
    <>
      {scene.furniture
        .filter((i) => poses[i.id])
        .map((i) => {
          const fp = footprint({ ...i, pose: poses[i.id] })
          return (
            <group key={i.id}>
              <FloorFill pts={fp} color="#1c1a17" opacity={0.06} />
              <Line
                points={loop(fp)}
                color="#1c1a17"
                lineWidth={1.5}
                dashed
                dashSize={0.08}
                gapSize={0.06}
              />
            </group>
          )
        })}
    </>
  )
}
