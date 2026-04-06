# ADR 001: Arquitectura de 7 Capas M.A.I.I.E. v2.0

* **Estado:** Aprobado
* **Fecha:** 2026-02-03
* **Autor:** Edisson A.G.C. (CEO/Arquitecto)

## Contexto
Necesitamos un sistema que permita generar activos de software vendibles (assets), garantice seguridad bancaria y sea evolutivo, evitando el "código espagueti" de los scripts monolíticos.

## Decisión
Se adopta una arquitectura de "Sala Limpia" (Clean-Room) con separación estricta de 7 capas físicas:

1.  **config/**: Abstracción de credenciales (evita hardcoding de keys).
2.  **core/** (Capa 2): Lógica determinística pura. Prohibido el uso de random().
3.  **economy/** (Capa 6): Gestión financiera aislada. Verificable independientemente.
4.  **security/** (Capa 5): Logs de auditoría inmutables.
5.  **orchestrator/** (Capa 3): Script de coordinación (El "Cuerpo").
6.  **output/**: Zona de entrega de productos finales.
7.  **docs/**: Memoria institucional y decisiones técnicas.

## Consecuencias
* **Positiva:** Permite vender módulos sueltos (ej: vender solo la carpeta `economy`).
* **Positiva:** Facilita la auditoría por agentes externos (Claude).
* **Negativa:** Requiere disciplina estricta para no mezclar lógica entre carpetas.