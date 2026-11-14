import { useEffect, useState } from 'react'
import './App.css'

const services = ['reconstruction', 'spatial_engine', 'media_gen'] as const

export default function App() {
  const [status, setStatus] = useState<Record<string, string>>({})

  useEffect(() => {
    const controller = new AbortController()
    for (const service of services) {
      fetch(`/api/${service}/health`, { signal: controller.signal })
        .then(async (response) => {
          if (!response.ok) throw new Error('Service unavailable')
          const body: unknown = await response.json()
          if (
            !body ||
            typeof body !== 'object' ||
            !('status' in body) ||
            body.status !== 'ok'
          ) {
            throw new Error('Invalid health response')
          }
          setStatus((previous) => ({ ...previous, [service]: 'Connected' }))
        })
        .catch(() => {
          if (!controller.signal.aborted) {
            setStatus((previous) => ({
              ...previous,
              [service]: 'Unavailable — start the service and refresh',
            }))
          }
        })
    }
    return () => controller.abort()
  }, [])

  return (
    <main>
      <p className="eyebrow">SpaceShift · Development</p>
      <h1>Your room, reimagined.</h1>
      <p>
        The workspace is ready for the room editor, spatial audit, and media
        tools.
      </p>
      <h2>Service connections</h2>
      <ul aria-live="polite">
        {services.map((service) => (
          <li key={service}>
            <strong>{service.replaceAll('_', ' ')}</strong>
            <span>{status[service] ?? 'Connecting…'}</span>
          </li>
        ))}
      </ul>
    </main>
  )
}
