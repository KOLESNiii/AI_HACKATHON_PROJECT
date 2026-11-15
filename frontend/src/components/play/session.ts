import { PerspectiveCamera, Vector3 } from 'three'
import type { PointerLockControls } from 'three/addons/controls/PointerLockControls.js'
import { DEG, planAngle, type Pt } from '../../lib/geometry'
import { canStand, EYE_HEIGHT_M, walkingDelta, walkStep } from '../../lib/walk'
import { useStore } from '../../store'
import { editorKey } from '../editor/keyboard'
import {
  captureEditorView,
  restoreEditorView,
  type EditorOrbit,
  type EditorView,
} from './controls'

interface SessionOptions {
  camera: PerspectiveCamera
  editorCamera: PerspectiveCamera
  orbit: EditorOrbit
  surface: HTMLCanvasElement
  look: Pick<PointerLockControls, 'isLocked' | 'enabled'>
  setCamera: (camera: PerspectiveCamera) => void
}

/** Browser capture and camera lifecycle, kept outside React so races can be tested. */
export class PlaySession {
  readonly keys = new Set<string>()
  private pending: { roomSession: number; intent: 'start' | 'resume' } | null =
    null
  private active: { roomSession: number; view: EditorView } | null = null
  private expectedUnlock = false
  private forward = new Vector3()

  private options: SessionOptions

  constructor(options: SessionOptions) {
    this.options = options
  }

  requestPlay = () => this.requestCapture('start')
  resumePlay = () => this.requestCapture('resume')

  private requestCapture(intent: 'start' | 'resume') {
    const s = useStore.getState()
    if (this.pending || s.screen !== 'editor') return
    if (intent === 'start') {
      if (s.mode !== 'edit' || s.interacting) return
      if (!s.human || !canStand(s.human, s.scene)) {
        s.toast('Place the human on clear floor before playing.')
        return
      }
    } else if (!this.active || s.mode !== 'play' || s.playPhase !== 'lighting')
      return
    const surface = this.options.surface
    if (!surface.requestPointerLock) {
      s.toast(
        'This browser does not support mouse capture. Try a desktop browser.',
      )
      return
    }
    const request = { roomSession: s.roomSession, intent }
    this.pending = request
    // Capture must remain inside the user's Play/Resume gesture.
    try {
      surface.requestPointerLock()?.catch(() => {
        if (this.pending === request) this.onError()
      })
    } catch {
      if (this.pending === request) this.onError()
    }
  }

  openLighting = () => {
    if (!this.active || !useStore.getState().openLightingPanel()) return
    this.clearKeys()
    this.options.look.enabled = false
    const doc = this.options.surface.ownerDocument
    if (doc.pointerLockElement === this.options.surface) {
      this.expectedUnlock = true
      doc.exitPointerLock()
    }
  }

  onLock = () => {
    const s = useStore.getState()
    const request = this.pending
    const { camera, editorCamera, orbit, look, setCamera } = this.options
    if (
      !request ||
      request.roomSession !== s.roomSession ||
      s.screen !== 'editor'
    ) {
      this.exit()
      return
    }
    this.pending = null
    if (request.intent === 'resume') {
      if (!this.active || !s.resumeWalking()) return this.exit()
    } else {
      if (!s.human || !s.startPlay()) return this.exit()
      this.active = {
        roomSession: s.roomSession,
        view: captureEditorView(editorCamera, orbit),
      }
      orbit.enabled = false
      camera.position.set(s.human.x, EYE_HEIGHT_M, s.human.z)
      const yaw = s.human.yaw_deg * DEG
      camera.lookAt(
        s.human.x + Math.sin(yaw),
        EYE_HEIGHT_M,
        s.human.z + Math.cos(yaw),
      )
      setCamera(camera)
    }
    this.expectedUnlock = false
    this.clearKeys()
    look.enabled = true
  }

  onUnlock = () => {
    this.clearKeys()
    const intentional = this.expectedUnlock
    this.expectedUnlock = false
    const s = useStore.getState()
    if (
      intentional &&
      this.active &&
      s.mode === 'play' &&
      s.playPhase === 'lighting'
    )
      return
    this.exit()
  }

  onError = () => {
    if (!this.pending) return
    const action = this.pending.intent === 'resume' ? 'Resume' : 'Play'
    this.pending = null
    useStore
      .getState()
      .toast(`Mouse capture was blocked. Click ${action} to retry.`)
  }

  clearKeys = () => this.keys.clear()

  onDown = (event: KeyboardEvent) => {
    if (!this.active) return
    if (event.key === 'Escape') {
      event.preventDefault()
      this.exit()
      return
    }
    const key = editorKey(event)
    if (!key) return this.clearKeys()
    if (key === 'l' && !event.repeat) {
      event.preventDefault()
      this.openLighting()
      return
    }
    if (useStore.getState().playPhase !== 'walking') return
    if (['w', 'a', 's', 'd'].includes(key)) {
      event.preventDefault()
      if (!event.repeat) this.keys.add(key)
    }
  }

  onUp = (event: KeyboardEvent) => this.keys.delete(event.key.toLowerCase())

  /** Store subscription invalidates captures even when the camera is paused. */
  sync = () => {
    const s = useStore.getState()
    if (
      (this.pending &&
        (this.pending.roomSession !== s.roomSession ||
          s.screen !== 'editor')) ||
      (this.active &&
        (this.active.roomSession !== s.roomSession ||
          s.mode !== 'play' ||
          s.screen !== 'editor'))
    )
      this.exit()
  }

  exit = () => {
    this.pending = null
    this.expectedUnlock = false
    this.clearKeys()
    const session = this.active
    this.active = null
    const { camera, editorCamera, orbit, surface, look, setCamera } =
      this.options
    look.enabled = false
    if (session) {
      camera.getWorldDirection(this.forward)
      if (useStore.getState().roomSession === session.roomSession) {
        useStore.getState().finishPlay({
          x: camera.position.x,
          z: camera.position.z,
          yaw_deg:
            ((planAngle(this.forward.x, this.forward.z) % 360) + 360) % 360,
        })
      }
      restoreEditorView(editorCamera, orbit, session.view)
      orbit.enabled = !useStore.getState().interacting
      setCamera(editorCamera)
    }
    const doc = surface.ownerDocument
    if (doc.pointerLockElement === surface) doc.exitPointerLock()
  }

  update(dt: number, obstacles: Pt[][]) {
    if (!this.active) return
    const s = useStore.getState()
    const { camera, look } = this.options
    if (
      !canStand(
        { x: camera.position.x, z: camera.position.z },
        s.scene,
        obstacles,
      )
    ) {
      this.exit()
      return
    }
    if (s.playPhase !== 'walking' || !look.isLocked) return
    camera.getWorldDirection(this.forward)
    const delta = walkingDelta(
      Math.atan2(this.forward.x, this.forward.z),
      Number(this.keys.has('d')) - Number(this.keys.has('a')),
      Number(this.keys.has('w')) - Number(this.keys.has('s')),
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
  }
}
