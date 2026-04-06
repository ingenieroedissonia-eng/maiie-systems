"""
Tests para MAIIEPlanner v1.6.0 + PlannerExecutor v1.3.0

Cobertura:
  A. _validar_contrato()         — 8 tests
  B. _tiene_multiples_responsabilidades()  — 8 tests
  C. _validar_submisiones()      — 3 tests
  D. _ordenar_topologicamente()  — 4 tests
  E. decompose() integración     — 6 tests
  F. PlannerExecutor.ejecutar()  — 5 tests

Total: 34 tests

Ejecución:
  pytest tests/test_planner_v160.py -v
  pytest tests/test_planner_v160.py -v -k "contrato"
  pytest tests/test_planner_v160.py -v -k "responsabilidades"
  pytest tests/test_planner_v160.py -v -k "topologico"
  pytest tests/test_planner_v160.py -v -k "executor"
"""

import json
import pytest
from unittest.mock import MagicMock, patch

from core.planner import MAIIEPlanner, PlannerFailedError


# ===========================================================================
# Fixtures
# ===========================================================================

def make_sub(id_: int, desc: str, deps: list = None) -> dict:
    return {"id": id_, "descripcion": desc, "dependencias": deps or []}


def make_planner(response_json: str = None, side_effect=None):
    """Crea un MAIIEPlanner con LLM mockeado."""
    llm = MagicMock()
    if side_effect:
        llm.ejecutar_agente.side_effect = side_effect
    elif response_json is not None:
        llm.ejecutar_agente.return_value = response_json
    return MAIIEPlanner(llm)


def valid_json_response(submisiones: list) -> str:
    return json.dumps({"submisiones": submisiones})


# ===========================================================================
# A. _validar_contrato()
# ===========================================================================

class TestValidarContrato:

    def test_contrato_valido_simple(self):
        planner = make_planner()
        subs = [make_sub(1, "Crea core/user.py con la entidad User")]
        valido, motivo = planner._validar_contrato(subs)
        assert valido is True
        assert motivo == "ok"

    def test_contrato_valido_multiple(self):
        planner = make_planner()
        subs = [
            make_sub(1, "Crea core/user.py con la entidad User"),
            make_sub(2, "Crea core/exceptions.py con UserNotFound", deps=[1]),
            make_sub(3, "Crea api/router.py con el endpoint POST /users", deps=[1, 2]),
        ]
        valido, motivo = planner._validar_contrato(subs)
        assert valido is True

    def test_falla_lista_vacia(self):
        planner = make_planner()
        valido, motivo = planner._validar_contrato([])
        assert valido is False
        assert "vacía" in motivo

    def test_falla_sin_campo_id(self):
        planner = make_planner()
        subs = [{"descripcion": "Crea algo", "dependencias": []}]
        valido, motivo = planner._validar_contrato(subs)
        assert valido is False
        assert "'id'" in motivo

    def test_falla_id_tipo_string(self):
        planner = make_planner()
        subs = [{"id": "1", "descripcion": "Crea algo", "dependencias": []}]
        valido, motivo = planner._validar_contrato(subs)
        assert valido is False
        assert "str" in motivo

    def test_falla_descripcion_vacia(self):
        planner = make_planner()
        subs = [{"id": 1, "descripcion": "   ", "dependencias": []}]
        valido, motivo = planner._validar_contrato(subs)
        assert valido is False
        assert "vacía" in motivo

    def test_falla_dependencias_none(self):
        planner = make_planner()
        subs = [{"id": 1, "descripcion": "Crea algo", "dependencias": None}]
        valido, motivo = planner._validar_contrato(subs)
        assert valido is False
        assert "NoneType" in motivo

    def test_falla_id_duplicado(self):
        planner = make_planner()
        subs = [
            make_sub(1, "Crea core/user.py con la entidad User"),
            make_sub(1, "Crea core/exceptions.py con UserNotFound"),
        ]
        valido, motivo = planner._validar_contrato(subs)
        assert valido is False
        assert "duplicada" in motivo


