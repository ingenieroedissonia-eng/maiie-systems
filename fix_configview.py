content = open('maiie-web/src/App.jsx', encoding='utf-8-sig').read()
content = content.replace('maiie-system-00007-488', 'maiie-system-00009-s8f')
open('maiie-web/src/App.jsx', 'w', encoding='utf-8').write(content)
print('OK')
