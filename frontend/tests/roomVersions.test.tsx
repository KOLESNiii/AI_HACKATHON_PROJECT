import { afterEach, beforeEach, expect, test } from 'bun:test'
import { renderToStaticMarkup } from 'react-dom/server'
import { VersionTreeView } from '../src/components/editor/VersionTree'
import { catalog } from '../src/data/catalog'
import { freshMockScene } from '../src/data/mockScene'
import type {
  AuditReport,
  LayoutProposal,
  RoomScene,
} from '../src/lib/contracts'
import { DEFAULT_ROOM_ID, demoRooms } from '../src/data/demoHome'
import { initialRoomHistory } from '../src/lib/roomVersions'
import { useStore } from '../src/store'

import { solveResponse } from './solveStream'

const initial = useStore.getState()
const originalFetch = globalThis.fetch
function room(): RoomScene {
  const scene = freshMockScene()
  scene.floor_polygon = [
    { x: 0, z: 0 },
    { x: 10, z: 0 },
    { x: 10, z: 10 },
    { x: 0, z: 10 },
  ]
  scene.furniture = scene.furniture.slice(0, 2).map((item, i) => ({
    ...item,
    is_fixed: i === 1,
    pose: { x: i + 3, z: 3, yaw_deg: 0 },
  }))
  return scene
}
function report(scene: RoomScene): AuditReport {
  return {
    scene_id: scene.scene_id,
    scene_revision: scene.revision,
    overall_score: null,
    walkable_floor_ratio: 0.8,
    glare_orientation_grounded: null,
    collisions: [],
    blocked_doors: [],
    out_of_bounds_item_ids: [],
    clearance_issues: [],
    glare_alerts: null,
    feng_shui: null,
  }
}
function proposal(scene: RoomScene): LayoutProposal {
  return {
    proposal_id: 'versioned-proposal',
    poses: { [scene.furniture[0].id]: { ...scene.furniture[0].pose, x: 5 } },
    report: report(scene),
    improved: true,
    outcome: 'completed',
    goal: 'balanced',
    explanation: 'Moved the bed.',
  }
}
beforeEach(() => {
  const scene = room()
  useStore.setState({
    ...initial,
    screen: 'editor',
    scene,
    ...initialRoomHistory(scene),
  })
})
afterEach(() => {
  useStore.getState().agentAbort?.abort()
  useStore.getState().auditAbort?.abort()
  globalThis.fetch = originalFetch
  useStore.setState(initial)
})

test('manual changes remain a working draft until explicitly saved', () => {
  const s = useStore.getState()
  const id = s.scene.furniture[0].id
  s.setInteracting(true)
  s.setPose(id, { x: 4 })
  s.setPose(id, { x: 5 })
  expect(useStore.getState().versions).toHaveLength(1)
  s.commitEdit(null)
  s.setInteracting(false)
  expect(useStore.getState().versions).toHaveLength(1)
  expect(useStore.getState().hasUnsavedChanges).toBe(true)
  s.saveVersion()
  const after = useStore.getState()
  expect(after.versions).toHaveLength(2)
  expect(after.versions[1]).toMatchObject({
    parentId: 'version-1',
    source: 'manual',
  })
  expect(after.versions[0].scene.furniture[0].pose.x).toBe(3)
  expect(after.versions[1].scene.furniture[0].pose.x).toBe(5)
  s.setPose(id, { x: 6 })
  expect(after.versions[1].scene.furniture[0].pose.x).toBe(5)
})

