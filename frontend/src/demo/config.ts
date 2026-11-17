/** True in the embeddable static build (`vite build --mode demo`): no backend, no API keys. */
export const DEMO = import.meta.env.MODE === 'demo'

export const REPO_URL = 'https://github.com/KOLESNiii/AI_HACKATHON_PROJECT'
export const DEVPOST_URL = 'https://devpost.com/software/refresh-xgdq08'

/** A root-relative app path (`/catalog/…`) under the build's base URL. */
export function withBase(path: string): string {
  // Outside Vite (bun test) there is no env, and paths stay root-relative.
  const base = import.meta.env?.BASE_URL ?? '/'
  return path.startsWith('/') ? base + path.slice(1) : path
}
