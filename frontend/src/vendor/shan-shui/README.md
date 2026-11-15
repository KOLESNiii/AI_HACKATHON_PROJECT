# Shan Shui Inf (vendored)

Unmodified `index.html` from [LingDong-/shan-shui-inf](https://github.com/LingDong-/shan-shui-inf)
(MIT, © 2018 Lingdong Huang; see `LICENSE`).

It is not shipped to the browser. `scripts/generate-landscapes.ts` runs it in headless
Chromium to pre-render the seamless panoramas in `public/landscapes/`, which
`src/components/intake/Landscape.tsx` scrolls behind the front page and processing screens.
