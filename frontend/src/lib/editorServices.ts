import { DEMO } from '../demo/config'
import { engineReady } from '../demo/engine'
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
        // The demo's engine downloads Python first; show the checks as running meanwhile.
        if (DEMO)
          useStore.setState({
            auditStatus: 'loading',
            fengShuiScoreStatus: 'loading',
          })
        void (DEMO ? engineReady : Promise.resolve()).then(
          () => {
            void useStore.getState().refreshAudit()
            void useStore.getState().refreshFengShuiScore()
          },
          () =>
            useStore.setState({
              auditStatus: 'error',
              auditError:
                'The in-browser spatial engine could not load. Check your connection and reload.',
              fengShuiScoreStatus: 'error',
              fengShuiScoreError:
                'The in-browser spatial engine could not load.',
            }),
        )
      }, debounceMs)
  }
  const unsubscribe = useStore.subscribe((s, before) => {
    if (s.roomSession !== before.roomSession) {
      start()
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
  // A room resumed from this session keeps its edits: audit it instead of reloading.
  function start() {
    if (useStore.getState().roomReady) {
      schedule()
      useStore.getState().resumeRoomPoll()
    } else void useStore.getState().loadRoom()
  }
  start()
  return () => {
    unsubscribe()
    clearTimeout(timer)
    const s = useStore.getState()
    if (s.agentBusy)
      useStore.setState({
        chat: [
          ...s.chat,
          {
            role: 'assistant',
            text: 'Layout request cancelled when you left the room. Ask again to continue.',
            progress: s.agentProgress,
          },
        ],
      })
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