test('restoring versions preserves siblings, recreates full layouts and increases audit revisions', () => {
  const s = useStore.getState()
  const original = s.scene
  s.rotateItem(original.furniture[0].id, 90)
  s.saveVersion()
  const first = useStore.getState()
  expect(first.currentVersionId).toBe('version-2')
  first.selectVersion('version-1')
  expect(useStore.getState().scene.furniture).toEqual(original.furniture)
  expect(useStore.getState().scene.revision).toBe(first.scene.revision + 1)
  useStore.getState().rotateItem(original.furniture[0].id, 180)
  useStore.getState().saveVersion()
  const branched = useStore.getState()
  expect(branched.versions).toHaveLength(3)
  expect(branched.versions[1].parentId).toBe('version-1')
  expect(branched.versions[2].parentId).toBe('version-1')
  branched.selectVersion('version-2')
  expect(useStore.getState().scene.furniture[0].pose.yaw_deg).toBe(90)
  expect(useStore.getState().scene.revision).toBe(branched.scene.revision + 1)
  useStore.getState().selectVersion('version-3')
  expect(useStore.getState().scene.furniture[0].pose.yaw_deg).toBe(180)
})

test('accepting an agent diff branches from the selected version and sends its current layout', async () => {
  const id = useStore.getState().scene.furniture[0].id
  useStore.getState().rotateItem(id, 90)
  useStore.getState().saveVersion()
  useStore.getState().selectVersion('version-1')
  const base = useStore.getState().scene
  let sent: RoomScene | undefined
  globalThis.fetch = (async (_url, init) => {
    sent = JSON.parse(String(init?.body)).scene
    return solveResponse(proposal(base))
  }) as typeof fetch
  await useStore.getState().sendChat('Improve the original room')
  expect(sent).toEqual(base)
  expect(sent?.furniture[0].pose.yaw_deg).toBe(0)
  expect(useStore.getState().chat[1].baseVersionId).toBe('version-1')
  useStore.getState().applyPoses(1)
  const state = useStore.getState()
  expect(state.versions).toHaveLength(3)
  expect(state.versions[2]).toMatchObject({
    parentId: 'version-1',
    source: 'agent',
  })
  expect(state.currentVersionId).toBe('version-3')
  state.selectVersion('version-2')
  expect(useStore.getState().scene.furniture[0].pose.yaw_deg).toBe(90)
  state.selectVersion('version-3')
  expect(useStore.getState().scene.furniture[0].pose.x).toBe(5)
})

test('versions restore furniture additions and deletions, assets and fixed fixtures', () => {
  const original = useStore.getState().scene
  useStore.getState().addFromCatalog(catalog[0])
  useStore.getState().saveVersion()
  const added = useStore.getState().scene.furniture.at(-1)!
  useStore.getState().deleteItem(original.furniture[0].id)
  useStore.getState().saveVersion()
  expect(useStore.getState().versions).toHaveLength(3)
  useStore.getState().selectVersion('version-1')
  expect(useStore.getState().scene.furniture).toEqual(original.furniture)
  useStore.getState().selectVersion('version-2')
  expect(useStore.getState().scene.furniture).toEqual([
    ...original.furniture,
    added,
  ])
  useStore.getState().selectVersion('version-3')
  expect(useStore.getState().scene.furniture.map((i) => i.id)).toEqual([
    original.furniture[1].id,
    added.id,
  ])
  expect(useStore.getState().scene.shell_glb_url).toBe(original.shell_glb_url)
})

test('unchanged or invalid edits, fixed items and navigation do not create versions', () => {
  const s = useStore.getState()
  s.commitEdit(null)
  s.rotateItem(s.scene.furniture[0].id, 360)
  s.rotateItem(s.scene.furniture[1].id, 90)
  s.deleteItem(s.scene.furniture[1].id)
  s.selectVersion('missing')
  s.selectVersion('version-1')
  expect(useStore.getState().versions).toHaveLength(1)
  expect(useStore.getState().currentVersionId).toBe('version-1')
})

