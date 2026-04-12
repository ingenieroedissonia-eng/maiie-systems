"""
MAIIE System V2 - Iterative Pipeline
MÃ³dulo: OrquestaciÃ³n de ciclo de refinamiento
Capa: Orchestrator
VersiÃ³n: 4.17.0 â€” LearningEngine calibraciÃ³n dinÃ¡mica activa

CHANGELOG v4.17.0:
- ADD: LearningEngine.update_from_missions() llamado en __init__ con el
       historial real de misiones aprobadas. A partir de esta versiÃ³n el
       LearningEngine calibra Î±, Î², Î³ al arrancar el pipeline en lugar de
       operar siempre con pesos estÃ¡ticos.
- ADD: recomendar_estrategia() inyectada en el prompt del ARCHITECT en
       iteraciÃ³n 1. Si el LearningEngine detecta patrones relevantes en
       el contexto de la orden, el ARCHITECT los recibe como guÃ­a.
- KEEP: Comportamiento idÃ©ntico si LearningEngine falla â€” defaults sin
        interrupciÃ³n. Cambio quirÃºrgico â€” sin modificaciones en contratos,
        lÃ³gica del pipeline ni otros agentes.

CHANGELOG v4.16.0:
- FIX: ENGINEER_BASE ahora recibe orden_ceo ademÃ¡s del plan_actual.
       Causa raÃ­z: el prompt del ENGINEER_BASE solo pasaba plan_actual,
       ignorando la orden_enriquecida del PlannerExecutor. El ARCHITECT
       recibÃ­a la submisiÃ³n atÃ³mica correctamente, pero el ENGINEER_BASE
       solo veÃ­a el plan arquitectÃ³nico completo y lo implementaba todo.
       SoluciÃ³n: prompt_base incluye orden_ceo como ORDEN ESPECÃFICA con
       prioridad sobre el plan arquitectÃ³nico de referencia.

CHANGELOG v4.15.0:
- ADD: LearningEngine conectado al pipeline en modo solo lectura.

CHANGELOG v4.14.0:
- FIX: ejecutar_mision() pasa orden_ceo a obtener_contexto() para activar
       bÃºsqueda semÃ¡ntica de misiones similares (mission_memory.py v1.4.0).

CHANGELOG v4.13.0:
- FIX: _validar_minimos() ahora ignora TODOs en comentarios y docstrings.

CHANGELOG v4.12.1:
- FIX: Agregados print() junto a console.print() para visibilidad
       en entornos uvicorn donde Rich no renderiza en stdout.

CHANGELOG v4.12.0:
- P2: Pipeline ahora tipea el orquestador como AgentExecutor.
- P3: Todas las llamadas a _activar_agente() â†’ ejecutar_agente().

CHANGELOG v4.11.0:
- FIX: ENGINEER_SENIOR degradation fallback implementado.

CHANGELOG v4.10.0:
- FIX: RepoGenerator usa el mejor codigo_base de todos los ciclos.

CHANGELOG v4.9.0:
- FIX: Prompt del ENGINEER_SENIOR incluye lista explÃ­cita de archivos.

CHANGELOG v4.8.0:
- FIX: Feedback sintÃ©tico al ARCHITECT con instrucciÃ³n de simplificaciÃ³n.

CHANGELOG v4.7.0:
- ADD: Estado del validador interno inyectado en prompt del AUDITOR.

CHANGELOG v4.6.0:
- FIX: _validar_minimos() bloquea el ciclo cuando detecta placeholders.

CHANGELOG v4.5.0:
- ADD: IntegraciÃ³n de RepoGenerator.
- ADD: PipelineResult incluye campo repo_path.
"""

import os
import re
import sys
import uuid
import logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List

from rich.console import Console

from core.registry import ModelRegistry, Config
from core.mission_schema import Mission
from core.mission_memory import MissionMemory
from core.contracts import AgentExecutor
from core.learning_engine import LearningEngine

