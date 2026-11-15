/**
 * Pre-renders seamless, wrap-around Shan Shui panoramas for the landscape backdrop.
 *
 *   bun scripts/generate-landscapes.ts
 *
 * Runs the vendored engine (src/vendor/shan-shui, MIT © Lingdong Huang) in headless
 * Chromium with a fixed seed per panorama. The engine draws a long strip, the loop's
 * start and length are chosen so both ends of the wrap land in sparse areas, and the
 * strip just past the loop's end is crossfaded into its start, so the image wraps
 * with no visible seam. The paper colour is multiplied in, and the result is saved
 * as WebP in public/landscapes/.
 *
 * Needs a Chromium binary: set CHROME_BIN, or install Playwright's headless shell
 * (`bunx playwright install chromium-headless-shell`).
 */
import { execFileSync } from 'node:child_process'
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readdirSync,
  readFileSync,
  writeFileSync,
} from 'node:fs'
import { homedir, tmpdir } from 'node:os'
import { join, resolve } from 'node:path'

const SEEDS = ['20261115', '417', '9087', '31337'] // one panorama each
// The loop's start and length are searched within these ranges (world units) so
// that both ends of the seam crossfade fall in sparse areas (water, sky), where
// blending two drawings is invisible instead of doubling the strokes.
const START_MAX = 1600
const LOOP_MIN = 3600
const LOOP_MAX = 4400
const SEAM = 500 // world units crossfaded across the wrap
const HEIGHT = 1200 // output px; the engine's view is 800 / 1.142 units tall
const PAPER = '#eae0ce' // paper-base in src/index.css
const QUALITY = 0.82

const root = resolve(import.meta.dir, '..')
const vendor = readFileSync(
  join(root, 'src/vendor/shan-shui/index.html'),
  'utf8',
)
const outDir = join(root, 'public/landscapes')

function chrome(): string {
  if (process.env.CHROME_BIN) return process.env.CHROME_BIN
  const cache = join(homedir(), '.cache/ms-playwright')
  for (const dir of existsSync(cache) ? readdirSync(cache) : []) {
    for (const bin of [
      'chrome-headless-shell-linux64/chrome-headless-shell',
      'chrome-linux/chrome',
      'chrome-linux64/chrome',
    ]) {
      const p = join(cache, dir, bin)
      if (existsSync(p)) return p
    }
  }
  throw new Error('No Chromium found: set CHROME_BIN')
}

