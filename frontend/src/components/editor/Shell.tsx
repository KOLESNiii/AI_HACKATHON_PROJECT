import { useGLTF } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { memo, useEffect, useLayoutEffect, useMemo } from 'react'
import type { Object3D } from 'three'
import type { WallSegment } from '../../lib/contracts'
import { inwardNormal } from '../../lib/geometry'
import { disposeInk, inkify } from './ink'

/**
 * Room shell in room coordinates (not normalised). Nodes: floor, ceiling, wall_<id>.
 * The ceiling is hidden and walls between the camera and the room are cut away (dollhouse view).
 * Memoised on url + walls so furniture drags don't re-render it.
 */
export const Shell = memo(function Shell({
  url,
  walls,
  cutaway = true,
}: {
  url: string
  walls: WallSegment[]
  cutaway?: boolean
}) {
  const gltf = useGLTF(url)
  const root = useMemo(() => {
    const clone = gltf.scene.clone(true)
    inkify(clone, (m) =>
      m.name.startsWith('floor') || m.parent?.name.startsWith('floor')
        ? '#d9b88a'
        : '#f1e8d8',
    )
    return clone
  }, [gltf.scene])
  useEffect(() => () => disposeInk(root), [root])

  const wallNodes = useMemo(() => {
    const out: {
      node: Object3D
      sx: number
      sz: number
      nx: number
      nz: number
    }[] = []
    for (const w of walls) {
      const node = root.getObjectByName(`wall_${w.id}`)
      if (!node) continue
      const n = inwardNormal(w)
      out.push({ node, sx: w.start.x, sz: w.start.z, nx: -n.x, nz: -n.z }) // outward
    }
    return out
  }, [root, walls])

  useLayoutEffect(() => {
    const ceiling = root.getObjectByName('ceiling')
    if (ceiling) ceiling.visible = !cutaway
    if (!cutaway) for (const w of wallNodes) w.node.visible = true
  }, [cutaway, root, wallNodes])

  useFrame(({ camera }) => {
    if (!cutaway) return
    for (const w of wallNodes) {
      const outside =
        (camera.position.x - w.sx) * w.nx + (camera.position.z - w.sz) * w.nz >
        0
      w.node.visible = !outside
    }
  })

  return <primitive object={root} />
})
