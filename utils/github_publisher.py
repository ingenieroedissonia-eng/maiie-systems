"""
MAIIE System V2 - GitHub Publisher
Módulo: Publicación de misiones aprobadas como repositorios privados en GitHub
Capa: Infrastructure
Versión: 1.1.0

CHANGELOG v1.1.0:
- ADD: publicar_sistema() — publica múltiples misiones (una ejecución completa
       del Planner) como un único repositorio consolidado en GitHub.
       Recibe una lista de mission_ids, lee el implementation.py de cada una,
       parsea los archivos y los sube todos al mismo repo.
       Los archivos de misiones posteriores sobreescriben los de anteriores
       si hay conflicto de ruta — la última versión gana.
- ADD: _consolidar_archivos() — agrega archivos de múltiples implementations
       en un solo dict sin duplicados.
- COMPAT: publicar_mision() sin cambios — sigue funcionando para misión única.

CHANGELOG v1.0.1:
- FIX: Sanitización de caracteres de control en orden_usuario al construir
       la descripción del repo. GitHub API rechaza con 422 si la descripción
       contiene \\n u otros caracteres de control.

CHANGELOG v1.0.0:
- ADD: Publicación de misión individual como repo privado en GitHub.
"""

import os
import re
import json
import time
import base64
import logging
from typing import Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv

from utils.artifact_manager import crear_storage_backend, GCSStorage

env_path = os.path.join(os.path.dirname(__file__), "..", "config", ".env")
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger("MAIIE.GitHubPublisher")

GITHUB_API      = "https://api.github.com"
FILE_PATTERN    = r"(?:#\s*File:|Archivo:)\s*([^\n]+)"
MAX_RETRIES     = 3
RETRY_DELAY_SEC = 2


