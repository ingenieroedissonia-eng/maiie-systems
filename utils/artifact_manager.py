"""
MAIIE System V2 - Artifact Manager
Módulo: Gestión estructurada de artefactos de misión
Capa: Infrastructure
Versión: 2.2.0

CHANGELOG v2.2.0:
- FIX: Migración de API de embeddings de vertexai.language_models
       (deprecada junio 2026) a google-genai SDK.
       _inicializar_vertex() reemplazado por _inicializar_genai().
       _generar_embedding() usa google.genai.Client en lugar de
       TextEmbeddingModel.from_pretrained().
       Sin cambios en interfaz pública ni en el resto del módulo.

CHANGELOG v2.1.0:
- ADD: Generación de embedding semántico al guardar misión.
       Al finalizar guardar_artefactos(), se genera el embedding del campo
       orden_usuario usando Vertex AI text-embedding-004 (ADC nativo, sin API key)
       y se persiste como mission_embedding.json en la misma carpeta de misión.
       El proceso es best-effort: si Vertex AI no está disponible o falla,
       los artefactos principales se guardan igualmente sin interrupción.
- ADD: _generar_embedding(texto) → List[float] usando Vertex AI ADC.
- ADD: _guardar_embedding(mission_path, orden_usuario, vector) persiste el vector
       como JSON usando el mismo StorageBackend activo (local o GCS).
- ADD: Campo "embedding_disponible" en manifest — permite a MissionMemory
       saber si existe mission_embedding.json sin hacer blob.exists() extra.

CHANGELOG v2.0.1:
- FIX: ensure_ascii=True en json.dumps del manifest para eliminar
       caracteres corruptos en Windows al serializar orden_usuario
       con tildes y caracteres especiales del español.

CHANGELOG v2.0.0:
- ADD: Abstracción de storage backend — local filesystem o Google Cloud Storage
       Controlado por variable de entorno MAIIE_STORAGE_BACKEND
         local (default) → escribe en output/missions/ igual que antes
         gcs             → escribe en GCS bucket configurable
       Variable adicional: MAIIE_GCS_BUCKET (nombre del bucket)
       El backend se selecciona al inicializar ArtifactManager.
       Sin cambios en la interfaz pública — pipeline.py no requiere modificación.
- FIX: Manifest ahora escribe clave "estado" en lugar de "status"

CHANGELOG v1.2.0:
- FIX: guardar_artefactos ahora acepta parámetro 'metadata' opcional
- FIX: manifest incluye compliance_score, deuda_tecnica, iteracion_final,
       orden_usuario y modelos
- FIX: status se deriva del metadata recibido, no hardcodeado
- FIX: mission_id se usa desde metadata si viene del pipeline (con UUID)
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "..", "config", ".env")
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger("MAIIE.Artifacts")

# Modelo de embedding — constante para facilitar futura migración
EMBEDDING_MODEL = "text-embedding-004"


# =========================================================
# STORAGE BACKEND ABSTRACTION
# =========================================================

class StorageBackend(ABC):
    """
    Contrato para backends de almacenamiento de artefactos.
    Implementaciones: LocalStorage, GCSStorage.
    """

    @abstractmethod
    def write(self, path: str, content: str) -> None:
        """Escribe contenido en la ruta especificada."""
        ...

    @abstractmethod
    def makedirs(self, path: str) -> None:
        """Crea directorios intermedios si no existen."""
        ...

    @abstractmethod
    def join(self, *parts: str) -> str:
        """Une partes de una ruta según el backend."""
        ...


# ---------------------------------------------------------
# LOCAL STORAGE
# ---------------------------------------------------------

class LocalStorage(StorageBackend):
    """
    Backend de almacenamiento local (filesystem).
    Comportamiento idéntico a v1.x — sin cambios en local.
    """

    def write(self, path: str, content: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def makedirs(self, path: str) -> None:
        os.makedirs(path, exist_ok=True)

    def join(self, *parts: str) -> str:
        return os.path.join(*parts)


# ---------------------------------------------------------
# GCS STORAGE
# ---------------------------------------------------------

class GCSStorage(StorageBackend):
    """
    Backend de almacenamiento en Google Cloud Storage.

    Requiere:
        google-cloud-storage instalado
        MAIIE_GCS_BUCKET configurado en .env
        Credenciales ADC activas (mismo mecanismo que Vertex AI)

    Las rutas se traducen a objetos GCS:
        output/missions/mission_xxx/architecture.md
        → gs://bucket/missions/mission_xxx/architecture.md
    """

    def __init__(self, bucket_name: str):
        self._bucket_name = bucket_name
        self._client = None
        self._bucket = None
        logger.info(f"GCS Storage configurado (lazy): gs://{bucket_name}")

    def _get_bucket(self):
        if self._client is None:
            try:
                from google.cloud import storage as gcs
                self._client = gcs.Client()
                self._bucket = self._client.bucket(self._bucket_name)
                logger.info("GCS conectado: gs://" + self._bucket_name)
            except Exception as e:
                raise RuntimeError("Error GCS: " + str(e)) from e
        return self._bucket

    def write(self, path: str, content: str) -> None:
        """Sube el contenido como objeto GCS."""
        gcs_path = path.replace("\\", "/").lstrip("/")
        blob = self._get_bucket().blob(gcs_path)
        blob.upload_from_string(content, content_type="text/plain")

    def makedirs(self, path: str) -> None:
        """En GCS los directorios no existen — no-op."""
        pass

    def join(self, *parts: str) -> str:
        """Une partes con / para rutas GCS."""
        return "/".join(p.strip("/").replace("\\", "/") for p in parts if p)


# ---------------------------------------------------------
# FACTORY
# ---------------------------------------------------------

def crear_storage_backend() -> StorageBackend:
    """
    Crea el backend de storage según MAIIE_STORAGE_BACKEND en .env.

    Valores válidos:
        local (default) — filesystem local
        gcs             — Google Cloud Storage

    Variables adicionales para gcs:
        MAIIE_GCS_BUCKET — nombre del bucket (obligatorio si backend=gcs)
    """
    backend = os.getenv("MAIIE_STORAGE_BACKEND", "local").lower().strip()

    if backend == "gcs":
        bucket = os.getenv("MAIIE_GCS_BUCKET", "")
        if not bucket:
            raise ValueError(
                "MAIIE_STORAGE_BACKEND=gcs requiere MAIIE_GCS_BUCKET en .env. "
                "Ejemplo: MAIIE_GCS_BUCKET=maiie-missions-prod"
            )
        return GCSStorage(bucket_name=bucket)

    if backend != "local":
        logger.warning(
            f"⚠️ MAIIE_STORAGE_BACKEND='{backend}' no reconocido. "
            f"Usando 'local' como fallback."
        )

    return LocalStorage()


# =========================================================
# ARTIFACT MANAGER
# =========================================================

class ArtifactManager:
    """
    Gestiona el almacenamiento estructurado de artefactos de misión.

    El backend de storage se selecciona desde .env:
        MAIIE_STORAGE_BACKEND=local  (default)
        MAIIE_STORAGE_BACKEND=gcs

    La interfaz pública (guardar_artefactos) no cambia — el pipeline
    no necesita modificación al cambiar de backend.

    v2.2.0: Embeddings generados con google-genai SDK (sin deprecación).
    v2.1.0: Al guardar una misión, genera opcionalmente el embedding
    semántico de orden_usuario y lo persiste como mission_embedding.json.
    El proceso es best-effort: un fallo no interrumpe el guardado principal.
    """

    def __init__(self, base_output: str = "output"):
        self.base_output  = base_output
        self.storage      = crear_storage_backend()
        self.missions_dir = self.storage.join(self.base_output, "missions")

        if isinstance(self.storage, LocalStorage):
            self.storage.makedirs(self.missions_dir)

        # Intentar inicializar google-genai para embeddings.
        # Si no está disponible, _genai_disponible=False y el sistema
        # opera exactamente igual que v2.0.1 — cero impacto en el flujo.
        self._genai_disponible = self._inicializar_genai()

    # ---------------------------------------------------------
    # GOOGLE-GENAI — INICIALIZACIÓN Y EMBEDDING
    # v2.2.0: reemplaza vertexai.language_models (deprecada jun 2026)
    # ---------------------------------------------------------

    def _inicializar_genai(self) -> bool:
        """
        Verifica disponibilidad de google-genai para generación de embeddings.

        Usa ADC nativo — no requiere API key explícita.
        MAIIE_GCP_PROJECT debe estar configurado en .env.

        Returns:
            True si google-genai está disponible y configurado.
            False si no — las funciones de embedding retornan None
            sin lanzar excepciones.
        """
        try:
            from google import genai

            proyecto  = os.getenv("MAIIE_GCP_PROJECT", "")
            ubicacion = os.getenv("MAIIE_GCP_LOCATION", "us-central1")

            if not proyecto:
                logger.warning(
                    "⚠️ MAIIE_GCP_PROJECT no configurado — "
                    "embeddings desactivados. Misiones se guardarán sin vector."
                )
                return False

            # Cliente con ADC nativo — mismo mecanismo que el resto del sistema
            self._genai_client = genai.Client(
                vertexai=True,
                project=proyecto,
                location=ubicacion,
            )

            logger.info(
                f"🔢 google-genai inicializado para embeddings "
                f"(proyecto={proyecto}, modelo={EMBEDDING_MODEL})"
            )
            return True

        except ImportError:
            logger.warning(
                "⚠️ google-genai no instalado — embeddings desactivados. "
                "Ejecuta: pip install google-genai"
            )
            return False
        except Exception as e:
            logger.warning(f"⚠️ Error inicializando google-genai para embeddings: {e}")
            return False

    def _generar_embedding(self, texto: str) -> Optional[List[float]]:
        """
        Genera el embedding semántico de un texto usando google-genai SDK.

        Usa task_type=RETRIEVAL_DOCUMENT para optimizar la búsqueda
        de similitud coseno posterior en MissionMemory.

        Args:
            texto: Texto a vectorizar (orden_usuario de la misión).

        Returns:
            Lista de floats con el vector, o None si falla.
        """
        if not self._genai_disponible:
            return None

        if not texto or not texto.strip():
            return None

        try:
            from google.genai import types

            resultado = self._genai_client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=texto[:2000],  # text-embedding-004: límite ~2048 tokens
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT"
                ),
            )
            vector = resultado.embeddings[0].values

            logger.info(
                f"🔢 Embedding generado: {len(vector)} dims "
                f"({len(texto)} chars de entrada)"
            )
            return vector

        except Exception as e:
            logger.warning(
                f"⚠️ Error generando embedding — misión guardada sin vector: {e}"
            )
            return None

    def _guardar_embedding(
        self,
        mission_path: str,
        orden_usuario: str,
        vector: List[float],
    ) -> None:
        """
        Persiste el vector de embedding como mission_embedding.json.

        El archivo incluye metadata suficiente para que MissionMemory
        pueda reconstruir el contexto sin abrir el manifest completo.

        Args:
            mission_path:  Ruta de la carpeta de misión (local o GCS).
            orden_usuario: Texto original que generó el embedding.
            vector:        Lista de floats del embedding.
        """
        embedding_path = self.storage.join(mission_path, "mission_embedding.json")

        embedding_data = {
            "modelo":        EMBEDDING_MODEL,
            "dimensiones":   len(vector),
            "orden_usuario": orden_usuario[:500],  # preview para debug
            "vector":        vector,
            "timestamp":     datetime.now().isoformat(),
        }

        self.storage.write(
            embedding_path,
            json.dumps(embedding_data, ensure_ascii=True)
        )

        logger.info(f"🔢 Embedding persistido: {embedding_path}")

    # ---------------------------------------------------------
    # CREAR DIRECTORIO DE MISIÓN
    # ---------------------------------------------------------

    def crear_mision_dir(self, mission_id: Optional[str] = None) -> str:
        """
        Crea carpeta única para la misión.
        En GCS, solo retorna la ruta (los directorios son virtuales).
        """
        if mission_id:
            folder_name = (
                f"mission_{mission_id}"
                if not mission_id.startswith("mission_")
                else mission_id
            )
        else:
            timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"mission_{timestamp}"

        mission_path = self.storage.join(self.missions_dir, folder_name)
        self.storage.makedirs(mission_path)

        return mission_path

    # ---------------------------------------------------------
    # GUARDAR ARTEFACTOS
    # ---------------------------------------------------------

    def guardar_artefactos(
        self,
        arquitectura: str,
        codigo: str,
        auditoria: str,
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Guarda todos los artefactos de misión y genera el manifest completo.

        v2.1.0: Al finalizar el guardado principal, intenta generar y persistir
        mission_embedding.json con el vector semántico de orden_usuario.
        El embedding es best-effort — su fallo no interrumpe el guardado.

        Args:
            arquitectura:  Contenido del plan arquitectónico (markdown).
            codigo:        Código fuente generado (Python).
            auditoria:     Reporte de auditoría (markdown).
            metadata:      Diccionario opcional con datos del pipeline.

        Returns:
            Ruta de la carpeta de misión (filesystem o GCS path).
        """
        metadata     = metadata or {}
        mission_id   = metadata.get("mission_id")
        mission_path = self.crear_mision_dir(mission_id=mission_id)

        arch_path     = self.storage.join(mission_path, "architecture.md")
        impl_path     = self.storage.join(mission_path, "implementation.py")
        audit_path    = self.storage.join(mission_path, "audit.md")
        manifest_path = self.storage.join(mission_path, "mission_manifest.json")

        try:
            self.storage.write(arch_path,  arquitectura or "")
            self.storage.write(impl_path,  codigo or "")
            self.storage.write(audit_path, auditoria or "")

            estado_valor  = metadata.get("estado", "DESCONOCIDO")

            # FIX v2.0.1: sanitizar encoding antes de serializar
            orden_usuario = metadata.get("orden_usuario", "").encode(
                "utf-8", errors="replace"
            ).decode("utf-8")

            manifest = {
                "mission_id":       os.path.basename(mission_path),
                "timestamp":        datetime.now().isoformat(),

                # Clave principal — leída por MissionMemory v1.2.0+
                "estado":           estado_valor,

                # Alias backward compat — para lectores externos
                "status":           estado_valor,

                "compliance_score": metadata.get("compliance_score", 0),
                "deuda_tecnica":    metadata.get("deuda_tecnica", False),
                "iteracion_final":  metadata.get("iteracion_final", 0),
                "orden_usuario":    orden_usuario,

                "modelos": metadata.get("modelos", {
                    "architect": "google/gemini-2.5-flash-lite",
                    "engineer":  "google/gemini-2.5-pro",
                    "auditor":   "google/gemini-2.5-pro",
                }),

                "files": {
                    "architecture":   "architecture.md",
                    "implementation": "implementation.py",
                    "audit":          "audit.md",
                    "manifest":       "mission_manifest.json",
                },

                "storage_backend": os.getenv("MAIIE_STORAGE_BACKEND", "local"),

                # v2.1.0: flag para que MissionMemory evite blob.exists() extra
                "embedding_disponible": False,
            }

            # FIX v2.0.1: ensure_ascii=True elimina caracteres corruptos en Windows
            self.storage.write(
                manifest_path,
                json.dumps(manifest, indent=4, ensure_ascii=True)
            )

            logger.info(f"📦 Artefactos guardados en: {mission_path}")

        except Exception as e:
            logger.error(f"Error guardando artefactos: {e}")
            raise

        # ---------------------------------------------------------
        # v2.1.0: EMBEDDING — best-effort, fuera del bloque principal.
        # Los artefactos ya están en disco/GCS antes de llegar aquí.
        # ---------------------------------------------------------
        self._intentar_guardar_embedding(
            mission_path=mission_path,
            manifest_path=manifest_path,
            manifest=manifest,
            orden_usuario=orden_usuario,
        )

        return mission_path

    def _intentar_guardar_embedding(
        self,
        mission_path: str,
        manifest_path: str,
        manifest: dict,
        orden_usuario: str,
    ) -> None:
        """
        Genera y persiste el embedding de forma best-effort.

        Si falla en cualquier punto registra WARNING y retorna.
        Los artefactos principales ya están guardados antes de esta llamada.
        Si tiene éxito, actualiza el flag embedding_disponible en el manifest.
        """
        if not orden_usuario.strip():
            return

        vector = self._generar_embedding(orden_usuario)

        if vector is None:
            return

        try:
            self._guardar_embedding(
                mission_path=mission_path,
                orden_usuario=orden_usuario,
                vector=vector,
            )

            # Actualizar manifest: MissionMemory usará este flag para
            # saber si vale la pena buscar mission_embedding.json en GCS
            manifest["embedding_disponible"] = True
            self.storage.write(
                manifest_path,
                json.dumps(manifest, indent=4, ensure_ascii=True)
            )

        except Exception as e:
            logger.warning(
                f"⚠️ Embedding generado pero no pudo persistirse: {e}"
            )