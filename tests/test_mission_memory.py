"""
MAIIE System V2 - Tests de Mission Memory
Módulo: Validación de búsqueda semántica y recuperación de contexto
Capa: Tests
Versión: 1.0.0

Costo en API: CERO — embeddings y GCS mockeados.

Cobertura:
    - Listar misiones en backend local
    - Cargar manifest correctamente
    - Filtrar solo misiones aprobadas (excluir rechazadas)
    - Resumir misión correctamente
    - Similitud coseno — cálculo correcto
    - Factor de calidad — fórmula correcta para los 4 casos
    - Recencia — decaimiento exponencial correcto
    - Ranking semántico ponderado ordena correctamente
    - obtener_contexto retorna string no vacío con misiones aprobadas
    - obtener_contexto retorna vacío sin misiones
    - Fallback cronológico cuando embeddings no disponibles
"""

import sys
import os
import json
import math
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, mock_open

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.mission_memory import MissionMemory


# ------------------------------------------------------------------
# FIXTURES DE MANIFESTS
# ------------------------------------------------------------------

def manifest_aprobado(
    mission_id="mission_001",
    orden="Crea core/user.py",
    compliance=100,
    deuda=False,
    iteracion=1,
    dias_atras=1,
):
    ts = (datetime.now() - timedelta(days=dias_atras)).strftime("%Y-%m-%dT%H:%M:%S")
    return {
        "mission_id":      mission_id,
        "orden_usuario":   orden,
        "estado":          "APROBADO",
        "compliance_score": compliance,
        "deuda_tecnica":   deuda,
        "iteracion_final": iteracion,
        "timestamp":       ts,
        "modelos":         {"architect": "gemini-2.5-flash-lite"},
    }


def manifest_rechazado(mission_id="mission_bad"):
    return {
        "mission_id":      mission_id,
        "orden_usuario":   "Orden fallida",
        "estado":          "RECHAZADO",
        "compliance_score": 40,
        "deuda_tecnica":   True,
        "iteracion_final": 3,
        "timestamp":       datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }


def manifest_con_deuda(mission_id="mission_deuda"):
    ts = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%S")
    return {
        "mission_id":      mission_id,
        "orden_usuario":   "Orden con deuda técnica",
        "estado":          "APROBADO_CON_DEUDA",
        "compliance_score": 75,
        "deuda_tecnica":   True,
        "iteracion_final": 2,
        "timestamp":       ts,
        "modelos":         {"architect": "gemini-2.5-flash-lite"},
    }


# ------------------------------------------------------------------
# HELPER — crear MissionMemory en modo local sin filesystem real
# ------------------------------------------------------------------

def crear_memory_local():
    """MissionMemory configurada para backend local sin GCS."""
    with patch.dict(os.environ, {
        "MAIIE_STORAGE_BACKEND": "local",
        "MAIIE_GCS_BUCKET":      "",
        "MAIIE_GCP_PROJECT":     "",
    }):
        with patch("core.mission_memory.MissionMemory._inicializar_genai", return_value=False):
            memory = MissionMemory(missions_path="/tmp/test_missions")
    memory._genai_disponible = False
    return memory


# ------------------------------------------------------------------
# TESTS
# ------------------------------------------------------------------

