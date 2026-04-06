content = open('orchestrator/planner_executor.py', 'r', encoding='utf-8').read()

old = '''            resultado = self.pipeline.ejecutar_mision(orquestador, orden_enriquecida)
            resultados.append(resultado)
            ids_resueltos.add(sub["id"])'''

new = '''            try:
                resultado = self.pipeline.ejecutar_mision(orquestador, orden_enriquecida)
            except Exception as e:
                logger.error("Error en submision [%s]: %s — continuando", sub["id"], e, exc_info=True)
                ids_resueltos.add(sub["id"])
                continue
            resultados.append(resultado)
            ids_resueltos.add(sub["id"])'''

content = content.replace(old, new)
open('orchestrator/planner_executor.py', 'w', encoding='utf-8').write(content)
print("OK")
