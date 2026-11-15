import { useStore } from '../store'

/** One editor lifetime, independent of the selected tab and play mode. */
export function connectEditorServices(debounceMs = 250): () => void {
  let timer: ReturnType<typeof setTimeout> | undefined
  const schedule = () => {
    clearTimeout(timer)
    const s = useStore.getState()
    s.auditAbort?.abort()
    s.fengShuiScoreAbort?.abort()
    useStore.setState({
      audit: null,
      auditAbort: null,
      auditStatus: 'idle',
      auditError: null,
      fengShuiScore: null,
      fengShuiScoreAbort: null,
      fengShuiScoreStatus: 'idle',
      fengShuiScoreError: null,
    })
    if (!s.interacting && !s.roomLoading)
      timer = setTimeout(() => {
        void useStore.getState().refreshAudit()
        void useStore.getState().refreshFengShuiScore()
      }, debounceMs)
  }
  const unsubscribe = useStore.subscribe((s, before) => {
    if (s.roomSession !== before.roomSession) {
      void s.loadRoom()
      return
    }
    // Drags move poses without a new revision; only committed edits invalidate results.
    const sceneChanged =
      s.scene.scene_id !== before.scene.scene_id ||
      s.scene.revision !== before.scene.revision
    if (sceneChanged) {
      s.fengShuiAbort?.abort()
      useStore.setState({
        fengShui: null,
        fengShuiAbort: null,
        fengShuiStatus: 'idle',
        fengShuiError: null,
      })
    }
    // Starting a drag keeps the committed revision's results; ending one only
    // refetches what the drag interrupted or what a mid-drag commit cleared.
    const dragEnded =
      before.interacting &&
      !s.interacting &&
      (s.auditStatus !== 'ready' || s.fengShuiScoreStatus !== 'ready')
    if (sceneChanged || dragEnded || s.roomLoading !== before.roomLoading)
      schedule()
  })
  void useStore.getState().loadRoom()
  return () => {
    unsubscribe()
    clearTimeout(timer)
    const s = useStore.getState()
    s.roomAbort?.abort()
    s.auditAbort?.abort()
    s.agentAbort?.abort()
    s.fengShuiAbort?.abort()
    s.fengShuiScoreAbort?.abort()
    useStore.setState({
      roomAbort: null,
      fengShuiAbort: null,
      fengShuiStatus: 'idle',
      fengShuiScore: null,
      fengShuiScoreAbort: null,
      fengShuiScoreStatus: 'idle',
      fengShuiScoreError: null,
      roomLoading: false,
      auditAbort: null,
      agentAbort: null,
      agentBusy: false,
      agentProgress: [],
    })
  }
}
