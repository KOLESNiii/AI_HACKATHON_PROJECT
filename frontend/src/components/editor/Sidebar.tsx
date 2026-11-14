import { useEffect, useMemo, useRef, useState, type FormEvent } from 'react'
import { catalog, catalogCategories } from '../../data/catalog'
import { checkHealth, services, type Service } from '../../lib/api'
import { fitsRoom, type LocalCollision } from '../../lib/geometry'
import { selectCurrentAudit, useStore, type Tab } from '../../store'
import { Button, Chip, StatusDot, type Status } from '../ui'

export interface LocalAnalysis {
  collisions: LocalCollision[]
  blockedDoors: { door_id: string; item_id: string }[]
  walkable: number
  area: number
}

const tabs: [Tab, string][] = [
  ['chat', 'Chat'],
  ['stats', 'Stats'],
  ['library', 'Library'],
]

export function Sidebar({ analysis }: { analysis: LocalAnalysis }) {
  const tab = useStore((s) => s.tab)
  const setTab = useStore((s) => s.setTab)
  return (
    <aside className="flex h-full w-[380px] shrink-0 flex-col border-l border-hairline-ink bg-scroll-panel">
      <nav className="flex border-b border-hairline-ink" role="tablist">
        {tabs.map(([t, label]) => (
          <button
            key={t}
            role="tab"
            aria-selected={tab === t}
            onClick={() => setTab(t)}
            className={`flex-1 cursor-pointer border-b-2 pt-3.5 pb-3 text-[13px] font-medium ${
              tab === t
                ? 'border-seal-vermilion text-ink-primary'
                : 'border-transparent text-ink-mist hover:text-ink-medium'
            }`}
          >
            {label}
          </button>
        ))}
      </nav>
      <div className="flex min-h-0 flex-1 flex-col px-6 py-5">
        {tab === 'chat' && <ChatTab />}
        {tab === 'stats' && <StatsTab analysis={analysis} />}
        {tab === 'library' && <LibraryTab />}
      </div>
    </aside>
  )
}

function ChatTab() {
  const chat = useStore((s) => s.chat)
  const sendChat = useStore((s) => s.sendChat)
  const [text, setText] = useState('')
  const end = useRef<HTMLDivElement>(null)
  useEffect(
    () => end.current?.scrollIntoView({ behavior: 'smooth' }),
    [chat.length],
  )
  const submit = (e: FormEvent) => {
    e.preventDefault()
    if (text.trim()) sendChat(text.trim())
    setText('')
  }
  return (
    <>
      <div className="flex min-h-0 flex-1 flex-col gap-[18px] overflow-y-auto">
        {chat.length === 0 && (
          <p className="text-[14px] leading-[23px] text-ink-medium">
            Ask SpaceShift to redesign this room, e.g.{' '}
            <em className="font-serif text-[16px]">
              “make it feel more open and get the desk out of the window glare.”
            </em>
          </p>
        )}
        {chat.map((m, i) => (
          <div
            key={i}
            className={`flex flex-col gap-1.5 ${m.role === 'user' ? 'items-end' : 'items-start'}`}
          >
            <span className="text-[11px] font-medium text-ink-mist">
              {m.role === 'user' ? 'You' : 'SpaceShift'}
            </span>
            <p
              className={`rounded-[2px] px-3 py-2.5 text-[14px] leading-[23px] ${
                m.role === 'user'
                  ? 'max-w-[284px] bg-paper-deep'
                  : 'w-full border border-hairline-ink bg-paper-card/65'
              }`}
            >
              {m.text}
            </p>
          </div>
        ))}
        <div ref={end} />
      </div>
      <form onSubmit={submit} className="flex items-center gap-2 pt-4">
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Ask SpaceShift to redesign the room…"
          className="min-w-0 flex-1 rounded-[2px] border border-hairline-ink bg-paper-card/65 px-3 py-[11px] text-[14px] placeholder:text-ink-mist focus:border-ink-medium focus:outline-none"
        />
        <Button type="submit" variant="primary" size="lg">
          Send
        </Button>
      </form>
    </>
  )
}

function useServiceHealth() {
  const [health, setHealth] = useState<Partial<Record<Service, boolean>>>({})
  useEffect(() => {
    const c = new AbortController()
    for (const s of services)
      checkHealth(s, c.signal).then(
        (ok) => !c.signal.aborted && setHealth((h) => ({ ...h, [s]: ok })),
      )
    return () => c.abort()
  }, [])
  return health
}

