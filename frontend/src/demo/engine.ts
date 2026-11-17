/** Main-thread client for the Pyodide spatial engine worker. */
type Kind = 'audit' | 'score'
interface Reply {
  id: number
  status: number
  body: unknown
  /** The interpreter died answering this; the next request starts a fresh worker. */
  fatal?: boolean
}

let worker: Worker | null = null
let seq = 0
const pending = new Map<number, (reply: Reply) => void>()
let readyResolve: () => void
let readyReject: (error: Error) => void
/** Settles once Python, shapely and pydantic are loaded and the engine imported. */
export const engineReady = new Promise<void>((resolve, reject) => {
  readyResolve = resolve
  readyReject = reject
})
engineReady.catch(() => {})

/** Starts downloading the engine; safe to call more than once. */
export function startEngine(): void {
  if (worker) return
  worker = new Worker(new URL('./engine.worker.ts', import.meta.url), {
    type: 'module',
  })
  worker.onmessage = (
    e: MessageEvent<Reply | { ready: boolean; error?: string }>,
  ) => {
    const data = e.data
    if ('ready' in data) {
      if (data.ready) readyResolve()
      else readyReject(new Error(data.error ?? 'engine failed to load'))
      return
    }
    pending.get(data.id)?.(data)
    pending.delete(data.id)
    if (data.fatal) restart()
  }
  worker.onerror = () =>
    readyReject(new Error('The in-browser spatial engine failed to start.'))
}

function restart() {
  worker?.terminate()
  worker = null
  for (const [id, resolve] of pending)
    resolve({
      id,
      status: 500,
      body: { detail: 'The spatial engine restarted. Try again.' },
    })
  pending.clear()
  startEngine()
}

export function runEngine(
  kind: Kind,
  body: string,
  signal?: AbortSignal | null,
): Promise<Reply> {
  startEngine()
  return new Promise((resolve, reject) => {
    if (signal?.aborted) return reject(signal.reason)
    const id = ++seq
    const abort = () => {
      pending.delete(id)
      reject(signal!.reason)
    }
    signal?.addEventListener('abort', abort, { once: true })
    pending.set(id, (reply) => {
      signal?.removeEventListener('abort', abort)
      resolve(reply)
    })
    worker!.postMessage({ id, kind, body })
  })
}
