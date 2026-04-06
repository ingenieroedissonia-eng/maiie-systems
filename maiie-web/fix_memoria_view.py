content = open('src/App.jsx', 'r', encoding='utf-8').read()

old = '''        {activeView === 'memoria' && (
          <div style={{flex:1,padding:'24px',overflowY:'auto'}}>
            <div style={{fontSize:'0.7rem',color:'var(--text-dim)',letterSpacing:'0.15em',textTransform:'uppercase',marginBottom:'16px'}}>Memoria Semantica</div>
          </div>
        )}'''

new = '''        {activeView === 'memoria' && (
          <div style={{flex:1,padding:'24px',overflowY:'auto'}}>
            <div style={{fontSize:'0.7rem',color:'var(--text-dim)',letterSpacing:'0.15em',textTransform:'uppercase',marginBottom:'16px'}}>Memoria Semantica</div>
            <MemoriaView systemStats={systemStats} />
          </div>
        )}'''

if old in content:
    open('src/App.jsx', 'w', encoding='utf-8').write(content.replace(old, new))
    print('OK patch memoria')
else:
    print('NO MATCH')
