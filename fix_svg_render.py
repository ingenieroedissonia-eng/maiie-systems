content = open('maiie-web/src/components/GraphConsole.jsx', 'r', encoding='utf-8').read()

old = '''              {edges.map(e => (
                <line key={e.key} x1={e.x1} y1={e.y1} x2={e.x2} y2={e.y2}
                  stroke="#1e3050" strokeWidth="1.5" markerEnd="url(#arr)" />
              ))}'''

new = '''              {edges.map(e => e.bent ? (
                <polyline key={e.key}
                  points={${e.x1}, , , ,}
                  stroke="#1e3050" strokeWidth="1.5" fill="none" markerEnd="url(#arr)" />
              ) : (
                <line key={e.key} x1={e.x1} y1={e.y1} x2={e.x2} y2={e.y2}
                  stroke="#1e3050" strokeWidth="1.5" markerEnd="url(#arr)" />
              ))}'''

if old in content:
    open('maiie-web/src/components/GraphConsole.jsx', 'w', encoding='utf-8').write(content.replace(old, new))
    print('OK SVG render')
else:
    print('NO MATCH')
