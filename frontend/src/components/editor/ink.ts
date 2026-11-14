import {
  Color,
  EdgesGeometry,
  LineBasicMaterial,
  LineSegments,
  Mesh,
  MeshToonMaterial,
  type Object3D,
} from 'three'
import type { FurnitureItem } from '../../lib/contracts'

/** Pine-ink outline shared by every drawn edge. */
export const inkLine = new LineBasicMaterial({
  color: '#1c1b19',
  transparent: true,
  opacity: 0.75,
})

/** Flat colour washes per category (Xuan Ink palette, lightened for surfaces). */
export const categoryWash: Record<FurnitureItem['category'], string> = {
  bed: '#a9bfa4',
  desk: '#d2a86e',
  chair: '#c99a62',
  table: '#d2a86e',
  wardrobe: '#c99a62',
  sofa: '#b7c4ae',
  storage: '#c99a62',
  fixture: '#e3dccd',
  other: '#d8c7a6',
}

/** Replace materials with flat toon washes and add ink edge lines (idempotent per clone). */
export function inkify(root: Object3D, wash: (mesh: Mesh) => string) {
  const meshes: Mesh[] = []
  root.traverse((o) => {
    if ((o as Mesh).isMesh && !o.userData.inked) meshes.push(o as Mesh)
  })
  for (const m of meshes) {
    m.userData.inked = true
    m.material = new MeshToonMaterial({ color: new Color(wash(m)) })
    const edges = new LineSegments(new EdgesGeometry(m.geometry, 28), inkLine)
    edges.raycast = () => {}
    m.add(edges)
  }
}

/** Free the materials and edge geometry that inkify created (source glTF geometry is cached and left alone). */
export function disposeInk(root: Object3D) {
  root.traverse((o) => {
    if (!o.userData.inked) return
    const m = o as Mesh
    ;(m.material as MeshToonMaterial).dispose()
    for (const c of m.children)
      if (c instanceof LineSegments) c.geometry.dispose()
  })
}
