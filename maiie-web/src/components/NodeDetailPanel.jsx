import React, { useState } from 'react';



const NodeDetailPanel = ({ selectedNode, missionStatus, codigoGenerado }) => {

  const [tab, setTab] = useState('status');

  const s = selectedNode?.status || 'idle';



  if (!selectedNode) return (

    <div className="detail-panel">

      <div className="det-header">

        <div className="lbl">Nodo Seleccionado</div>

        <div className="nname" style={{color:'var(--text-dim)'}}>--</div>

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

            {selectedNode?.feedback
              ? <div className="fb-item apr" style={{whiteSpace:'pre-wrap',fontSize:'0.68rem',lineHeight:'1.6'}}>{selectedNode.feedback}</div>
              : <div style={{color:'var(--text-dim)',fontSize:'0.76rem'}}>{s === 'pending' || s === 'idle' ? 'Sin feedback aun.' : s === 'running' ? 'En proceso -- pendiente de revision.' : 'Feedback no disponible.'}</div>
            }

          </div>

        )}

        {tab === 'code' && (

          <div style={{color:'var(--accent)',fontSize:'0.68rem',fontFamily:'Courier New,monospace',lineHeight:'1.6',whiteSpace:'pre-wrap',overflowX:'auto'}}>

            {selectedNode?.codigo || codigoGenerado || 'Codigo no generado aun.'}

          </div>

        )}

      </div>

    </div>

  );

};



export default NodeDetailPanel;

