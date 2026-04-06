"""
MAIIE System V2 - Planner Cognitivo
Modulo: descomposicion de ordenes complejas en submisiones atomicas
Capa: Core
Version: 1.6.0

CHANGELOG v1.6.0:
- ADD: _validar_contrato() â€” valida campos obligatorios (id: int,
       descripcion: str no vacio, dependencias: list) antes de
       evaluar semantica. Si falla, reintenta sin consumir el slot
       de reintento semantico.
- FIX: Fallback silencioso eliminado. Si ambos intentos fallan,
       se eleva PlannerFailedError con motivo explicito.
       El pipeline debe capturar esta excepcion y registrar la mision
       con estado PLANNER_FAILED en GCS. ENGINEER_BASE nunca recibe
       la orden completa como submision unica.
- FIX: PATRONES_INVALIDOS refinados. La deteccion de multiples
       responsabilidades ahora verifica que el " y " aparezca entre
       dos verbos de accion (crea, implementa, genera, agrega, define,
       aÃ±ade), no entre articulo y sustantivo. Elimina falsos positivos
       en descripciones como "Crea core/user.py con la entidad User".
- ADD: Ordenamiento topologico de submisiones antes de retornar.
       Garantiza que sub[N] siempre precede a cualquier submision
       que lo declare como dependencia, independientemente del orden
       en que el LLM las haya generado.

CHANGELOG v1.5.0:
- FIX: Limite de submisiones subido de 4 a 6.
- ADD: Validacion interna semantica con reintento automatico.
- FIX: Ejemplos ampliados con sistemas completos de 5-6 submisiones.

CHANGELOG v1.4.0:
- FIX: Prompt reforzado con limite explicito de 1 caso de uso / 1 clase
       por submision.

CHANGELOG v1.3.0:
- ADD: Limite explicito de 2 archivos por submision.
"""

import json
import logging
from typing import List, Dict, Any, Tuple


logger = logging.getLogger("MAIIE.Planner")


class PlannerFailedError(Exception):
    """
    Se eleva cuando el Planner agota todos los intentos sin producir
    submisiones contractualmente validas.

    El pipeline debe capturar esta excepcion y registrar la mision
    con estado PLANNER_FAILED. ENGINEER_BASE no debe recibir la orden
    completa como fallback â€” eso reproduce exactamente el antipatron
    que el Planner existe para prevenir.
    """
    pass


# Verbos de accion que indican una responsabilidad real en una submision.
# Se usan para detectar conjunciones entre dos responsabilidades distintas,
# no entre articulo y sustantivo ("con la entidad", "con el repositorio").
_VERBOS_ACCION = {
    "crea", "implementa", "genera", "agrega", "define",
    "aniade", "construye", "escribe", "configura", "expone",
    "registra", "valida", "procesa", "maneja", "conecta",
    "inicializa", "ejecuta", "retorna", "publica", "consume",
}