function Row({
  status,
  label,
  value,
}: {
  status: Status
  label: string
  value: string
}) {
  return (
    <div className="flex items-center justify-between border-b border-hairline-ink py-2">
      <span className="flex items-center gap-2 text-[13px] font-medium">
        <StatusDot status={status} />
        {label}
      </span>
      <span className="mono text-[11px] text-ink-medium">{value}</span>
    </div>
  )
}

function StatsTab({ analysis }: { analysis: LocalAnalysis }) {
  const audit = useStore(selectCurrentAudit)
  const auditStatus = useStore((s) => s.auditStatus)
  const scene = useStore((s) => s.scene)
  const health = useServiceHealth()
  const name = (id: string) =>
    scene.furniture.find((i) => i.id === id)?.name ?? id
  const walkable = audit ? audit.walkable_floor_ratio : analysis.walkable
  // The audit is authoritative when it matches this revision; otherwise show the local preview.
  const collisions = audit
    ? audit.collisions.map((c) => ({ a: c.item_a, b: c.item_b }))
    : analysis.collisions
  const blockedDoors = audit
    ? audit.blocked_doors.map((d) => ({
        door_id: d.door_id,
        item_id: d.blocked_by_item_id,
      }))
    : analysis.blockedDoors

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto">
      <div className="flex gap-6">
        <Metric
          label="Spatial score"
          value={audit ? String(Math.round(audit.overall_score)) : '--'}
          tone="text-accent-ochre"
        />
        <Metric
          label="Walkable floor"
          value={`${Math.round(walkable * 100)}%`}
        />
        <Metric label="Floor area" value={`${analysis.area.toFixed(1)} m²`} />
      </div>
      <span className="flex items-center gap-2 text-[11px] font-medium text-ink-medium">
        <StatusDot
          status={scene.north_compass_deg != null ? 'valid' : 'warning'}
        />
        {scene.north_compass_deg != null
          ? 'Glare orientation grounded'
          : 'North not grounded: calibrate the compass'}
      </span>
      <hr className="ink-divider" />
      <h3 className="font-serif text-[20px] leading-[23px] font-semibold">
        Findings
      </h3>
      <div className="flex flex-col">
        {collisions.map((c, i) => (
          <Row
            key={`col-${i}-${c.a}-${c.b}`}
            status="danger"
            label={`Collision · ${name(c.a)} × ${name(c.b)}`}
            value="overlap"
          />
        ))}
        {blockedDoors.map((d, i) => (
          <Row
            key={`door-${i}-${d.door_id}`}
            status="danger"
            label={`Door blocked by ${name(d.item_id)}`}
            value={d.door_id}
          />
        ))}
        {audit?.out_of_bounds_item_ids.map((id, i) => (
          <Row
            key={`oob-${i}-${id}`}
            status="danger"
            label={`${name(id)} outside the room`}
            value="bounds"
          />
        ))}
        {audit?.clearance_issues.map((c, i) => (
          <Row
            key={`clr-${i}-${c.item_id}`}
            status="warning"
            label={`${name(c.item_id)} clearance`}
            value={`${c.actual_m.toFixed(2)} / ${c.required_m.toFixed(2)} m`}
          />
        ))}
        {audit?.glare_alerts
          .filter((g) => g.severity !== 'none')
          .map((g, i) => (
            <Row
              key={`glare-${i}-${g.item_id}`}
              status={g.severity === 'severe' ? 'danger' : 'warning'}
              label={`Glare on ${name(g.item_id)}`}
              value={g.severity}
            />
          ))}
        {audit?.feng_shui.sightlines.map((s, i) => (
          <Row
            key={`fs-${i}-${s.from_item_id}`}
            status={s.status === 'command_position' ? 'valid' : 'danger'}
            label={`${name(s.from_item_id)} · ${s.status.replaceAll('_', ' ')}`}
            value={s.to_door_id}
          />
        ))}
        {collisions.length + blockedDoors.length === 0 && !audit && (
          <p className="py-2 text-[13px] text-ink-medium">
            No collisions or blocked doors.
          </p>
        )}
      </div>
      <p className="text-[11px] font-medium text-ink-mist">
        {audit && auditStatus === 'ok'
          ? 'Audit from the spatial engine.'
          : 'Local preview: collisions, door swings and walkable floor are computed in the browser. Clearance, glare and feng shui need the spatial engine audit.'}
      </p>
      <div className="mt-auto flex flex-col gap-1.5 pt-2">
        <span className="text-[11px] font-medium text-ink-medium">
          Services
        </span>
        {services.map((s) => (
          <span
            key={s}
            className="flex items-center gap-2 text-[11px] text-ink-medium"
          >
            <StatusDot
              status={
                health[s] == null ? 'pending' : health[s] ? 'valid' : 'danger'
              }
            />
            {s.replaceAll('_', ' ')}{' '}
            {health[s] == null
              ? '· checking'
              : health[s]
                ? '· connected'
                : '· not running'}
          </span>
        ))}
      </div>
    </div>
  )
}

