content = open('src/App.jsx', 'r', encoding='utf-8').read()

old = 'export default App;'

new = '''function MemoriaView({ systemStats }) {
  const total = systemStats?.total ?? '...';
  return (
    <div style={{display:'flex',flexDirection:'column',gap:'12px',maxWidth:'520px'}}>
      {[
        ['Misiones indexadas', String(total)],
        ['Dims embedding', '768'],
        ['Modelo embedding', 'text-embedding-004'],
        ['Bucket GCS', 'gs://maiie-missions-prod'],
        ['Busqueda semantica', 'ACTIVA'],
        ['alpha precision', '0.5977'],
        ['beta recall', '0.3023'],
        ['gamma coverage', '0.100'],
      ].map(([k, v]) => (
        <div key={k} style={{background:'var(--panel-bg)',border:'1px solid var(--border)',borderRadius:'6px',padding:'10px 14px',display:'flex',justifyContent:'space-between',alignItems:'center'}}>
          <span style={{fontSize:'0.72rem',color:'var(--text-dim)',letterSpacing:'0.05em'}}>{k}</span>
          <span style={{fontSize:'0.72rem',color:'var(--accent)',fontFamily:'monospace'}}>{v}</span>
        </div>
      ))}
    </div>
  );
}

export default App;'''

if old in content:
    open('src/App.jsx', 'w', encoding='utf-8').write(content.replace(old, new))
    print('OK MemoriaView agregado')
else:
    print('NO MATCH')
