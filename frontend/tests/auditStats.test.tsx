import { expect, test } from 'bun:test'
import { renderToStaticMarkup } from 'react-dom/server'
import { AuditStats } from '../src/components/editor/Sidebar'
import { freshMockScene } from '../src/data/mockScene'
import type { AuditReport } from '../src/lib/contracts'

const scene = freshMockScene()
const report: AuditReport = {
  scene_id: scene.scene_id,
  scene_revision: scene.revision,
  overall_score: null,
  walkable_floor_ratio: null,
  glare_orientation_grounded: null,
  collisions: [],
  blocked_doors: [],
  out_of_bounds_item_ids: [],
  clearance_issues: [],
  glare_alerts: null,
  feng_shui: null,
}

test('unassessed audit fields render without crashes or false zero results', () => {
  const html = renderToStaticMarkup(<AuditStats scene={scene} audit={report} />)
  expect(html).toContain('Not checked')
  expect(html).toContain('Overall score: Not checked')
  expect(html).toContain('Glare orientation: Not checked')
  expect(html).not.toContain('0%')
  expect(html).not.toContain('North not grounded')
})

test('assessed zero walking access is distinct from an unknown result', () => {
  const html = renderToStaticMarkup(
    <AuditStats scene={scene} audit={{ ...report, walkable_floor_ratio: 0 }} />,
  )
  expect(html).toContain('0%')
})

test('assessed glare fallback is displayed when orientation is ungrounded', () => {
  const html = renderToStaticMarkup(
    <AuditStats
      scene={scene}
      audit={{ ...report, glare_alerts: [], glare_orientation_grounded: false }}
    />,
  )
  expect(html).toContain(
    'North not grounded: glare uses the default orientation',
  )
  expect(html).not.toContain('Glare orientation: Not checked')
})

test('null assessments preserve collision findings', () => {
  const html = renderToStaticMarkup(
    <AuditStats
      scene={scene}
      audit={{
        ...report,
        collisions: [{ item_a: 'a', item_b: 'b', overlap_area_m2: 0.6 }],
      }}
    />,
  )
  expect(html).toContain('Collision · a × b')
  expect(html).toContain('0.60 m²')
})
