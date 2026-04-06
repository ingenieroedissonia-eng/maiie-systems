"""
MAIIE System V2 - Model Registry
Módulo: Gestión centralizada de proveedores LLM
Capa: Infrastructure
Versión: 3.6.0

CHANGELOG v3.6.0:
- P6: Guardrail de costo por sesión implementado.
      Se añade SessionGuardrail — contador de llamadas por proveedor
      que emite WARNING al 80% del límite y ERROR al 100%.
      El sistema NO bloquea llamadas (no es un circuit breaker).
      Su función es visibilidad: el operador ve en los logs cuántas
      llamadas se han hecho en la sesión actual antes de que el
      costo se salga de control.
      Variables de entorno:
        MAIIE_MAX_CALLS_OPENAI    (default: 50)
        MAIIE_MAX_CALLS_GOOGLE    (default: 100)
        MAIIE_MAX_CALLS_ANTHROPIC (default: 50)
      Al final de cada llamada exitosa se loguea el contador:
        📊 Llamadas sesión: openai=5/50 google=12/100 anthropic=0/50

CHANGELOG v3.5.0:
- P4: NEXT_GEN_MODELS externalizado a variable de entorno MAIIE_NEXT_GEN_MODELS

CHANGELOG v3.4.2:
- FIX: _init_google() eliminado parámetro http_client — no soportado
       en google-genai v1.61.0.

CHANGELOG v3.4.0:
- ADD: Modelos de cada agente configurables desde .env
- ADD: Config.get_provider() y Config.get_model_name()
- FIX: ValueError por créditos agotados con log más claro
- CHG: GCP project movido a variable de entorno MAIIE_GCP_PROJECT
"""

import os
import time
import logging
from typing import Optional, List, Set
from functools import wraps
from dotenv import load_dotenv
from google import genai
from openai import OpenAI
from anthropic import Anthropic


# =========================================================
# CARGAR VARIABLES DE ENTORNO
# =========================================================

env_path = os.path.join(os.path.dirname(__file__), "..", "config", ".env")
load_dotenv(dotenv_path=env_path)


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("MAIIE.ModelRegistry")


# =========================================================
# CONFIGURACIÓN CENTRALIZADA
# =========================================================

class Config:
    """Configuración centralizada del registry."""

    TIMEOUT     = int(os.getenv("MAIIE_API_TIMEOUT",     "120"))
    MAX_RETRIES = int(os.getenv("MAIIE_API_MAX_RETRIES", "5"))
    MAX_TOKENS  = int(os.getenv("MAIIE_API_MAX_TOKENS",  "4000"))
    TEMPERATURE = float(os.getenv("MAIIE_API_TEMPERATURE", "0.7"))

    # ⚠️ MODO SEGURO: OFFLINE POR DEFECTO
    MODE = os.getenv("MAIIE_MODE", "offline").lower()

    # --------------------------------------------------
    # MODELOS POR AGENTE — configurables desde .env
    # --------------------------------------------------

    MODEL_ARCHITECT = os.getenv(
        "MAIIE_MODEL_ARCHITECT",
        "google/gemini-2.5-flash-lite"
    )
    MODEL_ENGINEER = os.getenv(
        "MAIIE_MODEL_ENGINEER",
        "google/gemini-2.5-pro"
    )
    MODEL_SENIOR = os.getenv(
        "MAIIE_MODEL_SENIOR",
        "google/gemini-2.5-pro"
    )
    MODEL_AUDITOR = os.getenv(
        "MAIIE_MODEL_AUDITOR",
        "openai/gpt-4o"
    )

    GCP_PROJECT  = os.getenv("MAIIE_GCP_PROJECT",  "triple-course-481522-e2")
    GCP_LOCATION = os.getenv("MAIIE_GCP_LOCATION", "us-central1")

    # --------------------------------------------------
    # P4: NEXT_GEN_MODELS externalizado a .env
    # --------------------------------------------------

    _NEXT_GEN_DEFAULT = "gpt-5,gpt-4o,o1,o3,claude-opus-4,claude-sonnet-4"

    @classmethod
    def get_next_gen_models(cls) -> Set[str]:
        raw = os.getenv("MAIIE_NEXT_GEN_MODELS", cls._NEXT_GEN_DEFAULT)
        return {m.strip().lower() for m in raw.split(",") if m.strip()}

    @classmethod
    def is_next_gen_model(cls, model: str) -> bool:
        next_gen = cls.get_next_gen_models()
        return any(m in model.lower() for m in next_gen)

    @classmethod
    def get_provider(cls, model_string: str) -> str:
        if "/" in model_string:
            return model_string.split("/")[0].lower()

        model_lower = model_string.lower()
        if "gpt" in model_lower or "o1" in model_lower or "o3" in model_lower:
            return "openai"
        if "gemini" in model_lower:
            return "google"
        if "claude" in model_lower:
            return "anthropic"

        raise ValueError(f"No se pudo derivar proveedor desde modelo: '{model_string}'")

    @classmethod
    def get_model_name(cls, model_string: str) -> str:
        if "/" in model_string:
            return model_string.split("/", 1)[1]
        return model_string


