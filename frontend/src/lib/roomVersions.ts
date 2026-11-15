import type { RoomScene } from './contracts'

export interface RoomVersion {
  id: string
  parentId: string | null
  label: string
  summary: string
  source: 'original' | 'manual' | 'agent'
  /** Saved layout. Its revision is historical; restoring uses a new revision. */
  scene: RoomScene
}

export interface RoomHistory {
  versions: RoomVersion[]
  currentVersionId: string
  hasUnsavedChanges: boolean
}

export function initialRoomHistory(scene: RoomScene): RoomHistory {
  return {
    versions: [
      {
        id: 'version-1',
        parentId: null,
        label: 'Original room',
        summary: 'Starting layout',
        source: 'original',
        scene: structuredClone(scene),
      },
    ],
    currentVersionId: 'version-1',
    hasUnsavedChanges: false,
  }
}

function historyForScene(
  state: RoomHistory & { scene: RoomScene },
): RoomHistory {
  const parent = state.versions.find((v) => v.id === state.currentVersionId)
  return parent?.scene.scene_id === state.scene.scene_id
    ? {
        versions: state.versions,
        currentVersionId: state.currentVersionId,
        hasUnsavedChanges: state.hasUnsavedChanges,
      }
    : initialRoomHistory(state.scene)
}

/** Manual edits update the working layout and audit revision, without saving a node. */
export function editRoomLayout(
  state: RoomHistory & { scene: RoomScene },
  scene: RoomScene,
): RoomHistory & { scene: RoomScene } {
  const history = historyForScene(state)
  const selected = history.versions.find(
    (v) => v.id === history.currentVersionId,
  )!
  return {
    ...history,
    scene,
    hasUnsavedChanges:
      JSON.stringify(selected.scene.furniture) !==
      JSON.stringify(scene.furniture),
  }
}

/** Append to the selected node. Existing siblings and snapshots are never rewritten. */
export function recordRoomVersion(
  state: RoomHistory & { scene: RoomScene },
  scene: RoomScene,
  summary: string,
  source: 'manual' | 'agent',
): RoomHistory & { scene: RoomScene } {
  const history = historyForScene(state)
  const selected = history.versions.find(
    (v) => v.id === history.currentVersionId,
  )!
  // Saving an unchanged layout must not create a successor or a branch.
  if (
    JSON.stringify(selected.scene.furniture) === JSON.stringify(scene.furniture)
  )
    return {
      scene,
      versions: history.versions,
      currentVersionId: history.currentVersionId,
      hasUnsavedChanges: false,
    }
  const number = history.versions.length + 1
  const version: RoomVersion = {
    id: `version-${number}`,
    parentId: history.currentVersionId,
    label: `Version ${number}`,
    summary,
    source,
    scene: structuredClone(scene),
  }
  return {
    scene,
    versions: [...history.versions, version],
    currentVersionId: version.id,
    hasUnsavedChanges: false,
  }
}
