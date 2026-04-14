"""
MAIIE System V2 - API Gateway
MÃ³dulo: ExposiciÃ³n del sistema mediante API
Capa: Interface
VersiÃ³n: 2.2.0

CHANGELOG v2.2.0:
- ADD: Endpoint POST /publish-sistema â€” publica mÃºltiples misiones
       (una ejecuciÃ³n completa del Planner) como un Ãºnico repositorio
       consolidado en GitHub via GitHubPublisher.publicar_sistema().
       Recibe lista de mission_ids en orden de ejecuciÃ³n.
       Los archivos de todas las misiones se consolidan en un solo repo.
       Sin cambios en /publish ni en /mission.

CHANGELOG v2.1.0:
- ADD: Endpoint POST /publish â€” publica una misiÃ³n aprobada como repo
       privado en GitHub via GitHubPublisher.
       Requiere GITHUB_TOKEN y GITHUB_USERNAME en config/.env.
       Si no estÃ¡n configurados retorna 400 con mensaje claro.
       Completamente independiente del pipeline â€” no toca /mission.

CHANGELOG v2.0.1:
- ADD: Logging activado para diagnÃ³stico.
"""

import os
import sys
import logging
import threading
import uuid as _uuid

from core.missions_store_gcs import guardar as _gcs_guardar, obtener as _gcs_obtener

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("MAIIE.Main")
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from orchestrator.main import MAIIE_System
from orchestrator.pipeline import IterativePipeline
from core.planner import MAIIEPlanner
from orchestrator.planner_executor import PlannerExecutor

