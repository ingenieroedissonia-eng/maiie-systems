content = open('api/main.py', encoding='utf-8').read()

old = "            if resultado and resultado.aprobado and resultado.estado == 'APROBADO':"
new = "            if resultado and resultado.aprobado and not resultado.deuda_tecnica:"

content = content.replace(old, new)
open('api/main.py', 'w', encoding='utf-8').write(content)
print('OK:', 'not resultado.deuda_tecnica' in content)