function Metric({
  label,
  value,
  tone = 'text-ink-primary',
}: {
  label: string
  value: string
  tone?: string
}) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-[11px] font-medium text-ink-medium">{label}</span>
      <span className={`mono text-[20px] leading-6 font-bold ${tone}`}>
        {value}
      </span>
    </div>
  )
}

function LibraryTab() {
  const scene = useStore((s) => s.scene)
  const replacingId = useStore((s) => s.replacingId)
  const { addFromCatalog, replaceWithCatalog, cancelReplace } =
    useStore.getState()
  const replacing = scene.furniture.find((i) => i.id === replacingId) ?? null
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState<string>('all')
  // Keyed on the id/category strings: moving the item recreates the object but must not
  // reset a filter the user picked.
  const replacingKey = replacing ? `${replacing.id}:${replacing.category}` : ''
  useEffect(
    () => setCategory(replacingKey ? replacingKey.split(':')[1] : 'all'),
    [replacingKey],
  )

  const results = useMemo(
    () =>
      catalog.filter(
        (c) =>
          (category === 'all' || c.category === category) &&
          c.name.toLowerCase().includes(query.trim().toLowerCase()),
      ),
    [category, query],
  )

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4">
      {replacing && (
        <div className="flex items-center justify-between rounded-[2px] bg-paper-deep py-2 pr-2 pl-3">
          <div className="flex flex-col gap-0.5">
            <span className="text-[11px] font-medium text-ink-medium">
              Replacing
            </span>
            <span className="mono text-[12px]">
              {replacing.name} · {replacing.bbox_m.width.toFixed(2)}m ×{' '}
              {replacing.bbox_m.depth.toFixed(2)}m
            </span>
          </div>
          <Button onClick={cancelReplace}>Cancel</Button>
        </div>
      )}
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search furniture or paste a product link"
        className="rounded-[2px] border border-hairline-ink bg-paper-card/65 px-3 py-[11px] text-[14px] placeholder:text-ink-mist focus:border-ink-medium focus:outline-none"
      />
      {/^https?:\/\//.test(query.trim()) && (
        <p className="text-[11px] font-medium text-accent-ochre">
          Link import arrives with Dev 2&apos;s URL importer. Showing catalog
          matches meanwhile.
        </p>
      )}
      <div className="flex flex-wrap gap-1.5">
        {['all', ...catalogCategories].map((c) => (
          <Chip key={c} on={category === c} onClick={() => setCategory(c)}>
            {c[0].toUpperCase() + c.slice(1)}
          </Chip>
        ))}
      </div>
      <span className="text-[11px] font-medium text-ink-medium">
        {results.length} results
      </span>
      <div className="flex min-h-0 flex-1 flex-col gap-2.5 overflow-y-auto pb-2">
        {results.map((c) => {
          const fits = fitsRoom(scene, c.bbox_m.width, c.bbox_m.depth)
          return (
            <div
              key={c.sku}
              className="flex items-center gap-3 rounded-[2px] border border-hairline-ink bg-paper-card/65 p-2.5"
            >
              <div className="size-14 shrink-0 rounded-[2px] bg-ink-medium/16" />
              <div className="flex min-w-0 flex-1 flex-col gap-[3px]">
                <span className="truncate text-[13px] font-medium">
                  {c.name}
                </span>
                <span className="mono text-[11px] text-ink-medium">
                  {c.bbox_m.width.toFixed(2)}m × {c.bbox_m.depth.toFixed(2)}m ×{' '}
                  {c.bbox_m.height.toFixed(2)}m
                </span>
                <span className="flex items-center gap-2">
                  <span className="mono text-[12px]">£{c.price_gbp}</span>
                  <StatusDot status={fits ? 'valid' : 'danger'} />
                  <span
                    className={`text-[11px] font-medium ${fits ? 'text-accent-celadon' : 'text-seal-vermilion'}`}
                  >
                    {fits ? 'Fits' : "Doesn't fit"}
                  </span>
                </span>
              </div>
              <Button
                disabled={!fits}
                onClick={() =>
                  replacing
                    ? replaceWithCatalog(replacing.id, c)
                    : addFromCatalog(c)
                }
              >
                {replacing ? 'Replace' : 'Add'}
              </Button>
            </div>
          )
        })}
      </div>
    </div>
  )
}
