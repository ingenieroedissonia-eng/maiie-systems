content = open('orchestrator/planner_executor.py', 'r', encoding='utf-8').read()
old = '            resultado = self.pipeline.ejecutar_mision(orquestador, orden_enriquecida)\n            except'
new = '            try:\n                resultado = self.pipeline.ejecutar_mision(orquestador, orden_enriquecida)\n            except'
content = content.replace(old, new)
open('orchestrator/planner_executor.py', 'w', encoding='utf-8').write(content)
print("OK")
