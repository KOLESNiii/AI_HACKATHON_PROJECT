import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { DEMO } from './demo/config'

// The embeddable demo answers service calls in the browser (see src/demo/fetchShim.ts).
const ready = DEMO
  ? import('./demo/fetchShim').then(({ installDemoFetch }) => {
      installDemoFetch()
      return import('./demo/engine').then(({ startEngine }) => startEngine())
    })
  : Promise.resolve()

void ready.then(() =>
  createRoot(document.getElementById('root')!).render(
    <StrictMode>
      <App />
    </StrictMode>,
  ),
)
