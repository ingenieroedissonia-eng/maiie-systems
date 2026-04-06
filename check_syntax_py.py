import ast
files = [
    'api/main.py',
    'core/planner.py',
    'core/plan_validator.py',
    'core/project_state_manager.py',
    'orchestrator/pipeline.py'
]
for path in files:
    try:
        ast.parse(open(path, 'r', encoding='utf-8').read())
        print('OK:', path)
    except SyntaxError as e:
        print('ERROR:', path, '-', e.msg, 'linea', e.lineno)
