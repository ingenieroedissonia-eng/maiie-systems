"""
MAIIE System V2 - Agent Executor Contract
Módulo: Contratos formales entre capas del sistema
Capa: Core
Versión: 1.0.0

Arreglo quirúrgico P2 del Roadmap Estratégico v2.0.

Responsabilidad:
    Define el contrato formal que debe cumplir cualquier orquestador
    que interactúe con el IterativePipeline.

    Antes de este módulo, el pipeline dependía directamente del método
    privado _activar_agente() de MAIIE_System, generando acoplamiento
    a la implementación concreta.

    Con AgentExecutor, el pipeline depende de una abstracción. Cualquier
    clase que implemente este protocolo puede actuar como orquestador
    sin modificar el pipeline.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class AgentExecutor(Protocol):
    """
    Contrato formal para orquestadores de agentes en M.A.I.I.E.

    Método requerido:
        ejecutar_agente(rol, prompt_usuario, color) -> str

    Parámetros:
        rol:            Identificador del agente.
                        Valores válidos: "ARCHITECT", "ENGINEER_BASE",
                        "ENGINEER_SENIOR", "AUDITOR"
        prompt_usuario: Texto del prompt a enviar al agente.
        color:          Color Rich para la consola (ej. "cyan", "yellow").

    Retorna:
        Respuesta del modelo como string.
        Si el agente falla, retorna string con prefijo "[ERROR]".
    """

    def ejecutar_agente(
        self,
        rol: str,
        prompt_usuario: str,
        color: str,
    ) -> str:
        """Ejecuta un agente y retorna su respuesta."""
        ...