# =========================================================
# P6: SESSION GUARDRAIL — contador de llamadas por sesión
#
# No bloquea llamadas. Solo emite alertas en los logs cuando
# el sistema se acerca o supera los límites configurados.
# Propósito: visibilidad de consumo antes de que el costo
# se salga de control sin que nadie lo note.
#
# Límites configurables en .env:
#   MAIIE_MAX_CALLS_OPENAI    (default: 50)
#   MAIIE_MAX_CALLS_GOOGLE    (default: 100)
#   MAIIE_MAX_CALLS_ANTHROPIC (default: 50)
#
# Umbrales de alerta:
#   80% del límite → WARNING
#   100% del límite → ERROR (no bloquea, solo alerta)
# =========================================================

class SessionGuardrail:
    """
    Contador de llamadas API por proveedor en la sesión actual.

    Se instancia una vez por proceso (singleton dentro del
    ModelRegistry). Se resetea al reiniciar el servidor.
    """

    UMBRAL_WARNING = 0.80  # 80% del límite → WARNING
    UMBRAL_ERROR   = 1.00  # 100% del límite → ERROR

    def __init__(self):
        self._limites = {
            "openai":    int(os.getenv("MAIIE_MAX_CALLS_OPENAI",    "50")),
            "google":    int(os.getenv("MAIIE_MAX_CALLS_GOOGLE",    "100")),
            "anthropic": int(os.getenv("MAIIE_MAX_CALLS_ANTHROPIC", "50")),
        }
        self._contadores = {p: 0 for p in self._limites}

    def registrar_llamada(self, proveedor: str) -> None:
        """
        Incrementa el contador del proveedor y emite alertas
        si se superan los umbrales configurados.
        """
        proveedor = proveedor.lower()
        if proveedor not in self._contadores:
            return

        self._contadores[proveedor] += 1
        actual = self._contadores[proveedor]
        limite = self._limites[proveedor]
        ratio  = actual / limite

        if ratio >= self.UMBRAL_ERROR:
            logger.error(
                f"🚨 LÍMITE DE SESIÓN ALCANZADO — {proveedor}: "
                f"{actual}/{limite} llamadas. "
                f"Considera reiniciar el servidor para resetear contadores."
            )
        elif ratio >= self.UMBRAL_WARNING:
            logger.warning(
                f"⚠️ GUARDRAIL {proveedor}: {actual}/{limite} llamadas "
                f"({int(ratio * 100)}% del límite de sesión)."
            )

        # Log de estado resumido en cada llamada
        resumen = " | ".join(
            f"{p}={self._contadores[p]}/{self._limites[p]}"
            for p in self._limites
        )
        logger.info(f"📊 Sesión: {resumen}")

    def estado(self) -> dict:
        """Retorna estado actual de contadores para inspección externa."""
        return {
            p: {
                "llamadas": self._contadores[p],
                "limite":   self._limites[p],
                "porcentaje": round(self._contadores[p] / self._limites[p] * 100, 1)
            }
            for p in self._limites
        }


# =========================================================
# RETRY DECORATOR
# =========================================================

