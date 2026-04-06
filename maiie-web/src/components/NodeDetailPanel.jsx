import React, { useState } from 'react';

const NodeDetailPanel = ({ selectedNode, missionStatus }) => {
  const [tab, setTab] = useState('status');
  const s = selectedNode?.status || 'idle';

  if (!selectedNode) return (
    <div className="detail-panel">
      <div className="det-header">
        <div className="lbl">Nodo Seleccionado</div>
        <div className="nname" style={{color:'var(--text-dim)'}}>—</div>
      </div>
      <div className="det-content" style={{display:'flex',alignItems:'center',justifyContent:'center',color:'var(--text-dim)',fontSize:'0.76rem'}}>
        Selecciona un nodo del grafo
      </div>
    </div>
  );

  return (
    <div className="detail-panel">
      <div className="det-header">
        <div className="lbl">Nodo Seleccionado:</div>
        <div className="nname">{selectedNode.id} ({selectedNode.file})</div>
        <span className={`badge ${s}`} style={{marginTop:'5px',display:'inline-block'}}>{s.toUpperCase()}</span>
      </div>
      <div className="det-tabs">
        {[['status','Estado'],['feedback','Auditor Feedback'],['code','Codigo']].map(([k, lbl]) => (
          <div key={k} className={`det-tab${tab === k ? ' active' : ''}`} onClick={() => setTab(k)}>{lbl}</div>
        ))}
      </div>
      <div className="det-content">
        {tab === 'status' && (
          <div>
            <div className="sb-stat" style={{marginBottom:'10px'}}>
              <span className="lbl">Estado</span>
              <span className={`badge ${s}`}>{s.toUpperCase()}</span>
            </div>
            {missionStatus && <>
              <div className="sb-stat"><span className="lbl">Iteracion</span><span className="val">{missionStatus.iteracion || 1}</span></div>
              <div className="sb-stat">
                <span className="lbl">Aprobado</span>
                <span className={`badge ${missionStatus.aprobado ? 'success' : 'retrying'}`}>{missionStatus.aprobado ? 'SI' : 'NO'}</span>
              </div>
            </>}
          </div>
        )}
        {tab === 'feedback' && (
          <div>
            {s === 'retrying' && <>
              <div className="fb-item rej"><div className="fb-lbl r">Ciclo 1: RECHAZADO</div>Razon: TODO detectado, FALTA DE ROBUSTEZ</div>
              <div className="fb-item ret"><div className="fb-lbl y">Ciclo 2: RETRYING...</div></div>
            </>}
            {s === 'success' && <div className="fb-item apr"><div className="fb-lbl g">APROBADO</div>{missionStatus?.observaciones || 'Subm. aprobada por el Auditor.'}</div>}
            {(s === 'pending' || s === 'idle') && <div style={{color:'var(--text-dim)',fontSize:'0.76rem'}}>Sin feedback aun.</div>}
            {s === 'running' && <div style={{color:'var(--text-dim)',fontSize:'0.76rem'}}>En proceso — pendiente de revision.</div>}
          </div>
        )}
        {tab === 'code' && (
          <div style={{color:'var(--text-dim)',fontSize:'0.73rem',fontFamily:'Courier New,monospace',lineHeight:'1.7',whiteSpace:'pre-wrap'}}>
            {s === 'idle' ? 'Codigo no generado aun.' : `# ${selectedNode.file}\n# Generado por MAIIE Engineer\n# Estado: ${s.toUpperCase()}\n# Iteracion: ${missionStatus?.iteracion || 1}`}
          </div>
        )}
      </div>
    </div>
  );
};

export default NodeDetailPanel;
