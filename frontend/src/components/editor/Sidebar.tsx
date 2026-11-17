import { useEffect, useMemo, useRef, useState, type FormEvent } from 'react'
import { catalog, catalogCategories } from '../../data/catalog'
import type {
  AuditReport,
  LayoutProgress,
  RoomScene,
} from '../../lib/contracts'
import { MAX_LAYOUT_INSTRUCTION_CHARS } from '../../lib/contracts'
import { matchingAudit } from '../../lib/layoutDiff'
import { importCatalogUrl } from '../../lib/catalogImport'
import type { CatalogItem } from '../../data/catalog'
import { fitsRoom } from '../../lib/geometry'
import { importKey, type ProductOption } from '../../lib/products'
import { useStore, type Tab } from '../../store'
import { Button, Chip, ScoreRing, StatusDot, type Status } from '../ui'
import { LayoutProposalCard } from './LayoutProposalCard'
import { CatalogPreview } from './CatalogPreview'
import { FengShuiScoreCard } from './FengShuiScoreCard'
import { matchingFengShuiScore, type FengShuiScore } from '../../lib/fengShui'
import { DEMO } from '../../demo/config'
import { ExamplePrompts } from './ExamplePrompts'
import { examplesFor } from '../../demo/examples'

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
      <div className="flex min-h-0 flex-1 flex-col px-6 pt-6 pb-5">
        {tab === 'chat' && <ChatTab />}
        {tab === 'stats' && <StatsTab />}
        {tab === 'library' && <LibraryTab />}
      </div>
    </aside>
  )
}

export function HarnessProgress({ updates }: { updates: LayoutProgress[] }) {
  if (!updates.length) return null
  return (
    <details className="w-full text-[11px] leading-5 text-ink-medium">
      <summary className="cursor-pointer">
        Activity · {updates.length}{' '}
        {updates.length === 1 ? 'update' : 'updates'}
      </summary>
      <ol className="mt-1 list-decimal space-y-1 pl-5">
        {updates.map((update, i) => (
          <li key={i}>{update.message}</li>
        ))}
      </ol>
    </details>
  )
}

export function HarnessStatus({
  updates,
  onCancel,
}: {
  updates: LayoutProgress[]
  onCancel: () => void
}) {
  return (
    <div className="flex flex-col gap-2">
      <div
        role="status"
        className="flex items-center justify-between gap-2 text-[11px] font-medium text-ink-mist"
      >
        <span>
          {updates.at(-1)?.message ?? 'Connecting to the layout assistant…'}
        </span>
        <Button onClick={onCancel}>Cancel</Button>
      </div>
      <HarnessProgress updates={updates} />
    </div>
  )
}

function ChatTab() {
  const chat = useStore((s) => s.chat)
  const busy = useStore((s) => s.agentBusy)
  const progress = useStore((s) => s.agentProgress)
  const scene = useStore((s) => s.scene)
  const roomSession = useStore((s) => s.roomSession)
  const currentVersionId = useStore((s) => s.currentVersionId)
  const hasUnsavedChanges = useStore((s) => s.hasUnsavedChanges)
  const versionLabel = useStore(
    (s) => s.versions.find((v) => v.id === s.currentVersionId)?.label,
  )
  const blocked = useStore(
    (s) => s.interacting || s.roomLoading || s.mode !== 'edit',
  )
  const { sendChat, cancelAgent, applyPoses, rejectProposal } =
    useStore.getState()
  const [text, setText] = useState('')
  const end = useRef<HTMLDivElement>(null)
  useEffect(() => {
    end.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chat.length])

  const submit = (e: FormEvent) => {
    e.preventDefault()
    const msg = text.trim()
    if (!msg || busy || blocked) return
    setText('')
    void sendChat(msg)
  }

  return (
    <>
      {!DEMO && (
        <p className="mb-3 text-[11px] font-medium text-ink-mist">
          Working from {versionLabel ?? 'this layout'}
          {hasUnsavedChanges ? ' · Unsaved changes' : ''}
        </p>
      )}
      <div className="flex min-h-0 flex-1 flex-col gap-[18px] overflow-y-auto">
        {chat.length === 0 &&
          DEMO &&
          examplesFor(scene.scene_id).length > 0 && (
            <p className="text-[14px] leading-[23px] text-ink-medium">
              Ask Refresh to redesign this room. It proposes a layout, checks
              every move for collisions, blocked doors and access, and changes
              nothing until you press{' '}
              <strong className="font-semibold text-ink-primary">Accept</strong>
              .
            </p>
          )}
        {chat.length === 0 && !DEMO && (
          <p className="text-[14px] leading-[23px] text-ink-medium">
            Ask Refresh to redesign this room, e.g.{' '}
            <em className="font-serif text-[16px]">
              “make it feel more open, but keep the bed where it is.”
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
            <HarnessProgress updates={m.progress ?? []} />
            {m.proposal && (
              <LayoutProposalCard
                message={m}
                stale={
                  m.roomSession !== roomSession ||
                  m.baseScene !== scene ||
                  m.baseVersionId !== currentVersionId
                }
                blocked={blocked}
                onAccept={() => applyPoses(i)}
                onReject={() => rejectProposal(i)}
              />
            )}
          </div>
        ))}
        {busy && <HarnessStatus updates={progress} onCancel={cancelAgent} />}
        <div ref={end} />
      </div>
      {DEMO ? (
        <ExamplePrompts compact={chat.length > 0} />
      ) : (
        <form onSubmit={submit} className="flex items-center gap-2 pt-4">
          <input
            aria-label="Room redesign request"
            maxLength={MAX_LAYOUT_INSTRUCTION_CHARS}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Ask Refresh to redesign the room…"
            className="min-w-0 flex-1 rounded-[2px] border border-hairline-ink bg-paper-card/65 px-3 py-[11px] text-[14px] placeholder:text-ink-mist focus:border-ink-medium focus:outline-none"
          />
          <Button
            type="submit"
            variant="primary"
            size="lg"
            disabled={busy || blocked || !text.trim()}
          >
            Send
          </Button>
        </form>
      )}
    </>
  )
}