test('switching versions cancels pending requests, clears Stats and drops late agent results', async () => {
  useStore.getState().rotateItem(useStore.getState().scene.furniture[0].id, 90)
  useStore.getState().saveVersion()
  const from = useStore.getState().scene
  let resolve!: (value: Response) => void
  globalThis.fetch = (() =>
    new Promise<Response>((done) => {
      resolve = done
    })) as typeof fetch
  useStore.setState({ audit: report(from), auditStatus: 'ready' })
  const pending = useStore.getState().sendChat('Improve this room')
  const controller = useStore.getState().agentAbort!
  useStore.getState().selectVersion('version-1')
  expect(controller.signal.aborted).toBe(true)
  expect(useStore.getState().agentBusy).toBe(false)
  expect(useStore.getState().audit).toBeNull()
  expect(useStore.getState().chat.at(-1)?.text).toContain('selected version')
  resolve(solveResponse(proposal(from)))
  await pending
  expect(useStore.getState().chat.some((m) => m.proposal)).toBe(false)
  expect(useStore.getState().versions).toHaveLength(2)
})

test('an old proposal stays stale after navigating away and back to its base version', async () => {
  const id = useStore.getState().scene.furniture[0].id
  useStore.getState().rotateItem(id, 90)
  useStore.getState().saveVersion()
  const base = useStore.getState().scene
  globalThis.fetch = (async () => solveResponse(proposal(base))) as typeof fetch
  await useStore.getState().sendChat('Improve this room')
  useStore.getState().selectVersion('version-1')
  useStore.getState().selectVersion('version-2')
  const restored = useStore.getState().scene
  useStore.getState().applyPoses(1)
  expect(useStore.getState().scene).toBe(restored)
  expect(useStore.getState().versions).toHaveLength(2)
})

test('version switching is disabled during gestures, loading and Play, and a new room resets history', () => {
  const s = useStore.getState()
  s.rotateItem(s.scene.furniture[0].id, 90)
  s.saveVersion()
  for (const block of [
    { interacting: true },
    { roomLoading: true },
    { mode: 'play' as const },
  ]) {
    useStore.setState({
      interacting: false,
      roomLoading: false,
      mode: 'edit',
      ...block,
    })
    s.selectVersion('version-1')
    expect(useStore.getState().currentVersionId).toBe('version-2')
  }
  s.openRoom()
  expect(useStore.getState().versions).toHaveLength(1)
  expect(useStore.getState().versions[0].scene.furniture).toEqual(
    useStore.getState().scene.furniture,
  )
})

test('tree renders nested branches with the selected version and usable button labels', () => {
  const s = useStore.getState()
  s.rotateItem(s.scene.furniture[0].id, 90)
  s.saveVersion()
  s.selectVersion('version-1')
  s.rotateItem(s.scene.furniture[0].id, 180)
  s.saveVersion()
  const state = useStore.getState()
  const html = renderToStaticMarkup(
    <VersionTreeView
      versions={state.versions}
      currentId={state.currentVersionId}
      disabled={false}
      hasUnsavedChanges={false}
      onSave={() => {}}
      onDiscard={() => {}}
      onSelect={() => {}}
    />,
  )
  expect(html).toContain('Room versions')
  expect(html).toContain('Original room')
  expect(html).toContain('Version 2')
  expect(html).toContain('Version 3, current layout')
  expect(html).toContain('aria-current="true"')
  expect(html).toContain('Manual edit')
  expect(html).toContain('3 versions')
})

test('several manual edits save as one successor, and successive saves form a linear chain', () => {
  const s = useStore.getState()
  const id = s.scene.furniture[0].id
  s.rotateItem(id, 5)
  s.rotateItem(id, 5)
  s.setPose(id, { x: 4 })
  s.commitEdit(null)
  expect(useStore.getState().versions).toHaveLength(1)
  const working = useStore.getState().scene
  const audit = report(working)
  useStore.setState({ audit, auditStatus: 'ready' })
  s.saveVersion()
  expect(useStore.getState().scene).toBe(working)
  expect(useStore.getState().audit).toBe(audit)
  expect(useStore.getState().hasUnsavedChanges).toBe(false)
  s.rotateItem(id, 5)
  s.saveVersion()
  s.rotateItem(id, 5)
  s.saveVersion()
  expect(useStore.getState().versions.map((v) => v.parentId)).toEqual([
    null,
    'version-1',
    'version-2',
    'version-3',
  ])
})

