import { useEffect } from 'react'
import { connectEditorServices } from '../../lib/editorServices'

/** One editor service lifetime: canonical room, live audit and Feng Shui scores. */
export function useLiveAudit() {
  useEffect(() => connectEditorServices(), [])
}
