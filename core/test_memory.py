"""
MAIIE System V2 - Mission Memory Test
Prueba básica del módulo MissionMemory
"""

import logging
from mission_memory import MissionMemory

logging.basicConfig(level=logging.INFO)

def main():
    memory = MissionMemory()

    print("\n=== LISTADO DE MISIONES ===")
    misiones = memory.listar_misiones()
    for m in misiones:
        print(m)

    if not misiones:
        print("\nNo hay misiones disponibles.")
        return

    ultima = misiones[-1]

    print(f"\n=== MANIFEST DE {ultima} ===")
    manifest = memory.cargar_manifest(ultima)
    print(manifest)

    print(f"\n=== ARQUITECTURA DE {ultima} ===")
    arquitectura = memory.cargar_arquitectura(ultima)
    if arquitectura:
        print(arquitectura[:500])  # solo primeros 500 caracteres

    print("\n=== CONTEXTO RECUPERADO ===")
    contexto = memory.obtener_contexto()
    print(contexto[:500])  # limitar salida

if __name__ == "__main__":
    main()