/**
 * The spatial engine's deterministic checks, run unchanged in the browser with Pyodide:
 * the same `audit_scene` and `score_feng_shui` the FastAPI service calls, imported from
 * services/spatial_engine and contracts/schema.py at build time. No model calls.
 */
import schema from '../../../contracts/schema.py?raw'
import audit from '../../../services/spatial_engine/audit.py?raw'
import fengShuiInputs from '../../../services/spatial_engine/feng_shui_inputs.py?raw'
import fengShuiMetric from '../../../services/spatial_engine/feng_shui_metric.py?raw'
import fengShuiScore from '../../../services/spatial_engine/feng_shui_score.py?raw'
import geometry from '../../../services/spatial_engine/geometry.py?raw'
import reachability from '../../../services/spatial_engine/reachability.py?raw'
import report from '../../../services/spatial_engine/report.py?raw'

const PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v314.0.6/full/'

const SOURCES: Record<string, string> = {
  'contracts/__init__.py': '',
  'contracts/schema.py': schema,
  'services/__init__.py': '',
  'services/spatial_engine/__init__.py': '',
  'services/spatial_engine/audit.py': audit,
  'services/spatial_engine/feng_shui_inputs.py': fengShuiInputs,
  'services/spatial_engine/feng_shui_metric.py': fengShuiMetric,
  'services/spatial_engine/feng_shui_score.py': fengShuiScore,
  'services/spatial_engine/geometry.py': geometry,
  'services/spatial_engine/reachability.py': reachability,
  'services/spatial_engine/report.py': report,
}

/** Mirrors the service: validation and geometry input errors become 422s. */
const BRIDGE = `
import json, sys
sys.path.insert(0, '/engine')
from pydantic import ValidationError
from shapely.errors import ShapelyError
from contracts.schema import RoomScene
from services.spatial_engine.geometry import SpatialInputError
from services.spatial_engine.report import audit_scene
from services.spatial_engine.feng_shui_inputs import FengShuiRequest
from services.spatial_engine.feng_shui_score import score_feng_shui

def _run(kind, body):
    try:
        if kind == 'audit':
            out = audit_scene(RoomScene.model_validate_json(body))
        else:
            out = score_feng_shui(FengShuiRequest.model_validate_json(body))
        return json.dumps({'status': 200, 'body': out.model_dump(mode='json')})
    except ValidationError as exc:
        detail = [{'loc': ['body', *e['loc']], 'msg': e['msg'], 'type': e['type']}
                  for e in exc.errors(include_input=False, include_context=False)]
        return json.dumps({'status': 422, 'body': {'detail': detail}})
    except SpatialInputError as exc:
        return json.dumps({'status': 422, 'body': {'detail': [{'loc': ['body'], 'msg': str(exc), 'type': 'value_error'}]}})
    except (ShapelyError, ArithmeticError):
        return json.dumps({'status': 422, 'body': {'detail': [{'loc': ['body'], 'msg': 'Room geometry could not be processed', 'type': 'value_error'}]}})
`

interface Pyodide {
  loadPackage: (names: string[]) => Promise<unknown>
  runPython: (code: string) => unknown
  globals: { get: (name: string) => (...args: unknown[]) => string }
  FS: {
    mkdirTree: (path: string) => void
    writeFile: (path: string, data: string) => void
  }
}

async function boot() {
  const { loadPyodide } = (await import(
    /* @vite-ignore */ `${PYODIDE_URL}pyodide.mjs`
  )) as { loadPyodide: (o: { indexURL: string }) => Promise<Pyodide> }
  const py = await loadPyodide({ indexURL: PYODIDE_URL })
  await py.loadPackage(['numpy', 'shapely', 'pydantic'])
  for (const [path, source] of Object.entries(SOURCES)) {
    py.FS.mkdirTree(`/engine/${path.slice(0, path.lastIndexOf('/'))}`)
    py.FS.writeFile(`/engine/${path}`, source)
  }
  py.runPython(BRIDGE)
  return py.globals.get('_run')
}

const run = boot()
run.then(
  () => postMessage({ ready: true }),
  (error: unknown) => postMessage({ ready: false, error: String(error) }),
)

onmessage = async (
  e: MessageEvent<{ id: number; kind: 'audit' | 'score'; body: string }>,
) => {
  const { id, kind, body } = e.data
  try {
    const result = JSON.parse((await run)(kind, body)) as {
      status: number
      body: unknown
    }
    postMessage({ id, ...result })
  } catch (error) {
    // A Python exception is answered inside `_run`; reaching here means Pyodide itself
    // failed (e.g. an uncaught C++ exception) and this interpreter can't be used again.
    postMessage({
      id,
      status: 500,
      body: { detail: String(error) },
      fatal: true,
    })
  }
}
