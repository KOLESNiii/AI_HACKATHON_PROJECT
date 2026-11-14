import { Vector3 } from 'three'
import { useStore } from '../../store'

const rotationDegrees: Record<string, number> = {
  q: 90,
  e: -90,
  arrowleft: 5,
  arrowright: -5,
}

/** Leave text entry, native form controls and browser shortcuts alone. */
export function editorKey(event: KeyboardEvent): string | null {
  const el = event.target as HTMLElement | null
  if (
    event.defaultPrevented ||
    event.isComposing ||
    event.ctrlKey ||
    event.metaKey ||
    event.altKey ||
    el?.isContentEditable ||
    el?.closest?.('input, textarea, select, [role="textbox"]')
  )
    return null
  return event.key.toLowerCase()
}

/** Positive yaw turns counterclockwise when viewed from above. */
export function handleItemKey(event: KeyboardEvent): void {
  const key = editorKey(event)
  const { selectedId, interacting, mode, rotateItem, deleteItem } =
    useStore.getState()
  if (!key || !selectedId || interacting || mode !== 'edit') return
  const degrees = rotationDegrees[key]
  if (degrees !== undefined) {
    event.preventDefault()
    // Holding a quarter-turn key should not spin the item uncontrollably.
    if (!event.repeat || Math.abs(degrees) === 5)
      rotateItem(selectedId, degrees)
  } else if (key === 'delete' || key === 'backspace') {
    event.preventDefault()
    deleteItem(selectedId)
  }
}

/** Translate camera and orbit target together along the floor, relative to the view. */
export function panCamera(
  position: Vector3,
  target: Vector3,
  right: number,
  forward: number,
  distance: number,
): void {
  const ahead = new Vector3().subVectors(target, position).setY(0).normalize()
  const sideways = new Vector3(-ahead.z, 0, ahead.x)
  const offset = sideways
    .multiplyScalar(right)
    .addScaledVector(ahead, forward)
    .normalize()
    .multiplyScalar(distance)
  position.add(offset)
  target.add(offset)
}
