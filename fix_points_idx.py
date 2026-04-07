lines = open('maiie-web/src/components/GraphConsole.jsx', 'r', encoding='utf-8').read().split('\n')
lines[157] = "                  points={e.x1+','+e.y1+' '+e.x2+','+e.y2+' '+e.x3+','+e.y3+' '+e.x4+','+e.y4}"
open('maiie-web/src/components/GraphConsole.jsx', 'w', encoding='utf-8').write('\n'.join(lines))
print('OK')