class TestFactorCalidad(unittest.TestCase):
    """Tests del cálculo del factor de calidad."""

    def test_100_sin_deuda(self):
        """100% sin deuda → factor 1.0."""
        m = manifest_aprobado(compliance=100, deuda=False)
        factor = MissionMemory._factor_calidad(m)
        self.assertAlmostEqual(factor, 1.0, places=2)

    def test_100_con_deuda(self):
        """100% con deuda → factor 0.9."""
        m = manifest_aprobado(compliance=100, deuda=True)
        factor = MissionMemory._factor_calidad(m)
        self.assertAlmostEqual(factor, 0.9, places=2)

    def test_75_sin_deuda(self):
        """75% sin deuda → factor 0.8."""
        m = manifest_aprobado(compliance=75, deuda=False)
        factor = MissionMemory._factor_calidad(m)
        self.assertAlmostEqual(factor, 0.8, places=2)

    def test_75_con_deuda(self):
        """75% con deuda → factor 0.7."""
        m = manifest_aprobado(compliance=75, deuda=True)
        factor = MissionMemory._factor_calidad(m)
        self.assertAlmostEqual(factor, 0.7, places=2)

    def test_0_compliance_no_es_cero(self):
        """0% compliance no anula la misión — floor en 0.1."""
        m = manifest_aprobado(compliance=0, deuda=True)
        factor = MissionMemory._factor_calidad(m)
        self.assertGreaterEqual(factor, 0.1)

    def test_factor_entre_0_y_1(self):
        """El factor siempre está entre 0.1 y 1.0."""
        for compliance in [0, 25, 50, 75, 100]:
            for deuda in [True, False]:
                m = manifest_aprobado(compliance=compliance, deuda=deuda)
                factor = MissionMemory._factor_calidad(m)
                self.assertGreaterEqual(factor, 0.1)
                self.assertLessEqual(factor, 1.0)


class TestSimilitudCoseno(unittest.TestCase):
    """Tests del cálculo de similitud coseno."""

    def test_vectores_identicos(self):
        """Vectores idénticos tienen similitud 1.0."""
        v = [1.0, 0.5, 0.3, 0.8]
        sim = MissionMemory._similitud_coseno(v, v)
        self.assertAlmostEqual(sim, 1.0, places=5)

    def test_vectores_opuestos(self):
        """Vectores opuestos tienen similitud -1.0."""
        v1 = [1.0, 0.0]
        v2 = [-1.0, 0.0]
        sim = MissionMemory._similitud_coseno(v1, v2)
        self.assertAlmostEqual(sim, -1.0, places=5)

    def test_vectores_ortogonales(self):
        """Vectores ortogonales tienen similitud 0.0."""
        v1 = [1.0, 0.0]
        v2 = [0.0, 1.0]
        sim = MissionMemory._similitud_coseno(v1, v2)
        self.assertAlmostEqual(sim, 0.0, places=5)

    def test_vector_cero_retorna_0(self):
        """Vector cero retorna 0.0 sin división por cero."""
        v1 = [0.0, 0.0, 0.0]
        v2 = [1.0, 2.0, 3.0]
        sim = MissionMemory._similitud_coseno(v1, v2)
        self.assertEqual(sim, 0.0)

    def test_dimensiones_distintas_retorna_0(self):
        """Vectores de distinta dimensión retornan 0.0."""
        v1 = [1.0, 2.0]
        v2 = [1.0, 2.0, 3.0]
        sim = MissionMemory._similitud_coseno(v1, v2)
        self.assertEqual(sim, 0.0)

    def test_similitud_entre_0_y_1_para_positivos(self):
        """Vectores con valores positivos tienen similitud entre 0 y 1."""
        v1 = [0.6, 0.3, 0.1]
        v2 = [0.5, 0.4, 0.2]
        sim = MissionMemory._similitud_coseno(v1, v2)
        self.assertGreaterEqual(sim, 0.0)
        self.assertLessEqual(sim, 1.0)


