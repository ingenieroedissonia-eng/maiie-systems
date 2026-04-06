"""
MAIIE System V2 - Backfill de Embeddings
Script utilitario — ejecución única
Registro 58 / Prioridad 4

Genera mission_embedding.json para todas las misiones en GCS
que no tienen embedding todavía.

Uso:
    python backfill_embeddings.py

Requiere:
    - google-cloud-aiplatform instalado
    - google-cloud-storage instalado
    - ADC activo (gcloud auth application-default login)
    - MAIIE_GCP_PROJECT en config/.env o variable de entorno
"""

import os
import json
import math
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "config", ".env"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(message)s"
)
logger = logging.getLogger("backfill")

# ------------------------------------------------------------------
# CONFIGURACIÓN
# ------------------------------------------------------------------

BUCKET_NAME    = os.getenv("MAIIE_GCS_BUCKET", "maiie-missions-prod")
MISSIONS_PATH  = "output/missions"
EMBEDDING_MODEL = "text-embedding-004"
GCP_PROJECT    = os.getenv("MAIIE_GCP_PROJECT", "")
GCP_LOCATION   = os.getenv("MAIIE_GCP_LOCATION", "us-central1")


# ------------------------------------------------------------------
# INICIALIZAR CLIENTES
# ------------------------------------------------------------------

def init_clients():
    from google.cloud import storage as gcs
    import vertexai

    if not GCP_PROJECT:
        raise ValueError("MAIIE_GCP_PROJECT no configurado en .env")

    vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)
    client = gcs.Client()
    bucket = client.bucket(BUCKET_NAME)

    logger.info(f"✅ GCS conectado: gs://{BUCKET_NAME}")
    logger.info(f"✅ Vertex AI inicializado: {GCP_PROJECT} / {GCP_LOCATION}")

    return client, bucket


# ------------------------------------------------------------------
# LISTAR MISIONES
# ------------------------------------------------------------------

def listar_misiones(client, bucket_name):
    prefix = f"{MISSIONS_PATH}/"
    blobs  = client.list_blobs(bucket_name, prefix=prefix, delimiter="/")
    _      = list(blobs)

    misiones = []
    for p in (blobs.prefixes or []):
        parts      = p.rstrip("/").split("/")
        mission_id = parts[-1]
        if mission_id.startswith("mission_"):
            misiones.append(mission_id)

    return sorted(misiones)


# ------------------------------------------------------------------
# CARGAR MANIFEST
# ------------------------------------------------------------------

def cargar_manifest(bucket, mission_id):
    blob_path = f"{MISSIONS_PATH}/{mission_id}/mission_manifest.json"
    blob      = bucket.blob(blob_path)

    if not blob.exists():
        return None

    try:
        return json.loads(blob.download_as_text(encoding="utf-8"))
    except Exception as e:
        logger.warning(f"  ⚠️  Error leyendo manifest de {mission_id}: {e}")
        return None


# ------------------------------------------------------------------
# VERIFICAR SI YA TIENE EMBEDDING
# ------------------------------------------------------------------

def tiene_embedding(bucket, mission_id):
    blob_path = f"{MISSIONS_PATH}/{mission_id}/mission_embedding.json"
    return bucket.blob(blob_path).exists()


# ------------------------------------------------------------------
# GENERAR EMBEDDING
# ------------------------------------------------------------------

def generar_embedding(texto):
    from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

    modelo  = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)
    entrada = TextEmbeddingInput(
        text=texto[:2000],
        task_type="RETRIEVAL_DOCUMENT"
    )
    resultado = modelo.get_embeddings([entrada])
    return resultado[0].values


# ------------------------------------------------------------------
# GUARDAR EMBEDDING EN GCS
# ------------------------------------------------------------------

