import { useGLTF } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useEffect, useMemo } from 'react'
import type { Object3D } from 'three'
import type { RoomScene } from '../../lib/contracts'
import { disposeInk, inkify } from './ink'

/**
 * Room shell in room coordinates (not normalised). Nodes: floor, ceiling, wall_<id>.
 * The ceiling is hidden and walls between the camera and the room are cut away (dollhouse view).
 */
export function Shell({ scene }: { scene: RoomScene }) {
  const gltf = useGLTF(scene.shell_glb_url)
  const root = useMemo(() => {
    const clone = gltf.scene.clone(true)
    inkify(clone, (m) =>
      m.name.startsWith('floor') || m.parent?.name.startsWith('floor')
        ? '#d9b88a'
        : '#f1e8d8',
    )
    return clone
  }, [gltf.scene])

  const walls = useMemo(() => {
    const out: {
      node: Object3D
      sx: number
      sz: number
      nx: number
      nz: number
    }[] = []
    for (const w of scene.walls) {
      const node = root.getObjectByName(`wall_${w.id}`)
      if (!node) continue
      const dx = w.end.x - w.start.x,
        dz = w.end.z - w.start.z
      out.push({ node, sx: w.start.x, sz: w.start.z, nx: dz, nz: -dx }) // outward normal
    }
    const ceiling = root.getObjectByName('ceiling')
    if (ceiling) ceiling.visible = false
    return out
  }, [root, scene.walls])

  useEffect(() => () => disposeInk(root), [root])

  useFrame(({ camera }) => {
    for (const w of walls) {
      const outside =
        (camera.position.x - w.sx) * w.nx + (camera.position.z - w.sz) * w.nz >
        0
      w.node.visible = !outside
    }
  })

  return <primitive object={root} />
}
