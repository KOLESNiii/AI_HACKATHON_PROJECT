import { useFrame, useThree } from '@react-three/fiber'
import {
  useEffect,
  useImperativeHandle,
  useMemo,
  useRef,
  type Ref,
} from 'react'
import { PerspectiveCamera, Vector3 } from 'three'
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js'
import { DEG, planAngle } from '../../lib/geometry'
import {
  canStand,
  EYE_HEIGHT_M,
  walkingDelta,
  walkingObstacles,
  walkStep,
} from '../../lib/walk'
import { useStore } from '../../store'
import { editorKey } from '../editor/keyboard'
import {
  captureEditorView,
  pointOnFloor,
  restoreEditorView,
  resizePlayCamera,
  type EditorOrbit,
  type EditorView,
  type PlayControllerHandle,
} from './controls'

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
  const keys = useRef(new Set<string>())
  const pending = useRef<number | null>(null)
  const active = useRef<{ view: EditorView; roomSession: number } | null>(null)
  const forward = useMemo(() => new Vector3(), [])

  useEffect(() => {
    resizePlayCamera(camera, size.width, size.height)
  }, [camera, size.width, size.height])

  useImperativeHandle(
    controllerRef,
    () => ({
      floorPoint: (x, y) =>
        pointOnFloor(x, y, gl.domElement.getBoundingClientRect(), editorCamera),
      requestPlay: () => {
        const s = useStore.getState()
        if (pending.current != null || s.mode !== 'edit' || s.interacting)
          return
        if (!s.human || !canStand(s.human, s.scene)) {
          s.toast('Place the human on clear floor before playing.')
          return
        }
        if (!gl.domElement.requestPointerLock) {
          s.toast(
            'This browser does not support mouse capture. Try a desktop browser.',
          )
          return
        }
        pending.current = s.roomSession
        // Keep the request in the actual button gesture so browsers can grant capture.
        try {
          const result = gl.domElement.requestPointerLock()
          result?.catch(() => {
            if (pending.current == null) return
            pending.current = null
            useStore
              .getState()
              .toast('Mouse capture was blocked. Click Play to retry.')
          })
        } catch {
          pending.current = null
          s.toast('Mouse capture was blocked. Click Play to retry.')
        }
      },
    }),
    [gl, editorCamera],
  )

  useEffect(() => {
    const held = keys.current
    const clear = () => held.clear()
    const exit = () => {
      pending.current = null
      clear()
      const session = active.current
      active.current = null
      if (session && orbit) {
        camera.getWorldDirection(forward)
        const pose = {
          x: camera.position.x,
          z: camera.position.z,
          yaw_deg: ((planAngle(forward.x, forward.z) % 360) + 360) % 360,
        }
        if (useStore.getState().roomSession === session.roomSession)
          useStore.getState().finishPlay(pose)
        restoreEditorView(editorCamera, orbit, session.view)
        set({ camera: editorCamera })
      }
      if (document.pointerLockElement === gl.domElement)
        document.exitPointerLock()
    }
    const onLock = () => {
      const s = useStore.getState()
      if (
        !orbit ||
        pending.current !== s.roomSession ||
        !s.human ||
        !s.startPlay()
      ) {
        exit()
        return
      }
      active.current = {
        view: captureEditorView(editorCamera, orbit),
        roomSession: s.roomSession,
      }
      pending.current = null
      clear()
      orbit.enabled = false
      camera.position.set(s.human.x, EYE_HEIGHT_M, s.human.z)
      const yaw = s.human.yaw_deg * DEG
      camera.lookAt(
        s.human.x + Math.sin(yaw),
        EYE_HEIGHT_M,
        s.human.z + Math.cos(yaw),
      )
      set({ camera })
    }
    const onError = () => {
      if (pending.current == null) return
      pending.current = null
      useStore
        .getState()
        .toast('Mouse capture was blocked. Click Play to retry.')
    }
    const onDown = (event: KeyboardEvent) => {
      if (!active.current) return
      if (event.key === 'Escape') {
        exit()
        return
      }
      const key = editorKey(event)
      if (!key) return clear()
      if (['w', 'a', 's', 'd'].includes(key)) {
        event.preventDefault()
        if (!event.repeat) held.add(key)
      }
    }
    const onUp = (event: KeyboardEvent) => held.delete(event.key.toLowerCase())
    const onVisibility = () => {
      if (document.hidden) exit()
    }
    look.connect(gl.domElement)
    look.addEventListener('lock', onLock)
    look.addEventListener('unlock', exit)
    document.addEventListener('pointerlockerror', onError)
    document.addEventListener('visibilitychange', onVisibility)
    window.addEventListener('keydown', onDown)
    window.addEventListener('keyup', onUp)
    window.addEventListener('blur', exit)
    window.addEventListener('focusin', clear)
    return () => {
      exit()
      look.removeEventListener('lock', onLock)
      look.removeEventListener('unlock', exit)
      look.disconnect()
      document.removeEventListener('pointerlockerror', onError)
      document.removeEventListener('visibilitychange', onVisibility)
      window.removeEventListener('keydown', onDown)
      window.removeEventListener('keyup', onUp)
      window.removeEventListener('blur', exit)
      window.removeEventListener('focusin', clear)
    }
  }, [camera, editorCamera, forward, gl, look, orbit, set])

  useFrame((_, dt) => {
    if (!active.current || !look.isLocked) return
    const s = useStore.getState()
    if (
      s.mode !== 'play' ||
      !canStand(
        { x: camera.position.x, z: camera.position.z },
        s.scene,
        obstacles,
      )
    ) {
      document.exitPointerLock()
      return
    }
    camera.getWorldDirection(forward)
    const yaw = Math.atan2(forward.x, forward.z)
    const held = keys.current
    const delta = walkingDelta(
      yaw,
      Number(held.has('d')) - Number(held.has('a')),
      Number(held.has('w')) - Number(held.has('s')),
      dt,
    )
    if (!delta.x && !delta.z) return
    const next = walkStep(
      { x: camera.position.x, z: camera.position.z },
      delta,
      s.scene,
      obstacles,
    )
    camera.position.set(next.x, EYE_HEIGHT_M, next.z)
  })
  return null
}
