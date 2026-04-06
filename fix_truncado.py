content = open('maiie-web/src/components/GraphConsole.jsx', 'r', encoding='utf-8').read()

old = "    file: sub.descripcion.length > 35 ? sub.descripcion.slice(0, 35) + '...' : sub.descripcion,"

new = "    file: sub.descripcion.length > 40 ? sub.descripcion.slice(0, sub.descripcion.lastIndexOf(' ', 40)) + '...' : sub.descripcion,"

if old in content:
    open('maiie-web/src/components/GraphConsole.jsx', 'w', encoding='utf-8').write(content.replace(old, new))
    print('OK truncado inteligente')
else:
    print('NO MATCH')
