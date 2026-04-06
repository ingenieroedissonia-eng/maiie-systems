import React, { useState, useEffect, useRef } from 'react';
import './index.css';
import Sidebar from './components/Sidebar';
import GraphConsole from './components/GraphConsole';
import NodeDetailPanel from './components/NodeDetailPanel';
import { getMissionStatus, sendMissionOrder } from './services/apiService';


function App() {
  const [missionId, setMissionId] = useState(null);
  const [missionStatus, setMissionStatus] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  const [mName, setMName] = useState('');
  const [mDesc, setMDesc] = useState('');
  const statusRef = useRef(null);

  const handleSend = async () => {
    if (!mName.trim() || !mDesc.trim()) return;
    setIsLoading(true); setError(null); setMissionStatus(null);
    setMissionId(null); setSelectedNode(null); statusRef.current = null;
    setShowModal(false);
    try {
      const res = await sendMissionOrder({ orden: mDesc });
      if (res?.mission_id) {
        setMissionId(res.mission_id);
        setMissionStatus(res);
        statusRef.current = res;
        setMName(''); setMDesc('');
      } else throw new Error('Respuesta invalida del servidor.');
    } catch (e) { setError(e.message || 'Error inesperado.'); }
    finally { setIsLoading(false); }
  };

  useEffect(() => {
    if (!missionId) return;
    const id = setInterval(async () => {
      const cur = statusRef.current;
      if (cur?.status === 'done' || cur?.status === 'error') { clearInterval(id); return; }
      try {
        const s = await getMissionStatus(missionId);
        statusRef.current = s; setMissionStatus(s);
        if (s?.status === 'done' || s?.status === 'error') clearInterval(id);
      } catch (e) { setError(e.message); clearInterval(id); }
    }, 3000);
    return () => clearInterval(id);
  }, [missionId]);

  return (
    <>
      <header className="app-header">
        <div className="logo">M</div>
        <div className="brand">
          <h1>MAIIE SYSTEMS</h1>
          <p>Control de Misiones de Ingenieria Cognitiva</p>
        </div>
        <button className="exit-btn">⎋</button>
      </header>

      <div className="workspace">
        <Sidebar onNewMission={() => setShowModal(true)} missionStatus={missionStatus} />
        <GraphConsole
          missionStatus={missionStatus}
          missionId={missionId}
          selectedNode={selectedNode}
          onSelectNode={setSelectedNode}
        />
        <NodeDetailPanel selectedNode={selectedNode} missionStatus={missionStatus} />
      </div>

      <div className="statusbar">
        <span><span className="dot" />MAIIE Core API v2.3.0</span>
        <span>missions_store: In-Memory (RAM)</span>
        {isLoading && <span style={{color:'var(--accent)'}}>● Enviando mision...</span>}
        {missionStatus?.status === 'running' && <span style={{color:'var(--yellow)'}}>● En proceso</span>}
        {missionStatus?.status === 'done' && <span style={{color:'var(--green)'}}>● Mision completada — Aprobado: {missionStatus.aprobado ? 'SI' : 'NO'}</span>}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setShowModal(false)}>
          <div className="modal">
            <h2>Nueva Mision</h2>
            <div className="fg">
              <label>Nombre de la Mision</label>
              <input value={mName} onChange={e => setMName(e.target.value)} placeholder="ej. Reconnaissance Alpha" />
            </div>
            <div className="fg">
              <label>Descripcion / Orden</label>
              <textarea value={mDesc} onChange={e => setMDesc(e.target.value)} rows={4} placeholder="Describe los objetivos..." />
            </div>
            {error && <div style={{color:'var(--red)',fontSize:'0.76rem',marginBottom:'8px'}}>{error}</div>}
            <div className="modal-actions">
              <button className="btn-s" onClick={() => setShowModal(false)}>Cancelar</button>
              <button className="btn-p" onClick={handleSend} disabled={isLoading}>
                {isLoading ? 'Enviando...' : 'Enviar Mision'}
              </button>
            </div>
          </div>
        </div>
      )}

      {error && !showModal && <div className="err-toast">⚠ {error}</div>}
    </>
  );
}

export default App;



