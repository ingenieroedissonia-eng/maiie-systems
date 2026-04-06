content = open('api/main.py', 'r', encoding='utf-8').read()
idx = content.find('def _run()')
print(content[idx:idx+600])
