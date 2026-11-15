const sameFile = (a: File, b: File) =>
  a.name === b.name && a.size === b.size && a.lastModified === b.lastModified

/** `current` plus the new files that fit: right type, not already chosen, within `max`. */
export function addFiles(
  current: File[],
  incoming: Iterable<File>,
  max: number,
  matches: (f: File) => boolean,
): { files: File[]; skipped: number } {
  const files = [...current]
  let skipped = 0
  for (const f of incoming) {
    if (files.some((x) => sameFile(x, f))) continue
    if (!matches(f) || files.length >= max) skipped++
    else files.push(f)
  }
  return { files, skipped }
}

export const isPlanImage = (f: File) =>
  f.type === 'image/png' || f.type === 'image/jpeg'
export const isVideo = (f: File) => f.type.startsWith('video/')
