import { OrbitControls } from '@react-three/drei'
import { Canvas, useThree } from '@react-three/fiber'
import { Suspense, useEffect, useMemo, useState, type RefObject } from 'react'
import type { PerspectiveCamera } from 'three'
import { useShallow } from 'zustand/react/shallow'
import { bounds } from '../../lib/geometry'
import { flaggedItemIds, spatialPreview } from '../../lib/spatialPreview'
import { useStore } from '../../store'
import type { PlayControllerHandle } from '../play/controls'
import { Human } from '../play/Human'
import { PlayController } from '../play/PlayController'
import { DoorSwings } from './DoorSwings'
import { Furniture, MeshBoundary } from './Furniture'
import { KeyboardControls } from './KeyboardControls'
import { SelectionTools } from './SelectionTools'
import { Shell } from './Shell'

/** Interactive room in the ink "clarity" style (Canvas/Room Render in Figma). */
export function RoomView({
  controller,
}: {
  controller: RefObject<PlayControllerHandle | null>
}) {
  // Subscribe to stable parts only; each Furniture reads its own pose, so drags
  // re-render just the moving item.
  const shellUrl = useStore((s) => s.scene.shell_glb_url)
  const walls = useStore((s) => s.scene.walls)
  const floor = useStore((s) => s.scene.floor_polygon)
  const doors = useStore((s) => s.scene.doors)
  const ids = useStore(useShallow((s) => s.scene.furniture.map((i) => i.id)))
  // Live preview of the spatial engine's checks. Re-renders this view only when the
  // set of flagged items or blocked doors changes.
  const flagged = useStore(
    useShallow((s) => {
      const p = spatialPreview(s.scene)
      return [
        ...flaggedItemIds(p),
        ...p.blocked_doors.map((d) => `door:${d.door_id}`),
      ]
    }),
  )
  const select = useStore((s) => s.select)
  const toast = useStore((s) => s.toast)
  const play = useStore((s) => s.mode === 'play')

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

  const cameraOptions = useMemo(
    () => ({
      fov: 38,
      position: [
        centre[0] - span * 0.9,
        span * 1.45,
        centre[2] + span * 1.35,
      ] as [number, number, number],
      near: 0.05,
      far: 100,
    }),
    [centre, span],
  )

  return (
    <Canvas
      gl={{ alpha: true, antialias: true }}
      camera={cameraOptions}
      onPointerMissed={() => {
        if (useStore.getState().mode === 'edit') select(null)
      }}
      dpr={[1, 2]}
    >
      <ambientLight intensity={1.6} />
      <directionalLight
        position={[centre[0] + 3, 8, centre[2] + 5]}
        intensity={1.4}
      />
      <MeshBoundary fallback={<ShellFailed onFail={toast} />}>
        <Suspense fallback={null}>
          <Shell url={shellUrl} walls={walls} cutaway={!play} />
        </Suspense>
      </MeshBoundary>
      {!play && (
        <DoorSwings
          doors={doors}
          walls={walls}
          blocked={flagged
            .filter((f) => f.startsWith('door:'))
            .map((f) => f.slice(5))}
        />
      )}
      {ids.map((id) => (
        <Furniture key={id} id={id} flagged={flagged.includes(id)} />
      ))}
      {!play && <SelectionTools />}
      <Navigation centre={centre} span={span} controller={controller} />
    </Canvas>
  )
}

function Navigation({
  centre,
  span,
  controller,
}: {
  centre: [number, number, number]
  span: number
  controller: RefObject<PlayControllerHandle | null>
}) {
  const currentCamera = useThree((s) => s.camera)
  const [editorCamera] = useState(() => currentCamera as PerspectiveCamera)
  const play = useStore((s) => s.mode === 'play')
  const interacting = useStore((s) => s.interacting)
  return (
    <>
      <OrbitControls
        camera={editorCamera}
        makeDefault
        target={centre}
        enabled={!play && !interacting}
        maxPolarAngle={Math.PI / 2.15}
        minDistance={2}
        maxDistance={span * 4}
        enableDamping
      />
      <KeyboardControls speed={Math.max(1, span * 0.35)} />
      <PlayController controllerRef={controller} editorCamera={editorCamera} />
      {!play && <Human controller={controller} />}
    </>
  )
}

/** Shown (as nothing in 3D, plus a toast) when the room shell .glb can't load. */
function ShellFailed({ onFail }: { onFail: (text: string) => void }) {
  useEffect(() => onFail('The room shell could not be loaded.'), [onFail])
  return null
}
