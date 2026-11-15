import { Environment, Lightformer } from '@react-three/drei'
import { useThree } from '@react-three/fiber'
import {
  memo,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from 'react'
import { Object3D, RectAreaLight, Vector3 } from 'three'
import { RectAreaLightUniformsLib } from 'three/addons/lights/RectAreaLightUniformsLib.js'
import type { RoomScene } from '../../lib/contracts'
import { bounds, inwardNormal } from '../../lib/geometry'
import {
  ceilingLights,
  roomHeight,
  sunlightAt,
  windowLights,
  type LightPosition,
  type PlayLightingSettings,
  type WindowLight,
} from '../../lib/lighting'
import { useStore } from '../../store'
import { invalidatePlayShadows } from './materials'

const WARM_LIGHT = '#ffdbad'
// These shared lookup textures belong to the lighting library, not to each window.
RectAreaLightUniformsLib.init()

/** Captures stay bounded at 5 Hz while direct lights follow every slider change. */
function useEnvironmentSettings(settings: PlayLightingSettings) {
  const [sample, setSample] = useState(settings)
  const last = useRef(0)
  useEffect(() => {
    const timer = setTimeout(
      () => {
        last.current = performance.now()
        setSample(settings)
      },
      Math.max(0, 200 - (performance.now() - last.current)),
    )
    return () => clearTimeout(timer)
  }, [settings])
  return sample
}

export function PlayLighting() {
  const renderScene = useThree((s) => s.scene)
  const scene = useStore((s) => s.scene)
  const settings = useStore((s) => s.playLighting)
  const windows = useMemo(() => windowLights(scene), [scene])
  const ceiling = useMemo(() => ceilingLights(scene), [scene])
  const sun = sunlightAt(settings.timeOfDay, scene.north_compass_deg ?? 0)
  const daylight = windows.length ? sun.brightness : 0
  const artificial = settings.artificialPercent / 100
  const sampled = useEnvironmentSettings(settings)
  useLayoutEffect(
    () => invalidatePlayShadows(renderScene),
    [renderScene, settings, scene],
  )
  const { centre, radius, distance } = useMemo(() => {
    const b = bounds(scene.floor_polygon)
    const radius =
      Math.hypot(b.maxX - b.minX, b.maxZ - b.minZ, roomHeight(scene)) / 2 + 0.5
    return {
      centre: new Vector3(
        (b.minX + b.maxX) / 2,
        roomHeight(scene) / 2,
        (b.minZ + b.maxZ) / 2,
      ),
      radius,
      distance: radius * 3,
    }
  }, [scene])
  const target = useMemo(() => {
    const object = new Object3D()
    object.position.copy(centre)
    return object
  }, [centre])
  const ceilingTargets = useMemo(
    () =>
      ceiling.map(([x, , z]) => {
        const object = new Object3D()
        object.position.set(x, 0, z)
        return object
      }),
    [ceiling],
  )
  const position = new Vector3(...sun.direction)
    .multiplyScalar(distance)
    .add(centre)

  return (
    <>
      <color attach="background" args={[sun.sky]} />
      <primitive object={target} />
      <directionalLight
        position={position}
        target={target}
        color={sun.color}
        intensity={windows.length ? sun.intensity : 0}
        castShadow
        shadow-autoUpdate={false}
        shadow-mapSize={[2048, 2048]}
        shadow-camera-left={-radius}
        shadow-camera-right={radius}
        shadow-camera-top={radius}
        shadow-camera-bottom={-radius}
        shadow-camera-near={0.1}
        shadow-camera-far={distance + radius * 2}
        shadow-normalBias={0.015}
        shadow-bias={-0.0001}
      />
      {windows.map((win) => (
        <WindowFill key={win.id} window={win} intensity={daylight * 1.8} />
      ))}
      <ambientLight color={WARM_LIGHT} intensity={artificial * 0.16} />
      {ceiling.map((point, i) => (
        <group key={i}>
          <primitive object={ceilingTargets[i]} />
          <spotLight
            position={point}
            target={ceilingTargets[i]}
            color={WARM_LIGHT}
            intensity={artificial * 65}
            angle={1.35}
            penumbra={0.65}
            decay={2}
            castShadow={i === 0}
            shadow-autoUpdate={false}
            shadow-mapSize={[1024, 1024]}
            shadow-camera-near={0.05}
            shadow-camera-far={radius * 4}
            shadow-normalBias={0.01}
            shadow-bias={-0.0001}
          />
          <mesh
            position={[point[0], point[1] + 0.02, point[2]]}
            rotation={[Math.PI / 2, 0, 0]}
          >
            <circleGeometry args={[0.14, 24]} />
            <meshStandardMaterial
              color="#eee8de"
              emissive={WARM_LIGHT}
              emissiveIntensity={artificial * 4}
              roughness={0.65}
            />
          </mesh>
        </group>
      ))}
      <DoorLightBlockers scene={scene} />
      <LightingEnvironment
        settings={sampled}
        windows={windows}
        ceiling={ceiling}
        centre={centre}
        north={scene.north_compass_deg ?? 0}
      />
    </>
  )
}

function WindowFill({
  window: win,
  intensity,
}: {
  window: WindowLight
  intensity: number
}) {
  const light = useMemo(() => {
    const light = new RectAreaLight('#dceaff', 0, win.width, win.height)
    light.position.set(...win.position)
    light.rotation.y = win.rotationY
    return light
  }, [win])
  useEffect(() => () => light.dispose(), [light])
  return <primitive object={light} intensity={intensity} />
}

/** Closed adjoining rooms are absent from this shell; only windows admit exterior sun. */
function DoorLightBlockers({ scene }: { scene: RoomScene }) {
  const blockers = useMemo(
    () =>
      scene.doors.flatMap((door) => {
        const wall = scene.walls.find((w) => w.id === door.wall_id)
        if (!wall) return []
        const normal = inwardNormal(wall)
        const side = door.swings_into_room
          ? normal
          : { x: -normal.x, z: -normal.z }
        const leaf = door.swing_clockwise
          ? { x: side.z, z: -side.x }
          : { x: -side.z, z: side.x }
        return [
          {
            id: door.id,
            position: [
              door.hinge_pos.x + (leaf.x * door.width_m) / 2,
              door.head_height_m / 2,
              door.hinge_pos.z + (leaf.z * door.width_m) / 2,
            ] as LightPosition,
            rotation: -Math.atan2(leaf.z, leaf.x),
            width: door.width_m,
            height: door.head_height_m,
          },
        ]
      }),
    [scene],
  )
  return blockers.map((door) => (
    <mesh
      key={door.id}
      position={door.position}
      rotation={[0, door.rotation, 0]}
      castShadow
      raycast={() => null}
    >
      <boxGeometry args={[door.width, door.height, 0.08]} />
      <meshBasicMaterial colorWrite={false} depthWrite={false} />
    </mesh>
  ))
}

/** A local procedural reflection environment; no remote HDRIs or room recaptures. */
const LightingEnvironment = memo(function LightingEnvironment({
  settings,
  windows,
  ceiling,
  centre,
  north,
}: {
  settings: PlayLightingSettings
  windows: WindowLight[]
  ceiling: LightPosition[]
  centre: Vector3
  north: number
}) {
  const sun = sunlightAt(settings.timeOfDay, north)
  const artificial = settings.artificialPercent / 100
  return (
    <Environment resolution={128} frames={1} environmentIntensity={0.3}>
      {windows.map((win) => (
        <Lightformer
          key={win.id}
          position={[
            win.position[0] - centre.x,
            win.position[1] - centre.y,
            win.position[2] - centre.z,
          ]}
          rotation={[0, win.rotationY, 0]}
          scale={[win.width, win.height]}
          color={sun.color}
          intensity={sun.brightness * 3}
        />
      ))}
      {ceiling.map((point, i) => (
        <Lightformer
          key={i}
          position={[
            point[0] - centre.x,
            point[1] - centre.y,
            point[2] - centre.z,
          ]}
          rotation={[Math.PI / 2, 0, 0]}
          scale={[0.7, 0.7]}
          color={WARM_LIGHT}
          intensity={artificial * 5}
        />
      ))}
    </Environment>
  )
})
