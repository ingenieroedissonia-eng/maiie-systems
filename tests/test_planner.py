"""
MAIIE System V2 - Tests del Planner
Módulo: Validación de descomposición atómica de órdenes
Capa: Tests
Versión: 1.0.0

Costo en API: CERO — LLM mockeado.

Cobertura:
    - Descomposición correcta de orden simple
    - Descomposición de orden compleja en 5-6 submisiones
    - Fallback a orden única cuando el LLM retorna JSON inválido
    - Fallback a orden única cuando el LLM retorna lista vacía
    - Validación interna detecta submisiones con múltiples responsabilidades
    - Reintento automático cuando hay más de 2 submisiones inválidas
    - Límite de 6 submisiones respetado
    - Dependencias parseadas correctamente
"""

import sys
import os
import json
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.planner import MAIIEPlanner


# ------------------------------------------------------------------
# HELPER — crear LLM mock con respuesta JSON configurable
# ------------------------------------------------------------------

def crear_llm_mock(submisiones: list) -> MagicMock:
    """LLM mock que retorna JSON válido con las submisiones dadas."""
    llm = MagicMock()
    payload = json.dumps({"submisiones": submisiones}, ensure_ascii=False)
    llm.ejecutar_agente.return_value = payload
    return llm


def crear_llm_mock_invalido(respuesta: str) -> MagicMock:
    """LLM mock que retorna texto no parseable como JSON."""
    llm = MagicMock()
    llm.ejecutar_agente.return_value = respuesta
    return llm


# ------------------------------------------------------------------
# SUBMISIONES DE EJEMPLO
# ------------------------------------------------------------------

SUBMISIONES_SIMPLES = [
    {"id": 1, "descripcion": "Crea core/user.py con la entidad User", "dependencias": []},
]

SUBMISIONES_POST_USERS = [
    {"id": 1, "descripcion": "Crea core/user.py con la entidad User con campos id, nombre, email", "dependencias": []},
    {"id": 2, "descripcion": "Crea core/exceptions.py con la excepción UserAlreadyExists", "dependencias": [1]},
    {"id": 3, "descripcion": "Crea core/use_cases.py con el caso de uso CreateUser", "dependencias": [1, 2]},
    {"id": 4, "descripcion": "Crea infrastructure/user_repository.py con InMemoryUserRepository", "dependencias": [1]},
    {"id": 5, "descripcion": "Crea api/user_router.py con el endpoint POST /users en FastAPI con validación Pydantic", "dependencias": [3, 4]},
]

SUBMISIONES_CON_INVALIDAS = [
    {"id": 1, "descripcion": "Crea core/user.py con la entidad User", "dependencias": []},
    {"id": 2, "descripcion": "Crea core/exceptions.py y el repositorio de usuarios", "dependencias": []},  # inválida
    {"id": 3, "descripcion": "Crea core/use_cases.py y la configuración de la app", "dependencias": []},  # inválida
    {"id": 4, "descripcion": "Crea el router y el schema Pydantic", "dependencias": []},                  # inválida
]

SUBMISIONES_6_MAXIMO = [
    {"id": i, "descripcion": f"Crea modulo_{i}.py con la clase Modulo{i}", "dependencias": []}
    for i in range(1, 7)
]


# ------------------------------------------------------------------
# TESTS
# ------------------------------------------------------------------

