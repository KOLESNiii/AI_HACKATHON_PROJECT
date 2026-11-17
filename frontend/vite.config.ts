import { fileURLToPath } from 'node:url'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig, searchForWorkspaceRoot } from 'vite'

export default defineConfig(({ mode }) => ({
  plugins: [react(), tailwindcss()],
  // The embeddable demo (`bun run build:demo`) serves compressed meshes, room shells and
  // the IKEA catalog from a generated folder; see scripts/build-demo.ts.
  publicDir: mode === 'demo' ? 'demo-public' : 'public',
  worker: { format: 'es' },
  server: {
    port: 5173,
    strictPort: true,
    fs: {
      // The editor imports the shared contracts and mock fixture from ../contracts; the
      // demo's in-browser engine imports the spatial engine's Python from ../services.
      allow: [
        searchForWorkspaceRoot(process.cwd()),
        fileURLToPath(new URL('../contracts', import.meta.url)),
        fileURLToPath(new URL('../services', import.meta.url)),
      ],
    },
    proxy: Object.fromEntries(
      [
        ['reconstruction', 8001],
        ['spatial_engine', 8002],
        ['media_gen', 8003],
      ].map(([name, port]) => [
        `/api/${name}`,
        {
          target: `http://127.0.0.1:${port}`,
          rewrite: (path: string) => path.replace(`/api/${name}`, ''),
        },
      ]),
    ),
  },
}))
