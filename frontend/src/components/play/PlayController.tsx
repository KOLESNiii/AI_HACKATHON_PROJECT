import { useFrame, useThree } from '@react-three/fiber'
import {
  useEffect,
  useImperativeHandle,
  useMemo,
  useRef,
  type Ref,
} from 'react'
import { PerspectiveCamera } from 'three'
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js'
import { walkingObstacles } from '../../lib/walk'
import { useStore } from '../../store'
import {
  pointOnFloor,
  resizePlayCamera,
  type EditorOrbit,
  type PlayControllerHandle,
} from './controls'
import { PlaySession } from './session'

/** Owns the first-person camera; the editor's camera and orbit target stay separate. */
export function PlayController({
  controllerRef,
  editorCamera,
}: {
  controllerRef: Ref<PlayControllerHandle>
  editorCamera: PerspectiveCamera
}) {
  const { gl, set, size } = useThree()
  const orbit = useThree((s) => s.controls) as unknown as EditorOrbit | null
  const camera = useMemo(() => new PerspectiveCamera(70, 1, 0.05, 100), [])
  const look = useMemo(() => {
    const controls = new PointerLockControls(camera)
    controls.minPolarAngle = Math.PI / 36
    controls.maxPolarAngle = (Math.PI * 35) / 36
    return controls
  }, [camera])
  const scene = useStore((s) => s.scene)
  const obstacles = useMemo(() => walkingObstacles(scene), [scene])
  const session = useRef<PlaySession | null>(null)

  useEffect(() => {
    resizePlayCamera(camera, size.width, size.height)
  }, [camera, size.width, size.height])

  useImperativeHandle(
    controllerRef,
    () => ({
      floorPoint: (x, y) =>
        pointOnFloor(x, y, gl.domElement.getBoundingClientRect(), editorCamera),
      requestPlay: () => session.current?.requestPlay(),
      openLighting: () => session.current?.openLighting(),
      resumePlay: () => session.current?.resumePlay(),
      exitPlay: () => session.current?.exit(),
    }),
    [gl, editorCamera],
  )

  useEffect(() => {
    if (!orbit) return
    const current = new PlaySession({
      camera,
      editorCamera,
      orbit,
      surface: gl.domElement,
      look,
      setCamera: (next) => set({ camera: next }),
    })
    session.current = current
    const doc = gl.domElement.ownerDocument
    const onVisibility = () => {
      if (doc.hidden) current.exit()
    }
    const unsubscribe = useStore.subscribe(current.sync)
    look.connect(gl.domElement)
    look.addEventListener('lock', current.onLock)
    look.addEventListener('unlock', current.onUnlock)
    doc.addEventListener('pointerlockerror', current.onError)
    doc.addEventListener('visibilitychange', onVisibility)
    window.addEventListener('keydown', current.onDown)
    window.addEventListener('keyup', current.onUp)
    window.addEventListener('blur', current.exit)
    window.addEventListener('focusin', current.clearKeys)
    return () => {
      unsubscribe()
      current.exit()
      session.current = null
      look.removeEventListener('lock', current.onLock)
      look.removeEventListener('unlock', current.onUnlock)
      look.disconnect()
      doc.removeEventListener('pointerlockerror', current.onError)
      doc.removeEventListener('visibilitychange', onVisibility)
      window.removeEventListener('keydown', current.onDown)
      window.removeEventListener('keyup', current.onUp)
      window.removeEventListener('blur', current.exit)
      window.removeEventListener('focusin', current.clearKeys)
    }
  }, [camera, editorCamera, gl, look, orbit, set])

  useFrame((_, dt) => session.current?.update(dt, obstacles))
  return null
}
