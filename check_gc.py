content = open('maiie-web/src/components/GraphConsole.jsx', 'r', encoding='utf-8').read()
idx = content.find('.finally')
print(repr(content[idx-100:idx+200]))