from utils.helpers import limpiar_codigo_md, guardar_artefacto
from utils.artifact_manager import ArtifactManager
from utils.repo_generator import RepoGenerator


# ------------------------------------------------------------------
# PATH SETUP
# ------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


# ------------------------------------------------------------------
# LOGGING & CONSOLE
# ------------------------------------------------------------------

console = Console()
logger = logging.getLogger("MAIIE.Pipeline")


# ------------------------------------------------------------------
# ESTADOS DE CERTIFICACIÃ“N
# ------------------------------------------------------------------

class EstadoCertificacion:
    APROBADO        = "APROBADO"
    APROBADO_DEUDA  = "APROBADO_CON_DEUDA"
    RECHAZADO       = "RECHAZADO"
    INDEFINIDO      = "INDEFINIDO"


# ------------------------------------------------------------------
# RESULT STRUCTURE
# ------------------------------------------------------------------

@dataclass
class PipelineResult:
    """Estructura inmutable para el reporte de misiÃ³n."""

    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    orden_ceo: str = ""

    plan_arquitectonico: Optional[str] = None
    codigo_base: Optional[str] = None
    codigo_final: Optional[str] = None
    reporte_auditoria: Optional[str] = None

    aprobado: bool = False
    deuda_tecnica: bool = False
    compliance_score: int = 0
    iteracion: int = 0
    observaciones: str = ""
    repo_path: Optional[str] = None


# ------------------------------------------------------------------
# ITERATIVE PIPELINE
# ------------------------------------------------------------------

