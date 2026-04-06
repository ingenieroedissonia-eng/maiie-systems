content = open('api/main.py', 'r', encoding='utf-8').read()
idx = content.find('allow_origins')
print(content[idx:idx+200])
