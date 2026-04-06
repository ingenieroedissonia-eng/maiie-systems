"""
tests/test_artifact_manager.py
Cobertura: ArtifactManager, StorageBackend (Local y GCS mock), crear_storage_backend()
Versión: v1.0.0
Costo: CERO — GCS completamente mockeado, sin llamadas reales a Google Cloud.
"""

import json
import os
import pytest
from unittest.mock import MagicMock, patch, call
from utils.artifact_manager import (
    ArtifactManager,
    LocalStorage,
    GCSStorage,
    crear_storage_backend,
)


# =========================================================
# FIXTURES
# =========================================================

@pytest.fixture
def local_manager(tmp_path):
    """ArtifactManager con LocalStorage en directorio temporal."""
    with patch.dict(os.environ, {"MAIIE_STORAGE_BACKEND": "local"}, clear=False):
        with patch("utils.artifact_manager.ArtifactManager._inicializar_genai", return_value=False):
            manager = ArtifactManager(base_output=str(tmp_path / "output"))
    return manager, tmp_path


@pytest.fixture
def gcs_manager():
    """ArtifactManager con GCSStorage completamente mockeado."""
    mock_bucket = MagicMock()
    mock_blob   = MagicMock()
    mock_blob.exists.return_value = True
    mock_bucket.blob.return_value = mock_blob

    with patch.dict(os.environ, {
        "MAIIE_STORAGE_BACKEND": "gcs",
        "MAIIE_GCS_BUCKET": "maiie-missions-prod",
    }, clear=False):
        with patch("utils.artifact_manager.GCSStorage.__init__", return_value=None):
            with patch("utils.artifact_manager.ArtifactManager._inicializar_genai", return_value=False):
                manager = ArtifactManager(base_output="output")
                manager.storage._bucket      = mock_bucket
                manager.storage._bucket_name = "maiie-missions-prod"
                manager.storage._client      = MagicMock()
    return manager, mock_bucket, mock_blob


METADATA_APROBADO = {
    "mission_id":      "mission_20260319_190952_fc7af3a9",
    "estado":          "APROBADO",
    "compliance_score": 95,
    "deuda_tecnica":   False,
    "iteracion_final": 1,
    "orden_usuario":   "Crea api/user_router.py con el endpoint POST /users en FastAPI",
    "modelos": {
        "architect": "google/gemini-2.5-flash-lite",
        "engineer":  "google/gemini-2.5-pro",
        "auditor":   "google/gemini-2.5-pro",
    },
}


# =========================================================
# FACTORY — crear_storage_backend()
# =========================================================