/** One product found online: photo, shop, price and the published size, if read. */
function ProductCard({ product }: { product: ProductOption }) {
  const adding = useStore((s) => s.adding.includes(product.product_url))
  const inLibrary = useStore((s) =>
    s.library.some((e) => e.product.product_url === product.product_url),
  )
  const prefetch = useStore(
    (s) => s.prefetch[importKey(product, s.scene.scene_id)],
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
        {!inLibrary && prefetch && (
          <span className="truncate text-[11px] text-ink-mist">
            {prefetch === 'ready' ? '3D model ready' : 'Preparing 3D model…'}
          </span>
        )}
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

/** Only current-scene results belong in Stats, never a candidate's report. */
function StatsTab() {
  const scene = useStore((s) => s.scene)
  const raw = useStore((s) => s.audit)
  const interacting = useStore((s) => s.interacting)
  const roomLoading = useStore((s) => s.roomLoading)
  const loading = useStore((s) => s.auditStatus === 'loading') || roomLoading
  const error = useStore((s) => s.auditError)
  const refresh = useStore((s) => s.refreshAudit)
  const rawScore = useStore((s) => s.fengShuiScore)
  const scoreStatus = useStore((s) => s.fengShuiScoreStatus)
  const scoreError = useStore((s) => s.fengShuiScoreError)
  const refreshScore = useStore((s) => s.refreshFengShuiScore)
  const score =
    !interacting && matchingFengShuiScore(rawScore, scene) ? rawScore : null
  const audit = !interacting && matchingAudit(raw, scene) ? raw : null
  const findings =
    interacting || loading ? (
      <p role="status" className="text-[14px] text-ink-medium">
        {interacting
          ? 'Finish placing furniture to update Stats.'
          : 'Checking the room…'}
      </p>
    ) : error ? (
      <div className="flex flex-col gap-3">
        <p role="alert" className="text-[14px] text-ink-medium">
          {error}
        </p>
        <Button onClick={() => void refresh()}>Retry audit</Button>
      </div>
    ) : (
      <AuditStats audit={audit} scene={scene} fengShuiScore={score} />
    )
  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto">
      {findings}
      <hr className="ink-divider" />
      <FengShuiScoreCard
        scene={scene}
        score={score}
        status={scoreStatus}
        error={scoreError}
        blocked={interacting || roomLoading}
        onRetry={() => void refreshScore()}
      />
      {!DEMO && (
        <>
          <hr className="ink-divider" />
          <FengShuiSection />
        </>
      )}
    </div>
  )
}

/** Advisory `/feng-shui` result: model reasoning, not a measured score. */
function FengShuiSection() {
  const scene = useStore((s) => s.scene)
  const raw = useStore((s) => s.fengShui)
  const status = useStore((s) => s.fengShuiStatus)
  const error = useStore((s) => s.fengShuiError)
  const blocked = useStore((s) => s.interacting || s.roomLoading)
  const assess = useStore((s) => s.assessFengShui)
  const result =
    raw?.scene_id === scene.scene_id && raw.revision === scene.revision
      ? raw
      : null
  const name = (id: string) =>
    scene.furniture.find((i) => i.id === id)?.name ?? id
  return (
    <section aria-label="Feng shui assessment" className="flex flex-col gap-3">
      <div className="flex items-center justify-between gap-2">
        <h3 className="font-serif text-[20px] leading-[23px] font-semibold">
          Feng shui advice
        </h3>
        <Button
          disabled={blocked || status === 'loading'}
          onClick={() => void assess()}
        >
          {result ? 'Assess again' : 'Assess'}
        </Button>
      </div>
      {status === 'loading' && (
        <p role="status" className="text-[13px] text-ink-medium">
          Reviewing this layout…
        </p>
      )}
      {status === 'error' && error && (
        <p role="alert" className="text-[13px] text-ink-medium">
          {error}
        </p>
      )}
      {result?.outcome === 'assistant_unavailable' && (
        <p role="status" className="text-[13px] text-ink-medium">
          The feng shui assistant is unavailable right now. This is a service
          problem, not a verdict on your room.
        </p>
      )}
      {result?.assessment && (
        <>
          <p className="text-[13px] leading-[21px]">
            {result.assessment.summary}
          </p>
          <ul className="flex flex-col gap-2.5 text-[12px]">
            {result.assessment.findings.map((f, i) => (
              <li key={i} className="border-b border-hairline-ink pb-2">
                <span className="font-medium">
                  {f.object_ids.map(name).join(', ')} · {f.principle}
                </span>
                <p className="text-ink-medium">{f.recommendation}</p>
                <details className="mt-0.5 text-[11px] text-ink-mist">
                  <summary className="cursor-pointer">
                    Evidence · {f.confidence} confidence
                  </summary>
                  <p>{f.evidence}</p>
                </details>
              </li>
            ))}
          </ul>
          {result.assessment.missing_information.length > 0 && (
            <p className="text-[11px] text-ink-medium">
              Not known: {result.assessment.missing_information.join('; ')}
            </p>
          )}
          <p className="text-[11px] text-ink-mist">
            Traditional advice from the assistant, not a measured check.
          </p>
        </>
      )}
    </section>
  )
}

export function AuditStats({
  audit,
  scene,
  fengShuiScore,
}: {
  audit: AuditReport | null
  scene: RoomScene
  fengShuiScore?: FengShuiScore | null
}) {
  const name = (id: string) =>
    scene.furniture.find((i) => i.id === id)?.name ?? id
  const score = matchingFengShuiScore(fengShuiScore, scene)
    ? fengShuiScore
    : null

  if (!audit) {
    return (
      <div className="flex flex-col gap-3">
        <h3 className="font-serif text-[20px] leading-[23px] font-semibold">
          No audit yet
        </h3>
        <p className="text-[14px] leading-[23px] text-ink-medium">
          Spatial engine findings appear here: collisions, blocked doors,
          clearance, glare and feng shui.
        </p>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
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
            score
              ? score.score === null
                ? 'Not assessable'
                : `${score.score} / 100`
              : fengShuiScore !== undefined || audit.feng_shui == null
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
        {fengShuiScore === undefined && audit.feng_shui == null && (
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
        {fengShuiScore === undefined &&
          audit.feng_shui?.sightlines.map((s, i) => (
            <Row
              key={`fs-${i}`}
              status={s.status === 'command_position' ? 'valid' : 'danger'}
              label={`${name(s.from_item_id)} · ${s.status.replaceAll('_', ' ')}`}
              value={s.to_door_id}
            />
          ))}
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

/** Furniture library with retailer URL import and an offline IKEA catalog. */
function LibraryTab() {
  const roomLoading = useStore((s) => s.roomLoading)
  const floor = useStore((s) => s.scene.floor_polygon)
  const addFromCatalog = useStore((s) => s.addFromCatalog)
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState<string>('all')
  const [previewSku, setPreviewSku] = useState<string | null>(null)
  const [imported, setImported] = useState<CatalogItem | null>(null)
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState('')
  const request = useRef<AbortController | null>(null)
  useEffect(() => () => request.current?.abort(), [])
  const isUrl = !DEMO && /^https?:\/\//i.test(query.trim())
  const importLink = async () => {
    request.current?.abort()
    const controller = new AbortController()
    request.current = controller
    const { scene, roomSession } = useStore.getState()
    setBusy(true)
    setImported(null)
    setNotice('')
    try {
      const result = await importCatalogUrl(
        query.trim(),
        scene.scene_id,
        controller.signal,
      )
      if (
        !controller.signal.aborted &&
        roomSession === useStore.getState().roomSession
      ) {
        setImported(result.item)
        setNotice(result.warnings.join(' '))
      }
    } catch (error) {
      if (!controller.signal.aborted)
        setNotice(
          error instanceof Error ? error.message : 'Import failed. Try again.',
        )
    } finally {
      if (!controller.signal.aborted) setBusy(false)
    }
  }

  const results = useMemo(
    () =>
      isUrl
        ? imported
          ? [imported]
          : []
        : catalog.filter(
            (c) =>
              (category === 'all' || c.category === category) &&
              c.name.toLowerCase().includes(query.trim().toLowerCase()),
          ),
    [category, query, isUrl, imported],
  )
  const preview = results.find((item) => item.sku === previewSku) ?? results[0]

  const library = useStore((s) => s.library)
  const shopItems = library.filter(
    (e) =>
      (category === 'all' || e.item.category === category) &&
      e.product.name.toLowerCase().includes(query.trim().toLowerCase()),
  )

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4">
      <input
        value={query}
        onChange={(e) => {
          request.current?.abort()
          setBusy(false)
          setImported(null)
          setNotice('')
          setQuery(e.target.value)
        }}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && isUrl && !busy) void importLink()
        }}
        aria-label={
          DEMO ? 'Search furniture' : 'Search furniture or paste a product link'
        }
        placeholder={
          DEMO
            ? 'Search 100 IKEA pieces'
            : 'Search furniture or paste a product link'
        }
        className="rounded-[2px] border border-hairline-ink bg-paper-card/65 px-3 py-[11px] text-[14px] placeholder:text-ink-mist focus:border-ink-medium focus:outline-none"
      />
      {isUrl && (
        <Button disabled={busy} onClick={() => void importLink()}>
          {busy ? 'Importing product…' : 'Import product'}
        </Button>
      )}
      {busy && (
        <p role="status" className="text-[11px] text-ink-medium">
          Checking retailer models. If needed, AI reconstruction can take
          several minutes.
        </p>
      )}
      {notice && (
        <p role="status" className="text-[11px] font-medium text-accent-ochre">
          {notice}
        </p>
      )}
      {preview && <CatalogPreview item={preview} />}
      <div className="flex flex-wrap gap-1.5">
        {['all', ...catalogCategories].map((c) => (
          <Chip key={c} on={category === c} onClick={() => setCategory(c)}>
            {c[0].toUpperCase() + c.slice(1)}
          </Chip>
        ))}
      </div>
      <span className="text-[11px] font-medium text-ink-medium">
        {results.length + shopItems.length} results
      </span>
      <div className="flex min-h-0 flex-1 flex-col gap-2.5 overflow-y-auto pb-2">
        {shopItems.length > 0 && (
          <>
            <span className="text-[11px] font-medium text-ink-mist">
              Imported from shops
            </span>
            {shopItems.map((e) => (
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
              className={`flex items-center gap-3 rounded-[2px] border bg-paper-card/65 p-2.5 ${preview?.sku === c.sku ? 'border-seal-vermilion/60' : 'border-hairline-ink'}`}
            >
              {c.image_url ? (
                <img
                  src={c.image_url}
                  alt={c.name}
                  loading="lazy"
                  className="size-14 shrink-0 rounded-[2px] bg-white object-contain"
                />
              ) : (
                <div className="size-14 shrink-0 rounded-[2px] bg-ink-medium/16" />
              )}
              <div className="flex min-w-0 flex-1 flex-col gap-[3px]">
                <button
                  type="button"
                  aria-label={`Preview ${c.name}, ${c.bbox_m.width.toFixed(2)} by ${c.bbox_m.depth.toFixed(2)} metres`}
                  aria-pressed={preview?.sku === c.sku}
                  onClick={() => setPreviewSku(c.sku)}
                  className="cursor-pointer truncate text-left text-[13px] font-medium hover:text-seal-vermilion"
                >
                  {c.name}
                </button>
                {c.product_url && (
                  <a
                    href={c.product_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[11px] text-ink-medium underline"
                  >
                    View product
                  </a>
                )}
                <span className="mono text-[11px] text-ink-medium">
                  {c.bbox_m.width.toFixed(2)}m × {c.bbox_m.depth.toFixed(2)}m ×{' '}
                  {c.bbox_m.height.toFixed(2)}m
                </span>
                <span className="flex items-center gap-2">
                  <span className="mono text-[12px]">
                    {c.price_gbp == null
                      ? 'Price unavailable'
                      : `£${c.price_gbp}`}
                  </span>
                  <StatusDot status={fits ? 'valid' : 'danger'} />
                  <span
                    className={`text-[11px] font-medium ${fits ? 'text-accent-celadon' : 'text-seal-vermilion'}`}
                  >
                    {fits ? 'Size fits' : 'Too large'}
                  </span>
                </span>
              </div>
              <Button
                aria-label={`Add ${c.name}`}
                disabled={!fits || roomLoading}
                onClick={() => addFromCatalog(c)}
              >
                Add
              </Button>
            </div>
          )
        })}
        {results.length === 0 && (
          <p className="text-[13px] text-ink-medium">
            No models match. Try another name or category.
          </p>
        )}
      </div>
    </div>
  )
}
