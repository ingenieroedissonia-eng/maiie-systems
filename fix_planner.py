lines = open('core/planner.py', 'r', encoding='utf-8').readlines()
nueva_regla = '- PROHIBIDO generar dos submisiones para el mismo archivo. Si un archivo necesita varias funciones, TODAS van en UNA sola submision. Ejemplo: Crea src/api/maiie.js con las funciones enviarMision, obtenerEstado y publicarMision\n'
lines.insert(103, nueva_regla)
open('core/planner.py', 'w', encoding='utf-8').writelines(lines)
print('Fix aplicado')
