lines = open('api/main.py', 'r', encoding='utf-8').read().split('\n')
for i, l in enumerate(lines):
    if 'mission_id = _uuid' in l or 'def _run' in l or 'threading.Thread' in l or 'USAR_PLANNER' in l:
        print(f'{i+1}: {repr(l)}')