class TestPlannerDescomposicion(unittest.TestCase):
    """Tests de descomposición de órdenes en submisiones atómicas."""

    def test_descomposicion_orden_simple(self):
        """Orden simple produce una sola submisión correcta."""
        planner = MAIIEPlanner(crear_llm_mock(SUBMISIONES_SIMPLES))
        resultado = planner.decompose("Crea core/user.py con la entidad User")

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["id"], 1)
        self.assertIn("user.py", resultado[0]["descripcion"].lower())

    def test_descomposicion_post_users_5_submisiones(self):
        """Orden POST /users se descompone en 5 submisiones atómicas."""
        planner = MAIIEPlanner(crear_llm_mock(SUBMISIONES_POST_USERS))
        resultado = planner.decompose(
            "Crea un endpoint POST /users con validación Pydantic en FastAPI"
        )

        self.assertEqual(len(resultado), 5)

        # Verificar que el router esté incluido
        descripciones = [s["descripcion"].lower() for s in resultado]
        tiene_router = any("router" in d or "endpoint" in d for d in descripciones)
        self.assertTrue(tiene_router, "El router/endpoint debe estar en las submisiones")

    def test_ids_son_secuenciales(self):
        """Los IDs de las submisiones son secuenciales desde 1."""
        planner = MAIIEPlanner(crear_llm_mock(SUBMISIONES_POST_USERS))
        resultado = planner.decompose("Orden de prueba")

        ids = [s["id"] for s in resultado]
        self.assertEqual(ids, list(range(1, len(ids) + 1)))

    def test_dependencias_parseadas(self):
        """Las dependencias entre submisiones se parsean correctamente."""
        planner = MAIIEPlanner(crear_llm_mock(SUBMISIONES_POST_USERS))
        resultado = planner.decompose("Orden de prueba")

        # Submisión 3 depende de 1 y 2
        sub_3 = next(s for s in resultado if s["id"] == 3)
        self.assertIn(1, sub_3["dependencias"])
        self.assertIn(2, sub_3["dependencias"])

    def test_limite_6_submisiones(self):
        """El sistema acepta hasta 6 submisiones."""
        planner = MAIIEPlanner(crear_llm_mock(SUBMISIONES_6_MAXIMO))
        resultado = planner.decompose("Orden compleja con 6 módulos")

        self.assertEqual(len(resultado), 6)


class TestPlannerFallback(unittest.TestCase):
    """Tests del comportamiento de fallback ante fallos del LLM."""

    def test_json_invalido_retorna_orden_completa(self):
        """JSON inválido del LLM produce fallback a orden única."""
        planner = MAIIEPlanner(crear_llm_mock_invalido("esto no es JSON válido"))
        orden   = "Crea core/user.py"
        resultado = planner.decompose(orden)

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["descripcion"], orden)
        self.assertEqual(resultado[0]["id"], 1)

    def test_lista_vacia_retorna_orden_completa(self):
        """Lista vacía del LLM produce fallback a orden única."""
        llm = MagicMock()
        llm.ejecutar_agente.return_value = json.dumps({"submisiones": []})
        planner   = MAIIEPlanner(llm)
        orden     = "Crea core/user.py"
        resultado = planner.decompose(orden)

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["descripcion"], orden)

    def test_respuesta_vacia_retorna_orden_completa(self):
        """Respuesta vacía del LLM produce fallback a orden única."""
        planner   = MAIIEPlanner(crear_llm_mock_invalido(""))
        orden     = "Crea core/user.py"
        resultado = planner.decompose(orden)

        self.assertEqual(len(resultado), 1)

    def test_json_con_markdown_se_parsea(self):
        """JSON envuelto en bloques markdown se parsea correctamente."""
        payload = "```json\n" + json.dumps({"submisiones": SUBMISIONES_SIMPLES}) + "\n```"
        planner = MAIIEPlanner(crear_llm_mock_invalido(payload))
        resultado = planner.decompose("Crea core/user.py")

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["id"], 1)


