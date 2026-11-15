import { useEffect } from 'react'
import { auditScene, SpatialError } from '../../lib/spatial'
import { useStore } from '../../store'

/** Wait for an edit burst (drags commit one revision each) to settle before auditing. */
const SETTLE_MS = 250

/**
 * Keeps the spatial audit in step with the scene: every committed edit (a new revision)
 * is audited once, an older request is cancelled when a newer edit arrives, and a result
 * is stored only if the scene is still at the revision it was computed for.
 */
export function useLiveAudit() {
  const sceneId = useStore((s) => s.scene.scene_id)
  const revision = useStore((s) => s.scene.revision)

  useEffect(() => {
    const controller = new AbortController()
    const timer = setTimeout(async () => {
      const { scene, setAudit } = useStore.getState()
      if (scene.scene_id !== sceneId || scene.revision !== revision) return
      try {
        const report = await auditScene(scene, controller.signal)
        const now = useStore.getState().scene
        if (now.scene_id === sceneId && now.revision === revision)
          setAudit(report)
      } catch (error) {
        if (controller.signal.aborted) return
        const now = useStore.getState().scene
        if (now.scene_id !== sceneId || now.revision !== revision) return
        setAudit(
          null,
          error instanceof SpatialError
            ? error.message
            : 'The spatial service could not be reached.',
        )
      }
    }, SETTLE_MS)
    return () => {
      clearTimeout(timer)
      controller.abort()
    }
  }, [sceneId, revision])
}
