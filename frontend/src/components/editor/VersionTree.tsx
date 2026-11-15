import { useEffect, useRef } from 'react'
import type { RoomVersion } from '../../lib/roomVersions'
import { useStore } from '../../store'
import { Button } from '../ui'

/** Layout snapshots form a tree; choosing a node does not delete any descendants. */
export function VersionTreeView({
  versions,
  currentId,
  disabled,
  hasUnsavedChanges,
  onSelect,
  onSave,
  onDiscard,
}: {
  versions: RoomVersion[]
  currentId: string
  disabled: boolean
  hasUnsavedChanges: boolean
  onSelect: (id: string) => void
  onSave: () => void
  onDiscard: () => void
}) {
  const selected = useRef<HTMLButtonElement>(null)
  useEffect(() => {
    selected.current?.scrollIntoView({ block: 'nearest', inline: 'nearest' })
  }, [currentId])
  const children = new Map<string | null, RoomVersion[]>()
  for (const version of versions) {
    const siblings = children.get(version.parentId) ?? []
    siblings.push(version)
    children.set(version.parentId, siblings)
  }
  const branch = (parentId: string | null) => {
    const siblings = children.get(parentId) ?? []
    const fork = parentId !== null && siblings.length > 1
    return (
      <ul className={fork ? 'ml-2 border-l border-hairline-ink pl-3' : ''}>
        {siblings.map((version) => {
          const current = version.id === currentId
          return (
            <li key={version.id} className="relative py-1">
              {parentId && (
                <span
                  aria-hidden="true"
                  className={
                    fork
                      ? 'absolute top-6 -left-3 w-3 border-t border-hairline-ink'
                      : 'absolute -top-1 left-3 h-2 border-l border-hairline-ink'
                  }
                />
              )}
              <button
                ref={current ? selected : undefined}
                type="button"
                aria-current={current ? 'true' : undefined}
                aria-label={`${version.label}${current ? ', current layout' : ''}`}
                title={version.summary}
                disabled={disabled}
                onClick={() => onSelect(version.id)}
                className={`flex w-full min-w-36 cursor-pointer flex-col gap-1 rounded-[2px] border p-2.5 text-left disabled:cursor-wait disabled:opacity-50 ${current ? 'border-seal-vermilion bg-paper-deep' : 'border-hairline-ink bg-paper-card/45 hover:bg-paper-deep'}`}
              >
                <span className="flex items-center gap-2 text-[12px] font-medium">
                  <span
                    aria-hidden="true"
                    className={`size-1.5 shrink-0 rounded-full ${current ? 'bg-seal-vermilion' : 'bg-ink-mist'}`}
                  />
                  {version.label}
                </span>
                <span className="text-[10px] text-ink-mist">
                  {version.source === 'agent'
                    ? 'Agent layout'
                    : version.source === 'manual'
                      ? 'Manual edit'
                      : 'Starting point'}
                  {current
                    ? ` · Current${hasUnsavedChanges ? ' · Unsaved' : ''}`
                    : ''}
                </span>
                <span className="line-clamp-2 text-[11px] leading-4 text-ink-medium">
                  {version.summary}
                </span>
              </button>
              {children.has(version.id) && branch(version.id)}
            </li>
          )
        })}
      </ul>
    )
  }
  return (
    <aside
      aria-label="Room versions"
      className="flex h-full w-56 shrink-0 flex-col border-r border-hairline-ink bg-scroll-panel"
    >
      <div className="border-b border-hairline-ink px-4 py-4">
        <h2 className="font-serif text-[19px]">Room versions</h2>
        <p className="mt-1 text-[11px] leading-4 text-ink-medium">
          Ctrl+S saves manual edits. Save from an older version to branch.
        </p>
        <div className="mt-3 flex flex-col gap-2">
          <p
            role="status"
            className={`text-[11px] ${hasUnsavedChanges ? 'text-accent-ochre' : 'text-ink-mist'}`}
          >
            {hasUnsavedChanges
              ? 'Unsaved layout changes'
              : 'No unsaved changes'}
          </p>
          <Button disabled={disabled || !hasUnsavedChanges} onClick={onSave}>
            Save version · Ctrl+S
          </Button>
          {hasUnsavedChanges && (
            <Button disabled={disabled} onClick={onDiscard}>
              Discard changes
            </Button>
          )}
        </div>
      </div>
      <nav
        aria-label="Layout version tree"
        className="min-h-0 flex-1 overflow-auto p-3"
      >
        {branch(null)}
      </nav>
      <p className="border-t border-hairline-ink px-4 py-3 text-[10px] text-ink-mist">
        {versions.length} version{versions.length === 1 ? '' : 's'} · Saved
        while this room is open
      </p>
    </aside>
  )
}

export function VersionTree() {
  const versions = useStore((s) => s.versions)
  const currentId = useStore((s) => s.currentVersionId)
  const hasUnsavedChanges = useStore((s) => s.hasUnsavedChanges)
  const disabled = useStore(
    (s) => s.roomLoading || s.interacting || s.mode !== 'edit',
  )
  const onSelect = useStore((s) => s.selectVersion)
  const onSave = useStore((s) => s.saveVersion)
  const onDiscard = useStore((s) => s.discardChanges)
  return (
    <VersionTreeView
      versions={versions}
      currentId={currentId}
      disabled={disabled}
      hasUnsavedChanges={hasUnsavedChanges}
      onSelect={onSelect}
      onSave={onSave}
      onDiscard={onDiscard}
    />
  )
}