class GitHubPublisher:
    """
    Publica misiones aprobadas como repositorios privados en GitHub.

    v1.1.0: Soporta publicación de sistemas completos (múltiples misiones
    de una ejecución del Planner) en un único repositorio consolidado.

    Flujo publicar_mision() — misión individual:
        1. Recuperar implementation.py desde GCS/local
        2. Parsear archivos del implementation
        3. Crear repo privado en GitHub
        4. Subir cada archivo al repo

    Flujo publicar_sistema() — sistema completo:
        1. Recuperar implementation.py de cada mission_id
        2. Consolidar todos los archivos en un único dict
        3. Crear un solo repo privado en GitHub
        4. Subir todos los archivos consolidados
    """

    def __init__(self):
        self.token    = os.getenv("GITHUB_TOKEN", "").strip()
        self.username = os.getenv("GITHUB_USERNAME", "").strip()

        if not self.token:
            raise ValueError(
                "GITHUB_TOKEN no configurado. "
                "Agrega GITHUB_TOKEN al archivo config/.env"
            )
        if not self.username:
            raise ValueError(
                "GITHUB_USERNAME no configurado. "
                "Agrega GITHUB_USERNAME al archivo config/.env"
            )

        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept":        "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        self.storage = crear_storage_backend()
        logger.info(f"GitHubPublisher inicializado - usuario: {self.username}")

    def _sanitize_github_text(self, text: str, max_len: int = 100) -> str:
        if not text:
            return ""
        text = re.sub(r"[\x00-\x1f\x7f]", " ", text)
        text = text.encode("ascii", "ignore").decode()
        text = " ".join(text.split())
        return text[:max_len]

    # ----------------------------------------------------------
    # LEER ARTEFACTOS DESDE STORAGE
    # ----------------------------------------------------------

    def _leer_implementation(self, mission_id: str) -> Optional[str]:
        """
        Recupera el implementation.py de una misión desde GCS o local.
        """
        if not mission_id.startswith("mission_"):
            folder = f"mission_{mission_id}"
        else:
            folder = mission_id

        impl_path = self.storage.join("output/missions", folder, "implementation.py")

        try:
            if isinstance(self.storage, GCSStorage):
                gcs_path = impl_path.replace("\\", "/").lstrip("/")
                blob     = self.storage._get_bucket().blob(gcs_path)
                if not blob.exists():
                    logger.error(f"❌ implementation.py no encontrado en GCS: {gcs_path}")
                    return None
                content = blob.download_as_text(encoding="utf-8")
                logger.info(f"☁️ implementation.py recuperado: {gcs_path}")
                return content
            else:
                if not os.path.exists(impl_path):
                    logger.error(f"❌ implementation.py no encontrado: {impl_path}")
                    return None
                with open(impl_path, "r", encoding="utf-8") as f:
                    content = f.read()
                logger.info(f"📂 implementation.py recuperado: {impl_path}")
                return content

        except Exception as e:
            logger.error(f"❌ Error leyendo implementation.py de {mission_id}: {e}")
            return None

    def _leer_manifest(self, mission_id: str) -> Optional[dict]:
        """Recupera el manifest de una misión."""
        if not mission_id.startswith("mission_"):
            folder = f"mission_{mission_id}"
        else:
            folder = mission_id

        manifest_path = self.storage.join(
            "output/missions", folder, "mission_manifest.json"
        )

        try:
            if isinstance(self.storage, GCSStorage):
                gcs_path = manifest_path.replace("\\", "/").lstrip("/")
                blob     = self.storage._get_bucket().blob(gcs_path)
                if not blob.exists():
                    return None
                return json.loads(blob.download_as_text(encoding="utf-8"))
            else:
                if not os.path.exists(manifest_path):
                    return None
                with open(manifest_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"❌ Error leyendo manifest de {mission_id}: {e}")
            return None

    # ----------------------------------------------------------
    # PARSEAR Y CONSOLIDAR ARCHIVOS
    # ----------------------------------------------------------

    def _parsear_archivos(self, implementation_text: str) -> Dict[str, str]:
        """
        Extrae los archivos del implementation.py.
        Mismo patrón que RepoGenerator._parsear_bloques().
        """
        matches = list(re.finditer(FILE_PATTERN, implementation_text))

        if not matches:
            logger.warning("⚠️ No se detectaron archivos en implementation.py")
            return {}

        archivos = {}

        for i, match in enumerate(matches):
            file_path = match.group(1).strip()
            start     = match.end()
            end       = matches[i + 1].start() if i + 1 < len(matches) else len(implementation_text)
            content   = implementation_text[start:end].strip()

            content = re.sub(r"^```[a-zA-Z]*\n?", "", content, flags=re.MULTILINE)
            content = re.sub(r"```$",              "", content, flags=re.MULTILINE)
            content = content.strip()

            if file_path not in archivos:
                archivos[file_path] = content

        logger.info(f"📋 {len(archivos)} archivo(s) parseados")
        return archivos

    def _consolidar_archivos(
        self, mission_ids: List[str]
    ) -> Tuple[Dict[str, str], List[str]]:
        """
        Consolida los archivos de múltiples misiones en un único dict.

        Las misiones se procesan en orden — si dos misiones generan el mismo
        archivo, la última versión gana (submisión más reciente tiene prioridad).

        Args:
            mission_ids: Lista de IDs de misión en orden de ejecución.

        Returns:
            (archivos_consolidados, missions_fallidas)
        """
        consolidado    = {}
        fallidas       = []
        total_archivos = 0

        for mission_id in mission_ids:
            implementation = self._leer_implementation(mission_id)

            if not implementation:
                logger.warning(
                    f"⚠️ Sin implementation.py para {mission_id} — omitiendo"
                )
                fallidas.append(mission_id)
                continue

            archivos = self._parsear_archivos(implementation)

            if not archivos:
                logger.warning(
                    f"⚠️ Sin archivos parseados en {mission_id} — omitiendo"
                )
                fallidas.append(mission_id)
                continue

            consolidado.update(archivos)
            total_archivos += len(archivos)
            logger.info(
                f"✅ {mission_id}: {len(archivos)} archivo(s) consolidados"
            )

        logger.info(
            f"📦 Consolidación completa: {len(consolidado)} archivo(s) únicos "
            f"de {len(mission_ids)} misión(es) "
            f"({len(fallidas)} fallida(s))"
        )

        return consolidado, fallidas

    # ----------------------------------------------------------
    # API DE GITHUB
    # ----------------------------------------------------------

    def _request_con_retry(self, method: str, url: str, **kwargs) -> requests.Response:
        for intento in range(1, MAX_RETRIES + 1):
            try:
                response = requests.request(method, url, headers=self.headers, **kwargs)

                if response.status_code in [403, 429]:
                    retry_after = int(
                        response.headers.get("Retry-After", RETRY_DELAY_SEC * intento)
                    )
                    logger.warning(
                        f"⚠️ Rate limit GitHub — esperando {retry_after}s "
                        f"(intento {intento}/{MAX_RETRIES})"
                    )
                    time.sleep(retry_after)
                    continue

                return response

            except requests.RequestException as e:
                if intento == MAX_RETRIES:
                    raise
                logger.warning(f"⚠️ Error de red — reintentando: {e}")
                time.sleep(RETRY_DELAY_SEC * intento)

        raise RuntimeError(f"Request fallido después de {MAX_RETRIES} intentos: {url}")

    def _crear_repo(self, nombre: str, descripcion: str = "") -> Tuple[str, str]:
        url = f"{GITHUB_API}/user/repos"
        descripcion = self._sanitize_github_text(descripcion or "", 300)
        descripcion = descripcion[:350]
        data = {
            "name":        nombre,
            "private":     True,
            "description": descripcion,
            "auto_init":   False,
        }

        response = self._request_con_retry("POST", url, json=data)

        if response.status_code == 422:
            nombre_unico = f"{nombre}-{int(time.time())}"
            logger.warning(f"⚠️ Repo '{nombre}' ya existe — usando '{nombre_unico}'")
            data["name"] = nombre_unico
            response     = self._request_con_retry("POST", url, json=data)

        if response.status_code != 201:
            raise RuntimeError(
                f"Error creando repo GitHub: {response.status_code} — {response.text[:200]}"
            )

        repo_data      = response.json()
        html_url       = repo_data["html_url"]
        default_branch = repo_data.get("default_branch", "main")

        logger.info(f"✅ Repo creado: {html_url}")
        return html_url, default_branch

    def _subir_archivo(
        self,
        repo_nombre: str,
        file_path: str,
        contenido: str,
        commit_message: str = "",
    ) -> None:
        url           = f"{GITHUB_API}/repos/{self.username}/{repo_nombre}/contents/{file_path}"
        contenido_b64 = base64.b64encode(contenido.encode("utf-8")).decode("utf-8")
        mensaje       = commit_message or f"add {file_path}"

        data     = {"message": mensaje, "content": contenido_b64}
        response = self._request_con_retry("PUT", url, json=data)

        if response.status_code not in [200, 201]:
            raise RuntimeError(
                f"Error subiendo {file_path}: {response.status_code} — {response.text[:200]}"
            )

    def _subir_archivos(
        self,
        repo_nombre: str,
        archivos: Dict[str, str],
        label: str = "",
    ) -> Tuple[int, List[str]]:
        exitosos = 0
        errores  = []

        for file_path, contenido in archivos.items():
            try:
                self._subir_archivo(
                    repo_nombre=repo_nombre,
                    file_path=file_path,
                    contenido=contenido,
                    commit_message=f"[MAIIE] {label} — add {file_path}",
                )
                logger.info(f"📄 Subido: {file_path}")
                exitosos += 1
            except Exception as e:
                logger.error(f"❌ Error subiendo {file_path}: {e}")
                errores.append(file_path)

        return exitosos, errores

    # ----------------------------------------------------------
    # INTERFAZ PÚBLICA
    # ----------------------------------------------------------


    def _generar_readme(self, mission_id: str, archivos: dict, manifest: dict) -> str:
        orden = manifest.get("orden_usuario", "Sistema generado por MAIIE")
        orden = self._sanitize_github_text(orden, 200)
        compliance = manifest.get("compliance_score", 100)
        iteracion = manifest.get("iteracion_final", 1)
        timestamp = manifest.get("timestamp", "")[:10]
        modelos = manifest.get("modelos", {})
        lista_archivos = "\n".join(f"- `{f}`" for f in sorted(archivos.keys()))

        return f"""# {mission_id}

> Generated by **MAIIE Systems** — Multi-Agent Intelligent Implementation Engine

## Description

{orden}

## Architecture

This project was autonomously designed and implemented by MAIIE using a multi-agent pipeline:

- **ARCHITECT** ({modelos.get("architect", "gemini-2.5-flash-lite")}): System design and clean architecture
- **ENGINEER** ({modelos.get("engineer", "gemini-2.5-pro")}): Full implementation
- **AUDITOR** ({modelos.get("auditor", "gemini-2.5-pro")}): Quality certification

## Quality Metrics

| Metric | Value |
|--------|-------|
| Compliance Score | {compliance}% |
| Certified in Iteration | {iteracion} |
| Generated | {timestamp} |
| DoD Status | ✅ APPROVED |

## Files

{lista_archivos}

## Stack

- Python 3.11+ with type hints
- FastAPI / React (depending on mission type)
- Clean Architecture (Core / Infrastructure / Presentation)
- Production-ready error handling

---

*Built with [MAIIE Systems](https://maiie-systems.vercel.app) by Edisson A.G.C.*
"""

    def publicar_mision(
        self,
        mission_id: str,
        repo_nombre: Optional[str] = None,
        descripcion: str = "",
    ) -> dict:
        """
        Publica una misión individual como repo privado en GitHub.
        Sin cambios respecto a v1.0.1.
        """
        logger.info(f"🚀 Publicando misión: {mission_id}")

        manifest = self._leer_manifest(mission_id)
        if manifest is None:
            raise ValueError(f"Misión no encontrada: {mission_id}")

        estado = manifest.get("estado", manifest.get("status", "")).upper().replace(" ", "_")
        if estado not in {"APROBADO", "APROBADO_CON_DEUDA"}:
            raise ValueError(
                f"La misión {mission_id} no está aprobada (estado: {estado})."
            )

        implementation = self._leer_implementation(mission_id)
        if not implementation:
            raise ValueError(f"implementation.py no encontrado para misión: {mission_id}")

        archivos = self._parsear_archivos(implementation)
        if not archivos:
            raise ValueError(
                f"No se encontraron archivos en implementation.py de {mission_id}."
            )

        if not repo_nombre:
            nombre_base = mission_id.replace("mission_", "maiie-").replace("_", "-")
            repo_nombre = re.sub(r"[^a-zA-Z0-9\-]", "", nombre_base)[:100]

        if not descripcion:
            orden       = manifest.get("orden_usuario", "")
            orden       = self._sanitize_github_text(orden, 200)
            descripcion = f"Generated by MAIIE Systems - {orden}"

        repo_url, _ = self._crear_repo(repo_nombre, descripcion)

        readme_content = self._generar_readme(mission_id, archivos, manifest)
        archivos["README.md"] = readme_content

        exitosos, errores = self._subir_archivos(
            repo_nombre=repo_nombre,
            archivos=archivos,
            label=mission_id,
        )

        logger.info(
            f"🏁 Publicación completa — {exitosos} archivo(s), "
            f"{len(errores)} error(es). Repo: {repo_url}"
        )

        return {
            "repo_url":   repo_url,
            "archivos":   exitosos,
            "errores":    errores,
            "mission_id": mission_id,
        }

    def publicar_sistema(
        self,
        mission_ids: List[str],
        repo_nombre: Optional[str] = None,
        descripcion: str = "",
    ) -> dict:
        """
        Publica un sistema completo (múltiples misiones del Planner)
        como un único repositorio consolidado en GitHub.

        Los archivos de todas las misiones se consolidan en un solo repo.
        Si dos misiones generan el mismo archivo, la última versión gana.

        Args:
            mission_ids:  Lista de IDs de misión en orden de ejecución.
            repo_nombre:  Nombre del repo — si no se provee, usa el ID
                          de la primera misión como base.
            descripcion:  Descripción del repo en GitHub.

        Returns:
            {
                "repo_url":        str,
                "archivos":        int,
                "errores":         list,
                "mission_ids":     list,
                "missions_fallidas": list,
            }
        """
        if not mission_ids:
            raise ValueError("Lista de mission_ids vacía.")

        logger.info(
            f"🚀 Publicando sistema: {len(mission_ids)} misión(es) → 1 repo"
        )

        # Consolidar archivos de todas las misiones
        archivos, missions_fallidas = self._consolidar_archivos(mission_ids)

        if not archivos:
            raise ValueError(
                "No se encontraron archivos en ninguna de las misiones. "
                "Verifica que las misiones existen y tienen implementation.py."
            )

        # Nombre del repo basado en la primera misión
        if not repo_nombre:
            base        = mission_ids[0].replace("mission_", "maiie-").replace("_", "-")
            repo_nombre = re.sub(r"[^a-zA-Z0-9\-]", "", base)[:100]

        # Descripción basada en el manifest de la primera misión válida
        if not descripcion:
            for mid in mission_ids:
                manifest = self._leer_manifest(mid)
                if manifest:
                    orden       = manifest.get("orden_usuario", "sistema generado por MAIIE")
                    orden       = self._sanitize_github_text(orden, 200)
                    descripcion = f"Generated by MAIIE Systems - {orden}"
                    break
            if not descripcion:
                descripcion = "Generated by MAIIE Systems"

        # Crear repo único
        repo_url, _ = self._crear_repo(repo_nombre, descripcion)

        # Subir todos los archivos consolidados
        exitosos, errores = self._subir_archivos(
            repo_nombre=repo_nombre,
            archivos=archivos,
            label=f"sistema-{len(mission_ids)}-misiones",
        )

        logger.info(
            f"🏁 Sistema publicado — {exitosos} archivo(s), "
            f"{len(errores)} error(es). Repo: {repo_url}"
        )

        return {
            "repo_url":          repo_url,
            "archivos":          exitosos,
            "errores":           errores,
            "mission_ids":       mission_ids,
            "missions_fallidas": missions_fallidas,
        }