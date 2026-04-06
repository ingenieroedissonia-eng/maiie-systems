content = open('maiie-web/src/components/NodeDetailPanel.jsx', 'r', encoding='utf-8').read()

old = '''        {tab === 'code' && (
          <div style={{color:'var(--text-dim)',fontSize:'0.73rem',fontFamily:'Courier New,monospace',lineHeight:'1.7',whiteSpace:'pre-wrap'}}>
            {s === 'idle' ? 'Codigo no generado aun.' : # \n# Generado por MAIIE Engineer\n# Estado: \n# Iteracion: }
          </div>
        )}'''

new = '''        {tab === 'code' && (
          <div style={{color:'var(--accent)',fontSize:'0.68rem',fontFamily:'Courier New,monospace',lineHeight:'1.6',whiteSpace:'pre-wrap',overflowX:'auto'}}>
            {s === 'idle' ? 'Codigo no generado aun.' : selectedNode.descripcion}
          </div>
        )}'''

if old in content:
    open('maiie-web/src/components/NodeDetailPanel.jsx', 'w', encoding='utf-8').write(content.replace(old, new))
    print('OK NodeDetailPanel')
else:
    print('NO MATCH')
