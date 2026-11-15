import {
  DirectionalLight,
  MeshBasicMaterial,
  Mesh,
  MeshStandardMaterial,
  SpotLight,
  type Material,
  type Object3D,
} from 'three'

/** Walking moves only the camera: reuse shadows until lighting or geometry changes. */
export function invalidatePlayShadows(scene: Object3D) {
  scene.traverse((node) => {
    if (node instanceof DirectionalLight || node instanceof SpotLight)
      node.shadow.needsUpdate = true
  })
}

/** Clone only materials; GLTF geometry and textures remain owned by the loader cache. */
export function preparePlayMaterials(
  root: Object3D,
  shell = false,
): () => void {
  const owned = new Set<Material>()
  root.traverse((node) => {
    if (!(node instanceof Mesh)) return
    const floor =
      node.name.startsWith('floor') || node.parent?.name.startsWith('floor')
    const clone = (source: Material) => {
      let material: MeshStandardMaterial
      if (!shell && source instanceof MeshStandardMaterial) {
        material = source.clone()
      } else {
        material = new MeshStandardMaterial({
          color: shell ? (floor ? '#b79166' : '#eee8de') : '#b8ad9a',
          roughness: shell ? (floor ? 0.36 : 0.9) : 0.75,
          metalness: 0,
        })
        // GLTF's unlit extension uses MeshBasicMaterial. Keep its texture/albedo
        // while making it respond to play lighting.
        if (!shell && source instanceof MeshBasicMaterial) {
          material.color.copy(source.color)
          material.map = source.map
          material.vertexColors = source.vertexColors
          material.side = source.side
          material.opacity = source.opacity
          material.transparent = source.transparent
          material.alphaTest = source.alphaTest
        }
      }
      owned.add(material)
      return material
    }
    node.material = Array.isArray(node.material)
      ? node.material.map(clone)
      : clone(node.material)
    node.castShadow = true
    node.receiveShadow = true
  })
  return () => owned.forEach((material) => material.dispose())
}