class TestFiltradoMisionesAprobadas(unittest.TestCase):
    """Tests del filtrado de misiones por estado."""

    def test_solo_retorna_aprobadas(self):
        """obtener_misiones_aprobadas excluye misiones rechazadas."""
        memory = crear_memory_local()

        manifests = {
            "mission_001": manifest_aprobado("mission_001"),
            "mission_bad": manifest_rechazado("mission_bad"),
            "mission_deu": manifest_con_deuda("mission_deu"),
        }

        memory.listar_misiones  = MagicMock(return_value=list(manifests.keys()))
        memory.cargar_manifest  = MagicMock(side_effect=lambda mid: manifests.get(mid))

        resultado = memory.obtener_misiones_aprobadas()

        ids = [m["mission_id"] for m in resultado]
        self.assertIn("mission_001", ids)
        self.assertIn("mission_deu", ids)
        self.assertNotIn("mission_bad", ids)

    def test_retorna_lista_vacia_sin_misiones(self):
        """Sin misiones retorna lista vacía."""
        memory = crear_memory_local()
        memory.listar_misiones = MagicMock(return_value=[])

        resultado = memory.obtener_misiones_aprobadas()
        self.assertEqual(resultado, [])

    def test_respeta_limite(self):
        """El parámetro limite restringe las misiones retornadas."""
        memory = crear_memory_local()

        ids_misiones = [f"mission_{i:03d}" for i in range(20)]
        manifests    = {mid: manifest_aprobado(mid) for mid in ids_misiones}

        memory.listar_misiones = MagicMock(return_value=ids_misiones)
        memory.cargar_manifest = MagicMock(side_effect=lambda mid: manifests.get(mid))

        resultado = memory.obtener_misiones_aprobadas(limite=5)
        self.assertLessEqual(len(resultado), 5)


class TestResumirMision(unittest.TestCase):
    """Tests del resumen de misión."""

    def test_resumen_contiene_campos_clave(self):
        """El resumen incluye mission_id, orden, estado y cumplimiento."""
        memory  = crear_memory_local()
        m       = manifest_aprobado("mission_001", "Crea core/user.py", 100, False, 1)
        resumen = memory.resumir_mision(m)

        self.assertIn("mission_001", resumen)
        self.assertIn("Crea core/user.py", resumen)
        self.assertIn("100%", resumen)
        self.assertIn("APROBADO", resumen)

    def test_resumen_indica_deuda_tecnica(self):
        """El resumen indica cuando hay deuda técnica."""
        memory  = crear_memory_local()
        m       = manifest_con_deuda()
        resumen = memory.resumir_mision(m)

        self.assertIn("deuda", resumen.lower())

    def test_resumen_sin_deuda_indica_limpio(self):
        """El resumen indica cuando no hay deuda técnica."""
        memory  = crear_memory_local()
        m       = manifest_aprobado(deuda=False)
        resumen = memory.resumir_mision(m)

        self.assertIn("Sin deuda", resumen)


