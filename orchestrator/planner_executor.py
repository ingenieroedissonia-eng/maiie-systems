"""
MAIIE System V2 - Planner Executor
Modulo: Ejecucion de submisiones con contexto incremental
Capa: Orchestrator
Version: 1.4.0
"""

import logging
from typing import List, Any

from core.planner import MAIIEPlanner, PlannerFailedError
from core.plan_validator import PlanValidator, PlanValidationError
from core.project_state_manager import ProjectStateManager
from core.contracts import AgentExecutor


logger = logging.getLogger("MAIIE.PlannerExecutor")


class PlannerExecutor:

    def __init__(self, planner: MAIIEPlanner, pipeline):
        self.planner  = planner
        self.pipeline = pipeline

    def _construir_plan_completo(self, submisiones: List[dict]) -> str:
        lineas = ["PLAN COMPLETO DEL SISTEMA:"]
        for sub in submisiones:
            lineas.append(f"  [{sub['id']}] {sub['descripcion']}")
        return "\n".join(lineas)

    def _extraer_firmas(self, codigo: str, descripcion: str) -> str:
        if not codigo:
            return ""
        lineas_firmas = []
        lineas = codigo.split("\n")
        for linea in lineas:
            stripped = linea.strip()
            if (
                stripped.startswith("# File:")
                or stripped.startswith("from ")
                or stripped.startswith("import ")
                or stripped.startswith("class ")
                or stripped.startswith("def ")
                or stripped.startswith("async def ")
            ):
                lineas_firmas.append(linea)
        if not lineas_firmas:
            return f"# {descripcion} implementado"
        return "\n".join(lineas_firmas)

    def _verificar_dependencias(self, sub: dict, ids_resueltos: set) -> bool:
        dependencias = sub.get("dependencias", [])
        faltantes = [dep for dep in dependencias if isinstance(dep, int) and dep not in ids_resueltos]
        if faltantes:
            logger.warning(
                f"Submision [{sub['id']}] tiene dependencias no resueltas: "
                f"{faltantes} - ejecutando de todas formas"
            )
            return False
        return True

    def ejecutar(self, orquestador: AgentExecutor, orden: str, submisiones_previas: List[dict] = None, on_submision_done=None) -> List[Any]:
        logger.info("Iniciando ejecucion con Planner + contexto incremental")

        if submisiones_previas:
            logger.info(f"Usando {len(submisiones_previas)} submisiones previas (sin nuevo decompose)")
            submisiones = submisiones_previas
        else:
            try:
                submisiones = self.planner.decompose(orden)
            except PlannerFailedError as e:
                logger.error(f"Mision abortada en fase de planificacion. Motivo: {e}")
                return [], []

        validator = PlanValidator()
        valido, motivo = validator.validar(submisiones)
        if not valido:
            logger.error(f"Plan invalido: {motivo}")
            raise PlanValidationError(motivo)

        logger.info(f"Plan recibido: {len(submisiones)} submision(es)")
        for sub in submisiones:
            deps = sub.get("dependencias", [])
            dep_str = f" (deps: {deps})" if deps else ""
            logger.info(f"   [{sub['id']}] {sub['descripcion']}{dep_str}")

        resultados        = []
        contexto_compacto = ""
        ids_resueltos: set = set()
        plan_completo = self._construir_plan_completo(submisiones)
        estado_proyecto = ProjectStateManager()

        pendientes = list(submisiones)
        max_reintentos = len(pendientes) * 2
        reintentos = 0
        while pendientes:
            if reintentos > max_reintentos:
                logger.error("Ciclo de dependencias irresolvible. Abortando.")
                break
            sub = pendientes.pop(0)
            if not self._verificar_dependencias(sub, ids_resueltos):
                pendientes.append(sub)
                reintentos += 1
                continue
            reintentos = 0
            logger.info(f"Submision [{sub['id']}]: {sub['descripcion']}")

            resumen_proyecto = estado_proyecto.resumen()
            if contexto_compacto:
                orden_enriquecida = (
                    f"{sub['descripcion']}\n\n"
                    f"--- {plan_completo} ---\n\n"
                    f"--- ARCHIVOS YA GENERADOS EN EL PROYECTO ---\n"
                    f"{resumen_proyecto}\n\n"
                    f"--- MODULOS YA IMPLEMENTADOS (imports y firmas exactas) ---\n"
                    f"{contexto_compacto}\n"
                    f"--- FIN ---\n\n"
                    f"CRITICO: Usa EXACTAMENTE las mismas rutas de importacion mostradas arriba.\n"
                    f"NO inventes rutas nuevas. Si ves 'from core.interfaces import X', usa esa ruta exacta.\n"
                    f"Implementa SOLO lo que describe esta submision.\n"
                )
            else:
                orden_enriquecida = (
                    f"{sub['descripcion']}\n\n"
                    f"--- {plan_completo} ---\n\n"
                    f"Implementa SOLO lo que describe esta submision.\n"
                    f"Las capas posteriores se implementaran en submisiones siguientes.\n"
                )

            try:
                resultado = self.pipeline.ejecutar_mision(orquestador, orden_enriquecida)
            except Exception as e:
                logger.error("Error en submision [%s]: %s — continuando", sub["id"], e, exc_info=True)
                ids_resueltos.add(sub["id"])
                continue
            resultados.append(resultado)
            ids_resueltos.add(sub["id"])
            if on_submision_done:
                try:
                    _feedback = resultado.reporte_auditoria if resultado and hasattr(resultado, "reporte_auditoria") else None
                    on_submision_done(sub["id"], "done", resultado.codigo_final if resultado and resultado.codigo_final else None, feedback=_feedback)
                except Exception as _cb_err:
                    logger.warning(f"Callback on_submision_done error: {_cb_err}")

            if resultado and resultado.codigo_final:
                estado_proyecto.registrar(sub["descripcion"], resultado.codigo_final)
                firmas = self._extraer_firmas(resultado.codigo_final, sub["descripcion"])
                contexto_compacto += (
                    f"\n# === [{sub['id']}] {sub['descripcion']} ===\n"
                    f"{firmas}\n"
                )
                logger.info(f"Contexto acumulado hasta submision {sub['id']}")
            else:
                logger.warning(f"Submision {sub['id']} no genero codigo_final")

        logger.info(f"Ejecucion completa: {len(resultados)} resultado(s)")
        return submisiones, resultados
