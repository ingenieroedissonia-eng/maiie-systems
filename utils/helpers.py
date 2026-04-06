"""
MAIIE System V2 - Utilities & Helpers
Módulo: Funciones auxiliares para procesamiento y persistencia
Capa: Utils
Versión: 3.3.0

CHANGELOG v3.3.0:
- FIX: guardar_artefacto() ya no usa os.getcwd() para construir la ruta.
       Causa raíz: en Cloud Run os.getcwd() retorna /app — directorio
       efímero que desaparece con cada redeploy. Los artefactos prod_*.py
       se perdían entre revisiones porque la ruta incluía /app/output.
       Solución: en GCSStorage la ruta se construye sin os.getcwd(),
       usando solo subcarpeta/nombre_archivo igual que ArtifactManager.
       En LocalStorage el comportamiento es idéntico a v3.2.0 — sin cambios.

CHANGELOG v3.2.0:
- CHG: guardar_artefacto ahora usa el storage backend configurado
       (LocalStorage o GCSStorage según MAIIE_STORAGE_BACKEND en .env).
       En local el comportamiento es idéntico a v3.1.0.
       En GCS escribe el artefacto prod_*.py como objeto en el bucket.
       Nota: el backup automático solo aplica en LocalStorage —
       GCS no tiene concepto de rename/backup nativo en este módulo.

CHANGELOG v3.1.0:
- ADD: limpiar_codigo_md con extracción de múltiples bloques
- ADD: limpiar_nombre_archivo con sanitización de caracteres
- ADD: guardar_artefacto con versionado automático y backup
- ADD: truncar_texto_inteligente preservando inicio y fin
- ADD: extraer_puntos_criticos filtrando bloqueadores
- ADD: generar_resumen_mision para reporte visual al CEO
"""

import os
import re
import logging
from datetime import datetime
from typing import Dict, Optional

from utils.artifact_manager import crear_storage_backend, LocalStorage

logger = logging.getLogger("MAIIE.Helpers")

# ============================================================================
# PROCESAMIENTO DE CÓDIGO
# ============================================================================

def limpiar_codigo_md(texto: str) -> str:
    """
    Extrae código puro de bloques Markdown.
    Maneja múltiples bloques y diferentes sintaxis.

    Args:
        texto: Texto con bloques de código Markdown

    Returns:
        Código limpio sin marcadores Markdown
    """
    if not texto or not texto.strip():
        logger.warning("⚠️ Texto vacío recibido")
        return ""

    patrones = [
        r"```python\n(.*?)```",
        r"```py\n(.*?)```",
        r"```\n(.*?)```",
        r"```(.*?)```"
    ]

    codigo_detectado = []

    for patron in patrones:
        matches = re.findall(patron, texto, re.DOTALL)
        if matches:
            codigo_detectado.extend(matches)

    if codigo_detectado:
        resultado = "\n\n".join([c.strip() for c in codigo_detectado])
        logger.info(f"✅ Extraídos {len(codigo_detectado)} bloques de código")
        return resultado

    # Fallback: limpieza heurística
    logger.debug("Sin bloques Markdown. Aplicando limpieza heurística")
    lineas = texto.split('\n')

    prefijos_excluir = [
        'Aquí tienes', 'Espero que', 'Este código',
        'La implementación', 'He creado', 'A continuación'
    ]

    lineas_limpias = [
        l for l in lineas
        if not any(l.strip().startswith(p) for p in prefijos_excluir)
    ]

    return "\n".join(lineas_limpias).strip()


def limpiar_nombre_archivo(nombre: str) -> str:
    """
    Sanitiza nombres de archivo para compatibilidad con OS.

    Args:
        nombre: Nombre de archivo original

    Returns:
        Nombre sanitizado válido para el sistema de archivos
    """
    if not nombre:
        return "unnamed_file"

    nombre_limpio = re.sub(r'[\\/*?:"<>|]', "", nombre)
    nombre_limpio = nombre_limpio.replace(" ", "_")

    if len(nombre_limpio) > 200:
        nombre_limpio = nombre_limpio[:200]

    return nombre_limpio if nombre_limpio else "unnamed_file"


# ============================================================================
# PERSISTENCIA Y ARTEFACTOS
# ============================================================================