class TestCrearStorageBackend:

    def test_local_es_default(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("MAIIE_STORAGE_BACKEND", None)
            backend = crear_storage_backend()
        assert isinstance(backend, LocalStorage)

    def test_local_explicito(self):
        with patch.dict(os.environ, {"MAIIE_STORAGE_BACKEND": "local"}, clear=False):
            backend = crear_storage_backend()
        assert isinstance(backend, LocalStorage)

    def test_gcs_requiere_bucket(self):
        with patch.dict(os.environ, {
            "MAIIE_STORAGE_BACKEND": "gcs",
            "MAIIE_GCS_BUCKET": "",
        }, clear=False):
            with pytest.raises(ValueError, match="MAIIE_GCS_BUCKET"):
                crear_storage_backend()

    def test_gcs_con_bucket_retorna_gcs_storage(self):
        with patch.dict(os.environ, {
            "MAIIE_STORAGE_BACKEND": "gcs",
            "MAIIE_GCS_BUCKET": "maiie-missions-prod",
        }, clear=False):
            with patch("utils.artifact_manager.GCSStorage.__init__", return_value=None) as mock_init:
                backend = crear_storage_backend()
        mock_init.assert_called_once_with(bucket_name="maiie-missions-prod")

    def test_valor_desconocido_usa_local(self):
        with patch.dict(os.environ, {"MAIIE_STORAGE_BACKEND": "s3"}, clear=False):
            backend = crear_storage_backend()
        assert isinstance(backend, LocalStorage)


# =========================================================
# LOCAL STORAGE
# =========================================================

class TestLocalStorage:

    def test_write_crea_archivo(self, tmp_path):
        storage = LocalStorage()
        path    = str(tmp_path / "test.txt")
        storage.write(path, "contenido")
        assert open(path).read() == "contenido"

    def test_write_sobreescribe(self, tmp_path):
        storage = LocalStorage()
        path    = str(tmp_path / "test.txt")
        storage.write(path, "v1")
        storage.write(path, "v2")
        assert open(path).read() == "v2"

    def test_makedirs_crea_directorio(self, tmp_path):
        storage  = LocalStorage()
        new_path = str(tmp_path / "a" / "b" / "c")
        storage.makedirs(new_path)
        assert os.path.isdir(new_path)

    def test_join_usa_os_path(self):
        storage = LocalStorage()
        result  = storage.join("output", "missions", "mission_123")
        assert result == os.path.join("output", "missions", "mission_123")


# =========================================================
# GCS STORAGE
# =========================================================

class TestGCSStorage:

    def _make_storage(self):
        with patch("utils.artifact_manager.GCSStorage.__init__", return_value=None):
            storage = GCSStorage.__new__(GCSStorage)
            storage._bucket      = MagicMock()
            storage._bucket_name = "test-bucket"
            storage._client      = MagicMock()
        return storage

    def test_write_llama_upload(self):
        storage  = self._make_storage()
        mock_blob = MagicMock()
        storage._bucket.blob.return_value = mock_blob
        storage.write("output/missions/m1/architecture.md", "contenido")
        storage._bucket.blob.assert_called_once_with("output/missions/m1/architecture.md")
        mock_blob.upload_from_string.assert_called_once()

    def test_write_normaliza_backslash(self):
        storage   = self._make_storage()
        mock_blob = MagicMock()
        storage._bucket.blob.return_value = mock_blob
        storage.write("output\\missions\\m1\\file.md", "x")
        llamada = storage._bucket.blob.call_args[0][0]
        assert "\\" not in llamada

    def test_makedirs_es_noop(self):
        storage = self._make_storage()
        storage.makedirs("output/missions/m1")
        storage._bucket.blob.assert_not_called()

    def test_join_usa_slash(self):
        storage = self._make_storage()
        result  = storage.join("output", "missions", "mission_123")
        assert result == "output/missions/mission_123"

    def test_join_elimina_slashes_dobles(self):
        storage = self._make_storage()
        result  = storage.join("output/", "/missions/", "/mission_123")
        assert "//" not in result


# =========================================================
# ARTIFACT MANAGER — LOCAL
# =========================================================

class TestArtifactManagerLocal:

    def test_guardar_crea_cuatro_archivos(self, local_manager):
        manager, tmp_path = local_manager
        mission_path = manager.guardar_artefactos(
            arquitectura="arch", codigo="code", auditoria="audit",
            metadata=METADATA_APROBADO,
        )
        archivos = os.listdir(mission_path)
        assert "architecture.md"      in archivos
        assert "implementation.py"    in archivos
        assert "audit.md"             in archivos
        assert "mission_manifest.json" in archivos

    def test_manifest_contiene_campos_criticos(self, local_manager):
        manager, tmp_path = local_manager
        mission_path = manager.guardar_artefactos(
            arquitectura="arch", codigo="code", auditoria="audit",
            metadata=METADATA_APROBADO,
        )
        manifest_path = os.path.join(mission_path, "mission_manifest.json")
        manifest = json.loads(open(manifest_path).read())

        assert manifest["estado"]           == "APROBADO"
        assert manifest["status"]           == "APROBADO"
        assert manifest["compliance_score"] == 95
        assert manifest["deuda_tecnica"]    is False
        assert manifest["iteracion_final"]  == 1
        assert "orden_usuario"              in manifest
        assert "modelos"                    in manifest

    def test_manifest_mission_id_desde_basename(self, local_manager):
        manager, tmp_path = local_manager
        mission_path = manager.guardar_artefactos(
            arquitectura="arch", codigo="code", auditoria="audit",
            metadata=METADATA_APROBADO,
        )
        manifest = json.loads(open(os.path.join(mission_path, "mission_manifest.json")).read())
        assert manifest["mission_id"] == os.path.basename(mission_path)

    def test_mission_id_desde_metadata(self, local_manager):
        manager, tmp_path = local_manager
        mission_path = manager.guardar_artefactos(
            arquitectura="arch", codigo="code", auditoria="audit",
            metadata=METADATA_APROBADO,
        )
        assert "mission_20260319_190952_fc7af3a9" in mission_path

    def test_estado_desconocido_si_metadata_vacio(self, local_manager):
        manager, tmp_path = local_manager
        mission_path = manager.guardar_artefactos(
            arquitectura="", codigo="", auditoria="", metadata={},
        )
        manifest = json.loads(open(os.path.join(mission_path, "mission_manifest.json")).read())
        assert manifest["estado"] == "DESCONOCIDO"

    def test_embedding_disponible_false_sin_genai(self, local_manager):
        manager, tmp_path = local_manager
        mission_path = manager.guardar_artefactos(
            arquitectura="arch", codigo="code", auditoria="audit",
            metadata=METADATA_APROBADO,
        )
        manifest = json.loads(open(os.path.join(mission_path, "mission_manifest.json")).read())
        assert manifest["embedding_disponible"] is False

    def test_fallo_en_write_lanza_excepcion(self, local_manager):
        manager, tmp_path = local_manager
        with patch.object(manager.storage, "write", side_effect=IOError("disco lleno")):
            with pytest.raises(IOError):
                manager.guardar_artefactos(
                    arquitectura="arch", codigo="code", auditoria="audit",
                    metadata=METADATA_APROBADO,
                )


# =========================================================
# ARTIFACT MANAGER — GCS
# =========================================================

class TestArtifactManagerGCS:

    def test_guardar_llama_write_cuatro_veces(self, gcs_manager):
        manager, mock_bucket, mock_blob = gcs_manager
        writes = []
        manager.storage.write = lambda path, content: writes.append(path)
        manager.guardar_artefactos(
            arquitectura="arch", codigo="code", auditoria="audit",
            metadata=METADATA_APROBADO,
        )
        # architecture, implementation, audit, manifest
        assert len(writes) == 4

    def test_rutas_gcs_usan_slash(self, gcs_manager):
        manager, mock_bucket, mock_blob = gcs_manager
        rutas = []
        manager.storage.write = lambda path, content: rutas.append(path)
        manager.guardar_artefactos(
            arquitectura="arch", codigo="code", auditoria="audit",
            metadata=METADATA_APROBADO,
        )
        for ruta in rutas:
            assert "\\" not in ruta, f"Backslash encontrado en ruta GCS: {ruta}"

    def test_manifest_serializado_como_json_valido(self, gcs_manager):
        manager, mock_bucket, mock_blob = gcs_manager
        contenidos = {}
        def mock_write(path, content):
            contenidos[path] = content
        manager.storage.write = mock_write
        manager.guardar_artefactos(
            arquitectura="arch", codigo="code", auditoria="audit",
            metadata=METADATA_APROBADO,
        )
        manifest_key = next(k for k in contenidos if "manifest" in k)
        parsed = json.loads(contenidos[manifest_key])
        assert parsed["estado"] == "APROBADO"
        assert parsed["compliance_score"] == 95

    def test_storage_backend_en_manifest_es_gcs(self, gcs_manager):
        manager, mock_bucket, mock_blob = gcs_manager
        contenidos = {}
        manager.storage.write = lambda path, content: contenidos.update({path: content})
        with patch.dict(os.environ, {"MAIIE_STORAGE_BACKEND": "gcs"}, clear=False):
            manager.guardar_artefactos(
                arquitectura="arch", codigo="code", auditoria="audit",
                metadata=METADATA_APROBADO,
            )
        manifest_key = next(k for k in contenidos if "manifest" in k)
        parsed = json.loads(contenidos[manifest_key])
        assert parsed["storage_backend"] == "gcs"