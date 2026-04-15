"""
MAIIE System V2 - Planner Executor
Modulo: Ejecucion de submisiones con contexto incremental
Capa: Orchestrator
Version: 1.6.2 (ENGINEER CONTROL v2 - 100% GOLD FROZEN + CLAUDE AUDIT FIX)
"""

import os
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

    # --- MOTORES DE FILTRADO COGNITIVO ---

    def _inferir_tipo_tarea(self, sub: dict) -> str:
        if 'tipo' in sub and sub['tipo']:
            return str(sub['tipo']).upper()
        if 'metadata' in sub and isinstance(sub['metadata'], dict):
            if 'tipo' in sub['metadata']: return str(sub['metadata']['tipo']).upper()
            if 'capa' in sub['metadata']: return str(sub['metadata']['capa']).upper()

        desc_lower = sub.get('descripcion', '').lower()
        if any(k in desc_lower for k in ['react', 'jsx', 'css', 'frontend', 'ui', 'component', 'html', 'tailwind']):
            return "FRONTEND"
        elif any(k in desc_lower for k in ['api', 'endpoint', 'database', 'sql', 'backend', 'router', 'model', 'crud']):
            return "BACKEND"
        elif any(k in desc_lower for k in ['docker', 'ci/cd', 'deploy', 'infra', 'pipeline']):
            return "INFRA"
        return "GENERAL"

    def _determinar_modo_explicito(self, sub: dict, estado_proyecto: ProjectStateManager) -> str:
        resumen = estado_proyecto.resumen().lower()
        
        target = sub.get('archivo_objetivo') or (sub.get('metadata', {}).get('archivo_objetivo') if isinstance(sub.get('metadata'), dict) else None)
        if target:
            target_clean = str(target).lower().strip()
            if target_clean in resumen:
                return "MODE_PATCH"
            return "MODE_CREATE"

        desc_lower = sub.get('descripcion', '').lower()
        palabras_update = ['modificar', 'actualizar', 'refactorizar', 'fix', 'añadir a', 'corregir', 'reemplazar']
        if any(k in desc_lower for k in palabras_update):
            return "MODE_PATCH"
            
        palabras = [w.strip(".,'`\"") for w in desc_lower.split()]
        lineas_resumen = [l for l in resumen.split('\n') if l.strip()]
        
        for word in palabras:
            if len(word) > 3 and ('.' in word or '_' in word or '/' in word):
                for linea in lineas_resumen:
                    if word in linea:
                        return "MODE_PATCH"
                        
        return "MODE_CREATE"

    def _filtrar_reglas(self, raw_rules: str, tipo_tarea: str) -> str:
        if not raw_rules: return ""
        lineas = raw_rules.split('\n')
        reglas_filtradas = []
        capturando = True
        for linea in lineas:
            if linea.startswith("## "):
                header = linea.upper()
                if "GENERAL" in header or "ENVIRONMENT" in header or "CONSTRAINT" in header or "INFRA" in header:
                    capturando = True
                elif tipo_tarea in header:
                    capturando = True
                else:
                    capturando = False
            
            if capturando:
                reglas_filtradas.append(linea)
        return "\n".join(reglas_filtradas)

    def _filtrar_estado_relevante(self, resumen: str, sub: dict) -> str:
        descripcion = sub.get('descripcion', '')
        keywords = [w for w in descripcion.lower().replace('.', ' ').replace('/', ' ').split() if len(w) > 3]
        
        target = sub.get('archivo_objetivo') or (sub.get('metadata', {}).get('archivo_objetivo') if isinstance(sub.get('metadata'), dict) else None)
        if target:
            keywords.append(str(target).lower().strip())

        if not keywords: return resumen
        lineas = resumen.split('\n')
        relevantes = [linea for linea in lineas if not linea.strip() or any(k in linea.lower() for k in keywords)]
        return "\n".join(relevantes) if len(relevantes) > 2 else resumen

    # -----------------------------------------------------

    def _construir_prompt_estructurado(self, sub: dict, estado_proyecto: ProjectStateManager, contexto_bloques: List[str], plan_completo: str) -> str:
        
        tipo_tarea = self._inferir_tipo_tarea(sub)
        modo = self._determinar_modo_explicito(sub, estado_proyecto)
        estado_filtrado = self._filtrar_estado_relevante(estado_proyecto.resumen(), sub)

        task_section = (
            f"--- [TASK] ---\n"
            f"OBJETIVO: {sub['descripcion']}\n"
            f"TIPO: {tipo_tarea}\n"
        )

        plan_section = (
            f"--- [GLOBAL PLAN] ---\n"
            f"{plan_completo}\n"
            f"RECUERDA: Tú estás implementando SOLO la tarea actual [TASK]. Las demás se harán después.\n"
        )

        mode_section = (
            f"--- [MODE] ---\n"
            f"MODE: {modo}\n"
            f"REGLA DE MODO: Si es MODE_PATCH, respeta el codigo existente. Si es MODE_CREATE, estructura desde cero.\n"
        )

        state_section = (
            f"--- [PROJECT STATE (RELEVANT)] ---\n"
            f"{estado_filtrado}\n"
        )

        recent_context = "".join(contexto_bloques[-3:]) if contexto_bloques else "N/A"
        recent_section = (
            f"--- [RECENT CHANGES] ---\n"
            f"{recent_context}\n"
        )

        rules_content = ""
        rules_path = "config/prompts/engineer_rules.txt"
        if os.path.exists(rules_path):
            try:
                with open(rules_path, "r", encoding="utf-8") as f:
                    rules_content = self._filtrar_reglas(f.read().strip(), tipo_tarea)
            except Exception as e:
                logger.warning(f"Error cargando engineer_rules.txt: {e}")
        else:
            logger.warning(f"ATENCIÓN: engineer_rules.txt no encontrado. Usando reglas por defecto (SOLID).")
            rules_content = "Sigue principios SOLID y Clean Architecture rigurosamente."

        rules_section = (
            f"--- [RULES] ---\n"
            f"{rules_content}\n"
        )

        constraints_section = (
            f"--- [CONSTRAINTS] ---\n"
            f"1. APLICA RIGUROSAMENTE EL {modo}.\n"
            f"2. IMPORTS: Usa exactamente lo exportado en [RECENT CHANGES].\n"
            f"3. NO TOQUES configuraciones que no pertenezcan al [TASK].\n"
        )

        return f"{task_section}\n{plan_section}\n{mode_section}\n{state_section}\n{recent_section}\n{rules_section}\n{constraints_section}"

    def ejecutar(self, orquestador: AgentExecutor, orden: str, submisiones_previas: List[dict] = None, on_submision_done=None) -> List[Any]:
        logger.info("Iniciando ejecucion con Planner + contexto incremental v1.6.2 (GOLD + AUDIT)")

        if submisiones_previas:
            submisiones = submisiones_previas
        else:
            try:
                submisiones = self.planner.decompose(orden)
            except PlannerFailedError as e:
                logger.error(f"Mision abortada. Motivo: {e}")
                return [], []

        validator = PlanValidator()
        valido, motivo = validator.validar(submisiones)
        if not valido:
            raise PlanValidationError(motivo)

        resultados        = []
        contexto_bloques   = []  
        ids_resueltos: set = set()
        estado_proyecto = ProjectStateManager()
        
        plan_completo = self._construir_plan_completo(submisiones)
        
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

            orden_enriquecida = self._construir_prompt_estructurado(sub, estado_proyecto, contexto_bloques, plan_completo)

            try:
                resultado = self.pipeline.ejecutar_mision(orquestador, orden_enriquecida)
            except Exception as e:
                logger.error("Error en submision [%s]: %s", sub["id"], e)
                ids_resueltos.add(sub["id"])
                continue
            
            resultados.append(resultado)
            ids_resueltos.add(sub["id"])
            
            if on_submision_done:
                try:
                    _feedback = resultado.reporte_auditoria if resultado and hasattr(resultado, "reporte_auditoria") else None
                    on_submision_done(sub["id"], "done", resultado.codigo_final if resultado else None, feedback=_feedback)
                except Exception as _cb_err:
                    logger.warning(f"Error crítico en callback on_submision_done para sub {sub['id']}: {_cb_err}")

            if resultado and resultado.codigo_final:
                estado_proyecto.registrar(sub["descripcion"], resultado.codigo_final)
                firmas = self._extraer_firmas(resultado.codigo_final, sub["descripcion"])
                
                bloque_contexto = (
                    f"\n# === [{sub['id']}] ACCION: {sub['descripcion']} ===\n"
                    f"# INTENCION: Implementar lógicas de esta capa.\n"
                    f"# QUÉ NO TOCAR: Componentes y endpoints previos.\n"
                    f"{firmas}\n"
                )
                contexto_bloques.append(bloque_contexto)
            else:
                logger.warning(f"Submision {sub['id']} sin codigo final")

        return submisiones, resultados