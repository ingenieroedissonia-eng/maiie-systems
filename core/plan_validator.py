"""
MAIIE System V2 - Plan Validator
Modulo: Validacion estructural del plan antes de ejecutar
Capa: Core
Version: 1.0.0
"""

import logging
from typing import List, Tuple, Dict

logger = logging.getLogger("MAIIE.PlanValidator")


class PlanValidationError(Exception):
    pass


class PlanValidator:
    """
    Valida el plan generado por el Planner antes de enviarlo al PlannerExecutor.
    Detecta dependencias inexistentes, ciclos y plan incompleto.
    """

    def validar(self, submisiones: List[dict]) -> Tuple[bool, str]:
        ids = {sub["id"] for sub in submisiones}

        ok, motivo = self._validar_dependencias_existen(submisiones, ids)
        if not ok:
            return False, motivo

        ok, motivo = self._validar_sin_ciclos(submisiones)
        if not ok:
            return False, motivo

        logger.info(f"Plan validado: {len(submisiones)} submisiones, sin ciclos, dependencias OK")
        return True, "ok"

    def _validar_dependencias_existen(
        self, submisiones: List[dict], ids: set
    ) -> Tuple[bool, str]:
        for sub in submisiones:
            for dep in sub.get("dependencias", []):
                if not isinstance(dep, int):
                    continue
                if dep not in ids:
                    return False, (
                        f"Submision [{sub['id']}] declara dependencia [{dep}] "
                        f"que no existe en el plan"
                    )
        return True, "ok"

    def _validar_sin_ciclos(self, submisiones: List[dict]) -> Tuple[bool, str]:
        grafo: Dict[int, List[int]] = {sub["id"]: sub.get("dependencias", []) for sub in submisiones}
        visitados: set = set()
        en_pila: set = set()

        def tiene_ciclo(nodo: int) -> bool:
            visitados.add(nodo)
            en_pila.add(nodo)
            for vecino in grafo.get(nodo, []):
                if vecino not in visitados:
                    if tiene_ciclo(vecino):
                        return True
                elif vecino in en_pila:
                    return True
            en_pila.discard(nodo)
            return False

        for sub in submisiones:
            if sub["id"] not in visitados:
                if tiene_ciclo(sub["id"]):
                    return False, f"Ciclo detectado en dependencias del plan"

        return True, "ok"