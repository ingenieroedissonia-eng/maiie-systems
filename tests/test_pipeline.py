"""
MAIIE System V2 - Tests del Pipeline
Módulo: Validación del ciclo ARCHITECT → ENGINEER_BASE → AUDITOR
Capa: Tests
Versión: 1.0.2

CHANGELOG v1.0.2:
- FIX: Fixture CODIGO_CON_TODO corregido — el TODO estaba en un comentario #
       lo cual es correcto según el diseño del validador (Registro 50).
       El fixture ahora tiene el TODO en código ejecutable real (asignación
       de variable) para que el validador lo detecte correctamente.
       Causa raíz: el test verificaba comportamiento incorrecto — el validador
       está diseñado para ignorar TODOs en comentarios # y docstrings.

CHANGELOG v1.0.1:
- FIX: Fixture CODIGO_CON_TODO ampliado para superar el filtro de bloques
       mínimos del validador interno y llegar al check de TODOs.

Costo en API: CERO — todos los agentes son mocks.
Costo en GCS: CERO — storage mockeado en memoria.

Cobertura:
    - Ciclo completo aprobado en iteración 1
    - Ciclo completo aprobado en iteración 2 tras rechazo inicial
    - Bloqueo por TODOs en código ejecutable
    - Bloqueo por código vacío
    - Límite de iteraciones alcanzado sin aprobación
    - LearningEngine ausente no interrumpe el pipeline
    - Detección correcta de compliance_score desde reporte del Auditor
    - Verificación de certificación: APROBADO / APROBADO CON DEUDA / RECHAZADO
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from orchestrator.pipeline import IterativePipeline, PipelineResult, EstadoCertificacion


# ------------------------------------------------------------------
# CÓDIGO DE EJEMPLO PARA MOCKS
# ------------------------------------------------------------------

CODIGO_VALIDO = '''
# File: core/user.py
"""Módulo de usuario."""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class User:
    """Entidad de usuario del dominio."""

    id: str
    nombre: str
    email: str

    def validar(self) -> bool:
        """Valida que el usuario tenga datos mínimos requeridos."""
        if not self.email or "@" not in self.email:
            raise ValueError(f"Email inválido: {self.email}")
        if not self.nombre or len(self.nombre.strip()) < 2:
            raise ValueError("Nombre demasiado corto")
        return True

    def to_dict(self) -> dict:
        """Serializa el usuario a diccionario."""
        return {
            "id":     self.id,
            "nombre": self.nombre,
            "email":  self.email,
        }
'''

# v1.0.2: TODO en código ejecutable real (asignación de variable)
# El validador detecta TODOs en líneas ejecutables, no en comentarios #
CODIGO_CON_TODO = '''
# File: core/user.py
"""
Módulo de usuario del dominio.

Contiene la entidad principal User con sus métodos de negocio.
"""

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class User:
    """Entidad de usuario del dominio."""

    id: str
    nombre: str
    email: str
    activo: bool = True

    def validar(self) -> bool:
        """Valida que el usuario tenga datos mínimos requeridos."""
        resultado = TODO
        return resultado

    def desactivar(self) -> None:
        """Desactiva el usuario en el sistema."""
        self.activo = False
        logger.info(f"Usuario desactivado: {self.id}")

    def to_dict(self) -> dict:
        """Serializa el usuario a diccionario para persistencia."""
        return {
            "id":     self.id,
            "nombre": self.nombre,
            "email":  self.email,
            "activo": self.activo,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Reconstruye un usuario desde diccionario."""
        return cls(
            id=data["id"],
            nombre=data["nombre"],
            email=data["email"],
            activo=data.get("activo", True),
        )
