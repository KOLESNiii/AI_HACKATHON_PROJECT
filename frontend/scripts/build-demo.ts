/**
 * Builds the embeddable, backend-free demo: `bun run build:demo [--base /path/] [--out dir]`.
 *
 * 1. Room shells for every demo room, generated once by the reconstruction service's own
 *    shell builder (needs `uv`), instead of on request.
 * 2. The demo furniture and the 100-piece IKEA catalog, meshopt-compressed with WebP
 *    textures. Geometry is not simplified, so every bounding box is unchanged.
 * 3. `vite build --mode demo` with `demo-public/` as the public folder.
 *
 * Compressed files are cached in demo-public/ (gitignored) and only redone when missing.
 */
import { $ } from 'bun'
import { cpSync, existsSync, mkdirSync, readdirSync } from 'node:fs'
import { join, resolve } from 'node:path'

const args = process.argv.slice(2)
const flag = (name: string, fallback: string) => {
  const i = args.indexOf(name)
  return i >= 0 ? args[i + 1] : fallback
}
const base = flag('--base', '/')
const outDir = resolve(flag('--out', 'dist-demo'))

const frontend = resolve(import.meta.dir, '..')
const repo = resolve(frontend, '..')
const pub = join(frontend, 'demo-public')
const gltf = join(frontend, 'node_modules/.bin/gltf-transform')

async function compressDir(from: string, to: string) {
  mkdirSync(to, { recursive: true })
  const files = readdirSync(from).filter((f) => f.endsWith('.glb'))
  let done = 0
  const queue = files.filter((f) => !existsSync(join(to, f)))
  const worker = async () => {
    for (let f = queue.shift(); f; f = queue.shift()) {
      await $`${gltf} optimize ${join(from, f)} ${join(to, f)} --compress meshopt --simplify false --texture-compress webp --texture-size 1024`.quiet()
      done++
    }
  }
  await Promise.all(Array.from({ length: 6 }, worker))
  console.log(
    `  ${to.replace(frontend + '/', '')}: ${files.length} models (${done} compressed now)`,
  )
}

console.log('Room shells')
const shells = join(pub, 'demo/shells')
mkdirSync(shells, { recursive: true })
await $`uv run --extra reconstruction python -c ${`
import sys
from pathlib import Path
from services.reconstruction.demo_assets import demo_rooms, demo_shell
out = Path(sys.argv[1])
for room_id in demo_rooms():
    (out / f"{room_id}.glb").write_bytes(demo_shell(room_id))
print("  demo/shells:", len(demo_rooms()), "rooms")
`} ${shells}`
  .cwd(repo)
  .env({ ...process.env, PYTHONPATH: repo })

console.log('Furniture and catalog meshes')
await compressDir(
  join(repo, 'contracts/mock_room/assets'),
  join(pub, 'demo/assets'),
)
await compressDir(
  join(frontend, 'public/catalog/ikea/assets'),
  join(pub, 'catalog/ikea/assets'),
)
for (const dir of ['catalog/ikea/images', 'landscapes', 'audio'])
  cpSync(join(frontend, 'public', dir), join(pub, dir), { recursive: true })
cpSync(
  join(frontend, 'public/catalog/ikea/NOTICE.md'),
  join(pub, 'catalog/ikea/NOTICE.md'),
)

console.log(`Vite build → ${outDir} (base ${base})`)
await $`bun --bun vite build --mode demo --base ${base} --outDir ${outDir} --emptyOutDir`.cwd(
  frontend,
)
