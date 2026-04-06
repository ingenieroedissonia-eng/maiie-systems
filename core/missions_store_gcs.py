"""
MAIIE System V2 - GCS Missions Store
Modulo: Persistencia de estado de misiones en Google Cloud Storage
Capa: Infrastructure
Version: 1.0.0
"""

import json
import logging
from google.cloud import storage

logger = logging.getLogger("MAIIE.MissionsStoreGCS")

BUCKET_NAME = "maiie-missions-prod"
PREFIX = "missions_store/"

_client = storage.Client()
_bucket = _client.bucket(BUCKET_NAME)


def guardar(mission_id: str, data: dict) -> None:
    try:
        blob = _bucket.blob(f"{PREFIX}{mission_id}.json")
        blob.upload_from_string(json.dumps(data), content_type="application/json")
    except Exception as e:
        logger.error("GCS guardar error [%s]: %s", mission_id, e)


def obtener(mission_id: str) -> dict | None:
    try:
        blob = _bucket.blob(f"{PREFIX}{mission_id}.json")
        if not blob.exists():
            return None
        return json.loads(blob.download_as_text())
    except Exception as e:
        logger.error("GCS obtener error [%s]: %s", mission_id, e)
        return None
    
def listar() -> list:
    try:
        blobs = _client.list_blobs(BUCKET_NAME, prefix=PREFIX)
        resultado = []
        for blob in blobs:
            mid = blob.name.replace(PREFIX, '').replace('.json', '')
            resultado.append(mid)
        return resultado
    except Exception as e:
        logger.error('GCS listar error: %s', e)
        return []

