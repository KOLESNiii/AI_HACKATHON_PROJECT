import type { FurnitureItem } from '../../lib/contracts'
import { useStore } from '../../store'
import { Button, Tag } from '../ui'

/** Floats above the selected item (HUD/Object Pill in Figma). */
export function ObjectPill({ item }: { item: FurnitureItem }) {
  const { rotateItem, snapItem, startReplace, deleteItem } = useStore.getState()
  const tags = [
    item.is_proxy && 'Proxy',
    item.dimension_source === 'estimated' && 'Estimated size',
    item.correction_needed.length > 0 && 'Needs correction',
  ].filter(Boolean) as string[]
  const locked = item.is_fixed
  return (
    <div
      className="scroll-panel flex items-center gap-3 py-2 pr-2 pl-3.5 whitespace-nowrap select-none"
      onPointerDown={(e) => e.stopPropagation()}
    >
      <div className="flex items-center gap-2.5">
        <span className="text-[13px] font-medium">{item.name}</span>
        <span className="mono text-[12px] text-ink-medium">
          {item.bbox_m.width.toFixed(2)}m × {item.bbox_m.depth.toFixed(2)}m
        </span>
        {tags.map((t) => (
          <Tag key={t}>{t}</Tag>
        ))}
      </div>
      <span className="h-5 w-px bg-hairline-ink" />
      <div className="flex gap-1.5">
        <Button disabled={locked} onClick={() => rotateItem(item.id, 90)}>
          Rotate 90°
        </Button>
        <Button disabled={locked} onClick={() => snapItem(item.id)}>
          Snap Wall
        </Button>
        <Button disabled={locked} onClick={() => startReplace(item.id)}>
          Swap via Link/Search
        </Button>
        <Button disabled={locked} onClick={() => deleteItem(item.id)}>
          Delete
        </Button>
      </div>
    </div>
  )
}