'''

CODIGO_VACIO = ""

REPORTE_APROBADO = """
ITERACIÓN: 1
CUMPLIMIENTO: 100%
ESTADO: APROBADO

EVALUACIÓN DoD:
Ejecutabilidad: SÍ
Estructura: SÍ
Robustez: SÍ
Comprensibilidad: SÍ
Production-ready: SÍ

El código cumple todos los estándares de producción.
"""

REPORTE_APROBADO_CON_DEUDA = """
ITERACIÓN: 1
CUMPLIMIENTO: 80%
ESTADO: APROBADO CON DEUDA

EVALUACIÓN DoD:
Ejecutabilidad: SÍ
Estructura: SÍ
Robustez: NO
Comprensibilidad: SÍ
Production-ready: NO

El código es funcional pero tiene deuda técnica menor.
"""

REPORTE_RECHAZADO = """
ITERACIÓN: 1
CUMPLIMIENTO: 40%
ESTADO: RECHAZADO

EVALUACIÓN DoD:
Ejecutabilidad: NO
Estructura: SÍ
Robustez: NO
Comprensibilidad: SÍ
Production-ready: NO

- ARCHIVO FALTANTE CRÍTICO: infrastructure/user_repository.py
"""


# ------------------------------------------------------------------
# ORQUESTADOR MOCK
# ------------------------------------------------------------------

def crear_orquestador_mock(
    plan="Plan arquitectónico de prueba.",
    codigo=CODIGO_VALIDO,
    reporte=REPORTE_APROBADO,
    codigos_por_ciclo=None,
    reportes_por_ciclo=None,
):
    orquestador = MagicMock()
    call_count  = {"n": 0}

    def ejecutar_agente(rol, prompt, color):
        if rol == "ARCHITECT":
            return plan
        elif rol == "ENGINEER_BASE":
            if codigos_por_ciclo:
                idx = min(call_count["n"], len(codigos_por_ciclo) - 1)
                result = codigos_por_ciclo[idx]
                call_count["n"] += 1
                return result
            return codigo
        elif rol == "AUDITOR":
            if reportes_por_ciclo:
                idx = min(call_count["n"] - 1, len(reportes_por_ciclo) - 1)
                return reportes_por_ciclo[idx]
            return reporte
        return ""

    orquestador.ejecutar_agente.side_effect = ejecutar_agente
    return orquestador


# ------------------------------------------------------------------
# FIXTURES DE PIPELINE
# ------------------------------------------------------------------

def crear_pipeline_mockeado(max_iteraciones=3):
    with patch("orchestrator.pipeline.MissionMemory") as MockMemory, \
         patch("orchestrator.pipeline.ArtifactManager") as MockArtifacts, \
         patch("orchestrator.pipeline.RepoGenerator") as MockRepo, \
         patch("orchestrator.pipeline.LearningEngine") as MockLearning, \
         patch("orchestrator.pipeline.guardar_artefacto"):

        mock_memory = MagicMock()
        mock_memory.obtener_contexto.return_value = "Contexto de misiones previas simulado."
        mock_memory.obtener_misiones_aprobadas.return_value = []
        MockMemory.return_value = mock_memory

        mock_artifacts = MagicMock()
        mock_artifacts.guardar_artefactos.return_value = None
        MockArtifacts.return_value = mock_artifacts

        mock_repo = MagicMock()
        mock_repo.generar_repo.return_value = "output/generated_projects/test_mission"
        MockRepo.return_value = mock_repo

        mock_learning = MagicMock()
        mock_learning.get_weights.return_value = {"alpha": 0.6, "beta": 0.3, "gamma": 0.1}
        mock_learning.recomendar_estrategia.return_value = ""
        mock_learning.update_from_missions.return_value = None
        MockLearning.return_value = mock_learning

        pipeline = IterativePipeline(max_iteraciones=max_iteraciones)
        pipeline.memory         = mock_memory
        pipeline.artifacts      = mock_artifacts
        pipeline.repo_generator = mock_repo
        pipeline.learning       = mock_learning

    return pipeline


# ------------------------------------------------------------------
# TESTS
# ------------------------------------------------------------------

class TestPipelineCicloCompleto(unittest.TestCase):

    def test_aprobado_iteracion_1(self):
        """Pipeline aprueba en primera iteración con código válido."""
        pipeline    = crear_pipeline_mockeado()
        orquestador = crear_orquestador_mock(codigo=CODIGO_VALIDO, reporte=REPORTE_APROBADO)

        resultado = pipeline.ejecutar_mision(orquestador, "Crea core/user.py con la entidad User")

        self.assertTrue(resultado.aprobado)
        self.assertEqual(resultado.compliance_score, 100)
        self.assertEqual(resultado.iteracion, 1)
        self.assertFalse(resultado.deuda_tecnica)

    def test_aprobado_iteracion_2_tras_rechazo(self):
        """Pipeline reintenta y aprueba en segunda iteración."""
        pipeline   = crear_pipeline_mockeado()
        call_count = {"n": 0}

        def ejecutar_agente(rol, prompt, color):
            if rol == "ARCHITECT":
                return "Plan de prueba."
            elif rol == "ENGINEER_BASE":
                call_count["n"] += 1
                return CODIGO_VALIDO
            elif rol == "AUDITOR":
                if call_count["n"] == 1:
                    return REPORTE_RECHAZADO
                return REPORTE_APROBADO
            return ""

        orquestador = MagicMock()
        orquestador.ejecutar_agente.side_effect = ejecutar_agente

        resultado = pipeline.ejecutar_mision(orquestador, "Crea core/user.py")

        self.assertTrue(resultado.aprobado)
        self.assertEqual(resultado.iteracion, 2)

    def test_aprobado_con_deuda_tecnica(self):
        """Pipeline detecta aprobación con deuda técnica correctamente."""
        pipeline    = crear_pipeline_mockeado()
        orquestador = crear_orquestador_mock(codigo=CODIGO_VALIDO, reporte=REPORTE_APROBADO_CON_DEUDA)

        resultado = pipeline.ejecutar_mision(orquestador, "Crea core/user.py")

        self.assertTrue(resultado.aprobado)
        self.assertTrue(resultado.deuda_tecnica)
        self.assertEqual(resultado.compliance_score, 80)

    def test_limite_iteraciones_sin_aprobacion(self):
        """Pipeline retorna resultado no aprobado al agotar iteraciones."""
        pipeline    = crear_pipeline_mockeado(max_iteraciones=3)
        orquestador = crear_orquestador_mock(codigo=CODIGO_VALIDO, reporte=REPORTE_RECHAZADO)

        resultado = pipeline.ejecutar_mision(orquestador, "Crea core/user.py")

        self.assertFalse(resultado.aprobado)
        self.assertEqual(resultado.iteracion, 3)
        self.assertEqual(resultado.compliance_score, 40)

    def test_resultado_contiene_campos_requeridos(self):
        """PipelineResult tiene todos los campos esperados."""
        pipeline    = crear_pipeline_mockeado()
        orquestador = crear_orquestador_mock(codigo=CODIGO_VALIDO, reporte=REPORTE_APROBADO)

        resultado = pipeline.ejecutar_mision(orquestador, "Crea core/user.py")

        self.assertIsNotNone(resultado.orden_ceo)
        self.assertIsNotNone(resultado.plan_arquitectonico)
        self.assertIsNotNone(resultado.codigo_final)
        self.assertIsNotNone(resultado.reporte_auditoria)
        self.assertIsNotNone(resultado.timestamp)


class TestValidacionMinimos(unittest.TestCase):

    def setUp(self):
        self.pipeline = crear_pipeline_mockeado()

    def test_codigo_valido_pasa(self):
        valido, msg = self.pipeline._validar_minimos(CODIGO_VALIDO)
        self.assertTrue(valido)
        self.assertEqual(msg, "Validación básica OK")

    def test_codigo_vacio_falla(self):
        valido, msg = self.pipeline._validar_minimos(CODIGO_VACIO)
        self.assertFalse(valido)
        self.assertIn("vacío", msg.lower())

    def test_codigo_con_todo_en_ejecutable_falla(self):
        """TODO en línea ejecutable real bloquea el validador."""
        valido, msg = self.pipeline._validar_minimos(CODIGO_CON_TODO)
        self.assertFalse(valido)
        self.assertIn("TODO", msg)

    def test_todo_en_comentario_no_falla(self):
        """TODOs dentro de comentarios # no deben bloquear."""
        codigo = CODIGO_VALIDO + "\n# TODO: optimizar en el futuro\n"
        valido, _ = self.pipeline._validar_minimos(codigo)
        self.assertTrue(valido)

    def test_todo_en_docstring_no_falla(self):
        """TODOs dentro de docstrings no deben bloquear."""
        codigo = CODIGO_VALIDO + '\n"""\nTODO: mejorar documentación\n"""\n'
        valido, _ = self.pipeline._validar_minimos(codigo)
        self.assertTrue(valido)

    def test_demasiados_pass_falla(self):
        codigo = CODIGO_VALIDO + "\n\ndef a(): pass\ndef b(): pass\ndef c(): pass\n"
        valido, msg = self.pipeline._validar_minimos(codigo)
        self.assertFalse(valido)
        self.assertIn("placeholders", msg.lower())

    def test_codigo_sin_bloques_suficientes_falla(self):
        codigo = "# File: x.py\nclass A:\n    pass\n"
        valido, _ = self.pipeline._validar_minimos(codigo)
        self.assertFalse(valido)


class TestExtraccionComplianceScore(unittest.TestCase):

    def setUp(self):
        self.pipeline = crear_pipeline_mockeado()

    def test_extrae_100(self):
        self.assertEqual(self.pipeline._extraer_compliance_score(REPORTE_APROBADO), 100)

    def test_extrae_80(self):
        self.assertEqual(self.pipeline._extraer_compliance_score(REPORTE_APROBADO_CON_DEUDA), 80)

    def test_extrae_40(self):
        self.assertEqual(self.pipeline._extraer_compliance_score(REPORTE_RECHAZADO), 40)

    def test_reporte_vacio_retorna_0(self):
        self.assertEqual(self.pipeline._extraer_compliance_score(""), 0)

    def test_reporte_sin_cumplimiento_retorna_0(self):
        self.assertEqual(self.pipeline._extraer_compliance_score("Sin datos aquí."), 0)


class TestVerificacionCertificacion(unittest.TestCase):

    def setUp(self):
        self.pipeline = crear_pipeline_mockeado()

    def test_detecta_aprobado(self):
        aprobado, deuda, estado = self.pipeline._verificar_certificacion(REPORTE_APROBADO)
        self.assertTrue(aprobado)
        self.assertFalse(deuda)
        self.assertEqual(estado, EstadoCertificacion.APROBADO)

    def test_detecta_aprobado_con_deuda(self):
        aprobado, deuda, estado = self.pipeline._verificar_certificacion(REPORTE_APROBADO_CON_DEUDA)
        self.assertTrue(aprobado)
        self.assertTrue(deuda)
        self.assertEqual(estado, EstadoCertificacion.APROBADO_DEUDA)

    def test_detecta_rechazado(self):
        aprobado, deuda, estado = self.pipeline._verificar_certificacion(REPORTE_RECHAZADO)
        self.assertFalse(aprobado)
        self.assertFalse(deuda)
        self.assertEqual(estado, EstadoCertificacion.RECHAZADO)

    def test_reporte_vacio_es_indefinido(self):
        aprobado, deuda, estado = self.pipeline._verificar_certificacion("")
        self.assertFalse(aprobado)
        self.assertEqual(estado, EstadoCertificacion.INDEFINIDO)


class TestExtraerArchivosBase(unittest.TestCase):

    def setUp(self):
        self.pipeline = crear_pipeline_mockeado()

    def test_extrae_archivo_unico(self):
        archivos = self.pipeline._extraer_archivos_base(CODIGO_VALIDO)
        self.assertEqual(len(archivos), 1)
        self.assertIn("core/user.py", archivos)

    def test_extrae_multiples_archivos(self):
        codigo = "# File: core/user.py\ncode\n\n# File: core/exceptions.py\ncode\n"
        archivos = self.pipeline._extraer_archivos_base(codigo)
        self.assertEqual(len(archivos), 2)

    def test_sin_archivos_retorna_lista_vacia(self):
        archivos = self.pipeline._extraer_archivos_base("código sin encabezado File:")
        self.assertEqual(archivos, [])

    def test_no_duplica_archivos(self):
        codigo = "# File: core/user.py\ncode\n\n# File: core/user.py\ncode\n"
        archivos = self.pipeline._extraer_archivos_base(codigo)
        self.assertEqual(len(archivos), 1)


class TestLearningEngineIntegracion(unittest.TestCase):

    def test_pipeline_funciona_sin_learning_engine(self):
        """Si LearningEngine no está disponible, el pipeline no se interrumpe."""
        pipeline          = crear_pipeline_mockeado()
        pipeline.learning = None
        orquestador       = crear_orquestador_mock(codigo=CODIGO_VALIDO, reporte=REPORTE_APROBADO)

        resultado = pipeline.ejecutar_mision(orquestador, "Crea core/user.py")
        self.assertTrue(resultado.aprobado)

    def test_learning_engine_es_consultado(self):
        """LearningEngine.get_weights() es llamado antes de cada misión."""
        pipeline    = crear_pipeline_mockeado()
        orquestador = crear_orquestador_mock(codigo=CODIGO_VALIDO, reporte=REPORTE_APROBADO)

        pipeline.ejecutar_mision(orquestador, "Crea core/user.py")
        pipeline.learning.get_weights.assert_called()

    def test_recomendar_estrategia_es_llamado_en_iteracion_1(self):
        """recomendar_estrategia() es llamado en la primera iteración."""
        pipeline    = crear_pipeline_mockeado()
        orquestador = crear_orquestador_mock(codigo=CODIGO_VALIDO, reporte=REPORTE_APROBADO)

        pipeline.ejecutar_mision(orquestador, "Crea core/user.py")
        pipeline.learning.recomendar_estrategia.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)