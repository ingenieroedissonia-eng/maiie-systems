backtick = chr(96)
dollar = chr(36)
old = 'await fetch(' + dollar + '{API_URL}/mission,'
new = 'await fetch(' + backtick + dollar + '{API_URL}/mission' + backtick + ','
content = open('maiie-web/api/mission.js', 'r', encoding='utf-8').read()
content = content.replace(old, new)
open('maiie-web/api/mission.js', 'w', encoding='utf-8').write(content)
print(repr(content[content.find('await fetch'):content.find('await fetch')+55]))
