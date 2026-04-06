import ast
content = open('orchestrator/planner_executor.py', 'r', encoding='utf-8').read()
try:
    ast.parse(content)
    print('OK')
except SyntaxError as e:
    print(f'Error linea {e.lineno}: {e.msg}')
    print(e.text)