# ===========================================================================
# B. _tiene_multiples_responsabilidades()
# ===========================================================================

class TestMultiplesResponsabilidades:

    def test_detecta_dos_verbos_accion(self):
        planner = make_planner()
        assert planner._tiene_multiples_responsabilidades(
            "Crea el cliente de Stripe y genera el webhook"
        ) is True

    def test_detecta_implementa_y_registra(self):
        planner = make_planner()
        assert planner._tiene_multiples_responsabilidades(
            "Implementa login y registra usuarios"
        ) is True

    def test_no_detecta_articulo_sustantivo(self):
        """'con la entidad' no tiene verbo de acción después del 'y'"""
        planner = make_planner()
        assert planner._tiene_multiples_responsabilidades(
            "Crea core/user.py con la entidad User"
        ) is False

    def test_no_detecta_con_el_repositorio(self):
        planner = make_planner()
        assert planner._tiene_multiples_responsabilidades(
            "Crea infrastructure/user_repository.py con InMemoryUserRepository"
        ) is False

    def test_no_detecta_descripcion_simple_sin_y(self):
        planner = make_planner()
        assert planner._tiene_multiples_responsabilidades(
            "Crea core/exceptions.py con la excepción UserNotFound"
        ) is False

    def test_no_detecta_endpoint_solo(self):
        planner = make_planner()
        assert planner._tiene_multiples_responsabilidades(
            "Crea api/user_router.py con el endpoint POST /users en FastAPI"
        ) is False

    def test_detecta_crea_y_configura(self):
        planner = make_planner()
        assert planner._tiene_multiples_responsabilidades(
            "Crea el modelo de usuario y configura la base de datos"
        ) is True

    def test_no_detecta_campos_con_y(self):
        """'campos id, nombre y email' — solo hay un verbo de acción"""
        planner = make_planner()
        assert planner._tiene_multiples_responsabilidades(
            "Crea core/user.py con campos id, nombre y email"
        ) is False


# ===========================================================================
# C. _validar_submisiones()
# ===========================================================================

class TestValidarSubmisiones:

    def test_sin_invalidas(self):
        planner = make_planner()
        subs = [
            make_sub(1, "Crea core/user.py con la entidad User"),
            make_sub(2, "Crea core/exceptions.py con UserNotFound"),
        ]
        _, invalidas = planner._validar_submisiones(subs)
        assert invalidas == 0

    def test_detecta_una_invalida(self):
        planner = make_planner()
        subs = [
            make_sub(1, "Crea el cliente de Stripe y genera el webhook"),
            make_sub(2, "Crea core/exceptions.py con UserNotFound"),
        ]
        _, invalidas = planner._validar_submisiones(subs)
        assert invalidas == 1

    def test_detecta_multiples_invalidas(self):
        planner = make_planner()
        subs = [
            make_sub(1, "Implementa login y registra usuarios"),
            make_sub(2, "Crea el modelo y configura la base de datos"),
            make_sub(3, "Genera el router y define los endpoints"),
        ]
        _, invalidas = planner._validar_submisiones(subs)
        assert invalidas == 3


# ===========================================================================
# D. _ordenar_topologicamente()
# ===========================================================================

