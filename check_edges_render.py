content = open('maiie-web/src/components/GraphConsole.jsx', 'r', encoding='utf-8').read()
idx = content.find('edges.map')
print(repr(content[idx:idx+300]))
