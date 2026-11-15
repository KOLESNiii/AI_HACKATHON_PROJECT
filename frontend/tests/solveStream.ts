/** The actual SSE wire format used by solve; fixtures never fall back to JSON. */
export function solveEvent(event: string, data: unknown): string {
  return `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`
}

export function solveResponse(proposal: unknown): Response {
  return new Response(solveEvent('result', proposal), {
    headers: { 'Content-Type': 'text/event-stream' },
  })
}
