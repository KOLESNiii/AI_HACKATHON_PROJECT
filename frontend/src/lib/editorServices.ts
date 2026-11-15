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
    if (s.scene !== before.scene) {
      s.fengShuiAbort?.abort()
      useStore.setState({
        fengShui: null,
        fengShuiAbort: null,
        fengShuiStatus: 'idle',
        fengShuiError: null,
      })
    }
    if (
      s.scene !== before.scene ||
      s.interacting !== before.interacting ||
      s.roomLoading !== before.roomLoading
    )
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
