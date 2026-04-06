content = open('maiie-web/api/mission.js', 'r', encoding='utf-8').read()
fixed = content.replace('await fetch(\/mission,', 'await fetch(\/mission,')
open('maiie-web/api/mission.js', 'w', encoding='utf-8').write(fixed)
print('OK')
