content = open('orchestrator/planner_executor.py', 'r', encoding='utf-8').read()
idx = content.find('resultado = self.pipeline')
print(content[idx:idx+400])
