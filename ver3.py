content = open('orchestrator/planner_executor.py', 'r', encoding='utf-8').read()
idx = content.find('resultado = self.pipeline')
print(repr(content[idx-20:idx+50]))