// Runs inside the engine's page after it has initialised.
const generator = `
(function () {
  var START_MAX = ${START_MAX}, LOOP_MIN = ${LOOP_MIN}, LOOP_MAX = ${LOOP_MAX};
  var SEAM = ${SEAM}, H = ${HEIGHT}, TOTAL = START_MAX + LOOP_MAX + SEAM;
  var vh = MEM.windy / 1.142, k = H / vh;
  chunkloader(0, TOTAL);
  chunkrender(0, TOTAL);
  var stripW = Math.round(TOTAL * k);
  var svg = "<svg xmlns='http://www.w3.org/2000/svg' width='" + stripW + "' height='" + H +
    "' viewBox='0 0 " + TOTAL + " " + vh + "'>" + MEM.canv + "</svg>";
  function done(text) {
    var pre = document.createElement('pre'); pre.id = 'OUT'; pre.textContent = text;
    document.body.appendChild(pre);
  }
  var img = new Image();
  img.onerror = function () { done('ERROR'); };
  img.onload = function () {
    var strip = document.createElement('canvas');
    strip.width = stripW; strip.height = H;
    var s = strip.getContext('2d');
    s.fillStyle = '#fff'; s.fillRect(0, 0, stripW, H);
    s.drawImage(img, 0, 0);

    // Ink per world unit along x, from a small copy of the strip.
    var cols = TOTAL, small = document.createElement('canvas');
    small.width = cols; small.height = 80;
    var sm = small.getContext('2d');
    sm.drawImage(strip, 0, 0, cols, 80);
    var px = sm.getImageData(0, 0, cols, 80).data, prefix = new Float64Array(cols + 1);
    for (var x = 0; x < cols; x++) {
      var ink = 0;
      for (var y = 0; y < 80; y++) ink += 255 - px[(y * cols + x) * 4];
      prefix[x + 1] = prefix[x] + ink;
    }
    function inkIn(a) { return prefix[a + SEAM] - prefix[a]; }
    var best = null;
    for (var st = 0; st <= START_MAX; st += 4)
      for (var len = LOOP_MIN; len <= LOOP_MAX; len += 4) {
        var cost = inkIn(st) + inkIn(st + len);
        if (!best || cost < best.cost) best = { cost: cost, st: st, len: len };
      }

    var x0 = Math.round(best.st * k), loopW = Math.round(best.len * k);
    var seamW = Math.round(SEAM * k);
    var out = document.createElement('canvas');
    out.width = loopW; out.height = H;
    var o = out.getContext('2d');
    o.drawImage(strip, x0, 0, loopW, H, 0, 0, loopW, H);
    // Wrap: over [0, seam) fade from the strip's continuation past the loop end
    // (which matches the image's right edge) into the loop's own start.
    var tail = document.createElement('canvas');
    tail.width = seamW; tail.height = H;
    tail.getContext('2d').drawImage(strip, x0 + loopW, 0, seamW, H, 0, 0, seamW, H);
    var head = document.createElement('canvas');
    head.width = seamW; head.height = H;
    var h = head.getContext('2d');
    h.drawImage(strip, x0, 0, seamW, H, 0, 0, seamW, H);
    var ramp = h.createLinearGradient(0, 0, seamW, 0);
    ramp.addColorStop(0, 'rgba(0,0,0,0)');
    ramp.addColorStop(1, 'rgba(0,0,0,1)');
    h.globalCompositeOperation = 'destination-in';
    h.fillStyle = ramp; h.fillRect(0, 0, seamW, H);
    o.drawImage(tail, 0, 0);
    o.drawImage(head, 0, 0);
    // Paper colour: white becomes paper, ink stays ink.
    o.globalCompositeOperation = 'multiply';
    o.fillStyle = '${PAPER}'; o.fillRect(0, 0, loopW, H);
    done(JSON.stringify({ start: best.st, loop: best.len }) + '\\n' + out.toDataURL('image/webp', ${QUALITY}));
  };
  img.src = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml' }));
})();
`

const page = vendor
  .replace(/^\s*present\(\);\s*$/m, '')
  .replace('</body>', '<script>console.log = function () {};</script></body>')
  .concat(`<script>${generator}</scr` + `ipt>`)

const tmp = mkdtempSync(join(tmpdir(), 'shan-shui-'))
const file = join(tmp, 'generate.html')
writeFileSync(file, page)
mkdirSync(outDir, { recursive: true })

for (const [i, seed] of SEEDS.entries()) {
  const dom = execFileSync(
    chrome(),
    [
      '--no-sandbox',
      '--disable-gpu',
      '--headless',
      '--window-size=1280,800',
      '--virtual-time-budget=60000',
      '--dump-dom',
      `file://${file}?seed=${seed}`,
    ],
    { maxBuffer: 512 * 1024 * 1024, stdio: ['ignore', 'pipe', 'ignore'] },
  ).toString()
  const match = dom.match(
    /<pre id="OUT">(\{[^\n]*\})\ndata:image\/webp;base64,([^<]+)<\/pre>/,
  )
  const info = match?.[1]
  const data = match?.[2]
  if (!data) throw new Error(`Seed ${seed}: no image produced`)
  const path = join(outDir, `landscape-${i + 1}.webp`)
  writeFileSync(path, Buffer.from(data, 'base64'))
  console.log(
    `${path}  seed ${seed}  ${info}  ${((data.length * 0.75) / 1024).toFixed(0)} KB`,
  )
}
