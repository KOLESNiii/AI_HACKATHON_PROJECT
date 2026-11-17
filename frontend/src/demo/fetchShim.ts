/**
 * The demo's backend: answers the editor's service calls in the browser so the static build
 * needs no Python services and no API keys.
 *
 * - `/spatial_engine/audit` and `/feng-shui/score` run the real engine in Pyodide.
 * - `/spatial_engine/chat/stream` replays a recorded agent run, only for its own room and
 *   starting layout; anything else gets the stream's error event.
 * - Demo meshes and the IKEA catalog are static files under the build's base URL.
 */
import { roomScene } from '../data/demoHome'
import type { RoomScene } from '../lib/contracts'
import { withBase } from './config'
import { runEngine } from './engine'
import { findExample, isStartingLayout, type Example } from './examples'

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })

function sse(event: string, data: unknown): string {
  return `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`
}

const sleep = (ms: number, signal?: AbortSignal | null) =>
  new Promise<void>((resolve, reject) => {
    const timer = setTimeout(resolve, ms)
    signal?.addEventListener(
      'abort',
      () => {
        clearTimeout(timer)
        reject(signal.reason)
      },
      { once: true },
    )
  })

/** The recorded reply, re-addressed to the revision the editor is on now. */
function replyFor(example: Example, scene: RoomScene): unknown {
  const reply = structuredClone(example.reply) as Record<
    string,
    Record<string, unknown> | null
  >
  const readdress = (report: Record<string, unknown> | null | undefined) => {
    if (report) {
      report.scene_id = scene.scene_id
      report.scene_revision = scene.revision
    }
  }
  readdress(reply.report)
  readdress(reply.proposal?.report as Record<string, unknown> | undefined)
  return reply
}

function replay(
  scene: RoomScene,
  instruction: string,
  signal?: AbortSignal | null,
): Response {
  const example = findExample(scene.scene_id, instruction)
  const encoder = new TextEncoder()
  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      const send = (text: string) => controller.enqueue(encoder.encode(text))
      try {
        if (!example || !isStartingLayout(scene)) {
          await sleep(300, signal)
          send(
            sse('error', {
              message:
                'This demo replays recorded agent runs on each room’s starting layout. Reset the room to try an example.',
            }),
          )
          return controller.close()
        }
        let at = 0
        for (const { t, data } of example.progress) {
          await sleep(Math.max(0, t - at) * 1000, signal)
          at = t
          send(sse('progress', data))
        }
        await sleep(Math.max(0.4, example.duration - at) * 1000, signal)
        send(sse('reply', replyFor(example, scene)))
        controller.close()
      } catch {
        /* Cancelled by the editor. */
      }
    },
  })
  return new Response(stream, {
    headers: { 'Content-Type': 'text/event-stream' },
  })
}

async function engine(
  kind: 'audit' | 'score',
  init: RequestInit | undefined,
): Promise<Response> {
  const body = typeof init?.body === 'string' ? init.body : '{}'
  const reply = await runEngine(kind, body, init?.signal)
  return json(reply.body, reply.status)
}

const MOCK_ROOM = '/api/reconstruction/mock-room/'

export function installDemoFetch(): void {
  const realFetch = window.fetch.bind(window)
  window.fetch = async (input, init) => {
    const raw =
      typeof input === 'string'
        ? input
        : input instanceof URL
          ? input.href
          : input.url
    const url = new URL(raw, location.href)
    if (url.origin !== location.origin) return realFetch(input, init)
    const path = url.pathname

    // Static assets: demo room meshes and shells, and the IKEA catalog.
    if (path.startsWith(MOCK_ROOM))
      return realFetch(withBase(`/demo/${path.slice(MOCK_ROOM.length)}`), {
        signal: init?.signal,
      })
    if (path.startsWith('/catalog/') && import.meta.env.BASE_URL !== '/')
      return realFetch(withBase(path), { signal: init?.signal })

    if (!path.startsWith('/api/')) return realFetch(input, init)
    if (path === '/api/spatial_engine/audit') return engine('audit', init)
    if (path === '/api/spatial_engine/feng-shui/score')
      return engine('score', init)
    if (path === '/api/spatial_engine/chat/stream') {
      const { scene, instruction } = JSON.parse(String(init?.body)) as {
        scene: RoomScene
        instruction: string
      }
      return replay(scene, instruction, init?.signal)
    }
    const room = /^\/api\/reconstruction\/scenes\/([^/]+)$/.exec(path)
    if (room) return json(roomScene(decodeURIComponent(room[1])))
    return json({ detail: 'Not available in the demo' }, 503)
  }
}
