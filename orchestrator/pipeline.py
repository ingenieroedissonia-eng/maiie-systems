"""
MAIIE System V2 - Iterative Pipeline
Modulo: Orquestacion de ciclo de refinamiento
Capa: Orchestrator
Version: 4.19.0 - Early kill + AST validation

CHANGELOG v4.19.0:
- ADD: Early kill - si el mismo feedback se repite 2 ciclos consecutivos,
       el pipeline rompe el loop y registra limite alcanzado.
       Evita desperdicio de tokens en errores no convergentes.
- ADD: Validacion AST en _validar_minimos() - rechaza codigo con
       SyntaxError antes de llegar al AUDITOR.

CHANGELOG v4.18.0:
- ADD: Contrato obligatorio routers FastAPI en engineer_base.txt

CHANGELOG v4.17.0:
- ADD: LearningEngine.update_from_missions() llamado en __init__ con el
       historial real de misiones aprobadas. A partir de esta version el
       LearningEngine calibra alpha, beta, gamma al arrancar el pipeline.
- ADD: recomendar_estrategia() inyectada en el prompt del ARCHITECT en
       iteracion 1.

CHANGELOG v4.16.0:
- FIX: ENGINEER_BASE ahora recibe orden_ceo ademas del plan_actual.

CHANGELOG v4.15.0:
- ADD: LearningEngine conectado al pipeline en modo solo lectura.

CHANGELOG v4.14.0:
- FIX: ejecutar_mision() pasa orden_ceo a obtener_contexto() para activar
       busqueda semantica de misiones similares.

CHANGELOG v4.13.0:
- FIX: _validar_minimos() ahora ignora TODOs en comentarios y docstrings.

CHANGELOG v4.12.1:
- FIX: Agregados print() junto a console.print() para visibilidad
       en entornos uvicorn donde Rich no renderiza en stdout.

CHANGELOG v4.12.0:
- P2: Pipeline ahora tipea el orquestador como AgentExecutor.
- P3: Todas las llamadas a _activar_agente() -> ejecutar_agente().

CHANGELOG v4.11.0:
- FIX: ENGINEER_SENIOR degradation fallback implementado.

CHANGELOG v4.10.0:
- FIX: RepoGenerator usa el mejor codigo_base de todos los ciclos.

CHANGELOG v4.9.0:
- FIX: Prompt del ENGINEER_SENIOR incluye lista explicita de archivos.

CHANGELOG v4.8.0:
- FIX: Feedback sintetico al ARCHITECT con instruccion de simplificacion.

CHANGELOG v4.7.0:
- ADD: Estado del validador interno inyectado en prompt del AUDITOR.

CHANGELOG v4.6.0:
- FIX: _validar_minimos() bloquea el ciclo cuando detecta placeholders.

CHANGELOG v4.5.0:
- ADD: Integracion de RepoGenerator.
- ADD: PipelineResult incluye campo repo_path.
"""

