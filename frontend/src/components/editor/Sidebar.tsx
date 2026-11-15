import { useEffect, useMemo, useRef, useState, type FormEvent } from 'react'
import { catalog, catalogCategories } from '../../data/catalog'
import { proposalSummary, sendAgentMessage } from '../../lib/agent'
import type { AuditReport, RoomScene } from '../../lib/contracts'
import { fitsRoom } from '../../lib/geometry'
import type { ProductOption } from '../../lib/products'
import { SpatialError } from '../../lib/spatial'
import { useStore, type Tab } from '../../store'
import { Button, Chip, ScoreRing, StatusDot, type Status } from '../ui'

const tabs: [Tab, string][] = [
  ['chat', 'Chat'],
  ['stats', 'Stats'],
  ['library', 'Library'],
]

/** Right sidebar (Figma "Sidebar"): Chat · Stats · Library. */
export function Sidebar() {
  const tab = useStore((s) => s.tab)
  const setTab = useStore((s) => s.setTab)
  return (
    <aside className="flex h-full w-[380px] shrink-0 flex-col border-l border-hairline-ink bg-scroll-panel">
      <nav className="flex border-b border-hairline-ink" role="tablist">
        {tabs.map(([t, label]) => (
          <button
            key={t}
            type="button"
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
      <div className="flex min-h-0 flex-1 flex-col px-6 pt-[76px] pb-5">
        {tab === 'chat' && <ChatTab />}
        {tab === 'stats' && <StatsTab />}
        {tab === 'library' && <LibraryTab />}
      </div>
    </aside>
  )
}

function ChatTab() {
  const chat = useStore((s) => s.chat)
  const busy = useStore((s) => s.agentBusy)
  const { pushChat, setAgentBusy, applyPoses, dismissProposal } =
    useStore.getState()
  const [text, setText] = useState('')
  const end = useRef<HTMLDivElement>(null)
  useEffect(() => {
    end.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chat.length])

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    const msg = text.trim()
    if (!msg || busy || useStore.getState().interacting) return
    setText('')
    const { scene, roomSession } = useStore.getState()
    const baseRevision = scene.revision
    const controller = new AbortController()
    pushChat({ role: 'user', text: msg })
    setAgentBusy(true, controller)
    const current = () => useStore.getState().roomSession === roomSession
    try {
      const reply = await sendAgentMessage(scene, msg, controller.signal)
      if (current())
        pushChat({
          role: 'assistant',
          text: reply.text,
          poses: reply.poses,
          additions: reply.additions,
          report: reply.report,
          outlook: reply.outlook,
          products: reply.products,
          baseRevision,
        })
    } catch (error) {
      if (current() && !controller.signal.aborted)
        pushChat({
          role: 'assistant',
          text:
            error instanceof SpatialError
              ? error.message
              : 'The agent could not be reached. Try again.',
        })
    } finally {
      if (current()) setAgentBusy(false)
    }
  }

  return (
    <>
      <div className="flex min-h-0 flex-1 flex-col gap-[18px] overflow-y-auto">
        {chat.length === 0 && (
          <p className="text-[14px] leading-[23px] text-ink-medium">
            Ask Refresh to redesign this room, e.g.{' '}
            <em className="font-serif text-[16px]">
              “make it feel more open and get the desk out of the window glare.”
            </em>{' '}
            or{' '}
            <em className="font-serif text-[16px]">
              “find me an oak desk for under £150.”
            </em>
          </p>
        )}
        {chat.map((m, i) => (
          <div
            key={i}
            className={`flex flex-col gap-1.5 ${m.role === 'user' ? 'items-end' : 'items-start'}`}
          >
            <span className="text-[11px] font-medium text-ink-mist">
              {m.role === 'user' ? 'You' : 'Refresh'}
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
            {!!m.products?.length && (
              <div className="flex w-full flex-col gap-2">
                {m.products.map((p) => (
                  <ProductCard key={p.product_url} product={p} />
                ))}
              </div>
            )}
            {(m.poses || !!m.additions?.length) && (
              <div className="flex w-full flex-col gap-2 rounded-[2px] bg-paper-deep py-2 pr-2 pl-3">
                <div className="flex items-center justify-between gap-2.5">
                  <span className="text-[11px] font-medium text-ink-medium">
                    {proposalSummary(m)}
                  </span>
                  <span className="flex gap-1.5">
                    {!m.applied && !m.dismissed && (
                      <Button onClick={() => dismissProposal(i)}>
                        Dismiss
                      </Button>
                    )}
                    <Button
                      disabled={m.applied || m.dismissed}
                      onClick={() => applyPoses(i)}
                    >
                      {m.applied
                        ? 'Applied'
                        : m.dismissed
                          ? 'Dismissed'
                          : 'Apply'}
                    </Button>
                  </span>
                </div>
                {m.outlook && (
                  <span className="text-[11px] text-ink-medium">
                    Once applied: {m.outlook}
                  </span>
                )}
              </div>
            )}
          </div>
        ))}
        {busy && (
          <span className="text-[11px] font-medium text-ink-mist">
            Refresh is thinking…
          </span>
        )}
        <div ref={end} />
      </div>
      <form onSubmit={submit} className="flex items-center gap-2 pt-4">
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          maxLength={500}
          placeholder="Ask Refresh to redesign the room…"
          className="min-w-0 flex-1 rounded-[2px] border border-hairline-ink bg-paper-card/65 px-3 py-[11px] text-[14px] placeholder:text-ink-mist focus:border-ink-medium focus:outline-none"
        />
        <Button type="submit" variant="primary" size="lg" disabled={busy}>
          Send
        </Button>
      </form>
    </>
  )
}

/** One product found online: photo, shop, price and the published size, if read. */
function ProductCard({ product }: { product: ProductOption }) {
  const adding = useStore((s) => s.adding.includes(product.product_url))
  const inLibrary = useStore((s) =>
    s.library.some((e) => e.product.product_url === product.product_url),
  )
  const addProductToScene = useStore((s) => s.addProductToScene)
  const size = product.bbox_m
    ? `${product.bbox_m.width.toFixed(2)} × ${product.bbox_m.depth.toFixed(2)} × ${product.bbox_m.height.toFixed(2)} m`
    : 'Size read on import'
  return (
    <div className="flex items-center gap-3 rounded-[2px] border border-hairline-ink bg-paper-card/65 p-2.5">
      <ProductImage src={product.image_url} alt={product.name} />
      <div className="flex min-w-0 flex-1 flex-col gap-[3px]">
        <a
          href={product.product_url}
          target="_blank"
          rel="noreferrer noopener"
          title={product.name}
          className="line-clamp-2 text-[13px] leading-[17px] font-medium hover:underline"
        >
          {product.name}
        </a>
        <span className="truncate text-[11px] text-ink-medium">
          {product.retailer}
          {product.price_gbp != null && (
            <span className="mono text-ink-primary">
              {' · '}£{product.price_gbp.toFixed(product.price_gbp % 1 ? 2 : 0)}
            </span>
          )}
        </span>
        <span className="mono truncate text-[11px] text-ink-mist">{size}</span>
      </div>
      <Button
        disabled={adding}
        onClick={() => void addProductToScene(product)}
        title={
          inLibrary
            ? 'Already in your library: places another one'
            : 'Import into your library and place it in the room'
        }
      >
        {adding ? 'Adding…' : 'Add to scene'}
      </Button>
    </div>
  )
}

function ProductImage({ src, alt }: { src: string; alt: string }) {
  const [failed, setFailed] = useState(false)
  return failed ? (
    <div className="size-16 shrink-0 rounded-[2px] bg-ink-medium/16" />
  ) : (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      referrerPolicy="no-referrer"
      onError={() => setFailed(true)}
      className="size-16 shrink-0 rounded-[2px] bg-white object-contain"
    />
  )
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

/** Renders the spatial engine's AuditReport, refreshed by `useLiveAudit` after each edit. */
function StatsTab() {
  const scene = useStore((s) => s.scene)
  const raw = useStore((s) => s.audit)
  const error = useStore((s) => s.auditError)
  // Never show a report for another room or an older revision.
  const audit =
    raw &&
    raw.scene_id === scene.scene_id &&
    raw.scene_revision === scene.revision
      ? raw
      : null
  return <AuditStats audit={audit} scene={scene} error={error} />
}

export function AuditStats({
  audit,
  scene,
  error = null,
}: {
  audit: AuditReport | null
  scene: RoomScene
  error?: string | null
}) {
  const name = (id: string) =>
    scene.furniture.find((i) => i.id === id)?.name ?? id

  if (!audit) {
    return (
      <div className="flex flex-col gap-3">
        <h3 className="font-serif text-[20px] leading-[23px] font-semibold">
          {error ? 'Audit unavailable' : 'Checking the room…'}
        </h3>
        <p className="text-[14px] leading-[23px] text-ink-medium">
          {error ??
            'Spatial engine findings appear here: collisions, blocked doors, clearance and feng shui.'}
        </p>
      </div>
    )
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto">
      <div className="flex items-center gap-6">
        <ScoreRing score={audit.overall_score} size={52} />
        <Metric
          label="Walkable floor"
          value={
            audit.walkable_floor_ratio == null
              ? 'Not checked'
              : `${Math.round(audit.walkable_floor_ratio * 100)}%`
          }
        />
        <Metric
          label="Feng shui"
          value={
            audit.feng_shui == null
              ? 'Not checked'
              : String(audit.feng_shui.score)
          }
        />
      </div>
      {audit.overall_score == null && (
        <p className="text-[11px] text-ink-medium">
          Overall score: Not checked
        </p>
      )}
      <span className="flex items-center gap-2 text-[11px] font-medium text-ink-medium">
        <StatusDot
          status={
            audit.glare_orientation_grounded == null
              ? 'pending'
              : audit.glare_orientation_grounded
                ? 'valid'
                : 'warning'
          }
        />
        {audit.glare_orientation_grounded == null
          ? 'Glare orientation: Not checked'
          : audit.glare_orientation_grounded
            ? 'Glare orientation grounded'
            : 'North not grounded: glare uses the default orientation'}
      </span>
      <hr className="ink-divider" />
      <h3 className="font-serif text-[20px] leading-[23px] font-semibold">
        Findings
      </h3>
      <div className="flex flex-col">
        {audit.collisions.map((c, i) => (
          <Row
            key={`col-${i}`}
            status="danger"
            label={`Collision · ${name(c.item_a)} × ${name(c.item_b)}`}
            value={`${c.overlap_area_m2.toFixed(2)} m²`}
          />
        ))}
        {audit.blocked_doors.map((d, i) => (
          <Row
            key={`door-${i}`}
            status="danger"
            label={`Door blocked by ${name(d.blocked_by_item_id)}`}
            value={d.door_id}
          />
        ))}
        {audit.out_of_bounds_item_ids.map((id, i) => (
          <Row
            key={`oob-${i}`}
            status="danger"
            label={`${name(id)} outside the room`}
            value="bounds"
          />
        ))}
        {audit.clearance_issues.map((c, i) => (
          <Row
            key={`clr-${i}`}
            status="warning"
            label={`${name(c.item_id)} clearance`}
            value={`${c.actual_m.toFixed(2)} / ${c.required_m.toFixed(2)} m`}
          />
        ))}
        {audit.glare_alerts == null && (
          <Row status="pending" label="Glare" value="Not checked" />
        )}
        {audit.feng_shui == null && (
          <Row status="pending" label="Feng shui" value="Not checked" />
        )}
        {audit.glare_alerts
          ?.filter((g) => g.severity !== 'none')
          .map((g, i) => (
            <Row
              key={`glare-${i}`}
              status={g.severity === 'severe' ? 'danger' : 'warning'}
              label={`Glare on ${name(g.item_id)}`}
              value={g.severity}
            />
          ))}
        {audit.feng_shui?.sightlines.map((s, i) => (
          <div key={`fs-${i}`} className="border-b border-hairline-ink py-2">
            <span className="flex items-center gap-2 text-[13px] font-medium">
              <StatusDot
                status={s.status === 'command_position' ? 'valid' : 'warning'}
              />
              {`${name(s.from_item_id)} · ${s.status.replaceAll('_', ' ')}`}
            </span>
            <p className="mt-1 pl-4 text-[11px] leading-[17px] text-ink-medium">
              {s.reason}
            </p>
          </div>
        ))}
        {audit.feng_shui != null && (
          <p className="pt-2 text-[11px] leading-[17px] text-ink-mist">
            Feng shui here is a traditional placement guide for beds and desks
            (see the door, never sit with your back to it), not a prediction.
          </p>
        )}
      </div>
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-[11px] font-medium text-ink-medium">{label}</span>
      <span className="mono text-[20px] leading-6 font-bold">{value}</span>
    </div>
  )
}

/** Furniture library: mock catalog until Dev 2's catalog search / URL import lands. */
function LibraryTab() {
  const floor = useStore((s) => s.scene.floor_polygon)
  const addFromCatalog = useStore((s) => s.addFromCatalog)
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState<string>('all')

  const results = useMemo(
    () =>
      catalog.filter(
        (c) =>
          (category === 'all' || c.category === category) &&
          c.name.toLowerCase().includes(query.trim().toLowerCase()),
      ),
    [category, query],
  )

  const library = useStore((s) => s.library)
  const imported = library.filter(
    (e) =>
      (category === 'all' || e.item.category === category) &&
      e.product.name.toLowerCase().includes(query.trim().toLowerCase()),
  )

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4">
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search furniture or paste a product link"
        className="rounded-[2px] border border-hairline-ink bg-paper-card/65 px-3 py-[11px] text-[14px] placeholder:text-ink-mist focus:border-ink-medium focus:outline-none"
      />
      {/^https?:\/\//.test(query.trim()) && (
        <p className="text-[11px] font-medium text-accent-ochre">
          Link import arrives with the URL importer. Showing catalog matches
          meanwhile.
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
        {results.length + imported.length} results
      </span>
      <div className="flex min-h-0 flex-1 flex-col gap-2.5 overflow-y-auto pb-2">
        {imported.length > 0 && (
          <>
            <span className="text-[11px] font-medium text-ink-mist">
              Imported from shops
            </span>
            {imported.map((e) => (
              <ProductCard
                key={e.product.product_url}
                product={{ ...e.product, bbox_m: e.item.bbox_m }}
              />
            ))}
            <span className="pt-2 text-[11px] font-medium text-ink-mist">
              Catalog
            </span>
          </>
        )}
        {results.map((c) => {
          const fits = fitsRoom(floor, c.bbox_m.width, c.bbox_m.depth)
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
              <Button disabled={!fits} onClick={() => addFromCatalog(c)}>
                Add
              </Button>
            </div>
          )
        })}
      </div>
    </div>
  )
}