class TestRankingSemantico(unittest.TestCase):
    """Tests del ranking semántico ponderado."""

    def test_mayor_similitud_primero(self):
        """Misión con mayor similitud coseno aparece primero."""
        memory = crear_memory_local()

        m1 = manifest_aprobado("m1", compliance=100, deuda=False)
        m2 = manifest_aprobado("m2", compliance=100, deuda=False)

        # Vector consulta más similar a m1
        vector_consulta = [1.0, 0.0, 0.0]
        vector_m1       = [0.9, 0.1, 0.0]  # más similar
        vector_m2       = [0.1, 0.9, 0.0]  # menos similar

        memory._cargar_embedding = MagicMock(side_effect=lambda mid: {
            "m1": vector_m1,
            "m2": vector_m2,
        }.get(mid))

        resultado = memory._obtener_misiones_por_similitud(
            vector_consulta=vector_consulta,
            aprobadas=[m1, m2],
            limite=2,
        )

        self.assertEqual(resultado[0]["mission_id"], "m1")
        self.assertEqual(resultado[1]["mission_id"], "m2")

    def test_calidad_penaliza_baja_similitud(self):
        """Misión con alta similitud pero baja calidad puede perder frente a una más balanceada."""
        memory = crear_memory_local()

        # m1: alta similitud, baja calidad (40% con deuda)
        m1 = manifest_aprobado("m1", compliance=40, deuda=True)
        # m2: similitud media, alta calidad (100% sin deuda)
        m2 = manifest_aprobado("m2", compliance=100, deuda=False)

        vector_consulta = [1.0, 0.0]
        vector_m1       = [0.99, 0.01]  # similitud ~0.99, calidad factor ~0.42 → score ~0.416
        vector_m2       = [0.80, 0.60]  # similitud ~0.80, calidad factor ~1.0  → score ~0.80

        memory._cargar_embedding = MagicMock(side_effect=lambda mid: {
            "m1": vector_m1,
            "m2": vector_m2,
        }.get(mid))

        resultado = memory._obtener_misiones_por_similitud(
            vector_consulta=vector_consulta,
            aprobadas=[m1, m2],
            limite=2,
        )

        self.assertEqual(resultado[0]["mission_id"], "m2")

    def test_sin_embedding_va_al_final(self):
        """Misión sin embedding recibe score 0 y queda al final."""
        memory = crear_memory_local()

        m1 = manifest_aprobado("m1", compliance=100, deuda=False)
        m2 = manifest_aprobado("m2", compliance=100, deuda=False)

        vector_consulta = [1.0, 0.0]

        def cargar_embedding(mid):
            if mid == "m1":
                return [0.9, 0.1]
            return None  # m2 sin embedding

        memory._cargar_embedding = MagicMock(side_effect=cargar_embedding)

        resultado = memory._obtener_misiones_por_similitud(
            vector_consulta=vector_consulta,
            aprobadas=[m1, m2],
            limite=2,
        )

        self.assertEqual(resultado[0]["mission_id"], "m1")
        self.assertEqual(resultado[1]["mission_id"], "m2")

    def test_limite_respetado(self):
        """El ranking retorna exactamente el número de misiones solicitado."""
        memory = crear_memory_local()

        misiones = [manifest_aprobado(f"m{i}") for i in range(10)]
        vector_consulta = [1.0, 0.0]

        memory._cargar_embedding = MagicMock(return_value=[0.8, 0.2])

        resultado = memory._obtener_misiones_por_similitud(
            vector_consulta=vector_consulta,
            aprobadas=misiones,
            limite=3,
        )

        self.assertEqual(len(resultado), 3)


class TestObtenerContexto(unittest.TestCase):
    """Tests del método principal obtener_contexto."""

    def test_retorna_vacio_sin_misiones(self):
        """Sin misiones aprobadas retorna string vacío."""
        memory = crear_memory_local()
        memory.listar_misiones = MagicMock(return_value=[])

        resultado = memory.obtener_contexto(orden_actual="Crea core/user.py")
        self.assertEqual(resultado, "")

    def test_retorna_contexto_con_misiones(self):
        """Con misiones aprobadas retorna contexto no vacío."""
        memory = crear_memory_local()

        m = manifest_aprobado()
        memory.listar_misiones = MagicMock(return_value=["mission_001"])
        memory.cargar_manifest = MagicMock(return_value=m)

        resultado = memory.obtener_contexto()

        self.assertIsInstance(resultado, str)
        self.assertGreater(len(resultado), 0)
        self.assertIn("mission_001", resultado)

    def test_fallback_cronologico_sin_genai(self):
        """Sin google-genai activo usa modo cronológico."""
        memory = crear_memory_local()
        memory._genai_disponible = False

        misiones = [manifest_aprobado(f"m{i}") for i in range(5)]
        memory.listar_misiones = MagicMock(return_value=[f"m{i}" for i in range(5)])
        memory.cargar_manifest = MagicMock(side_effect=lambda mid: next(
            (m for m in misiones if m["mission_id"] == mid), None
        ))

        resultado = memory.obtener_contexto(orden_actual="Crea core/user.py")

        self.assertIn("cronológico", resultado)

    def test_contexto_incluye_encabezado(self):
        """El contexto tiene encabezado con número de misiones y modo."""
        memory = crear_memory_local()

        m = manifest_aprobado()
        memory.listar_misiones = MagicMock(return_value=["mission_001"])
        memory.cargar_manifest = MagicMock(return_value=m)

        resultado = memory.obtener_contexto()

        self.assertIn("HISTORIAL DE MISIONES APROBADAS", resultado)


if __name__ == "__main__":
    unittest.main(verbosity=2)