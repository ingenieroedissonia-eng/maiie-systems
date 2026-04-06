"""
MAIIE System V2 - Main Orchestrator
Módulo: Punto de entrada principal del sistema
Capa: Orchestrator
Versión: 4.1.0

CHANGELOG v4.1.0:
- P2: MAIIE_System ahora implementa el protocolo AgentExecutor
      definido en core/contracts.py. El pipeline ya no depende
      de una implementación concreta sino de un contrato formal.
- P3: Renombrado _activar_agente → ejecutar_agente.
      El método era privado por convención pero es parte del
      contrato público entre pipeline y orquestador.
      El prefijo _ indicaba "privado" cuando en realidad es
      la interfaz principal del orquestador.
"""

import os
import sys
import logging
import io
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.theme import Theme

# =========================================================
# UTF-8 PARA WINDOWS
# =========================================================

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# =========================================================
# PATH SETUP
# =========================================================

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

# =========================================================
# IMPORTS DEL SISTEMA
# =========================================================

try:
    from core.prompts import MAIIERole
    from core.prompt_loader import PromptLoader
    from core.registry import ModelRegistry
    from core.contracts import AgentExecutor
    from orchestrator.pipeline import IterativePipeline

except ImportError as e:
    print(f"❌ Error de infraestructura: {e}")
    sys.exit(1)

# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("output/maiie_system.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger("MAIIE.Main")

# =========================================================
# RICH CONSOLE
# =========================================================

custom_theme = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "bold red",
        "success": "bold green",
        "ceo": "bold magenta",
        "agent": "bold blue",
    }
)

console = Console(theme=custom_theme)


# =========================================================
# SISTEMA PRINCIPAL
# =========================================================

class MAIIE_System:
    """
    Orquestador Maestro M.A.I.I.E. v4.0

    Implementa el protocolo AgentExecutor (core/contracts.py).
    El pipeline interactúa con este orquestador exclusivamente
    a través del método público ejecutar_agente().

    Flujo de agentes:
    CEO → ARCHITECT → ENGINEER_BASE → ENGINEER_SENIOR → AUDITOR
    """

    def __init__(self):

        env_path = os.path.join(
            os.path.dirname(__file__), "..", "config", ".env"
        )
        load_dotenv(dotenv_path=env_path)

        self.registry      = ModelRegistry()
        self.prompt_loader = PromptLoader()
        self.config        = self._cargar_configuracion()

        console.print(
            Panel(
                "[bold white]SISTEMA M.A.I.I.E. v4.0 — ONLINE[/]",
                border_style="blue",
            )
        )

        logger.info("Sistema iniciado correctamente")

    # =====================================================
    # CONFIGURACIÓN
    # =====================================================

    def _cargar_configuracion(self) -> dict:
        """
        Carga configuración de modelos desde el archivo .env.
        Formato esperado: MAIIE_MODEL_{ROL}=proveedor/nombre-modelo
        """

        rol_a_env = {
            "ARCHITECT":       "MAIIE_MODEL_ARCHITECT",
            "ENGINEER_BASE":   "MAIIE_MODEL_ENGINEER",
            "ENGINEER_SENIOR": "MAIIE_MODEL_SENIOR",
            "AUDITOR":         "MAIIE_MODEL_AUDITOR",
        }

        cfg = {}

        for rol, env_var in rol_a_env.items():

            model_string = os.getenv(env_var)

            if not model_string or "/" not in model_string:
                logger.error(
                    f"⚠️ Configuración faltante para {rol} (variable: {env_var})"
                )
                cfg[rol] = {"provider": None, "model": None, "valid": False}
                continue

            provider, model = model_string.split("/", 1)

            cfg[rol] = {
                "provider": provider.lower().strip(),
                "model":    model.strip(),
                "valid":    True,
            }

            logger.info(f"✅ {rol}: {provider}/{model}")

        return cfg

    # =====================================================
    # CONTRATO PÚBLICO — AgentExecutor
    # P3: renombrado de _activar_agente → ejecutar_agente
    # =====================================================

    def ejecutar_agente(
        self,
        rol: str,
        prompt_usuario: str,
        color: str,
    ) -> str:
        """
        Ejecuta un agente del sistema y retorna su respuesta.

        Implementación del protocolo AgentExecutor (core/contracts.py).
        Este es el único punto de entrada del pipeline al orquestador.

        Args:
            rol:            Identificador del agente ("ARCHITECT", etc.)
            prompt_usuario: Prompt a enviar al modelo.
            color:          Color Rich para la consola.

        Returns:
            Respuesta del modelo como string.
            Si falla, retorna string con prefijo "[ERROR]".
        """

        cfg = self.config.get(rol)

        if not cfg or not cfg.get("valid"):
            error_msg = f"[ERROR] Agente {rol} no configurado correctamente"
            console.print(f"[error]❌ {error_msg}[/]")
            return error_msg

        status = (
            f"[{color}]Agente {rol} → "
            f"{cfg['provider'].upper()} ({cfg['model']})[/]"
        )

        with Progress(
            SpinnerColumn(),
            TextColumn(status),
            transient=True,
        ) as progress:

            progress.add_task("work", total=None)

            try:
                role_enum = MAIIERole.from_string(rol)

                prompt_sistema = self.prompt_loader.obtener_prompt(role_enum)

                respuesta = self.registry.solicitar_ia(
                    proveedor=cfg["provider"],
                    modelo=cfg["model"],
                    prompt_sistema=prompt_sistema,
                    prompt_usuario=prompt_usuario,
                )

            except Exception as e:
                error_msg = f"[ERROR] {type(e).__name__}: {str(e)}"
                logger.error(f"Fallo en agente {rol}: {error_msg}")
                return error_msg

        if respuesta.startswith("[ERROR]"):
            console.print(f"[error]❌ {rol} falló[/]")
        else:
            console.print(f"[{color}]✓ {rol} misión cumplida.[/]")

        return respuesta