test('viewing history and unchanged saves never fork; editing and saving an ancestor preserves its successor', () => {
  const s = useStore.getState()
  const id = s.scene.furniture[0].id
  s.rotateItem(id, 90)
  s.saveVersion()
  s.rotateItem(id, 90)
  s.saveVersion()
  const successor = useStore.getState().versions[2]
  s.selectVersion('version-1')
  s.saveVersion()
  s.selectVersion('version-2')
  s.saveVersion()
  expect(useStore.getState().versions).toHaveLength(3)
  s.rotateItem(id, 5)
  expect(useStore.getState().versions).toHaveLength(3)
  s.saveVersion()
  expect(useStore.getState().versions[2]).toBe(successor)
  expect(useStore.getState().versions[3].parentId).toBe('version-2')
  s.rotateItem(id, 5)
  s.saveVersion()
  expect(useStore.getState().versions[4].parentId).toBe('version-4')
})

test('unsaved changes block navigation until saved or explicitly discarded', () => {
  const s = useStore.getState()
  const id = s.scene.furniture[0].id
  s.rotateItem(id, 90)
  s.saveVersion()
  const saved = useStore.getState().scene
  s.addFromCatalog(catalog[0])
  s.rotateItem(id, 5)
  const dirty = useStore.getState().scene
  s.selectVersion('version-1')
  expect(useStore.getState().scene).toBe(dirty)
  expect(useStore.getState().currentVersionId).toBe('version-2')
  expect(useStore.getState().hasUnsavedChanges).toBe(true)
  expect(useStore.getState().toasts.at(-1)?.text).toContain('Ctrl+S')
  s.discardChanges()
  expect(useStore.getState().scene.furniture).toEqual(saved.furniture)
  expect(useStore.getState().scene.revision).toBe(dirty.revision + 1)
  expect(useStore.getState().hasUnsavedChanges).toBe(false)
  expect(useStore.getState().versions).toHaveLength(2)
  s.selectVersion('version-1')
  expect(useStore.getState().currentVersionId).toBe('version-1')
  s.rotateItem(id, 5)
  s.saveVersion()
  s.selectVersion('version-2')
  expect(useStore.getState().currentVersionId).toBe('version-2')
})

test('reverting edits and saving twice do not create empty versions or branches', () => {
  const s = useStore.getState()
  const id = s.scene.furniture[0].id
  s.rotateItem(id, 90)
  s.rotateItem(id, -90)
  expect(useStore.getState().hasUnsavedChanges).toBe(false)
  s.saveVersion()
  s.addFromCatalog(catalog[0])
  s.deleteItem(useStore.getState().scene.furniture.at(-1)!.id)
  expect(useStore.getState().hasUnsavedChanges).toBe(false)
  s.saveVersion()
  expect(useStore.getState().versions).toHaveLength(1)
  s.rotateItem(id, 90)
  s.saveVersion()
  s.saveVersion()
  expect(useStore.getState().versions).toHaveLength(2)
})

test('saving cancels an in-flight agent request without changing the live scene or audit', async () => {
  const s = useStore.getState()
  s.rotateItem(s.scene.furniture[0].id, 90)
  const scene = useStore.getState().scene
  const audit = report(scene)
  useStore.setState({ audit, auditStatus: 'ready' })
  let resolve!: (response: Response) => void
  globalThis.fetch = (() =>
    new Promise<Response>((done) => {
      resolve = done
    })) as typeof fetch
  const pending = s.sendChat('Improve the working layout')
  const controller = useStore.getState().agentAbort!
  s.saveVersion()
  expect(controller.signal.aborted).toBe(true)
  expect(useStore.getState().scene).toBe(scene)
  expect(useStore.getState().audit).toBe(audit)
  resolve(solveResponse(proposal(scene)))
  await pending
  expect(useStore.getState().chat.some((m) => m.proposal)).toBe(false)
})

