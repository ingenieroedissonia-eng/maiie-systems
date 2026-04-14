content = open('api/main.py', encoding='utf-8').read()

old = "            if resultado and resultado.aprobado:"
new = "            if resultado and resultado.aprobado and resultado.estado == 'APROBADO':"

content = content.replace(old, new)
open('api/main.py', 'w', encoding='utf-8').write(content)
print('OK:', "resultado.estado == 'APROBADO'" in content)
