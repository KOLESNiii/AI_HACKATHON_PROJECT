import { useFrame, useThree } from '@react-three/fiber'
import { useEffect, useRef } from 'react'
import type { Vector3 } from 'three'
import { useStore } from '../../store'
import { editorKey, handleItemKey, panCamera } from './keyboard'

const panKeys = new Set(['w', 'a', 's', 'd'])

/** Uses the same OrbitControls target as mouse navigation. */
export function KeyboardControls({ speed }: { speed: number }) {
  const controls = useThree((s) => s.controls) as {
    enabled: boolean
    target: Vector3
    update: () => void
  } | null
  const keys = useRef(new Set<string>())

  useEffect(() => {
    const held = keys.current
    const clear = () => held.clear()
    const onDown = (event: KeyboardEvent) => {
      const key = editorKey(event)
      if (!key) return clear()
      if (panKeys.has(key)) {
        if (useStore.getState().interacting) return
        event.preventDefault()
        held.add(key)
      } else {
        handleItemKey(event)
      }
    }
    const onUp = (event: KeyboardEvent) => held.delete(event.key.toLowerCase())
    window.addEventListener('keydown', onDown)
    window.addEventListener('keyup', onUp)
    window.addEventListener('blur', clear)
    window.addEventListener('focusin', clear)
    document.addEventListener('visibilitychange', clear)
    return () => {
      clear()
      window.removeEventListener('keydown', onDown)
      window.removeEventListener('keyup', onUp)
      window.removeEventListener('blur', clear)
      window.removeEventListener('focusin', clear)
      document.removeEventListener('visibilitychange', clear)
    }
  }, [])

  useFrame(({ camera }, delta) => {
    if (!controls?.enabled || useStore.getState().interacting) {
      keys.current.clear()
      return
    }
    const held = keys.current
    const right = Number(held.has('d')) - Number(held.has('a'))
    const forward = Number(held.has('w')) - Number(held.has('s'))
    if (!right && !forward) return
    panCamera(
      camera.position,
      controls.target,
      right,
      forward,
      speed * Math.min(delta, 0.05),
    )
    controls.update()
  })
  return null
}