import os
import re
import sys
import ast
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
# ESTADOS DE CERTIFICACION
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
    """Estructura inmutable para el reporte de mision."""

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

    ARCHITECT -> genera plan
        |
    ENGINEER_BASE -> implementa codigo
        |
    [tracking mejor_codigo_base por cantidad de # File:]
        |
    ENGINEER_SENIOR (opcional)
        | validacion previa del Senior
        | si Senior degrada -> fallback a Base (v4.11.0)
        |
    VALIDACION MINIMA - BLOQUEADOR (AST + placeholders)
        | si falla + hay ciclos -> feedback simplificacion -> continue
        | si falla + ultimo ciclo -> auditar igual para registrar estado
        |
    AUDITOR <- recibe estado del validador interno
        |
    CERTIFICACION
        |
    EARLY KILL (v4.19.0) - si mismo error 2 ciclos -> break
        |
    REPO GENERATOR <- usa mejor_codigo_base de todos los ciclos
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
        try:
            self.learning = LearningEngine()
            misiones_aprobadas = self.memory.obtener_misiones_aprobadas(limite=50)
            if misiones_aprobadas:
                self.learning.update_from_missions(misiones_aprobadas)
        except Exception as e:
            logger.warning(f"LearningEngine no disponible: {e} - usando defaults")
            self.learning = None

    # --------------------------------------------------------------
    # EXTRAER LISTA DE ARCHIVOS DEL CODIGO BASE
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
    # VALIDACION BASICA
    # v4.19.0: AST validation agregada
    # v4.13.0: TODOs solo se detectan en codigo ejecutable real.
    # --------------------------------------------------------------

    def _validar_minimos(self, codigo: str):

        if len(codigo.strip()) < 100:
            return False, "Codigo insuficiente"

        # Validacion AST - v4.19.0
        try:
            ast.parse(codigo)
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"

        lineas_pass = [l for l in codigo.split(chr(10)) if l.strip() == "pass"]
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
            return False, "TODOs detectados en codigo ejecutable"

        return True, "Validacion basica OK"

    # --------------------------------------------------------------
    # FEEDBACK SINTETICO DE SIMPLIFICACION
    # --------------------------------------------------------------

    def _feedback_simplificacion(self, iteracion: int, causa: str) -> str:
        return (
            f"ITERACION: {iteracion}\n"
            f"CUMPLIMIENTO: 0%\n"
            f"ESTADO: RECHAZADO\n\n"
            f"BLOQUEADOR INTERNO - El codigo fue rechazado antes de llegar al auditor.\n"
            f"CAUSA: {causa}\n\n"
            f"ACCION REQUERIDA PARA EL PROXIMO CICLO:\n"
            f"- El plan anterior era demasiado complejo para implementar sin placeholders.\n"
            f"- Disena un plan MAS SIMPLE con MAXIMO 3 entidades y 4 archivos.\n"
            f"- Reduce los casos de uso a los estrictamente necesarios.\n"
            f"- Un plan acotado produce codigo completo.\n"
            f"- Un plan ambicioso produce TODOs y placeholders.\n"
            f"- NO repitas el mismo plan. Simplifica."
        )

    # --------------------------------------------------------------
    # EXTRACCION DE COMPLIANCE SCORE
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
    # VERIFICACION DE CERTIFICACION
    # --------------------------------------------------------------

    def _verificar_certificacion(self, reporte: str) -> tuple:
        if not reporte:
            return False, False, EstadoCertificacion.INDEFINIDO

        reporte_upper = reporte.upper()

        if "APROBADO CON DEUDA" in reporte_upper or "APROBADO_CON_DEUDA" in reporte_upper:
            return True, True, EstadoCertificacion.APROBADO_DEUDA

        if "ESTADO: APROBADO" in reporte_upper or "## ESTADO:" in reporte_upper:
            return True, False, EstadoCertificacion.APROBADO

        if "ESTADO: RECHAZADO" in reporte_upper:
            return False, False, EstadoCertificacion.RECHAZADO

        return False, False, EstadoCertificacion.INDEFINIDO

    # --------------------------------------------------------------
    # FEEDBACK CRITICO
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
            if any(x in linea_upper for x in ["CRITICO", "BLOQUEADOR", "RECHAZADO", "ERROR"]):
                criticas.append(linea)

        if criticas:
            return "\n".join(criticas[:10])

        return feedback[:800]

    # --------------------------------------------------------------
    # EJECUCION PRINCIPAL
    # --------------------------------------------------------------

    def ejecutar_mision(self, orquestador: AgentExecutor, orden_ceo: str):

        logger.info(f"Iniciando mision. Orden: {orden_ceo[:50]}...")
        print(f"Iniciando mision: {orden_ceo[:60]}...")

        # v4.15.0: consultar pesos del LearningEngine antes de obtener contexto.
        if self.learning:
            pesos = self.learning.get_weights(contexto=orden_ceo)
            logger.info(
                f"LearningEngine pesos: "
                f"alpha={pesos['alpha']} beta={pesos['beta']} gamma={pesos['gamma']}"
            )

        # v4.14.0: pasa orden_ceo para activar busqueda semantica.
        contexto_memoria = self.memory.obtener_contexto(orden_actual=orden_ceo)
        if contexto_memoria:
            logger.info("Contexto de misiones previas recuperado")
            print("Contexto de misiones previas recuperado")

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

        # v4.19.0: early kill - tracking de feedback repetido
        ultimo_feedback   = None
        contador_error    = 0

        for iteracion in range(1, self.max_iteraciones + 1):

            console.print(f"\n[bold blue]CICLO {iteracion}/{self.max_iteraciones}[/]")
            print(f"CICLO {iteracion}/{self.max_iteraciones}")

            # --------------------------------------------------
            # ARCHITECT
            # v4.17.0: recibe recomendacion del LearningEngine
            # --------------------------------------------------

            if iteracion == 1:
                recomendacion = ""
                if self.learning:
                    recomendacion = self.learning.recomendar_estrategia(orden_ceo)

                prompt_arq = f"""
MISION:

{orden_ceo}

ARQUITECTURAS PREVIAS DEL SISTEMA:

{contexto_memoria}
{f"RECOMENDACION DEL LEARNING ENGINE:{chr(10)}{recomendacion}{chr(10)}" if recomendacion else ""}
Disena una arquitectura considerando experiencias previas del sistema.
"""
            else:
                feedback_limpio = self._extraer_feedback_critico(feedback_actual or "")
                prompt_arq = f"""
PLAN ANTERIOR:

{plan_actual}

FEEDBACK DEL CICLO {iteracion - 1}:

{feedback_limpio}

Corrige el plan segun el feedback recibido.
"""

            print(f"ARCHITECT ejecutando...")
            plan_actual          = orquestador.ejecutar_agente("ARCHITECT", prompt_arq, "cyan")
            mission.arquitectura = plan_actual
            print(f"ARCHITECT completado")

            # --------------------------------------------------
            # ENGINEER BASE
            # v4.16.0: recibe orden_ceo como ORDEN ESPECIFICA
            # --------------------------------------------------

            print(f"ENGINEER_BASE ejecutando...")
            constraint_feedback = ""
            if iteracion > 1 and feedback_actual:
                feedback_critico = self._extraer_feedback_critico(feedback_actual)
                if feedback_critico:
                    constraint_feedback = f"\nRESTRICCIONES OBLIGATORIAS DEL CICLO ANTERIOR:\n{feedback_critico}\nSI INCUMPLES ALGUNA -> RESPUESTA INVALIDA\n"

            prompt_base = (
                f"ORDEN ESPECIFICA A IMPLEMENTAR:\n"
                f"{orden_ceo}\n\n"
                f"PLAN ARQUITECTONICO (referencia de diseno):\n"
                f"{plan_actual}\n\n"
                f"{constraint_feedback}"
                f"REGLA CRITICA: Implementa UNICAMENTE lo que describe la ORDEN ESPECIFICA.\n"
                f"El plan arquitectonico es contexto de diseno - no lo implementes completo.\n"
                f"Si la orden dice 'Crea api/user_router.py', genera SOLO ese archivo."
            )
            raw_base    = orquestador.ejecutar_agente("ENGINEER_BASE", prompt_base, "yellow")
            codigo_base = limpiar_codigo_md(raw_base)
            mission.implementacion = codigo_base
            print(f"ENGINEER_BASE completado")

            archivos_este_ciclo = len(self._extraer_archivos_base(codigo_base))
            if archivos_este_ciclo > max_archivos_base:
                max_archivos_base = archivos_este_ciclo
                mejor_codigo_base = codigo_base
                logger.info(
                    f"Mejor Base actualizado: {archivos_este_ciclo} "
                    f"archivo(s) en ciclo {iteracion}"
                )
                print(f"Mejor Base actualizado: {archivos_este_ciclo} archivo(s)")

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
                        f"ARCHIVOS QUE DEBES ENTREGAR - OBLIGATORIO INCLUIR TODOS:\n"
                        f"{lista_archivos}\n"
                        f"No fusiones estos archivos. Cada uno debe aparecer "
                        f"en tu output con su # File: como primera linea.\n"
                    )
                else:
                    seccion_archivos = ""

                prompt_senior = f"""
Optimiza este codigo para produccion.

{seccion_archivos}
PLAN:

{plan_actual}

CODIGO:

{codigo_base}
"""
                print(f"ENGINEER_SENIOR ejecutando...")
                raw_senior    = orquestador.ejecutar_agente("ENGINEER_SENIOR", prompt_senior, "bright_yellow")
                codigo_senior = limpiar_codigo_md(raw_senior)
                print(f"ENGINEER_SENIOR completado")

                if archivos_base:
                    logger.info(
                        f"Senior recibio lista de {len(archivos_base)} "
                        f"archivo(s) del Base para preservar."
                    )
                    print(f"Senior recibio lista de {len(archivos_base)} archivo(s)")

                es_valido_senior, _ = self._validar_minimos(codigo_senior)
                es_valido_base, _   = self._validar_minimos(codigo_base)

                if not es_valido_senior and es_valido_base:
                    logger.warning(
                        "Senior degrado el codigo (TODOs/placeholders). "
                        "Usando Base directamente como codigo_final."
                    )
                    console.print("[bold yellow]Senior degrado - fallback a Base activado.[/]")
                    print("Senior degrado - fallback a Base activado")
                    codigo_final = codigo_base
                else:
                    codigo_final = codigo_senior

            else:
                codigo_final = codigo_base

            # --------------------------------------------------
            # VALIDACION MINIMA - BLOQUEADOR
            # --------------------------------------------------

            es_valido, mensaje_validacion = self._validar_minimos(codigo_final)

            if not es_valido:
                logger.warning(f"Validacion bloqueada: {mensaje_validacion}")
                print(f"BLOQUEADO: {mensaje_validacion}")

                if iteracion < self.max_iteraciones:
                    feedback_actual = self._feedback_simplificacion(
                        iteracion=iteracion,
                        causa=mensaje_validacion,
                    )
                    console.print(
                        f"[bold red]BLOQUEADO: {mensaje_validacion}. "
                        f"Re-ingenieria forzada...[/]"
                    )
                    print(f"Re-ingenieria forzada en ciclo {iteracion + 1}...")
                    continue

                else:
                    logger.warning(
                        "Validacion fallo en ciclo final - "
                        "auditando para registrar estado."
                    )
                    print("Validacion fallo en ciclo final - auditando igual")

            # --------------------------------------------------
            # ESTADO DEL VALIDADOR
            # --------------------------------------------------

            estado_validador = (
                f"ESTADO VALIDADOR INTERNO: BLOQUEADO - {mensaje_validacion}"
                if not es_valido
                else "ESTADO VALIDADOR INTERNO: OK"
            )
            print(f"{estado_validador}")

            # --------------------------------------------------
            # AUDITOR
            # --------------------------------------------------

            prompt_aud = f"""
{estado_validador}

ORDEN ORIGINAL DEL CEO:
{orden_ceo}

ITERACION DEL PIPELINE: {iteracion} de {self.max_iteraciones}

PLAN ARQUITECTONICO:

{plan_actual}

CODIGO A AUDITAR:

{codigo_final}

Si la ORDEN ORIGINAL contiene "SOLO", "UNICAMENTE" o una ruta especifica de archivo,
evalua UNICAMENTE el archivo entregado - NO rechaces por archivos faltantes del plan.
Evalua estrictamente el cumplimiento de estandares de produccion.
Indica el estado con exactamente una de estas frases en tu reporte:
- ESTADO: APROBADO
- ESTADO: APROBADO CON DEUDA
- ESTADO: RECHAZADO

Incluye CUMPLIMIENTO: XX% con el porcentaje numerico.
"""

            print(f"AUDITOR ejecutando...")
            feedback_actual   = orquestador.ejecutar_agente("AUDITOR", prompt_aud, "green")
            mission.auditoria = feedback_actual
            print(f"AUDITOR completado")

            logger.info(f"FEEDBACK AUDITOR CICLO {iteracion}")
            logger.info(feedback_actual[:800])

            # --------------------------------------------------
            # EVALUACION DE CERTIFICACION
            # --------------------------------------------------

            aprobado, deuda_tecnica, estado = self._verificar_certificacion(feedback_actual)
            compliance_score = self._extraer_compliance_score(feedback_actual)

            print(f"Cumplimiento: {compliance_score}% - Estado: {estado}")

            if aprobado:

                label = "APROBADO" if not deuda_tecnica else "APROBADO CON DEUDA TECNICA"
                logger.info(
                    f"{label} en iteracion {iteracion} - "
                    f"Cumplimiento: {compliance_score}%"
                )
                print(f"{label} en iteracion {iteracion} - Cumplimiento: {compliance_score}%")

                if deuda_tecnica:
                    logger.warning(
                        "Mision aprobada con deuda tecnica. "
                        "Revisar antes de deploy."
                    )
                    print("Deuda tecnica detectada - revisar antes de deploy")

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
                    f"RepoGenerator usara mejor Base: "
                    f"{archivos_repo} archivo(s) detectados"
                )
                print(f"RepoGenerator: {archivos_repo} archivo(s) detectados")

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

            # --------------------------------------------------
            # EARLY KILL - v4.19.0
            # Si el mismo feedback se repite 2 ciclos -> break
            # --------------------------------------------------

            feedback_critico = self._extraer_feedback_critico(feedback_actual)
            if feedback_critico and feedback_critico == ultimo_feedback:
                contador_error += 1
            else:
                contador_error = 0
            ultimo_feedback = feedback_critico

            if contador_error >= 2:
                logger.warning(
                    f"Early kill activado en ciclo {iteracion} - "
                    f"mismo error {contador_error} ciclos consecutivos"
                )
                print(f"Early kill activado - mismo error repetido. Terminando.")
                break

            console.print("[bold red]RECHAZADO. Re-ingenieria iniciada...[/]")
            print(f"RECHAZADO en ciclo {iteracion} - iniciando siguiente ciclo")

        # --------------------------------------------------
        # LIMITE DE ITERACIONES ALCANZADO
        # --------------------------------------------------

        compliance_score = self._extraer_compliance_score(feedback_actual or "")
        logger.warning(
            f"Limite de iteraciones alcanzado. "
            f"Ultimo cumplimiento: {compliance_score}%"
        )
        print(f"Limite de iteraciones alcanzado. Cumplimiento final: {compliance_score}%")

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
            observaciones="Limite de iteraciones alcanzado sin certificacion.",
            repo_path=None,
        )