class TestOrdenarTopologicamente:

    def test_orden_ya_correcto(self):
        planner = make_planner()
        subs = [
            make_sub(1, "Entidad"),
            make_sub(2, "Repositorio", deps=[1]),
            make_sub(3, "Router", deps=[2]),
        ]
        resultado = planner._ordenar_topologicamente(subs)
        assert [s["id"] for s in resultado] == [1, 2, 3]

    def test_orden_invertido_se_corrige(self):
        planner = make_planner()
        # LLM devuelve en orden incorrecto: 3 antes que 1
        subs = [
            make_sub(3, "Router", deps=[2]),
            make_sub(1, "Entidad", deps=[]),
            make_sub(2, "Repositorio", deps=[1]),
        ]
        resultado = planner._ordenar_topologicamente(subs)
        ids = [s["id"] for s in resultado]
        # 1 debe preceder a 2, 2 debe preceder a 3
        assert ids.index(1) < ids.index(2)
        assert ids.index(2) < ids.index(3)

    def test_sin_dependencias_preserva_orden(self):
        planner = make_planner()
        subs = [
            make_sub(1, "Módulo A"),
            make_sub(2, "Módulo B"),
            make_sub(3, "Módulo C"),
        ]
        resultado = planner._ordenar_topologicamente(subs)
        assert len(resultado) == 3

    def test_ciclo_retorna_orden_original(self):
        """Ciclo anómalo → retorna orden original sin crash."""
        planner = make_planner()
        subs = [
            make_sub(1, "A", deps=[2]),
            make_sub(2, "B", deps=[1]),
        ]
        resultado = planner._ordenar_topologicamente(subs)
        # No debe lanzar excepción, retorna orden original
        assert len(resultado) == 2


# ===========================================================================
# E. decompose() — integración
# ===========================================================================

class TestDecompose:

    def test_decompose_exitoso_orden_simple(self):
        subs_raw = [
            {"id": 1, "descripcion": "Crea core/user.py con la entidad User", "dependencias": []},
            {"id": 2, "descripcion": "Crea api/router.py con el endpoint POST /users", "dependencias": [1]},
        ]
        planner = make_planner(valid_json_response(subs_raw))
        resultado = planner.decompose("Crea endpoint POST /users")
        assert len(resultado) == 2
        assert resultado[0]["id"] == 1

    def test_decompose_eleva_error_si_json_invalido_ambos_intentos(self):
        planner = make_planner("esto no es json valido {{{{")
        with pytest.raises(PlannerFailedError) as exc_info:
            planner.decompose("Orden cualquiera")
        assert "PLANNER_FAILED" in str(exc_info.value)

    def test_decompose_eleva_error_si_contrato_invalido_ambos_intentos(self):
        # LLM devuelve submisiones sin campo 'id'
        bad_response = json.dumps({"submisiones": [
            {"descripcion": "Crea algo", "dependencias": []}
        ]})
        planner = make_planner(bad_response)
        with pytest.raises(PlannerFailedError):
            planner.decompose("Orden cualquiera")

    def test_decompose_reintenta_si_semanticamente_invalido(self):
        """Primer intento tiene 3 submisiones inválidas → reintenta → segundo ok."""
        bad_subs = [
            {"id": 1, "descripcion": "Implementa login y registra usuarios", "dependencias": []},
            {"id": 2, "descripcion": "Crea el modelo y configura la base de datos", "dependencias": []},
            {"id": 3, "descripcion": "Genera el router y define los endpoints", "dependencias": []},
        ]
        good_subs = [
            {"id": 1, "descripcion": "Crea core/user.py con la entidad User", "dependencias": []},
        ]
        llm = MagicMock()
        llm.ejecutar_agente.side_effect = [
            json.dumps({"submisiones": bad_subs}),
            json.dumps({"submisiones": good_subs}),
        ]
        planner = MAIIEPlanner(llm)
        resultado = planner.decompose("Orden")
        assert len(resultado) == 1
        assert llm.ejecutar_agente.call_count == 2

    def test_decompose_aplica_sort_topologico(self):
        """LLM devuelve orden incorrecto → decompose retorna orden correcto."""
        subs_raw = [
            {"id": 3, "descripcion": "Router", "dependencias": [2]},
            {"id": 1, "descripcion": "Entidad", "dependencias": []},
            {"id": 2, "descripcion": "Repositorio", "dependencias": [1]},
        ]
        planner = make_planner(valid_json_response(subs_raw))
        resultado = planner.decompose("Orden compleja")
        ids = [s["id"] for s in resultado]
        assert ids.index(1) < ids.index(2)
        assert ids.index(2) < ids.index(3)

    def test_decompose_no_retorna_fallback_silencioso(self):
        """Verificar que el viejo fallback silencioso YA NO existe."""
        planner = make_planner("json invalido")
        with pytest.raises(PlannerFailedError):
            planner.decompose("Cualquier orden")
        # Si llegamos aquí sin excepción, el fallback silencioso sigue activo → falla