def guardar_embedding(bucket, mission_id, orden_usuario, vector):
    blob_path = f"{MISSIONS_PATH}/{mission_id}/mission_embedding.json"
    blob      = bucket.blob(blob_path)

    data = {
        "modelo":        EMBEDDING_MODEL,
        "dimensiones":   len(vector),
        "orden_usuario": orden_usuario[:500],
        "vector":        vector,
        "timestamp":     datetime.now().isoformat(),
        "backfill":      True,  # marca para identificar embeddings generados por este script
    }

    blob.upload_from_string(
        json.dumps(data, ensure_ascii=True),
        content_type="text/plain"
    )


# ------------------------------------------------------------------
# ACTUALIZAR FLAG EN MANIFEST
# ------------------------------------------------------------------

def actualizar_manifest(bucket, mission_id, manifest):
    blob_path = f"{MISSIONS_PATH}/{mission_id}/mission_manifest.json"
    blob      = bucket.blob(blob_path)

    manifest["embedding_disponible"] = True

    blob.upload_from_string(
        json.dumps(manifest, indent=4, ensure_ascii=True),
        content_type="text/plain"
    )


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------

def main():
    logger.info("=" * 60)
    logger.info("MAIIE — Backfill de Embeddings")
    logger.info("=" * 60)

    client, bucket = init_clients()

    misiones = listar_misiones(client, BUCKET_NAME)
    logger.info(f"\n📦 Total misiones en GCS: {len(misiones)}\n")

    procesadas  = 0
    omitidas    = 0
    sin_manifest = 0
    errores     = 0

    for mission_id in misiones:

        logger.info(f"🔍 {mission_id}")

        # Verificar si ya tiene embedding
        if tiene_embedding(bucket, mission_id):
            logger.info(f"  ✅ Ya tiene embedding — omitiendo")
            omitidas += 1
            continue

        # Cargar manifest para obtener orden_usuario
        manifest = cargar_manifest(bucket, mission_id)

        if not manifest:
            logger.warning(f"  ⚠️  Sin manifest — omitiendo")
            sin_manifest += 1
            continue

        orden_usuario = manifest.get("orden_usuario", "").strip()

        if not orden_usuario:
            logger.warning(f"  ⚠️  orden_usuario vacío — omitiendo")
            sin_manifest += 1
            continue

        logger.info(f"  📝 Orden: {orden_usuario[:80]}...")

        # Generar embedding
        try:
            vector = generar_embedding(orden_usuario)
            logger.info(f"  🔢 Embedding generado: {len(vector)} dims")
        except Exception as e:
            logger.error(f"  ❌ Error generando embedding: {e}")
            errores += 1
            continue

        # Guardar mission_embedding.json
        try:
            guardar_embedding(bucket, mission_id, orden_usuario, vector)
            logger.info(f"  💾 mission_embedding.json guardado en GCS")
        except Exception as e:
            logger.error(f"  ❌ Error guardando embedding: {e}")
            errores += 1
            continue

        # Actualizar flag en manifest
        try:
            actualizar_manifest(bucket, mission_id, manifest)
            logger.info(f"  📋 Manifest actualizado: embedding_disponible=true")
        except Exception as e:
            logger.warning(f"  ⚠️  Embedding guardado pero manifest no actualizado: {e}")

        procesadas += 1

    # ------------------------------------------------------------------
    # RESUMEN
    # ------------------------------------------------------------------

    logger.info("\n" + "=" * 60)
    logger.info("RESUMEN DEL BACKFILL")
    logger.info("=" * 60)
    logger.info(f"  Total misiones:      {len(misiones)}")
    logger.info(f"  Procesadas:          {procesadas}")
    logger.info(f"  Ya tenían embedding: {omitidas}")
    logger.info(f"  Sin manifest:        {sin_manifest}")
    logger.info(f"  Errores:             {errores}")
    logger.info("=" * 60)

    if errores == 0:
        logger.info("✅ Backfill completado sin errores")
    else:
        logger.info(f"⚠️  Backfill completado con {errores} error(es)")


if __name__ == "__main__":
    main()