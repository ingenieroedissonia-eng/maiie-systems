"""
MAIIE System V2 - Mission Memory
Módulo: Recuperación de contexto desde misiones pasadas
Capa: Core
Versión: 1.6.0

CHANGELOG v1.6.0:
- ADD: Ponderación de calidad en ranking semántico.
       _obtener_misiones_por_similitud() ahora multiplica el score de
       similitud coseno por un factor de calidad derivado del manifest.
       Fórmula: score_final = similitud_coseno * factor_calidad
       Factor de calidad:
         compliance_score / 100 * 0.8 → peso del cumplimiento (80%)
         + 0.2 si sin deuda técnica, 0.1 si con deuda técnica → (20%)
       Resultado: misión 100% sin deuda pesa más que 75% con deuda
       aunque tengan similitud coseno idéntica.
       El log ahora muestra scores ponderados para trazabilidad.
       Sin cambios en interfaz pública.

CHANGELOG v1.5.0:
- FIX: Migración de API de embeddings de vertexai.language_models
       (deprecada junio 2026) a google-genai SDK.

CHANGELOG v1.4.0:
- ADD: Búsqueda semántica por similitud coseno.
- ADD: _cargar_embedding(), _similitud_coseno(), _obtener_misiones_por_similitud()
- RULE: Fallback automático a orden cronológico si google-genai no disponible.

CHANGELOG v1.3.0:
- ADD: Soporte para leer misiones desde Google Cloud Storage.

CHANGELOG v1.2.0:
- FIX: obtener_misiones_aprobadas() lee campo "estado" con fallback a "status".
"""

import os
import json
import logging
import math
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "..", "config", ".env")
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger("MAIIE.MissionMemory")

ESTADOS_VALIDOS = {"APROBADO", "APROBADO_CON_DEUDA"}
EMBEDDING_MODEL = "text-embedding-004"


