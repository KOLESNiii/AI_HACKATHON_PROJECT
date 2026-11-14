import {
  Plane,
  Raycaster,
  Vector2,
  Vector3,
  type Camera,
  type PerspectiveCamera,
  type Quaternion,
} from 'three'
import type { Pt } from '../../lib/geometry'

export interface PlayControllerHandle {
  floorPoint: (clientX: number, clientY: number) => Pt | null
  requestPlay: () => void
}

export interface EditorOrbit {
  target: Vector3
  enabled: boolean
  enableDamping: boolean
  update: () => void
}

export interface EditorView {
  position: Vector3
  quaternion: Quaternion
  zoom: number
  target: Vector3
}

export function resizePlayCamera(
  camera: PerspectiveCamera,
  width: number,
  height: number,
): void {
  camera.aspect = width / height
  camera.updateProjectionMatrix()
}

export function captureEditorView(
  camera: PerspectiveCamera,
  orbit: EditorOrbit,
): EditorView {
  return {
    position: camera.position.clone(),
    quaternion: camera.quaternion.clone(),
    zoom: camera.zoom,
    target: orbit.target.clone(),
  }
}

export function restoreEditorView(
  camera: PerspectiveCamera,
  orbit: EditorOrbit,
  view: EditorView,
): void {
  // Drain any residual orbit damping before restoring the exact saved view.
  const damping = orbit.enableDamping
  orbit.enableDamping = false
  orbit.update()
  orbit.enableDamping = damping
  orbit.target.copy(view.target)
  camera.position.copy(view.position)
  camera.quaternion.copy(view.quaternion)
  camera.zoom = view.zoom
  camera.updateProjectionMatrix()
}

const floor = new Plane(new Vector3(0, 1, 0), 0)

/** Project only points inside the canvas; furniture meshes never intercept placement. */
export function pointOnFloor(
  clientX: number,
  clientY: number,
  rect: Pick<DOMRect, 'left' | 'top' | 'width' | 'height'>,
  camera: Camera,
): Pt | null {
  const x = (clientX - rect.left) / rect.width
  const y = (clientY - rect.top) / rect.height
  if (
    !Number.isFinite(x) ||
    !Number.isFinite(y) ||
    x < 0 ||
    x > 1 ||
    y < 0 ||
    y > 1
  )
    return null
  const ray = new Raycaster()
  ray.setFromCamera(new Vector2(x * 2 - 1, 1 - y * 2), camera)
  const point = ray.ray.intersectPlane(floor, new Vector3())
  return point ? { x: point.x, z: point.z } : null
}