def retry_with_backoff(max_attempts: int = 5):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            for attempt in range(1, max_attempts + 1):

                try:
                    result = func(*args, **kwargs)

                    if not result or not result.strip():
                        raise ValueError(
                            "Respuesta vacía del modelo. "
                            "Posibles causas: créditos agotados, "
                            "rate limit, o modelo no disponible."
                        )

                    return result

                except Exception as e:

                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} falló después de {max_attempts} "
                            f"intentos: {type(e).__name__}: {str(e)[:100]}"
                        )
                        raise

                    wait_time = min(2 ** attempt, 30)
                    logger.warning(
                        f"⚠️ Intento {attempt}/{max_attempts} falló "
                        f"({type(e).__name__}). Reintentando en {wait_time}s..."
                    )
                    time.sleep(wait_time)

        return wrapper

    return decorator


# =========================================================
# MODEL REGISTRY
# =========================================================

class ModelRegistry:
    """
    Registry centralizado para gestión multi-proveedor de LLMs.
    Los modelos de cada agente se leen desde .env via Config.
    Para cambiar de proveedor o modelo: editar .env, no el código.
    """

    def __init__(self):

        self.client_openai    = self._init_openai()
        self.client_anthropic = self._init_anthropic()
        self.client_google    = self._init_google()
        self.guardrail        = SessionGuardrail()

        self._log_status()

    # -----------------------------------------------------

    def _init_openai(self) -> Optional[OpenAI]:

        if Config.MODE == "offline":
            return None

        try:
            api_key = os.getenv("MAIIE_KEY_OPENAI")

            if not api_key:
                logger.warning("🔑 API Key OpenAI no configurada")
                return None

            return OpenAI(
                api_key=api_key,
                timeout=Config.TIMEOUT,
                max_retries=0,
            )

        except Exception as e:
            logger.error(f"❌ Error inicializando OpenAI: {type(e).__name__}")
            return None

    # -----------------------------------------------------

    def _init_anthropic(self) -> Optional[Anthropic]:

        if Config.MODE == "offline":
            return None

        try:
            api_key = os.getenv("MAIIE_KEY_ANTHROPIC")

            if not api_key:
                logger.warning("🔑 API Key Anthropic no configurada")
                return None

            return Anthropic(
                api_key=api_key,
                timeout=Config.TIMEOUT,
                max_retries=0,
            )

        except Exception as e:
            logger.error(f"❌ Error inicializando Anthropic: {type(e).__name__}")
            return None

    # -----------------------------------------------------

    def _init_google(self) -> Optional[genai.Client]:
        """
        Inicializa el cliente de Vertex AI.
        Las credenciales se leen desde ADC automáticamente.
        """
        if Config.MODE == "offline":
            return None

        try:
            return genai.Client(
                vertexai=True,
                project=Config.GCP_PROJECT,
                location=Config.GCP_LOCATION,
            )

        except Exception as e:
            logger.error(f"❌ Error inicializando Google Vertex AI: {type(e).__name__}")
            return None

    # -----------------------------------------------------

    def _log_status(self):

        if Config.MODE == "offline":
            logger.info("🧠 MAIIE iniciado en MODO OFFLINE (sin llamadas a APIs)")
            return

        disponibles = self.listar_proveedores_disponibles()

        if disponibles:
            logger.info(
                f"🚀 M.A.I.I.E. v2.0 Online. Proveedores: {', '.join(disponibles)}"
            )
            logger.info(f"📐 ARCHITECT  → {Config.MODEL_ARCHITECT}")
            logger.info(f"🔧 ENGINEER   → {Config.MODEL_ENGINEER}")
            logger.info(f"🔍 AUDITOR    → {Config.MODEL_AUDITOR}")

            # Log límites del guardrail al arrancar
            limites = self.guardrail._limites
            logger.info(
                f"🛡️ Guardrail sesión: "
                f"openai={limites['openai']} | "
                f"google={limites['google']} | "
                f"anthropic={limites['anthropic']} llamadas máx."
            )
        else:
            logger.warning("⚠️ Sistema sin proveedores configurados")

    # =====================================================
    # MÉTODO PRINCIPAL
    # =====================================================

    def solicitar_ia(
        self,
        proveedor: str,
        modelo: str,
        prompt_sistema: str,
        prompt_usuario: str,
    ) -> str:

        proveedor = proveedor.lower().strip()

        if not all([modelo, prompt_sistema, prompt_usuario]):
            raise ValueError("Parámetros inválidos")

        # -------------------------------------------------
        # OFFLINE MODE
        # -------------------------------------------------

        if Config.MODE == "offline":

            logger.info(f"[OFFLINE MODE] Simulación {proveedor}/{modelo}")

            texto = (prompt_sistema + prompt_usuario).lower()

            if "architect" in texto:
                return """
PLAN ARQUITECTÓNICO (SIMULADO)

Arquitectura:
- domain
- services
- infrastructure
- logging
- error handling
"""

            if "engineer" in texto:
                return """
IMPLEMENTACIÓN (SIMULADA)

class ExampleService:

    def ejecutar(self):
        print("Servicio ejecutado correctamente")
"""

            if "auditor" in texto:
                return """
REPORTE AUDITORÍA

CUMPLIMIENTO: 85%
ESTADO: APROBADO

La arquitectura cumple con los estándares simulados.
"""

            return "[MAIIE OFFLINE RESPONSE]"

        # -------------------------------------------------
        # PRODUCCIÓN
        # -------------------------------------------------

        metodos = {
            "openai":    self._call_openai,
            "google":    self._call_google,
            "anthropic": self._call_anthropic,
        }

        if proveedor not in metodos:
            raise ValueError(
                f"Proveedor '{proveedor}' no reconocido. "
                f"Disponibles: {list(metodos.keys())}"
            )

        modelo_limpio = Config.get_model_name(modelo)
        resultado     = metodos[proveedor](modelo_limpio, prompt_sistema, prompt_usuario)

        # Registrar llamada exitosa en el guardrail
        self.guardrail.registrar_llamada(proveedor)

        return resultado

    # =====================================================
    # LLAMADAS REALES
    # =====================================================

    @retry_with_backoff()
    def _call_openai(self, model, sys_prompt, user_msg):

        if not self.client_openai:
            raise RuntimeError(
                "Cliente OpenAI no inicializado. "
                "Verifica MAIIE_KEY_OPENAI en .env y saldo disponible."
            )

        is_next = Config.is_next_gen_model(model)
        token_param = (
            {"max_completion_tokens": Config.MAX_TOKENS}
            if is_next
            else {"max_tokens": Config.MAX_TOKENS}
        )

        response = self.client_openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user",   "content": user_msg},
            ],
            temperature=Config.TEMPERATURE,
            **token_param,
        )

        return response.choices[0].message.content

    # -----------------------------------------------------

    @retry_with_backoff()
    def _call_google(self, model, sys_prompt, user_msg):

        if not self.client_google:
            raise RuntimeError(
                "Cliente Google Vertex AI no inicializado. "
                "Verifica autenticación ADC y proyecto GCP."
            )

        response = self.client_google.models.generate_content(
            model=model,
            config=genai.types.GenerateContentConfig(
                system_instruction=sys_prompt,
                temperature=Config.TEMPERATURE,
                max_output_tokens=Config.MAX_TOKENS,
            ),
            contents=[user_msg],
        )

        return response.text

    # -----------------------------------------------------

    @retry_with_backoff()
    def _call_anthropic(self, model, sys_prompt, user_msg):

        if not self.client_anthropic:
            raise RuntimeError(
                "Cliente Anthropic no inicializado. "
                "Verifica MAIIE_KEY_ANTHROPIC en .env y saldo disponible."
            )

        response = self.client_anthropic.messages.create(
            model=model,
            max_tokens=Config.MAX_TOKENS,
            temperature=Config.TEMPERATURE,
            system=sys_prompt,
            messages=[{"role": "user", "content": user_msg}],
        )

        return response.content[0].text

    # -----------------------------------------------------

    def listar_proveedores_disponibles(self) -> List[str]:

        disponibles = []

        if self.client_openai:
            disponibles.append("openai")

        if self.client_google:
            disponibles.append("google")

        if self.client_anthropic:
            disponibles.append("anthropic")

        return disponibles