app = FastAPI(
    title="MAIIE API",
    description="Motor de IngenierÃ­a de Sistemas con IA",
    version="2.2"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "https://maiie-systems-graph.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAIIE_API_KEY = os.getenv("MAIIE_API_KEY", "")

@app.middleware("http")
async def verificar_api_key(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)
    if request.url.path == "/" or request.url.path == "/docs" or request.url.path == "/openapi.json":
        return await call_next(request)
    if not MAIIE_API_KEY:
        return await call_next(request)
    key = request.headers.get("X-API-Key", "")
    if key != MAIIE_API_KEY:
        return JSONResponse(status_code=401, content={"detail": "API key invalida o ausente"})
    return await call_next(request)

sistema          = MAIIE_System()
pipeline         = IterativePipeline(max_iteraciones=5)
planner          = MAIIEPlanner(sistema)
planner_executor = PlannerExecutor(planner, pipeline)

USAR_PLANNER = True  # False â†’ bypass directo al pipeline original


# ------------------------------------------------------------------
# MODELOS DE REQUEST / RESPONSE
# ------------------------------------------------------------------

class MissionRequest(BaseModel):
    orden: str


class MissionResponse(BaseModel):
    mission_id: str
    status: str
    message: str

class MissionStatusResponse(BaseModel):
    mission_id: str
    status: str
    aprobado: Optional[bool] = None
    iteracion: Optional[int] = None
    observaciones: Optional[str] = None
    logs: list = []


class PublishRequest(BaseModel):
    mission_id:  str
    repo_nombre: Optional[str] = None
    descripcion: Optional[str] = ""


class PublishResponse(BaseModel):
    repo_url:   str
    archivos:   int
    errores:    list
    mission_id: str


class PublishSistemaRequest(BaseModel):
    mission_ids:  List[str]
    repo_nombre:  Optional[str] = None
    descripcion:  Optional[str] = ""


class PublishSistemaResponse(BaseModel):
    repo_url:           str
    archivos:           int
    errores:            list
    mission_ids:        List[str]
    missions_fallidas:  List[str]


# ------------------------------------------------------------------
# ENDPOINTS
# ------------------------------------------------------------------

@app.get("/")
def root():
    return {"mensaje": "MAIIE API ONLINE"}


@app.post("/mission", response_model=MissionResponse)
def ejecutar_mision(request: MissionRequest):
    mission_id = _uuid.uuid4().hex[:12]
    submisiones_iniciales = []
    if USAR_PLANNER:
        try:
            subs_raw = planner_executor.planner.decompose(request.orden)
            submisiones_iniciales = [{"id": s["id"], "descripcion": s["descripcion"], "status": "pending"} for s in subs_raw]
        except Exception:
            submisiones_iniciales = []
    _gcs_guardar(mission_id, {"status": "running", "aprobado": None, "iteracion": None, "observaciones": None, "logs": [], "submissions": submisiones_iniciales, "orden_usuario": request.orden[:120]})

    def _run():
        try:
            def _on_submision_done(sub_id, status, codigo, feedback=None):
                try:
                    estado_actual = _gcs_obtener(mission_id)
                    if not estado_actual:
                        return
                    subs = estado_actual.get("submissions", [])
                    for s in subs:
                        if s.get("id") == sub_id:
                            s["status"] = status
                            s["codigo"] = codigo
                            if feedback is not None:
                                s["feedback"] = feedback
                            break
                    estado_actual["submissions"] = subs
                    _gcs_guardar(mission_id, estado_actual)
                except Exception as _e:
                    logger.warning(f"_on_submision_done error sub {sub_id}: {_e}")

            if USAR_PLANNER:
                submisiones, resultados = planner_executor.ejecutar(sistema, request.orden, submisiones_previas=submisiones_iniciales, on_submision_done=_on_submision_done)
                resultado = resultados[-1] if resultados else None
            else:
                submisiones = []
                resultados = []
                resultado = pipeline.ejecutar_mision(sistema, request.orden)

            _gcs_guardar(mission_id, {
                "status": "done",
                "aprobado": resultado.aprobado if resultado else False,
                "iteracion": resultado.iteracion if resultado else None,
                "observaciones": resultado.observaciones if resultado else "Sin resultado",
                "logs": [],
                "submissions": [
                    dict(s, status="done",
                         feedback=resultados[i].reporte_auditoria if USAR_PLANNER and i < len(resultados) else None,
                         codigo=resultados[i].codigo_final if USAR_PLANNER and i < len(resultados) else None)
                    for i, s in enumerate(submisiones)
                ],
                "codigo_generado": resultado.codigo_final if resultado and hasattr(resultado, "codigo_final") else None
            })

            if resultado and resultado.aprobado and not resultado.deuda_tecnica:
                try:
                    from utils.github_publisher import GitHubPublisher
                    publisher = GitHubPublisher()
                    if resultado.repo_path:
                        pipeline_mission_id = resultado.repo_path.replace('\\', '/').rstrip('/').split('/')[-1]
                        publisher.publicar_mision(mission_id=pipeline_mission_id, descripcion=request.orden)
                        logger.info('GitHub autopublish OK: ' + str(pipeline_mission_id))
                    else:
                        logger.warning('GitHub autopublish: repo_path no disponible')
                except Exception as _ge:
                    logger.warning('GitHub autopublish error: ' + str(_ge))

        except Exception as e:
            _gcs_guardar(mission_id, {"status": "error", "aprobado": None, "iteracion": None, "observaciones": str(e), "logs": []})

    threading.Thread(target=_run, daemon=True).start()
    return MissionResponse(mission_id=mission_id, status="running", message="Mision iniciada. Consulta GET /mission/{id}/status")


@app.get("/mission/{mission_id}/submissions")
def obtener_submissions(mission_id: str):
    data = _gcs_obtener(mission_id)
    if not data:
        raise HTTPException(status_code=404, detail="Mission no encontrada")
    subs = data.get("submissions", [])
    return {"mission_id": mission_id, "submissions": subs[-10:], "status": data.get("status"), "codigo_generado": data.get("codigo_generado")}

@app.get("/mission/{mission_id}/status", response_model=MissionStatusResponse)
def estado_mision(mission_id: str):
    data = _gcs_obtener(mission_id)
    if not data:
        raise HTTPException(status_code=404, detail="Mission no encontrada")
    return MissionStatusResponse(mission_id=mission_id, status=data["status"], aprobado=data.get("aprobado"), iteracion=data.get("iteracion"), observaciones=data.get("observaciones"), logs=data.get("logs", []))


@app.post("/publish", response_model=PublishResponse)
def publicar_mision(request: PublishRequest):
    """
    Publica una misiÃ³n aprobada como repositorio privado en GitHub.

    Requiere en config/.env:
        GITHUB_TOKEN    â€” Personal Access Token con scope 'repo'
        GITHUB_USERNAME â€” Usuario u organizaciÃ³n de GitHub

    Args:
        mission_id:  ID de la misiÃ³n (ej: mission_20260319_183701_a935f67f)
        repo_nombre: Nombre del repo en GitHub (opcional)
        descripcion: DescripciÃ³n del repo (opcional)
    """
    try:
        from utils.github_publisher import GitHubPublisher
        publisher = GitHubPublisher()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inicializando GitHubPublisher: {e}")

    try:
        resultado = publisher.publicar_mision(
            mission_id=request.mission_id,
            repo_nombre=request.repo_nombre or None,
            descripcion=request.descripcion or "",
        )
        return PublishResponse(
            repo_url=resultado["repo_url"],
            archivos=resultado["archivos"],
            errores=resultado["errores"],
            mission_id=resultado["mission_id"],
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e}")


@app.post("/publish-sistema", response_model=PublishSistemaResponse)
def publicar_sistema(request: PublishSistemaRequest):
    """
    Publica un sistema completo (mÃºltiples misiones del Planner) como
    un Ãºnico repositorio consolidado en GitHub.

    Todos los archivos de todas las misiones se consolidan en un solo repo.
    Si dos misiones generan el mismo archivo, la Ãºltima versiÃ³n gana.

    Args:
        mission_ids:  Lista de IDs en orden de ejecuciÃ³n del Planner.
        repo_nombre:  Nombre del repo (opcional â€” se genera desde el primer ID)
        descripcion:  DescripciÃ³n del repo (opcional)

    Ejemplo:
        {
            "mission_ids": [
                "mission_20260320_015908_e4dbdde0",
                "mission_20260320_015946_52681631",
                "mission_20260320_020245_48bd2f67"
            ],
            "repo_nombre": "email-processing-system"
        }
    """
    if not request.mission_ids:
        raise HTTPException(status_code=400, detail="mission_ids no puede estar vacÃ­o")

    try:
        from utils.github_publisher import GitHubPublisher
        publisher = GitHubPublisher()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inicializando GitHubPublisher: {e}")

    try:
        resultado = publisher.publicar_sistema(
            mission_ids=request.mission_ids,
            repo_nombre=request.repo_nombre or None,
            descripcion=request.descripcion or "",
        )
        return PublishSistemaResponse(
            repo_url=resultado["repo_url"],
            archivos=resultado["archivos"],
            errores=resultado["errores"],
            mission_ids=resultado["mission_ids"],
            missions_fallidas=resultado["missions_fallidas"],
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e}")








@app.get('/mission/{mission_id}/graph')
def obtener_graph(mission_id: str):
    data = _gcs_obtener(mission_id)
    if not data:
        raise HTTPException(status_code=404, detail="Mission no encontrada")
    subs = data.get("submissions", [])
    return {
        "mission_id": mission_id,
        "status": data.get("status"),
        "submissions": [
            {
                "id": s.get("id"),
                "descripcion": s.get("descripcion"),
                "status": s.get("status")
            }
            for s in subs
        ]
    }

@app.get('/mission/{mission_id}/submission/{sub_id}')
def obtener_submission_detail(mission_id: str, sub_id: str):
    data = _gcs_obtener(mission_id)
    if not data:
        raise HTTPException(status_code=404, detail="Mission no encontrada")
    subs = data.get("submissions", [])
    for s in subs:
        if str(s.get("id")) == str(sub_id):
            return {
                "id": s.get("id"),
                "feedback": s.get("feedback"),
                "codigo": s.get("codigo")
            }
    raise HTTPException(status_code=404, detail="Submision no encontrada")
@app.get('/missions')
def listar_misiones():
    from core.missions_store_gcs import listar as _gcs_listar
    ids = _gcs_listar()
    resultado = []
    for mid in ids:
        data = _gcs_obtener(mid)
        if data:
            observaciones = data.get('observaciones') or ''
            observaciones = observaciones or ''
            resultado.append({
                'mission_id': mid,
                'status': data.get('status'),
                'aprobado': data.get('aprobado'),
                'observaciones': observaciones,
                'orden_usuario': data.get('orden_usuario', ''),
            })
    return {'missions': resultado}

@app.get('/system/metrics')
def system_metrics():
    try:
        estado = pipeline.learning.estado() if pipeline.learning else {}
        return {
            'learning_engine': estado,
            'pipeline_version': 'v4.19.0',
            'usar_planner': USAR_PLANNER,
            'max_iteraciones': pipeline.max_iteraciones,
        }
    except Exception as e:
        return {'error': str(e)}