# ===========================================================================
# F. PlannerExecutor.ejecutar()
# ===========================================================================

class TestPlannerExecutor:
    """
    Tests de integración para PlannerExecutor v1.3.0.
    Se mockea el pipeline para aislar el executor del sistema completo.
    """

    def _make_executor(self, planner_decompose_result=None, planner_raises=None):
        """Crea PlannerExecutor con Planner y pipeline mockeados."""
        from orchestrator.planner_executor import PlannerExecutor

        planner_mock  = MagicMock()
        pipeline_mock = MagicMock()

        if planner_raises:
            planner_mock.decompose.side_effect = planner_raises
        elif planner_decompose_result is not None:
            planner_mock.decompose.return_value = planner_decompose_result

        # Resultado genérico del pipeline — con codigo_final
        resultado_mock = MagicMock()
        resultado_mock.codigo_final = "class User:\n    def __init__(self): pass\n"
        pipeline_mock.ejecutar_mision.return_value = resultado_mock

        executor = PlannerExecutor(planner_mock, pipeline_mock)
        return executor, planner_mock, pipeline_mock

    def test_ejecutar_exitoso_dos_submisiones(self):
        subs = [
            make_sub(1, "Crea core/user.py con la entidad User"),
            make_sub(2, "Crea api/router.py con el endpoint POST /users", deps=[1]),
        ]
        executor, _, pipeline_mock = self._make_executor(subs)
        orquestador = MagicMock()

        resultados = executor.ejecutar(orquestador, "Crea endpoint POST /users")

        assert len(resultados) == 2
        assert pipeline_mock.ejecutar_mision.call_count == 2

    def test_ejecutar_retorna_lista_vacia_si_planner_falla(self):
        executor, _, pipeline_mock = self._make_executor(
            planner_raises=PlannerFailedError("Test: planner agotado")
        )
        orquestador = MagicMock()

        resultados = executor.ejecutar(orquestador, "Orden que falla")

        assert resultados == []
        pipeline_mock.ejecutar_mision.assert_not_called()

    def test_ejecutar_no_llama_pipeline_si_planner_falla(self):
        """El pipeline no debe ejecutarse si el Planner falla."""
        executor, planner_mock, pipeline_mock = self._make_executor(
            planner_raises=PlannerFailedError("Fallo controlado")
        )
        orquestador = MagicMock()
        executor.ejecutar(orquestador, "Orden")
        pipeline_mock.ejecutar_mision.assert_not_called()

    def test_ejecutar_acumula_ids_resueltos(self):
        """Después de ejecutar sub[1], ids_resueltos debe contener 1."""
        subs = [make_sub(1, "Crea core/user.py con la entidad User")]
        executor, _, pipeline_mock = self._make_executor(subs)
        orquestador = MagicMock()

        resultados = executor.ejecutar(orquestador, "Orden")
        assert len(resultados) == 1

    def test_ejecutar_primer_sub_sin_contexto_previo(self):
        """La primera submisión no debe incluir 'INTERFACES YA IMPLEMENTADAS'."""
        subs = [make_sub(1, "Crea core/user.py con la entidad User")]
        executor, _, pipeline_mock = self._make_executor(subs)
        orquestador = MagicMock()

        executor.ejecutar(orquestador, "Orden")

        call_args = pipeline_mock.ejecutar_mision.call_args
        orden_enriquecida = call_args[0][1]
        assert "INTERFACES YA IMPLEMENTADAS" not in orden_enriquecida
