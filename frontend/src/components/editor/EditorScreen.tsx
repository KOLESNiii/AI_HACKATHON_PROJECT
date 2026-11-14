import { useEffect, useMemo } from 'react'
import { requestAudit } from '../../lib/api'
import {
  findBlockedDoors,
  findCollisions,
  polygonArea,
  walkableRatio,
} from '../../lib/geometry'
import { selectCurrentAudit, useStore } from '../../store'
import { BottomDock, ScorePill, SunCompass } from './Hud'
import { RoomView } from './RoomView'
import { Sidebar, type LocalAnalysis } from './Sidebar'

/** Re-audit after each committed edit; drop responses for older revisions. */
function useAudit() {
  const scene = useStore((s) => s.scene)
  const setAudit = useStore((s) => s.setAudit)
  useEffect(() => {
    const controller = new AbortController()
    const session = useStore.getState().roomSession
    const t = setTimeout(() => {
      setAudit(useStore.getState().audit, 'pending')
      requestAudit(scene, controller.signal)
        .then((report) => {
          const now = useStore.getState()
          if (
            now.roomSession === session &&
            report.scene_id === now.scene.scene_id &&
            report.scene_revision === now.scene.revision
          )
            setAudit(report, 'ok')
        })
        .catch(() => {
          if (!controller.signal.aborted) setAudit(null, 'unavailable')
        })
    }, 400)
    return () => {
      clearTimeout(t)
      controller.abort()
    }
    // Keyed on revision (not the scene object) so dragging, which does not bump it, never audits.
  }, [
    scene.scene_id,
    scene.revision,
    scene.sun_hour,
    scene.north_compass_deg,
    setAudit,
  ])
}

export function EditorScreen() {
  const scene = useStore((s) => s.scene)
  const audit = useStore(selectCurrentAudit)
  useAudit()

  // The 5 cm walkable-floor scan only reruns on committed edits, not on every drag pointermove.
  const committed = `${scene.scene_id}@${scene.revision}`
  const walkable = useMemo(
    () => walkableRatio(useStore.getState().scene),
    [committed],
  )

  const analysis: LocalAnalysis = useMemo(
    () => ({
      collisions: findCollisions(scene.furniture),
      blockedDoors: findBlockedDoors(scene),
      walkable,
      area: polygonArea(scene.floor_polygon),
    }),
    [scene, walkable],
  )

  const collidingIds = useMemo(() => {
    const ids = new Set<string>()
    for (const c of analysis.collisions) {
      ids.add(c.a)
      ids.add(c.b)
    }
    for (const c of audit?.collisions ?? []) {
      ids.add(c.item_a)
      ids.add(c.item_b)
    }
    return ids
  }, [analysis.collisions, audit])

  const blockedDoorIds = useMemo(
    () =>
      new Set([
        ...analysis.blockedDoors.map((d) => d.door_id),
        ...(audit?.blocked_doors ?? []).map((d) => d.door_id),
      ]),
    [analysis.blockedDoors, audit],
  )

  return (
    <div className="flex h-full">
      <div className="relative min-w-0 flex-1">
        <RoomView collidingIds={collidingIds} blockedDoorIds={blockedDoorIds} />
        <div className="pointer-events-none absolute inset-0 p-6">
          <div className="pointer-events-auto absolute top-6 left-6">
            <ScorePill />
          </div>
          <div className="pointer-events-auto absolute top-6 right-6">
            <SunCompass />
          </div>
          <div className="pointer-events-auto absolute bottom-6 left-1/2 -translate-x-1/2">
            <BottomDock />
          </div>
        </div>
      </div>
      <Sidebar analysis={analysis} />
    </div>
  )
}
