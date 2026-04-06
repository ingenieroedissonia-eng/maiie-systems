lines = open('orchestrator/planner_executor.py', 'r', encoding='utf-8').readlines()
lines.pop(127)
open('orchestrator/planner_executor.py', 'w', encoding='utf-8').writelines(lines)
print('OK')
