files = [
    'api/main.py',
    'core/planner.py',
    'core/plan_validator.py',
    'core/project_state_manager.py',
    'orchestrator/pipeline.py'
]
bom = b'\xef\xbb\xbf'
for path in files:
    with open(path, 'rb') as fh:
        content = fh.read()
    if content.startswith(bom):
        with open(path, 'wb') as fh:
            fh.write(content[3:])
        print('Fixed:', path)
    else:
        print('OK:', path)
