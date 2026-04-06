content = open('api/main.py', 'r', encoding='utf-8').read()
old = 'allow_origins=["http://localhost:5173", "https://maiie-systems.vercel.app"]'
new = 'allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "https://maiie-systems-graph.vercel.app"]'
content = content.replace(old, new)
open('api/main.py', 'w', encoding='utf-8').write(content)
print('OK')