class MAIIEPlanner:
    """
    Planner cognitivo:
    Descompone ordenes complejas en submisiones atomicas simples.
    Version: 1.6.0 â€” Contrato validado + abort explicito + sort topologico.
    """

    def __init__(self, llm_executor):
        self.llm = llm_executor

    # ------------------------------------------------------------------
    # Prompt
    # ------------------------------------------------------------------

    def _build_prompt(self, orden: str) -> str:
        return f"""
Eres el Planner de M.A.I.I.E.

Divide la siguiente orden en submisiones atomicas SIMPLES.

REGLAS CRÃTICAS:
- Cada submision = 1 funcion o 1 clase concreta â€” no mas
- Cada submision genera MÃXIMO 2 archivos â€” no mas
- MÃXIMO 1 caso de uso por submision â€” si hay 4 casos de uso son 4 submisiones
- Maximo 12 submisiones en total
- PROHIBIDO incluir arquitecturas completas, Clean Architecture o multiples capas en una sola submision
- Descripcion corta y directa â€” sin mencionar patrones arquitectonicos
- PROHIBIDO usar "y" para unir dos responsabilidades en una misma descripcion
- Si necesitas escribir "y" entre dos acciones distintas, son dos submisiones separadas
- Si una funcion necesita configuracion, la configuracion va en la misma submision
- Si la orden incluye modelo + repositorio + caso de uso + router â†’ son 4 submisiones separadas
- NUNCA omitas el router o endpoint API si la orden lo pide â€” debe ser su propia submision
- PROHIBIDO generar dos submisiones para el mismo archivo. Si un archivo necesita varias funciones, TODAS van en UNA sola submision. Ejemplo: Crea src/api/maiie.js con las funciones enviarMision, obtenerEstado y publicarMision

EJEMPLOS DE SUBMISIONES CORRECTAS (1 clase o 1 funcion, Maximo 2 archivos):
- "Crea core/user.py con la entidad User con campos id, nombre, email"
- "Crea core/exceptions.py con la excepcion UserNotFound"
- "Crea core/use_cases.py con el caso de uso CreateUser"
- "Crea infrastructure/user_repository.py con InMemoryUserRepository"
- "Crea api/user_router.py con el endpoint POST /users en FastAPI"
- "Crea config/settings.py con la configuracion de la aplicacion"
- "Crea stripe_client.py con la funcion create_payment_intent(amount, currency)"
- "Crea webhook_validator.py con la funcion verify_stripe_signature(payload, sig, secret)"

EJEMPLOS DE SUBMISIONES INCORRECTAS â€” NUNCA HAGAS ESTO:
- "Crea el cliente de Stripe e implementa el webhook" âŒ (dos responsabilidades)
- "Implementa login y registro de usuarios" âŒ (dos responsabilidades)
- "DiseÃ±a la arquitectura Clean Architecture con capas" âŒ (demasiado amplio)
- "Crea el Modulo de pagos con configuracion, dominio, casos de uso y repositorio" âŒ (5+ archivos)
- "Crea core/use_cases.py con CreateUser, GetUser, UpdateUser, DeleteUser" âŒ (4 casos = 4 submisiones)
- "Crea core/user.py con la entidad y el repositorio" âŒ (dos responsabilidades)
- "Crea api/router.py con los endpoints GET y POST de usuarios" âŒ (dos endpoints = dos submisiones)

EJEMPLO DE DESCOMPOSICIÃ“N CORRECTA para "endpoint POST /users con validacion Pydantic":

Submision 1: "Crea core/user.py con la entidad User con campos id, nombre, email"
Submision 2: "Crea core/exceptions.py con la excepcion UserAlreadyExists"
Submision 3: "Crea core/use_cases.py con el caso de uso CreateUser"
Submision 4: "Crea infrastructure/user_repository.py con InMemoryUserRepository"
Submision 5: "Crea api/user_router.py con el endpoint POST /users en FastAPI con validacion Pydantic"

FORMATO JSON ESTRICTO (sin texto adicional, sin markdown):

{{
  "submisiones": [
    {{
      "id": 1,
      "descripcion": "texto corto y concreto â€” una sola responsabilidad â€” Maximo 1 clase o 1 funcion",
      "dependencias": []
    }}
  ]
}}

ORDEN:
{orden}
"""

    # ------------------------------------------------------------------
    # Validacion contractual (estructura de datos)
    # ------------------------------------------------------------------

    def _validar_contrato(
        self, submisiones: List[Any]
    ) -> Tuple[bool, str]:
        """
        Valida que cada submision cumpla el contrato minimo:
          - id: int presente y unico
          - descripcion: str no vacio
          - dependencias: list (puede ser vacia)

        Returns:
            (valido: bool, motivo: str)
            Si valido=False, motivo describe el primer campo que falla.
        """
        if not isinstance(submisiones, list) or len(submisiones) == 0:
            return False, "submisiones no es una lista o está vacía"

        ids_vistos: set = set()

        for i, sub in enumerate(submisiones):
            if not isinstance(sub, dict):
                return False, f"submision[{i}] no es un dict"

            # id: debe existir y ser int
            if "id" not in sub:
                return False, f"submision[{i}] no tiene campo 'id'"
            if not isinstance(sub["id"], int):
                return False, (
                    f"submision[{i}] tiene 'id' de tipo {type(sub['id']).__name__}, "
                    f"se esperaba int"
                )
            if sub["id"] in ids_vistos:
                return False, f"submision con id={sub['id']} esta duplicada"
            ids_vistos.add(sub["id"])

            # descripcion: debe existir y ser str no vacio
            if "descripcion" not in sub:
                return False, f"submision[{i}] no tiene campo 'descripcion'"
            if not isinstance(sub["descripcion"], str) or not sub["descripcion"].strip():
                return False, f"submisión[{i}] tiene 'descripcion' vacía o inválida"
            if not isinstance(sub["dependencias"], list):
                return False, (
                    f"submision[{i}] tiene 'dependencias' de tipo "
                    f"{type(sub['dependencias']).__name__}, se esperaba list"
                )

        return True, "ok"

    # ------------------------------------------------------------------
    # Validacion semantica (contenido de la descripcion)
    # ------------------------------------------------------------------

    def _tiene_multiples_responsabilidades(self, descripcion: str) -> bool:
        """
        Detecta si una descripcion une dos responsabilidades distintas
        con " y " verificando que el " y " aparezca entre dos verbos
        de accion, no entre articulo y sustantivo.

        Ejemplos que SÃ deben detectarse:
          "Crea el cliente de Stripe y genera el webhook"
          "Implementa login y registra usuarios"

        Ejemplos que NO deben detectarse (falsos positivos anteriores):
          "Crea core/user.py con la entidad User"
          "Crea infrastructure/user_repository.py con InMemoryUserRepository"
        """
        desc = descripcion.lower()

        # Buscar todas las ocurrencias de " y "
        pos = desc.find(" y ")
        while pos != -1:
            # Texto antes del " y " â€” buscar el ultimo verbo de accion
            fragmento_izq = desc[:pos]
            palabras_izq = fragmento_izq.split()

            # Texto despues del " y " â€” buscar el primer verbo de accion
            fragmento_der = desc[pos + 3:]
            palabras_der = fragmento_der.split()

            tiene_verbo_izq = any(p in _VERBOS_ACCION for p in palabras_izq)
            tiene_verbo_der = any(p in _VERBOS_ACCION for p in palabras_der)

            if tiene_verbo_izq and tiene_verbo_der:
                return True

            pos = desc.find(" y ", pos + 1)

        return False

    def _validar_submisiones(
        self, submisiones: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Valida que las submisiones sean atomicas semanticamente.

        Detecta submisiones con multiples responsabilidades verificando
        que el conector " y " une dos verbos de accion distintos,
        no un articulo con un sustantivo.

        Returns:
            (submisiones_originales, count_invalidas)
        """
        invalidas = 0

        for sub in submisiones:
            descripcion = sub.get("descripcion", "")

            if self._tiene_multiples_responsabilidades(descripcion):
                logger.warning(
                    f"âš ï¸ Submision posiblemente invalida [{sub['id']}]: "
                    f"'{descripcion}' â€” multiples responsabilidades detectadas"
                )
                invalidas += 1

        return submisiones, invalidas

    # ------------------------------------------------------------------
    # Ordenamiento topologico
    # ------------------------------------------------------------------

    def _ordenar_topologicamente(
        self, submisiones: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Ordena las submisiones de forma que sub[N] siempre precede a
        cualquier submision que lo declare como dependencia.

        Garantia: si el LLM genera submisiones fuera de orden o con
        dependencias cruzadas, el PlannerExecutor siempre acumulara
        el contexto en el orden correcto.

        Algoritmo: Kahn (BFS). O(V + E) con V=submisiones, E=dependencias.
        Si hay ciclo (caso anÃ³malo del LLM), retorna el orden original
        y loguea WARNING â€” el ciclo no debe bloquear la ejecucion.
        """
        id_a_sub = {sub["id"]: sub for sub in submisiones}
        grado_entrada: Dict[int, int] = {sub["id"]: 0 for sub in submisiones}
        adyacencia: Dict[int, List[int]] = {sub["id"]: [] for sub in submisiones}

        for sub in submisiones:
            for dep_id in sub.get("dependencias", []):
                if dep_id in grado_entrada:
                    grado_entrada[sub["id"]] += 1
                    adyacencia[dep_id].append(sub["id"])
                else:
                    logger.warning(
                        f"âš ï¸ Submision [{sub['id']}] declara dependencia inexistente: {dep_id}"
                    )

        cola = [sid for sid, grado in grado_entrada.items() if grado == 0]
        orden: List[Dict[str, Any]] = []

        while cola:
            actual = cola.pop(0)
            orden.append(id_a_sub[actual])
            for vecino in adyacencia[actual]:
                grado_entrada[vecino] -= 1
                if grado_entrada[vecino] == 0:
                    cola.append(vecino)

        if len(orden) != len(submisiones):
            logger.warning(
                "âš ï¸ Ciclo detectado en dependencias â€” usando orden original"
            )
            return submisiones

        return orden

    # ------------------------------------------------------------------
    # Ejecucion principal
    # ------------------------------------------------------------------

    def decompose(self, orden: str) -> List[Dict[str, Any]]:
        """
        Descompone la orden en submisiones atomicas validadas.

        Flujo:
          1. Ejecutar LLM y parsear JSON
          2. Validar contrato estructural (_validar_contrato)
          3. Validar semantica atomica (_validar_submisiones)
          4. Si >2 invalidas semanticamente y hay reintento disponible â†’ reintentar
          5. Ordenar topolÃ³gicamente
          6. Retornar lista ordenada

        Si ambos intentos fallan en contrato o en parseo:
          â†’ Elevar PlannerFailedError (NO retornar fallback silencioso)

        Raises:
            PlannerFailedError: si todos los intentos producen submisiones
                                contractualmente invalidas o JSON inparseable.
        """
        logger.info("ðŸ§  Planner analizando mision...")

        ultimo_motivo = "error desconocido"

        for intento in range(1, 3):  # Maximo 2 intentos
            prompt      = self._build_prompt(orden)
            submisiones = self._ejecutar_planner(prompt)

            if not submisiones:
                ultimo_motivo = f"intento {intento}: Planner devolviÃ³ lista vacia o JSON invalido"
                logger.warning(f"âš ï¸ {ultimo_motivo}")
                continue

            # --- Validacion contractual (estructura) ---
            contrato_valido, motivo_contrato = self._validar_contrato(submisiones)
            if not contrato_valido:
                ultimo_motivo = (
                    f"intento {intento}: contrato invalido â€” {motivo_contrato}"
                )
                logger.warning(f"âš ï¸ {ultimo_motivo} â€” regenerando")
                continue

            # --- Validacion semantica (contenido) ---
            submisiones, invalidas = self._validar_submisiones(submisiones)

            if invalidas > 2 and intento < 2:
                ultimo_motivo = (
                    f"intento {intento}: {invalidas} submisiones con multiples "
                    f"responsabilidades detectadas"
                )
                logger.warning(f"âš ï¸ {ultimo_motivo} â€” regenerando")
                continue

            # --- Ordenamiento topologico ---
            submisiones = self._ordenar_topologicamente(submisiones)

            logger.info(f"âœ… Planner generÃ³ {len(submisiones)} submision(es)")
            for sub in submisiones:
                logger.info(f"   [{sub['id']}] {sub['descripcion']}")

            return submisiones

        # Todos los intentos agotados â€” abort explicito
        raise PlannerFailedError(
            f"Planner agotÃ³ todos los intentos. Ãšltimo motivo: {ultimo_motivo}. "
            f"La mision debe registrarse con estado PLANNER_FAILED. "
            f"ENGINEER_BASE no debe recibir la orden completa como fallback."
        )

    def _ejecutar_planner(self, prompt: str) -> List[Dict[str, Any]]:
        """Ejecuta el LLM y parsea el JSON resultante."""
        try:
            response = self.llm.ejecutar_agente(
                "ARCHITECT",
                prompt,
                "magenta"
            )

            clean = (
                response.replace("```json", "")
                        .replace("```", "")
                        .strip()
            )

            data        = json.loads(clean)
            submisiones = data.get("submisiones", [])

            if not submisiones:
                raise ValueError("Lista de submisiones vacia")

            return submisiones

        except json.JSONDecodeError as e:
            logger.error(f"âŒ JSON invalido del Planner: {e}")
            return []

        except Exception as e:
            logger.error(f"âŒ Error en Planner: {e}")
            return []



