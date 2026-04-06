lines = open('orchestrator/planner_executor.py', 'r', encoding='utf-8').readlines()
for i, l in enumerate(lines[124:135], start=125):
    print(f'{i}: {repr(l)}')