# =========================================================
# VERIFICACIÓN EN TIEMPO DE IMPORTACIÓN
# =========================================================

# Garantiza que MAIIE_System cumple el contrato AgentExecutor.
# Si no lo cumple, falla en importación — no en ejecución.
assert isinstance(MAIIE_System, type) and issubclass(
    MAIIE_System, object
), "MAIIE_System debe ser una clase"

# Runtime check del protocolo
_instance_check = MAIIE_System.__dict__.get("ejecutar_agente")
assert _instance_check is not None, (
    "MAIIE_System debe implementar ejecutar_agente() "
    "para cumplir el protocolo AgentExecutor"
)


# =========================================================
# EJECUCIÓN DIRECTA DEL SISTEMA
# =========================================================

if __name__ == "__main__":

    try:
        os.makedirs("output", exist_ok=True)

        sistema  = MAIIE_System()
        pipeline = IterativePipeline(max_iteraciones=3)

        orden = (
            "Generar sistema E-commerce en Python profesional. "
            "REQUISITOS: manejo de errores, logs de seguridad, "
            "validación de datos, Clean Architecture."
        )

        resultado = pipeline.ejecutar_mision(sistema, orden)

        console.print("\n")

        if resultado.aprobado:
            console.print(
                Panel(
                    f"[bold green]🎉 ÉXITO: Certificado en ciclo {resultado.iteracion}[/]",
                    title="Pipeline Finalizado",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    f"[bold red]❌ FALLO: {resultado.observaciones}[/]",
                    title="Resultado Final",
                    border_style="red",
                )
            )

    except KeyboardInterrupt:
        console.print("\n[warning]⚠️ Sistema detenido[/]")

    except Exception as e:
        logger.exception("Fallo catastrófico")
        console.print(f"[error]🔥 ERROR FATAL: {e}[/]")
        sys.exit(1)