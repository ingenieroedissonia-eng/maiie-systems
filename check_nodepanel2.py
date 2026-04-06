lines = open('maiie-web/src/components/NodeDetailPanel.jsx', 'r', encoding='utf-8').read().split('\n')
for i, l in enumerate(lines):
    if "tab === 'code'" in l or 'Codigo no generado' in l or 'Generado por MAIIE' in l:
        print(f'{i+1}: {repr(l)}')