class MissionMemory:
    """
    Permite leer misiones pasadas y recuperar contexto útil
    para nuevas ejecuciones del pipeline.

    v1.6.0: Ranking semántico ponderado por calidad de misión.
    v1.5.0: Embeddings con google-genai SDK.
    v1.4.0: Búsqueda semántica por similitud coseno.
    """

    def __init__(self, missions_path: str = "output/missions"):
        self.missions_path = missions_path
        self.backend       = os.getenv("MAIIE_STORAGE_BACKEND", "local").lower().strip()
        self.bucket_name   = os.getenv("MAIIE_GCS_BUCKET", "")

        self._gcs_client = None
        self._gcs_bucket = None

        if self.backend != "gcs":
            if not os.path.exists(self.missions_path):
                logger.warning(f"Directorio de misiones no encontrado: {self.missions_path}")
        else:
            logger.info(f"GCS Memory configurado (lazy): gs://{self.bucket_name}")

        self._genai_disponible = self._inicializar_genai()

    # ----------------------------------------------------------
    # GCS INIT
    # ----------------------------------------------------------

    def _init_gcs(self):
        if self._gcs_client is None:
            try:
                from google.cloud import storage as gcs
                self._gcs_client = gcs.Client()
                self._gcs_bucket = self._gcs_client.bucket(self.bucket_name)
                logger.info(f"GCS Memory conectado: gs://{self.bucket_name}")
            except Exception as e:
                raise RuntimeError(f"Error conectando GCS Memory: {e}") from e

    # ----------------------------------------------------------
    # GOOGLE-GENAI
    # ----------------------------------------------------------

    def _inicializar_genai(self) -> bool:
        try:
            from google import genai

            proyecto  = os.getenv("MAIIE_GCP_PROJECT", "")
            ubicacion = os.getenv("MAIIE_GCP_LOCATION", "us-central1")

            if not proyecto:
                logger.warning(
                    "⚠️ MAIIE_GCP_PROJECT no configurado — "
                    "búsqueda semántica desactivada, usando orden cronológico."
                )
                return False

            self._genai_client = genai.Client(
                vertexai=True,
                project=proyecto,
                location=ubicacion,
            )

            logger.info(
                f"🔢 google-genai inicializado para búsqueda semántica "
                f"(proyecto={proyecto}, modelo={EMBEDDING_MODEL})"
            )
            return True

        except ImportError:
            logger.warning(
                "⚠️ google-genai no instalado — "
                "búsqueda semántica desactivada, usando orden cronológico."
            )
            return False
        except Exception as e:
            logger.warning(f"⚠️ Error inicializando google-genai: {e}")
            return False

    def _generar_embedding_consulta(self, texto: str) -> Optional[List[float]]:
        if not self._genai_disponible:
            return None

        if not texto or not texto.strip():
            return None

        try:
            from google.genai import types

            resultado = self._genai_client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=texto[:2000],
                config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
            )
            return resultado.embeddings[0].values

        except Exception as e:
            logger.warning(f"⚠️ Error generando embedding de consulta — fallback cronológico: {e}")
            return None

    # ----------------------------------------------------------
    # SIMILITUD COSENO
    # ----------------------------------------------------------

    @staticmethod
    def _similitud_coseno(a: List[float], b: List[float]) -> float:
        if len(a) != len(b):
            return 0.0

        dot     = sum(x * y for x, y in zip(a, b))
        norma_a = math.sqrt(sum(x * x for x in a))
        norma_b = math.sqrt(sum(x * x for x in b))

        if norma_a == 0.0 or norma_b == 0.0:
            return 0.0

        return dot / (norma_a * norma_b)

    # ----------------------------------------------------------
    # FACTOR DE CALIDAD — v1.6.0
    # ----------------------------------------------------------

    @staticmethod
    def _factor_calidad(manifest: Dict) -> float:
        """
        Calcula factor de calidad basado en compliance y deuda técnica.

        Fórmula:
            factor = (compliance_score / 100) * 0.8
                   + (0.2 si sin deuda, 0.1 si con deuda)

        Ejemplos:
            100% sin deuda → 0.80 + 0.20 = 1.00
            100% con deuda → 0.80 + 0.10 = 0.90
             75% sin deuda → 0.60 + 0.20 = 0.80
             75% con deuda → 0.60 + 0.10 = 0.70

        Floor en 0.1 para no anular misiones sin compliance_score registrado.
        """
        compliance = manifest.get("compliance_score", 0)
        deuda      = manifest.get("deuda_tecnica", True)

        peso_compliance = (compliance / 100) * 0.8
        peso_deuda      = 0.1 if deuda else 0.2

        return max(0.1, min(1.0, peso_compliance + peso_deuda))

    # ----------------------------------------------------------
    # CARGAR EMBEDDING
    # ----------------------------------------------------------

    def _cargar_embedding(self, mission_id: str) -> Optional[List[float]]:
        if self.backend == "gcs":
            return self._cargar_embedding_gcs(mission_id)
        return self._cargar_embedding_local(mission_id)

    def _cargar_embedding_local(self, mission_id: str) -> Optional[List[float]]:
        path = os.path.join(self.missions_path, mission_id, "mission_embedding.json")
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f).get("vector")
        except Exception as e:
            logger.warning(f"Error cargando embedding local de {mission_id}: {e}")
            return None

    def _cargar_embedding_gcs(self, mission_id: str) -> Optional[List[float]]:
        self._init_gcs()
        try:
            blob = self._gcs_bucket.blob(
                f"{self.missions_path}/{mission_id}/mission_embedding.json"
            )
            if not blob.exists():
                return None
            return json.loads(blob.download_as_text(encoding="utf-8")).get("vector")
        except Exception as e:
            logger.warning(f"Error cargando embedding GCS de {mission_id}: {e}")
            return None

    # ----------------------------------------------------------
    # RANKING SEMÁNTICO PONDERADO — v1.6.0
    # ----------------------------------------------------------

    def _obtener_misiones_por_similitud(
        self,
        vector_consulta: List[float],
        aprobadas: List[Dict],
        limite: int,
    ) -> List[Dict]:
        """
        Ordena misiones por score_final = similitud_coseno * factor_calidad.

        Misiones con mayor similitud semántica Y mejor calidad
        (compliance alto, sin deuda técnica) quedan primero.
        Misiones sin embedding reciben score 0.0 y van al final.
        """
        scored: List[Tuple[float, Dict]] = []

        for manifest in aprobadas:
            mission_id = manifest.get("mission_id", "")

            if not manifest.get("embedding_disponible", True):
                scored.append((0.0, manifest))
                continue

            vector_mision = self._cargar_embedding(mission_id)

            if vector_mision is None:
                scored.append((0.0, manifest))
                continue

            similitud   = self._similitud_coseno(vector_consulta, vector_mision)
            calidad     = self._factor_calidad(manifest)
            score_final = similitud * calidad

            scored.append((score_final, manifest))

        scored.sort(key=lambda x: x[0], reverse=True)

        top = [manifest for _, manifest in scored[:limite]]

        logger.info(
            f"🔍 Búsqueda semántica ponderada: top {len(top)} de {len(aprobadas)} misiones. "
            f"Scores: {[round(s, 3) for s, _ in scored[:limite]]}"
        )

        return top

    # ----------------------------------------------------------
    # LISTAR MISIONES
    # ----------------------------------------------------------

    def listar_misiones(self) -> List[str]:
        if self.backend == "gcs":
            return self._listar_misiones_gcs()
        return self._listar_misiones_local()

    def _listar_misiones_local(self) -> List[str]:
        if not os.path.exists(self.missions_path):
            return []
        misiones = [
            d for d in os.listdir(self.missions_path)
            if os.path.isdir(os.path.join(self.missions_path, d))
        ]
        return sorted(misiones)

    def _listar_misiones_gcs(self) -> List[str]:
        self._init_gcs()
        try:
            prefix = f"{self.missions_path}/"
            blobs  = self._gcs_client.list_blobs(
                self.bucket_name, prefix=prefix, delimiter="/"
            )
            _ = list(blobs)
            misiones = []
            for p in (blobs.prefixes or []):
                parts      = p.rstrip("/").split("/")
                mission_id = parts[-1]
                if mission_id.startswith("mission_"):
                    misiones.append(mission_id)
            return sorted(misiones)
        except Exception as e:
            logger.error(f"Error listando misiones en GCS: {e}")
            return []

    # ----------------------------------------------------------
    # CARGAR MANIFEST
    # ----------------------------------------------------------

    def cargar_manifest(self, mission_id: str) -> Optional[Dict]:
        if self.backend == "gcs":
            return self._cargar_manifest_gcs(mission_id)
        return self._cargar_manifest_local(mission_id)

    def _cargar_manifest_local(self, mission_id: str) -> Optional[Dict]:
        manifest_path = os.path.join(
            self.missions_path, mission_id, "mission_manifest.json"
        )
        if not os.path.exists(manifest_path):
            return None
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando manifest de {mission_id}: {e}")
            return None

    def _cargar_manifest_gcs(self, mission_id: str) -> Optional[Dict]:
        self._init_gcs()
        try:
            blob = self._gcs_bucket.blob(
                f"{self.missions_path}/{mission_id}/mission_manifest.json"
            )
            if not blob.exists():
                return None
            return json.loads(blob.download_as_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"Error cargando manifest GCS de {mission_id}: {e}")
            return None

    # ----------------------------------------------------------
    # CARGAR ARQUITECTURA
    # ----------------------------------------------------------

    def cargar_arquitectura(self, mission_id: str) -> Optional[str]:
        if self.backend == "gcs":
            return self._cargar_arquitectura_gcs(mission_id)
        return self._cargar_arquitectura_local(mission_id)

    def _cargar_arquitectura_local(self, mission_id: str) -> Optional[str]:
        path = os.path.join(self.missions_path, mission_id, "architecture.md")
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error leyendo arquitectura de {mission_id}: {e}")
            return None

    def _cargar_arquitectura_gcs(self, mission_id: str) -> Optional[str]:
        self._init_gcs()
        try:
            blob = self._gcs_bucket.blob(
                f"{self.missions_path}/{mission_id}/architecture.md"
            )
            if not blob.exists():
                return None
            return blob.download_as_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Error leyendo arquitectura GCS de {mission_id}: {e}")
            return None

    # ----------------------------------------------------------
    # MISIONES APROBADAS
    # ----------------------------------------------------------

    def obtener_misiones_aprobadas(self, limite: int = 10) -> List[Dict]:
        misiones  = self.listar_misiones()
        aprobadas = []

        for mission_id in misiones:
            manifest = self.cargar_manifest(mission_id)
            if not manifest:
                continue
            estado_raw = manifest.get("estado", manifest.get("status", ""))
            status     = estado_raw.upper().replace(" ", "_")
            if status not in ESTADOS_VALIDOS:
                continue
            aprobadas.append(manifest)

        return aprobadas[-limite:]

    # ----------------------------------------------------------
    # RESUMIR MISIÓN
    # ----------------------------------------------------------

    def resumir_mision(self, manifest: Dict) -> str:
        mission_id      = manifest.get("mission_id", "desconocido")
        orden           = manifest.get("orden_usuario", "Sin descripción")[:200]
        status          = manifest.get("estado", manifest.get("status", "DESCONOCIDO"))
        score           = manifest.get("compliance_score", 0)
        iteracion       = manifest.get("iteracion_final", 0)
        deuda           = manifest.get("deuda_tecnica", False)
        modelos         = manifest.get("modelos", {})
        architect_model = modelos.get("architect", "desconocido")
        deuda_label     = "⚠️ Con deuda técnica" if deuda else "✅ Sin deuda técnica"

        return (
            f"📋 Misión: {mission_id}\n"
            f"   Orden: {orden}\n"
            f"   Estado: {status} — Cumplimiento: {score}% — Iteraciones: {iteracion}\n"
            f"   Calidad: {deuda_label}\n"
            f"   Arquitecto: {architect_model}\n"
        )

    # ----------------------------------------------------------
    # OBTENER CONTEXTO
    # ----------------------------------------------------------

    def obtener_contexto(
        self,
        orden_actual: Optional[str] = None,
        limite: int = 3,
    ) -> str:
        """
        Recupera bloque de contexto de misiones aprobadas.

        v1.6.0: Ranking por score_final = similitud_coseno * factor_calidad.
        v1.4.0+: Búsqueda semántica si orden_actual está disponible.
        Fallback cronológico si google-genai no disponible.
        """
        aprobadas = self.obtener_misiones_aprobadas(limite=50)

        if not aprobadas:
            logger.info("Sin misiones aprobadas previas en memoria.")
            return ""

        if orden_actual and orden_actual.strip():
            vector_consulta = self._generar_embedding_consulta(orden_actual)

            if vector_consulta is not None:
                seleccionadas = self._obtener_misiones_por_similitud(
                    vector_consulta=vector_consulta,
                    aprobadas=aprobadas,
                    limite=limite,
                )
                modo = "semántico ponderado"
            else:
                seleccionadas = aprobadas[-limite:]
                modo = "cronológico (fallback — embedding de consulta falló)"
        else:
            seleccionadas = aprobadas[-limite:]
            modo = "cronológico"

        bloques = [self.resumir_mision(m) for m in seleccionadas]

        contexto = (
            f"HISTORIAL DE MISIONES APROBADAS ({len(bloques)} — modo {modo}):\n\n"
            + "\n".join(bloques)
        )

        logger.info(f"🧠 Contexto cargado: {len(bloques)} misión(es) — modo {modo}")

        return contexto
    