test('saving makes an older proposal stale even when its scene snapshot is unchanged', async () => {
  const s = useStore.getState()
  s.rotateItem(s.scene.furniture[0].id, 90)
  const base = useStore.getState().scene
  globalThis.fetch = (async () => solveResponse(proposal(base))) as typeof fetch
  await s.sendChat('Improve the working layout')
  s.saveVersion()
  expect(useStore.getState().scene).toBe(base)
  s.applyPoses(1)
  expect(useStore.getState().scene).toBe(base)
  expect(useStore.getState().versions).toHaveLength(2)
})

test('accepted agent proposals still create one immediate version from the reviewed working draft', async () => {
  const s = useStore.getState()
  s.rotateItem(s.scene.furniture[0].id, 90)
  const base = useStore.getState().scene
  globalThis.fetch = (async () => solveResponse(proposal(base))) as typeof fetch
  await s.sendChat('Improve this draft')
  s.applyPoses(1)
  const after = useStore.getState()
  expect(after.versions).toHaveLength(2)
  expect(after.versions[1]).toMatchObject({
    parentId: 'version-1',
    source: 'agent',
  })
  expect(after.hasUnsavedChanges).toBe(false)
  s.saveVersion()
  expect(useStore.getState().versions).toHaveLength(2)
})

test('leaving a room and reopening it later in the session keeps its edits, versions and chat', () => {
  const other = demoRooms.find(
    (r) => r.selectable && r.room_id !== DEFAULT_ROOM_ID,
  )!
  const open = (segmentId: string) => {
    useStore.setState({ segmentId })
    useStore.getState().openRoom()
    useStore.setState({ roomReady: true, screen: 'editor' })
  }
  open(DEFAULT_ROOM_ID)
  const s = useStore.getState()
  const id = s.scene.furniture.find((i) => !i.is_fixed)!.id
  s.rotateItem(id, 90)
  s.saveVersion()
  s.rotateItem(id, 90)
  useStore.setState({ chat: [{ role: 'user', text: 'Make it cosy' }] })
  const edited = useStore.getState()

  open(other.room_id)
  expect(useStore.getState().scene.scene_id).toBe(other.room_id)
  expect(useStore.getState().versions).toHaveLength(1)
  expect(useStore.getState().chat).toEqual([])

  open(DEFAULT_ROOM_ID)
  const back = useStore.getState()
  expect(back.scene).toBe(edited.scene)
  expect(back.versions).toBe(edited.versions)
  expect(back.currentVersionId).toBe('version-2')
  expect(back.hasUnsavedChanges).toBe(true)
  expect(back.chat).toEqual(edited.chat)
  expect(back.rooms[other.room_id]).toBeDefined()
})

test('a room still loading when left is not cached and loads again on reopen', () => {
  useStore.setState({ segmentId: null })
  useStore.getState().openRoom()
  const s = useStore.getState()
  s.rotateItem(s.scene.furniture.find((i) => !i.is_fixed)!.id, 90)
  useStore.getState().openRoom()
  expect(useStore.getState().roomReady).toBe(false)
  expect(useStore.getState().hasUnsavedChanges).toBe(false)
})

test('the editor audits a resumed room instead of reloading it from the server', async () => {
  const paths: string[] = []
  globalThis.fetch = (async (url: string | URL | Request) => {
    paths.push(String(url))
    return new Response('{}', { status: 500 })
  }) as typeof fetch
  useStore.setState({ roomReady: true })
  const { connectEditorServices } = await import('../src/lib/editorServices')
  const before = useStore.getState().scene
  const stop = connectEditorServices(0)
  await new Promise((r) => setTimeout(r, 10))
  stop()
  expect(paths.some((p) => p.includes('/scenes/'))).toBe(false)
  expect(paths.length).toBeGreaterThan(0)
  expect(useStore.getState().scene).toBe(before)
})