def guardar_artefacto(
    nombre_archivo: str,
    contenido: str,
    subcarpeta: str = "output"
) -> Optional[str]:
    """
    Persiste artefactos usando el storage backend configurado.

    En local: comportamiento idéntico a v3.2.0 con backup automático.
    En GCS: construye la ruta sin os.getcwd() para evitar pérdida de
    artefactos en Cloud Run donde el filesystem es efímero.

    Args:
        nombre_archivo: Nombre del archivo a guardar
        contenido:      Contenido a escribir
        subcarpeta:     Subdirectorio donde guardar (default: output)

    Returns:
        Ruta completa del archivo guardado o None si falla
    """
    try:
        if not contenido or not contenido.strip():
            logger.warning("⚠️ Contenido vacío, no se guardará")
            return None

        storage       = crear_storage_backend()
        nombre_limpio = limpiar_nombre_archivo(nombre_archivo)

        if isinstance(storage, LocalStorage):
            # LOCAL: usar os.getcwd() — comportamiento idéntico a v3.2.0
            directorio    = os.path.join(os.getcwd(), subcarpeta)
            ruta_completa = os.path.join(directorio, nombre_limpio)

            storage.makedirs(directorio)

            # Backup si existe
            if os.path.exists(ruta_completa):
                timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{ruta_completa}.{timestamp}.bak"
                os.rename(ruta_completa, backup_path)
                logger.info(f"📦 Backup creado: {backup_path}")

        else:
            # GCS: ruta relativa sin os.getcwd() — persiste entre redeployss
            # Mismo patrón que ArtifactManager para misiones
            ruta_completa = storage.join(subcarpeta, nombre_limpio)

        storage.write(ruta_completa, contenido)
        logger.info(f"💾 Artefacto guardado: {ruta_completa}")
        return ruta_completa

    except Exception as e:
        logger.error(f"❌ Error guardando {nombre_archivo}: {type(e).__name__}: {e}")
        return None


# ============================================================================
# GESTIÓN DE CONTEXTO
# ============================================================================

def truncar_texto_inteligente(texto: str, max_chars: int = 10000) -> str:
    """
    Trunca texto preservando inicio y fin.

    Args:
        texto:     Texto a truncar
        max_chars: Número máximo de caracteres

    Returns:
        Texto truncado con indicador si fue necesario
    """
    if not texto or len(texto) <= max_chars:
        return texto

    chars_inicio = int(max_chars * 0.45)
    chars_fin    = int(max_chars * 0.45)

    inicio         = texto[:chars_inicio]
    fin            = texto[-chars_fin:]
    chars_omitidos = len(texto) - max_chars

    return (
        f"{inicio}\n\n"
        f"--- [ MAIIE: {chars_omitidos} CARACTERES OMITIDOS ] ---\n\n"
        f"{fin}"
    )


def extraer_puntos_criticos(reporte_auditoria: str) -> str:
    """
    Filtra solo bloqueadores críticos de un reporte de auditoría.

    Args:
        reporte_auditoria: Texto completo del reporte

    Returns:
        Solo las líneas con indicadores críticos
    """
    if not reporte_auditoria or not reporte_auditoria.strip():
        return "Sin reporte de auditoría disponible"

    patrones_criticos = [
        r"(?i)CRÍTICO.*",
        r"(?i)BLOQUEADOR.*",
        r"(?i)VULNERABILIDAD.*",
        r"(?i)ERROR.*",
        r"❌.*",
        r"🔴.*"
    ]

    encontrados = []
    lineas = reporte_auditoria.split('\n')

    for linea in lineas:
        if any(re.search(patron, linea) for patron in patrones_criticos):
            encontrados.append(linea.strip())

    if encontrados:
        return "\n".join(encontrados[:20])

    return "\n".join(lineas[:15])


# ============================================================================
# DIAGNÓSTICO DE SISTEMA
# ============================================================================

def generar_resumen_mision(datos: Dict) -> str:
    """
    Genera reporte visual de misión para el CEO.

    Args:
        datos: Diccionario con datos de la misión

    Returns:
        String formateado con el resumen
    """
    timestamp     = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    estado        = "ÉXITO ✅" if datos.get('aprobado') else "FALLO ❌"
    iteracion     = datos.get('iteracion', 0)
    archivo       = datos.get('archivo', 'N/A')
    observaciones = datos.get('observaciones', '')

    resumen = f"""
╔═══════════════════════════════════════════════════════════════╗
║              RESUMEN DE MISIÓN M.A.I.I.E.                     ║
╚═══════════════════════════════════════════════════════════════╝

📅 Fecha:       {timestamp}
🎯 Estado:      {estado}
🔄 Iteraciones: {iteracion}
📄 Archivo:     {archivo}
"""

    if observaciones:
        resumen += f"\n💬 Notas:       {observaciones}\n"

    resumen += "\n" + "─" * 65 + "\n"

    return resumen