class TestPlannerValidacionInterna(unittest.TestCase):
    """Tests de la validación interna de submisiones atómicas."""

    def test_detecta_submision_con_y(self):
        """Submisión con 'y el' entre responsabilidades es detectada como inválida."""
        planner = MAIIEPlanner(MagicMock())
        submisiones = [
            {"id": 1, "descripcion": "Crea core/user.py y el repositorio", "dependencias": []},
        ]
        _, invalidas = planner._validar_submisiones(submisiones)
        self.assertEqual(invalidas, 1)

    def test_submision_valida_no_es_marcada(self):
        """Submisión atómica correcta no es marcada como inválida."""
        planner = MAIIEPlanner(MagicMock())
        submisiones = [
            {"id": 1, "descripcion": "Crea core/user.py con la entidad User", "dependencias": []},
        ]
        _, invalidas = planner._validar_submisiones(submisiones)
        self.assertEqual(invalidas, 0)

    def test_multiples_invalidas_son_contadas(self):
        """Múltiples submisiones inválidas son contadas correctamente."""
        planner = MAIIEPlanner(MagicMock())
        _, invalidas = planner._validar_submisiones(SUBMISIONES_CON_INVALIDAS)
        self.assertGreaterEqual(invalidas, 2)

    def test_reintento_cuando_muchas_invalidas(self):
        """Planner reintenta cuando hay más de 2 submisiones inválidas."""
        call_count = {"n": 0}

        def ejecutar_agente(rol, prompt, color):
            call_count["n"] += 1
            if call_count["n"] == 1:
                # Primera llamada: submisiones inválidas
                return json.dumps({"submisiones": SUBMISIONES_CON_INVALIDAS})
            else:
                # Segunda llamada: submisiones válidas
                return json.dumps({"submisiones": SUBMISIONES_SIMPLES})

        llm = MagicMock()
        llm.ejecutar_agente.side_effect = ejecutar_agente
        planner   = MAIIEPlanner(llm)
        resultado = planner.decompose("Orden de prueba")

        # Debe haber llamado al LLM dos veces
        self.assertEqual(call_count["n"], 2)
        # Resultado final debe ser las submisiones válidas
        self.assertEqual(len(resultado), 1)

    def test_sin_reintento_cuando_pocas_invalidas(self):
        """Planner NO reintenta con 1-2 submisiones inválidas — las acepta."""
        llm = MagicMock()
        submisiones_con_1_invalida = [
            {"id": 1, "descripcion": "Crea core/user.py con la entidad User", "dependencias": []},
            {"id": 2, "descripcion": "Crea core/exceptions.py y el logger", "dependencias": []},  # 1 inválida
        ]
        llm.ejecutar_agente.return_value = json.dumps(
            {"submisiones": submisiones_con_1_invalida}
        )
        planner   = MAIIEPlanner(llm)
        resultado = planner.decompose("Orden de prueba")

        # Solo 1 llamada — no reintentó
        llm.ejecutar_agente.assert_called_once()
        self.assertEqual(len(resultado), 2)


class TestPlannerEstructura(unittest.TestCase):
    """Tests de estructura y contrato del Planner."""

    def test_cada_submision_tiene_id(self):
        """Cada submisión tiene campo id."""
        planner = MAIIEPlanner(crear_llm_mock(SUBMISIONES_POST_USERS))
        resultado = planner.decompose("Orden de prueba")

        for sub in resultado:
            self.assertIn("id", sub)

    def test_cada_submision_tiene_descripcion(self):
        """Cada submisión tiene campo descripcion."""
        planner = MAIIEPlanner(crear_llm_mock(SUBMISIONES_POST_USERS))
        resultado = planner.decompose("Orden de prueba")

        for sub in resultado:
            self.assertIn("descripcion", sub)
            self.assertTrue(len(sub["descripcion"]) > 0)

    def test_cada_submision_tiene_dependencias(self):
        """Cada submisión tiene campo dependencias como lista."""
        planner = MAIIEPlanner(crear_llm_mock(SUBMISIONES_POST_USERS))
        resultado = planner.decompose("Orden de prueba")

        for sub in resultado:
            self.assertIn("dependencias", sub)
            self.assertIsInstance(sub["dependencias"], list)

    def test_llm_es_llamado_con_orden_en_prompt(self):
        """El LLM recibe un prompt que contiene la orden original."""
        llm = crear_llm_mock(SUBMISIONES_SIMPLES)
        planner = MAIIEPlanner(llm)
        orden   = "Orden específica de prueba XYZ123"
        planner.decompose(orden)

        prompt_usado = llm.ejecutar_agente.call_args[0][1]
        self.assertIn(orden, prompt_usado)


if __name__ == "__main__":
    unittest.main(verbosity=2)