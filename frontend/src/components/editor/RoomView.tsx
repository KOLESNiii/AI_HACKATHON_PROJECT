import { OrbitControls } from '@react-three/drei'
import { Canvas } from '@react-three/fiber'
import { Suspense, useMemo } from 'react'
import { bounds } from '../../lib/geometry'
import { useStore } from '../../store'
import { Furniture } from './Furniture'
import { DoorSwings, ProposedPoses } from './Overlays'
import { Shell } from './Shell'

/** Interactive room in the ink "clarity" style (Canvas/Room Render in Figma). */
export function RoomView({
  collidingIds,
  blockedDoorIds,
}: {
  collidingIds: Set<string>
  blockedDoorIds: Set<string>
}) {
  const scene = useStore((s) => s.scene)
  const layers = useStore((s) => s.layers)
  const proposal = useStore((s) => s.proposal)
  const select = useStore((s) => s.select)

  const { centre, span } = useMemo(() => {
    const b = bounds(scene.floor_polygon)
    return {
      centre: [(b.minX + b.maxX) / 2, 0, (b.minZ + b.maxZ) / 2] as [
        number,
        number,
        number,
      ],
      span: Math.max(b.maxX - b.minX, b.maxZ - b.minZ),
    }
  }, [scene.floor_polygon])

  return (
    <Canvas
      gl={{ alpha: true, antialias: true }}
      camera={{
        fov: 38,
        position: [
          centre[0] - span * 0.9,
          span * 1.45,
          centre[2] + span * 1.35,
        ],
        near: 0.05,
        far: 100,
      }}
      onPointerMissed={() => select(null)}
      dpr={[1, 2]}
    >
      <ambientLight intensity={1.6} />
      <directionalLight
        position={[centre[0] + 3, 8, centre[2] + 5]}
        intensity={1.4}
      />
      <Suspense fallback={null}>
        <Shell scene={scene} />
      </Suspense>
      {scene.furniture.map((item) => (
        <Furniture
          key={item.id}
          item={item}
          colliding={collidingIds.has(item.id)}
        />
      ))}
      {layers.clearance && (
        <DoorSwings scene={scene} blockedDoorIds={blockedDoorIds} />
      )}
      {proposal && <ProposedPoses scene={scene} poses={proposal.poses} />}
      <OrbitControls
        makeDefault
        target={centre}
        maxPolarAngle={Math.PI / 2.15}
        minDistance={2}
        maxDistance={span * 4}
        enableDamping
      />
    </Canvas>
  )
}
