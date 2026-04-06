"""
MAIIE System V2 - Repo Generator
Módulo: Reconstrucción de proyectos desde implementation.py
Capa: Infrastructure
Versión: 2.0.0

CHANGELOG v2.0.0:
- ADD: Abstracción de storage backend — reutiliza LocalStorage/GCSStorage
       de artifact_manager.py v2.0.0.
       Controlado por MAIIE_STORAGE_BACKEND en .env (local o gcs).
       Variable adicional: MAIIE_GCS_BUCKET para backend gcs.
       Sin cambios en la interfaz pública — pipeline.py no requiere modificación.

CHANGELOG v1.0.2:
- FIX: FILE_PATTERN acepta '# File:' y 'Archivo:' (dual pattern)

CHANGELOG v1.0.1:
- FIX: _parsear_bloques deduplica por file_path antes de retornar
"""

import os
import re
import logging

from utils.artifact_manager import crear_storage_backend, LocalStorage

logger = logging.getLogger("MAIIE.RepoGenerator")


class RepoGenerator:
    """
    Genera la estructura real de un proyecto a partir del
    implementation.py producido por el pipeline.

    El backend de storage se selecciona desde .env:
        MAIIE_STORAGE_BACKEND=local  (default)
        MAIIE_STORAGE_BACKEND=gcs
    """

    FILE_PATTERN = r"(?:#\s*File:|Archivo:)\s*([^\n]+)"

    def __init__(self, base_output: str = "output/generated_projects"):
        self.base_output = base_output
        self.storage     = crear_storage_backend()

        # Crear directorio base solo en local
        if isinstance(self.storage, LocalStorage):
            self.storage.makedirs(self.base_output)

    # ----------------------------------------------------------
    # PARSEAR BLOQUES
    # ----------------------------------------------------------

    def _parsear_bloques(self, implementation_text: str) -> list[dict]:
        """
        Divide el implementation_text en bloques por archivo.
        Aplica deduplicación por file_path.
        """
        matches = list(re.finditer(self.FILE_PATTERN, implementation_text))

        if not matches:
            return []

        bloques = []

        for i, match in enumerate(matches):

            file_path = match.group(1).strip()

            start = match.end()
            end   = matches[i + 1].start() if i + 1 < len(matches) else len(implementation_text)

            content = implementation_text[start:end].strip()

            # Limpiar bloques markdown residuales
            content = re.sub(r"^```[a-zA-Z]*\n?", "", content, flags=re.MULTILINE)
            content = re.sub(r"```$",              "", content, flags=re.MULTILINE)
            content = content.strip()

            bloques.append({"file_path": file_path, "content": content})

        # Deduplicar preservando primera ocurrencia
        vistos         = set()
        bloques_unicos = []
        for b in bloques:
            if b["file_path"] not in vistos:
                vistos.add(b["file_path"])
                bloques_unicos.append(b)

        duplicados = len(bloques) - len(bloques_unicos)
        if duplicados > 0:
            logger.warning(f"⚠️ {duplicados} bloque(s) duplicado(s) ignorado(s)")

        return bloques_unicos

    # ----------------------------------------------------------
    # GENERAR REPO
    # ----------------------------------------------------------

    def generar_repo(self, implementation_text: str, mission_id: str) -> str:
        """
        Reconstruye el proyecto completo desde el implementation_text.

        Args:
            implementation_text: contenido del implementation.py generado.
            mission_id:          ID de la misión (nombre de carpeta/prefijo GCS).

        Returns:
            Ruta del proyecto generado (filesystem o GCS path).
        """
        repo_path = self.storage.join(self.base_output, mission_id)
        self.storage.makedirs(repo_path)

        logger.info(f"📁 Generando repo: {repo_path}")

        bloques = self._parsear_bloques(implementation_text)

        if not bloques:
            logger.warning(
                "⚠️ No se detectaron archivos en implementation. "
                "Verifica que el ENGINEER_BASE usa '# File: ruta/archivo.py' "
                "como primera línea de cada bloque."
            )
            return repo_path

        archivos_generados = 0

        for bloque in bloques:
            file_path = bloque["file_path"]
            content   = bloque["content"]
            full_path = self.storage.join(repo_path, file_path)

            # Crear carpetas intermedias (solo aplica en local)
            parent = self.storage.join(repo_path, os.path.dirname(file_path))
            self.storage.makedirs(parent)

            try:
                self.storage.write(full_path, content)
                logger.info(f"📄 Archivo generado: {file_path}")
                archivos_generados += 1

            except Exception as e:
                logger.error(f"Error escribiendo {file_path}: {e}")

        logger.info(
            f"✅ Repo generado: {archivos_generados} archivo(s) en {repo_path}"
        )

        return repo_path