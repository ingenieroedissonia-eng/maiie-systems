"""
MAIIE System V2 - Prompt Type Definitions
Módulo: Definición de roles del sistema
Capa: Utils (Infraestructura)
Versión: 4.0.0
"""

from enum import Enum, unique

@unique
class MAIIERole(Enum):
    """
    Roles disponibles en el sistema MAIIE.
    Cada rol tiene un prompt asociado en /config/prompts/
    """
    ARCHITECT = "ARCHITECT"
    ENGINEER_BASE = "ENGINEER_BASE"
    ENGINEER_SENIOR = "ENGINEER_SENIOR"
    AUDITOR = "AUDITOR"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_string(cls, role_str: str) -> 'MAIIERole':
        """
        Convierte string a MAIIERole de forma segura.
        
        Args:
            role_str: Nombre del rol (case-insensitive)
            
        Returns:
            MAIIERole enum
            
        Raises:
            ValueError: Si el rol no existe
        """
        try:
            return cls[role_str.upper()]
        except KeyError:
            valid_roles = ', '.join([r.value for r in cls])
            raise ValueError(
                f"Rol '{role_str}' no válido. Roles disponibles: {valid_roles}"
            )

    @classmethod
    def list_all(cls) -> list[str]:
        """Retorna lista de todos los roles disponibles."""
        return [role.value for role in cls]