import { fileURLToPath } from 'node:url'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig, searchForWorkspaceRoot } from 'vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    strictPort: true,
    fs: {
      // The editor imports the shared contracts and mock fixture from ../contracts.
      allow: [
        searchForWorkspaceRoot(process.cwd()),
        fileURLToPath(new URL('../contracts', import.meta.url)),
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
})
