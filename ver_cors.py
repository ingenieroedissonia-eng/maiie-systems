content = open('api/main.py', 'r', encoding='utf-8').read()
idx = content.find('CORSMiddleware')
print(content[idx:idx+300])
