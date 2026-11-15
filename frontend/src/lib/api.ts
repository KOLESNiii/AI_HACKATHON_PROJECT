/** One request, with a bounded lifetime. Provider requests are never retried here. */
export async function requestWithTimeout<T>(
  path: string,
  body: unknown,
  signal: AbortSignal | undefined,
  timeoutMs: number,
  read: (response: Response, signal: AbortSignal) => Promise<T>,
  accept = 'application/json',
): Promise<T> {
  const controller = new AbortController()
  const abort = () => controller.abort(signal?.reason)
  if (signal?.aborted) abort()
  else signal?.addEventListener('abort', abort, { once: true })
  const timer = setTimeout(
    () =>
      controller.abort(
        new DOMException('Request timed out. Try again.', 'TimeoutError'),
      ),
    timeoutMs,
  )
  try {
    const response = await fetch(path, {
      method: body === undefined ? 'GET' : 'POST',
      headers: {
        Accept: accept,
        ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: controller.signal,
    })
    if (!response.ok) {
      if (response.status === 422) {
        let details = ''
        try {
          const body: unknown = await response.json()
          if (isRecord(body) && Array.isArray(body.detail))
            details = body.detail
              .filter(isRecord)
              .map((d) => d.msg)
              .filter((m): m is string => typeof m === 'string')
              .slice(0, 2)
              .join('; ')
        } catch {
          /* Fall back to the validation message. */
        }
        if (details)
          throw new Error(`The room could not be checked: ${details}`)
        throw new Error(
          'The room or request could not be validated. Check the room and try again.',
        )
      }
      throw new Error(
        `The room service could not complete the request (${response.status}). Try again.`,
      )
    }
    const data = await read(response, controller.signal)
    controller.signal.throwIfAborted()
    return data
  } catch (error) {
    if (controller.signal.aborted) throw controller.signal.reason
    if (error instanceof TypeError)
      throw new Error(
        'The room service could not be reached. Check that it is running and try again.',
      )
    if (error instanceof SyntaxError)
      throw new Error(
        'The room service returned an unreadable response. Try again.',
      )
    throw error
  } finally {
    clearTimeout(timer)
    signal?.removeEventListener('abort', abort)
  }
}

export async function requestJson(
  path: string,
  body: unknown,
  signal: AbortSignal | undefined,
  timeoutMs: number,
): Promise<{ data: unknown; headers: Headers }> {
  return requestWithTimeout(
    path,
    body,
    signal,
    timeoutMs,
    async (response) => ({
      data: (await response.json()) as unknown,
      headers: response.headers,
    }),
  )
}

export function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

export function isFiniteNumber(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value)
}

export function errorMessage(error: unknown): string {
  return error instanceof Error
    ? error.message
    : 'The room service request failed. Try again.'
}
