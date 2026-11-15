import { useGLTF } from '@react-three/drei'
import { useThree } from '@react-three/fiber'
import { useEffect, useLayoutEffect, useMemo } from 'react'
import { Box3, Vector3 } from 'three'
import type { FurnitureItem } from '../../lib/contracts'
import { invalidatePlayShadows, preparePlayMaterials } from '../play/materials'
import { categoryWash, disposeInk, inkify } from './ink'

/** Loads the .glb and fits it to bbox_m (never trust raw mesh scale), bottom-centre at origin. */
export function FurnitureMesh({
  item,
  play,
}: {
  item: Pick<FurnitureItem, 'glb_url' | 'bbox_m' | 'category'>
  play: boolean
}) {
  const gltf = useGLTF(item.glb_url)
  const renderScene = useThree((s) => s.scene)
  const { object, scale, offset, dispose } = useMemo(() => {
    const clone = gltf.scene.clone(true)
    const dispose = play ? preparePlayMaterials(clone) : () => disposeInk(clone)
    if (!play) inkify(clone, () => categoryWash[item.category])
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
      dispose,
      scale: s,
      offset: new Vector3(-centre.x * s.x, -box.min.y * s.y, -centre.z * s.z),
    }
  }, [
    gltf.scene,
    item.category,
    item.bbox_m.width,
    item.bbox_m.height,
    item.bbox_m.depth,
    play,
  ])
  useEffect(() => dispose, [dispose])
  useLayoutEffect(
    () => invalidatePlayShadows(renderScene),
    [renderScene, object],
  )
  return (
    <group position={offset} scale={scale}>
      <primitive object={object} dispose={null} />
    </group>
  )
}
