import { OrbitControls } from '@react-three/drei'
import { Canvas } from '@react-three/fiber'
import { Suspense, useEffect, useMemo } from 'react'
import { useShallow } from 'zustand/react/shallow'
import { bounds } from '../../lib/geometry'
import { useStore } from '../../store'
import { Furniture, MeshBoundary } from './Furniture'
import { SelectionTools } from './SelectionTools'
import { Shell } from './Shell'

/** Interactive room in the ink "clarity" style (Canvas/Room Render in Figma). */
export function RoomView() {
  // Subscribe to stable parts only; each Furniture reads its own pose, so drags
  // re-render just the moving item.
  const shellUrl = useStore((s) => s.scene.shell_glb_url)
  const walls = useStore((s) => s.scene.walls)
  const floor = useStore((s) => s.scene.floor_polygon)
  const ids = useStore(useShallow((s) => s.scene.furniture.map((i) => i.id)))
  const select = useStore((s) => s.select)
  const toast = useStore((s) => s.toast)

  const { centre, span } = useMemo(() => {
    const b = bounds(floor)
    return {
      centre: [(b.minX + b.maxX) / 2, 0, (b.minZ + b.maxZ) / 2] as [
        number,
        number,
        number,
      ],
      span: Math.max(b.maxX - b.minX, b.maxZ - b.minZ),
    }
  }, [floor])

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
      <MeshBoundary fallback={<ShellFailed onFail={toast} />}>
        <Suspense fallback={null}>
          <Shell url={shellUrl} walls={walls} />
        </Suspense>
      </MeshBoundary>
      {ids.map((id) => (
        <Furniture key={id} id={id} />
      ))}
      <SelectionTools />
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

/** Shown (as nothing in 3D, plus a toast) when the room shell .glb can't load. */
function ShellFailed({ onFail }: { onFail: (text: string) => void }) {
  useEffect(() => onFail('The room shell could not be loaded.'), [onFail])
  return null
}
