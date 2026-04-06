content = open('maiie-web/src/components/GraphConsole.jsx', 'r', encoding='utf-8').read()

old = "    if (!missionId || nodes.length > 0) return;"
new = "    if (!missionId || nodes.length !== 0) return;"

if old in content:
    open('maiie-web/src/components/GraphConsole.jsx', 'w', encoding='utf-8').write(content.replace(old, new))
    print('OK')
else:
    print('NO MATCH')
