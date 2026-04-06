content = open('maiie-web/src/components/MissionStatusPanel.jsx', 'r', encoding='utf-8').read()
content = content.lstrip('\n')
open('maiie-web/src/components/MissionStatusPanel.jsx', 'w', encoding='utf-8').write(content)
print('OK')
