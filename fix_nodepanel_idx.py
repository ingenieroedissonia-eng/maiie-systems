lines = open('maiie-web/src/components/NodeDetailPanel.jsx', 'r', encoding='utf-8').read().split('\n')
lines[57] = "        {tab === 'code' && ("
lines[58] = "          <div style={{color:'var(--accent)',fontSize:'0.68rem',fontFamily:'Courier New,monospace',lineHeight:'1.6',whiteSpace:'pre-wrap',overflowX:'auto'}}>"
lines[59] = "            {s === 'idle' ? 'Codigo no generado aun.' : selectedNode.descripcion}"
lines[60] = "          </div>"
lines[61] = "        )}"
open('maiie-web/src/components/NodeDetailPanel.jsx', 'w', encoding='utf-8').write('\n'.join(lines))
print('OK')
