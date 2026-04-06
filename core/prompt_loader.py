"""
MAIIE System V2 - Prompt Loader
Módulo: Carga de prompts desde archivos de configuración
Capa: Core
Versión: 2.0.0

CHANGELOG v2.0.0:
- ADD: Tracking de roles con fallback activo (_fallback_roles set)
- ADD: tiene_fallbacks() — permite al pipeline consultar si hay
       prompts críticos faltantes antes de ejecutar una misión
- ADD: Log de WARNING cuando se activa fallback (antes era ERROR
       silencioso sin consecuencias operativas)
- ADD: Arranque del sistema muestra resumen de prompts con fallback
       para que el operador lo vea inmediatamente en el log
- CHG: obtener_prompt() advierte en WARNING si el rol solicitado
       está en fallback — hace visible el problema en cada uso
"""

import os
import logging
from typing import Dict, Set
from core.prompts import MAIIERole

logger = logging.getLogger("MAIIE.PromptLoader")


class PromptLoader:
    """
    Carga prompts desde config/prompts/*.txt

    Roles críticos que bloquean la misión si están en fallback:
        ARCHITECT, ENGINEER_BASE, AUDITOR

    Roles no críticos (el sistema puede operar sin ellos):
        ENGINEER_SENIOR (opcional por defecto)
    """

    # Roles que NO deben operar en fallback bajo ninguna circunstancia.
    # Si alguno de estos está en fallback, el pipeline debería advertir
    # al operador antes de ejecutar la misión.
    ROLES_CRITICOS: Set[MAIIERole] = {
        MAIIERole.ARCHITECT,
        MAIIERole.ENGINEER_BASE,
        MAIIERole.AUDITOR,
    }

    def __init__(self):
        self.prompts_dir = os.path.join(
            os.path.dirname(__file__), "..", "config", "prompts"
        )
        self._cache: Dict[MAIIERole, str]  = {}
        self._fallback_roles: Set[MAIIERole] = set()

        self._cargar_todos()
        self._log_estado_inicial()

    # ----------------------------------------------------------

    def _cargar_todos(self):
        """Carga todos los prompts al inicio."""
        for role in MAIIERole:
            try:
                filename = f"{role.value.lower()}.txt"
                filepath = os.path.join(self.prompts_dir, filename)

                with open(filepath, "r", encoding="utf-8") as f:
                    contenido = f.read().strip()

                if not contenido:
                    raise ValueError(f"Archivo vacío: {filename}")

                self._cache[role] = contenido
                logger.info(f"✅ Prompt {role.value} cargado")

            except Exception as e:
                # Fallback activo — el rol operará con prompt mínimo
                self._fallback_roles.add(role)
                self._cache[role] = f"ACT AS {role.value}"

                if role in self.ROLES_CRITICOS:
                    logger.warning(
                        f"⚠️ FALLBACK ACTIVO en rol CRÍTICO {role.value}: {e}. "
                        f"El sistema usará prompt mínimo — calidad degradada."
                    )
                else:
                    logger.warning(
                        f"⚠️ FALLBACK ACTIVO en rol {role.value}: {e}. "
                        f"Rol no crítico — sistema operativo."
                    )

    # ----------------------------------------------------------

    def _log_estado_inicial(self):
        """
        Muestra resumen del estado de prompts al arrancar.
        Si hay fallbacks críticos, el operador lo ve inmediatamente.
        """
        if not self._fallback_roles:
            return

        criticos_en_fallback = self._fallback_roles & self.ROLES_CRITICOS
        no_criticos_en_fallback = self._fallback_roles - self.ROLES_CRITICOS

        if criticos_en_fallback:
            nombres = ", ".join(r.value for r in criticos_en_fallback)
            logger.warning(
                f"🚨 SISTEMA DEGRADADO — Roles críticos en fallback: {nombres}. "
                f"Revisa los archivos en config/prompts/ antes de ejecutar misiones."
            )

        if no_criticos_en_fallback:
            nombres = ", ".join(r.value for r in no_criticos_en_fallback)
            logger.warning(
                f"⚠️ Roles opcionales en fallback: {nombres}. "
                f"Sistema operativo con funcionalidad reducida."
            )

    # ----------------------------------------------------------

    def obtener_prompt(self, role: MAIIERole) -> str:
        """
        Retorna el prompt de un rol.

        Si el rol está en fallback, emite WARNING en cada uso
        para que el problema sea visible en los logs de misión.
        """
        if role in self._fallback_roles:
            logger.warning(
                f"⚠️ Rol {role.value} usando prompt de fallback mínimo. "
                f"Resultado puede ser de baja calidad."
            )

        return self._cache.get(role, f"ACT AS {role.value}")

    # ----------------------------------------------------------

    def tiene_fallbacks_criticos(self) -> bool:
        """
        Retorna True si algún rol crítico está usando fallback.

        El pipeline puede consultar esto antes de ejecutar una misión
        y decidir si abortar o advertir al operador.

        Ejemplo de uso en pipeline.py:
            if self.prompt_loader.tiene_fallbacks_criticos():
                logger.warning("⚠️ Misión ejecutada con prompts críticos en fallback")
        """
        return bool(self._fallback_roles & self.ROLES_CRITICOS)

    def roles_en_fallback(self) -> Set[MAIIERole]:
        """
        Retorna el conjunto de roles que están usando fallback.
        Útil para logging detallado en el pipeline.
        """
        return self._fallback_roles.copy()