class IterativePipeline:
    """
    Motor de Refinamiento Iterativo M.A.I.I.E.

    Recibe cualquier objeto que implemente AgentExecutor.
    No depende de MAIIE_System directamente.

    Flujo por ciclo:

    ARCHITECT â†’ genera plan
        â†“
    ENGINEER_BASE â†’ implementa cÃ³digo
        â†“
    [tracking mejor_codigo_base por cantidad de # File:]
        â†“
    ENGINEER_SENIOR (opcional)
        â†“ validaciÃ³n previa del Senior
        â†“ si Senior degrada â†’ fallback a Base (v4.11.0)
        â†“
    VALIDACIÃ“N MÃNIMA â€” BLOQUEADOR
        â†“ si falla + hay ciclos â†’ feedback simplificaciÃ³n â†’ continue
        â†“ si falla + Ãºltimo ciclo â†’ auditar igual para registrar estado
        â†“
    AUDITOR â† recibe estado del validador interno
        â†“
    CERTIFICACIÃ“N
        â†“
    REPO GENERATOR â† usa mejor_codigo_base de todos los ciclos
    """

    def __init__(self, max_iteraciones: int = 3):

        self.registry        = ModelRegistry()
        self.max_iteraciones = max_iteraciones

        self.use_senior = (
            os.getenv("MAIIE_USE_SENIOR_ENGINEER", "false").lower() == "true"
        )

        self.artifacts      = ArtifactManager()
        self.memory         = MissionMemory()
        self.repo_generator = RepoGenerator()

        # v4.17.0: LearningEngine calibrado con historial real al inicializar.
        # Si falla, el pipeline opera igual que v4.16.0 â€” sin interrupciÃ³n.
        try:
            self.learning = LearningEngine()
            misiones_aprobadas = self.memory.obtener_misiones_aprobadas(limite=50)
            if misiones_aprobadas:
                self.learning.update_from_missions(misiones_aprobadas)
        except Exception as e:
            logger.warning(f"âš ï¸ LearningEngine no disponible: {e} â€” usando defaults")
            self.learning = None

    # --------------------------------------------------------------
    # EXTRAER LISTA DE ARCHIVOS DEL CÃ“DIGO BASE
    # --------------------------------------------------------------

    def _extraer_archivos_base(self, codigo: str) -> List[str]:
        patron  = r"(?:#\s*File:|Archivo:)\s*([^\n]+)"
        matches = re.findall(patron, codigo)

        vistos = set()
        unicos = []
        for m in matches:
            ruta = m.strip()
            if ruta not in vistos:
                vistos.add(ruta)
                unicos.append(ruta)

        return unicos

    # --------------------------------------------------------------
    # VALIDACIÃ“N BÃSICA
    # v4.13.0: TODOs solo se detectan en cÃ³digo ejecutable real.
    # --------------------------------------------------------------

    def _validar_minimos(self, codigo: str):


        if len(codigo.strip()) < 100:
            return False, "Codigo insuficiente"






        lineas_pass = [l for l in codigo.split("
") if l.strip() == "pass"]
        if len(lineas_pass) > 3:
            return False, "Demasiados placeholders"

        lineas_ejecutables = []
        en_docstring = False
        for linea in codigo.split("\n"):
            stripped = linea.strip()

            if stripped.startswith('"""') or stripped.startswith("'''"):
                en_docstring = not en_docstring
                continue

            if en_docstring:
                continue

            if stripped.startswith("#"):
                continue

            lineas_ejecutables.append(linea)

        codigo_ejecutable = "\n".join(lineas_ejecutables)
        logger.info("VALIDADOR_SAMPLE: %s", repr(codigo_ejecutable[:3000]))
        
        if re.search(r'\bTODO\b', codigo_ejecutable, re.IGNORECASE):
            return False, "TODOs detectados en cÃ³digo ejecutable"
        return True, "ValidaciÃ³n bÃ¡sica OK"

    # --------------------------------------------------------------
    # FEEDBACK SINTÃ‰TICO DE SIMPLIFICACIÃ“N
    # --------------------------------------------------------------

    def _feedback_simplificacion(self, iteracion: int, causa: str) -> str:
        return (
            f"ITERACIÃ“N: {iteracion}\n"
            f"CUMPLIMIENTO: 0%\n"
            f"ESTADO: RECHAZADO\n\n"
            f"BLOQUEADOR INTERNO â€” El cÃ³digo fue rechazado antes de llegar al auditor.\n"
            f"CAUSA: {causa}\n\n"
            f"ACCIÃ“N REQUERIDA PARA EL PRÃ“XIMO CICLO:\n"
            f"- El plan anterior era demasiado complejo para implementar sin placeholders.\n"
            f"- DiseÃ±a un plan MÃS SIMPLE con MÃXIMO 3 entidades y 4 archivos.\n"
            f"- Reduce los casos de uso a los estrictamente necesarios.\n"
            f"- Un plan acotado produce cÃ³digo completo.\n"
            f"- Un plan ambicioso produce TODOs y placeholders.\n"
            f"- NO repitas el mismo plan. Simplifica."
        )

    # --------------------------------------------------------------
    # EXTRACCIÃ“N DE COMPLIANCE SCORE
    # --------------------------------------------------------------

    def _extraer_compliance_score(self, reporte: str) -> int:
        if not reporte:
            return 0

        patron = r"CUMPLIMIENTO[:\s*]+(\d{1,3})%"
        match  = re.search(patron, reporte, re.IGNORECASE)

        if match:
            return int(match.group(1))

        return 0

    # --------------------------------------------------------------
    # VERIFICACIÃ“N DE CERTIFICACIÃ“N
    # --------------------------------------------------------------

    def _verificar_certificacion(self, reporte: str) -> tuple[bool, bool, str]:
        if not reporte:
            return False, False, EstadoCertificacion.INDEFINIDO

        reporte_upper = reporte.upper()

        if "APROBADO CON DEUDA" in reporte_upper or "APROBADO_CON_DEUDA" in reporte_upper:
            return True, True, EstadoCertificacion.APROBADO_DEUDA

        if "ESTADO: APROBADO" in reporte_upper or "## ESTADO: âœ…" in reporte_upper:
            return True, False, EstadoCertificacion.APROBADO

        if "ESTADO: RECHAZADO" in reporte_upper:
            return False, False, EstadoCertificacion.RECHAZADO

        return False, False, EstadoCertificacion.INDEFINIDO

    # --------------------------------------------------------------
    # FEEDBACK CRÃTICO
    # --------------------------------------------------------------

    def _extraer_feedback_critico(self, feedback: str) -> str:
        if not feedback:
            return ""

        if "BLOQUEADOR INTERNO" in feedback:
            return feedback

        lineas   = feedback.split("\n")
        criticas = []

        for linea in lineas:
            linea_upper = linea.upper()
            if any(x in linea_upper for x in ["CRÃTICO", "BLOQUEADOR", "RECHAZADO", "ERROR", "âŒ"]):
                criticas.append(linea)

        if criticas:
            return "\n".join(criticas[:10])

        return feedback[:800]

    # --------------------------------------------------------------
    # EJECUCIÃ“N PRINCIPAL
    # --------------------------------------------------------------

    def ejecutar_mision(self, orquestador: AgentExecutor, orden_ceo: str):

        logger.info(f"ðŸš€ Iniciando misiÃ³n. Orden: {orden_ceo[:50]}...")
        print(f"ðŸš€ Iniciando misiÃ³n: {orden_ceo[:60]}...")

        # v4.15.0: consultar pesos del LearningEngine antes de obtener contexto.
        if self.learning:
            pesos = self.learning.get_weights(contexto=orden_ceo)
            logger.info(
                f"ðŸ§  LearningEngine pesos: "
                f"Î±={pesos['alpha']} Î²={pesos['beta']} Î³={pesos['gamma']}"
            )

        # v4.14.0: pasa orden_ceo para activar bÃºsqueda semÃ¡ntica.
        contexto_memoria = self.memory.obtener_contexto(orden_actual=orden_ceo)
        if contexto_memoria:
            logger.info("ðŸ§  Contexto de misiones previas recuperado")
            print("ðŸ§  Contexto de misiones previas recuperado")

        mission_suffix = uuid.uuid4().hex[:8]
        mission_id     = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{mission_suffix}"

        mission = Mission(
            mission_id=mission_id,
            timestamp=datetime.now(),
            orden_usuario=orden_ceo,
        )

        plan_actual     = None
        codigo_base     = None
        codigo_final    = None
        feedback_actual = None

        mejor_codigo_base = None
        max_archivos_base = 0

        for iteracion in range(1, self.max_iteraciones + 1):

            console.print(f"\n[bold blue]ðŸŒ€ CICLO {iteracion}/{self.max_iteraciones}[/]")
            print(f"ðŸŒ€ CICLO {iteracion}/{self.max_iteraciones}")

            # --------------------------------------------------
            # ARCHITECT
            # v4.17.0: recibe recomendaciÃ³n del LearningEngine
            # si detecta patrones relevantes en la orden.
            # --------------------------------------------------

            if iteracion == 1:
                recomendacion = ""
                if self.learning:
                    recomendacion = self.learning.recomendar_estrategia(orden_ceo)

                prompt_arq = f"""
MISIÃ“N:

{orden_ceo}

ARQUITECTURAS PREVIAS DEL SISTEMA:

{contexto_memoria}
{f"RECOMENDACIÃ“N DEL LEARNING ENGINE:{chr(10)}{recomendacion}{chr(10)}" if recomendacion else ""}
DiseÃ±a una arquitectura considerando experiencias previas del sistema.
"""
            else:
                feedback_limpio = self._extraer_feedback_critico(feedback_actual or "")
                prompt_arq = f"""
PLAN ANTERIOR:

{plan_actual}

FEEDBACK DEL CICLO {iteracion - 1}:

{feedback_limpio}

Corrige el plan segÃºn el feedback recibido.
"""

            print(f"ðŸ—ï¸  ARCHITECT ejecutando...")
            plan_actual          = orquestador.ejecutar_agente("ARCHITECT", prompt_arq, "cyan")
            mission.arquitectura = plan_actual
            print(f"âœ… ARCHITECT completado")

            # --------------------------------------------------
            # ENGINEER BASE
            # v4.16.0: recibe orden_ceo como ORDEN ESPECÃFICA con
            # prioridad sobre el plan arquitectÃ³nico de referencia.
            # --------------------------------------------------

            print(f"ðŸ”§ ENGINEER_BASE ejecutando...")
            prompt_base = (
                f"ORDEN ESPECÃFICA A IMPLEMENTAR:\n"
                f"{orden_ceo}\n\n"
                f"PLAN ARQUITECTÃ“NICO (referencia de diseÃ±o):\n"
                f"{plan_actual}\n\n"
                f"REGLA CRÃTICA: Implementa ÃšNICAMENTE lo que describe la ORDEN ESPECÃFICA.\n"
                f"El plan arquitectÃ³nico es contexto de diseÃ±o â€” no lo implementes completo.\n"
                f"Si la orden dice 'Crea api/user_router.py', genera SOLO ese archivo."
            )
            raw_base    = orquestador.ejecutar_agente("ENGINEER_BASE", prompt_base, "yellow")
            codigo_base = limpiar_codigo_md(raw_base)
            mission.implementacion = codigo_base
            print(f"âœ… ENGINEER_BASE completado")

            archivos_este_ciclo = len(self._extraer_archivos_base(codigo_base))
            if archivos_este_ciclo > max_archivos_base:
                max_archivos_base = archivos_este_ciclo
                mejor_codigo_base = codigo_base
                logger.info(
                    f"ðŸ“ Mejor Base actualizado: {archivos_este_ciclo} "
                    f"archivo(s) en ciclo {iteracion}"
                )
                print(f"ðŸ“ Mejor Base actualizado: {archivos_este_ciclo} archivo(s)")

            # --------------------------------------------------
            # ENGINEER SENIOR (opcional)
            # --------------------------------------------------

            if self.use_senior:

                archivos_base = self._extraer_archivos_base(codigo_base)

                if archivos_base:
                    lista_archivos = "\n".join(
                        f"- # File: {ruta}" for ruta in archivos_base
                    )
                    seccion_archivos = (
                        f"ARCHIVOS QUE DEBES ENTREGAR â€” OBLIGATORIO INCLUIR TODOS:\n"
                        f"{lista_archivos}\n"
                        f"No fusiones estos archivos. Cada uno debe aparecer "
                        f"en tu output con su # File: como primera lÃ­nea.\n"
                    )
                else:
                    seccion_archivos = ""

                prompt_senior = f"""
Optimiza este cÃ³digo para producciÃ³n.

{seccion_archivos}
PLAN:

{plan_actual}

CÃ“DIGO:

{codigo_base}
"""
                print(f"ðŸŽ¯ ENGINEER_SENIOR ejecutando...")
                raw_senior    = orquestador.ejecutar_agente("ENGINEER_SENIOR", prompt_senior, "bright_yellow")
                codigo_senior = limpiar_codigo_md(raw_senior)
                print(f"âœ… ENGINEER_SENIOR completado")

                if archivos_base:
                    logger.info(
                        f"ðŸ“‹ Senior recibiÃ³ lista de {len(archivos_base)} "
                        f"archivo(s) del Base para preservar."
                    )
                    print(f"ðŸ“‹ Senior recibiÃ³ lista de {len(archivos_base)} archivo(s)")

                es_valido_senior, _ = self._validar_minimos(codigo_senior)
                es_valido_base, _   = self._validar_minimos(codigo_base)

                if not es_valido_senior and es_valido_base:
                    logger.warning(
                        "âš ï¸ Senior degradÃ³ el cÃ³digo (TODOs/placeholders). "
                        "Usando Base directamente como codigo_final."
                    )
                    console.print(
                        "[bold yellow]âš ï¸ Senior degradÃ³ â€” fallback a Base activado.[/]"
                    )
                    print("âš ï¸ Senior degradÃ³ â€” fallback a Base activado")
                    codigo_final = codigo_base
                else:
                    codigo_final = codigo_senior

            else:
                codigo_final = codigo_base

            # --------------------------------------------------
            # VALIDACIÃ“N MÃNIMA â€” BLOQUEADOR
            # --------------------------------------------------

            es_valido, mensaje_validacion = self._validar_minimos(codigo_final)

            if not es_valido:
                logger.warning(f"ðŸš« ValidaciÃ³n bloqueada: {mensaje_validacion}")
                print(f"ðŸš« BLOQUEADO: {mensaje_validacion}")

                if iteracion < self.max_iteraciones:
                    feedback_actual = self._feedback_simplificacion(
                        iteracion=iteracion,
                        causa=mensaje_validacion,
                    )
                    console.print(
                        f"[bold red]ðŸš« BLOQUEADO: {mensaje_validacion}. "
                        f"Re-ingenierÃ­a forzada...[/]"
                    )
                    print(f"ðŸ” Re-ingenierÃ­a forzada en ciclo {iteracion + 1}...")
                    continue

                else:
                    logger.warning(
                        "âš ï¸ ValidaciÃ³n fallÃ³ en ciclo final â€” "
                        "auditando para registrar estado."
                    )
                    print("âš ï¸ ValidaciÃ³n fallÃ³ en ciclo final â€” auditando igual")

            # --------------------------------------------------
            # ESTADO DEL VALIDADOR
            # --------------------------------------------------

            estado_validador = (
                f"ESTADO VALIDADOR INTERNO: BLOQUEADO â€” {mensaje_validacion}"
                if not es_valido
                else "ESTADO VALIDADOR INTERNO: OK"
            )
            print(f"ðŸ” {estado_validador}")

            # --------------------------------------------------
            # AUDITOR
            # --------------------------------------------------

            prompt_aud = f"""
{estado_validador}

ORDEN ORIGINAL DEL CEO:
{orden_ceo}

ITERACIÃ“N DEL PIPELINE: {iteracion} de {self.max_iteraciones}

PLAN ARQUITECTÃ“NICO:

{plan_actual}

CÃ“DIGO A AUDITAR:

{codigo_final}

Si la ORDEN ORIGINAL contiene "SOLO", "UNICAMENTE" o una ruta especifica de archivo,
evalua UNICAMENTE el archivo entregado â€” NO rechaces por archivos faltantes del plan.
EvalÃºa estrictamente el cumplimiento de estÃ¡ndares de producciÃ³n.
Indica el estado con exactamente una de estas frases en tu reporte:
- ESTADO: APROBADO
- ESTADO: APROBADO CON DEUDA
- ESTADO: RECHAZADO

Incluye CUMPLIMIENTO: XX% con el porcentaje numÃ©rico.
"""
             
            print(f"ðŸ” AUDITOR ejecutando...")
            feedback_actual   = orquestador.ejecutar_agente("AUDITOR", prompt_aud, "green")
            mission.auditoria = feedback_actual
            print(f"âœ… AUDITOR completado")

            logger.info(f"ðŸ“‹ FEEDBACK AUDITOR CICLO {iteracion}")
            logger.info(feedback_actual[:800])

            # --------------------------------------------------
            # EVALUACIÃ“N DE CERTIFICACIÃ“N
            # --------------------------------------------------

            aprobado, deuda_tecnica, estado = self._verificar_certificacion(feedback_actual)
            compliance_score = self._extraer_compliance_score(feedback_actual)

            print(f"ðŸ“Š Cumplimiento: {compliance_score}% â€” Estado: {estado}")

            if aprobado:

                label = "âœ… APROBADO" if not deuda_tecnica else "âœ… APROBADO CON DEUDA TÃ‰CNICA"
                logger.info(
                    f"{label} en iteraciÃ³n {iteracion} â€” "
                    f"Cumplimiento: {compliance_score}%"
                )
                print(f"{label} en iteraciÃ³n {iteracion} â€” Cumplimiento: {compliance_score}%")

                if deuda_tecnica:
                    logger.warning(
                        "âš ï¸ MisiÃ³n aprobada con deuda tÃ©cnica. "
                        "Revisar antes de deploy."
                    )
                    print("âš ï¸ Deuda tÃ©cnica detectada â€” revisar antes de deploy")

                mission.aprobado        = True
                mission.iteracion_final = iteracion

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename  = f"prod_{timestamp}.py"
                guardar_artefacto(filename, codigo_final)
                mission.artefacto_codigo = filename

                self.artifacts.guardar_artefactos(
                    arquitectura=plan_actual,
                    codigo=codigo_final,
                    auditoria=feedback_actual,
                    metadata={
                        "mission_id":       mission_id,
                        "iteracion_final":  iteracion,
                        "estado":           estado,
                        "compliance_score": compliance_score,
                        "deuda_tecnica":    deuda_tecnica,
                        "orden_usuario":    orden_ceo[:300],
                        "modelos": {
                            "architect": Config.MODEL_ARCHITECT,
                            "engineer":  Config.MODEL_ENGINEER,
                            "auditor":   Config.MODEL_AUDITOR,
                        }
                    }
                )

                codigo_para_repo = mejor_codigo_base or codigo_base
                archivos_repo    = len(self._extraer_archivos_base(codigo_para_repo))
                logger.info(
                    f"ðŸ“ RepoGenerator usarÃ¡ mejor Base: "
                    f"{archivos_repo} archivo(s) detectados"
                )
                print(f"ðŸ“ RepoGenerator: {archivos_repo} archivo(s) detectados")

                repo_path = self.repo_generator.generar_repo(
                    implementation_text=codigo_para_repo,
                    mission_id=mission_id,
                )

                return PipelineResult(
                    orden_ceo=orden_ceo,
                    plan_arquitectonico=plan_actual,
                    codigo_base=codigo_base,
                    codigo_final=codigo_final,
                    reporte_auditoria=feedback_actual,
                    aprobado=True,
                    deuda_tecnica=deuda_tecnica,
                    compliance_score=compliance_score,
                    iteracion=iteracion,
                    observaciones=f"Estado: {estado}",
                    repo_path=repo_path,
                )

            console.print("[bold red]âš ï¸ RECHAZADO. ReingenierÃ­a iniciada...[/]")
            print(f"âŒ RECHAZADO en ciclo {iteracion} â€” iniciando siguiente ciclo")

        # --------------------------------------------------
        # LÃMITE DE ITERACIONES ALCANZADO
        # --------------------------------------------------

        compliance_score = self._extraer_compliance_score(feedback_actual or "")
        logger.warning(
            f"âš ï¸ LÃ­mite de iteraciones alcanzado. "
            f"Ãšltimo cumplimiento: {compliance_score}%"
        )
        print(f"â›” LÃ­mite de iteraciones alcanzado. Cumplimiento final: {compliance_score}%")

        return PipelineResult(
            orden_ceo=orden_ceo,
            plan_arquitectonico=plan_actual,
            codigo_base=codigo_base,
            codigo_final=codigo_final,
            reporte_auditoria=feedback_actual,
            aprobado=False,
            deuda_tecnica=False,
            compliance_score=compliance_score,
            iteracion=self.max_iteraciones,
            observaciones="LÃ­mite de iteraciones alcanzado sin certificaciÃ³n.",
            repo_path=None,
        )
