import React, { useState, useEffect, useRef } from 'react';
import './index.css';
import Sidebar from './components/Sidebar';
import GraphConsole from './components/GraphConsole';
import NodeDetailPanel from './components/NodeDetailPanel';
import { getMissionStatus, sendMissionOrder, getMissions, getMetrics } from './services/apiService';

function App() {
  const [missionId, setMissionId] = useState(null);
  const [missionStatus, setMissionStatus] = useState(null);
  const [executionState, setExecutionState] = useState({
  isActive: false,
  status: null
});
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  const [codigoGenerado, setCodigoGenerado] = useState(null);
  const [mName, setMName] = useState('');
  const [mDesc, setMDesc] = useState('');
  const [activeView, setActiveView] = useState('panel');
  const [systemStats, setSystemStats] = useState(null);
  const [allMissions, setAllMissions] = useState(null);
  const statusRef = useRef(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([getMissions(), getMetrics()])
      .then(([missionsData, metricsData]) => {
        if (!cancelled) {
          const missions = missionsData.missions || [];
          const le = metricsData.learning_engine || {};
          setSystemStats({
            total: missions.length,
            alpha: le.alpha ?? '0.6',
            beta: le.beta ?? '0.3',
            gamma: le.gamma ?? '0.1',
            calibrado: le.calibrado ?? false,
            misiones_procesadas: le.misiones_procesadas ?? 0,
          });
          setAllMissions(missions);
        }
      })
      .catch(() => { if (!cancelled) setSystemStats({ total: '?' }); });
    return () => { cancelled = true; };
  }, []);

  const handleSend = async () => {
    if (!mName.trim() || !mDesc.trim()) return;
    setIsLoading(true); setError(null); setMissionStatus(null);
    setMissionId(null); setSelectedNode(null); statusRef.current = null;
    setShowModal(false); setActiveView('panel');
    try {
      const res = await sendMissionOrder({ orden: mDesc });
      if (res?.mission_id) {
        setMissionId(res.mission_id);
        setMissionStatus(res);
        setExecutionState({
  isActive: true,
  status: 'running'
});
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
        if (s?.status === 'done' || s?.status === 'error') {
  setExecutionState({
    isActive: false,
    status: s.status
  });
  clearInterval(id);
}
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
        <Sidebar
          onNewMission={() => setShowModal(true)}
          missionStatus={missionStatus}
          activeView={activeView}
          onViewChange={setActiveView}
          systemStats={systemStats}
          allMissions={allMissions}
        />
        {activeView === 'panel' && (
          <>
            <GraphConsole
              missionStatus={missionStatus}
              missionId={missionId}
              selectedNode={selectedNode}
              onSelectNode={setSelectedNode}
              onCodigoGenerado={setCodigoGenerado}
            />
            <NodeDetailPanel selectedNode={selectedNode} missionStatus={missionStatus} codigoGenerado={codigoGenerado} />
          </>
        )}
        {activeView === 'historial' && (
          <div style={{flex:1,padding:'24px',overflowY:'auto'}}>
            <div style={{fontSize:'0.7rem',color:'var(--text-dim)',letterSpacing:'0.15em',textTransform:'uppercase',marginBottom:'16px'}}>Historial de Misiones</div>
            <HistorialView missions={allMissions} />
          </div>
        )}
        {activeView === 'memoria' && (
          <div style={{flex:1,padding:'24px',overflowY:'auto'}}>
            <div style={{fontSize:'0.7rem',color:'var(--text-dim)',letterSpacing:'0.15em',textTransform:'uppercase',marginBottom:'16px'}}>Memoria Semantica</div>
            <MemoriaView systemStats={systemStats} />
          </div>
        )}
        {activeView === 'config' && (
          <div style={{flex:1,padding:'24px',overflowY:'auto'}}>
            <div style={{fontSize:'0.7rem',color:'var(--text-dim)',letterSpacing:'0.15em',textTransform:'uppercase',marginBottom:'16px'}}>Configuracion del Sistema</div>
            <ConfigView />
          </div>
        )}
      </div>

      <div className="statusbar">
        <span><span className="dot" />MAIIE Core API v2.3.0</span>
        <span>missions_store: GCS</span>
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
              <input value={mName} onChange={e => setMName(e.target.value)} placeholder="ej. suma_simple" />
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

function HistorialView({ missions: propMissions }) {
  const [missions, setMissions] = useState(propMissions || []);
  const [loading, setLoading] = useState(!propMissions);

  useEffect(() => {
    if (propMissions) { setMissions(propMissions); setLoading(false); return; }
    getMissions()
      .then(data => setMissions(data.missions || []))
      .catch(() => setMissions([]))
      .finally(() => setLoading(false));
  }, [propMissions]);

  if (loading) return <div style={{color:'var(--text-dim)',fontSize:'0.8rem'}}>Cargando misiones...</div>;
  if (missions.length === 0) return <div style={{color:'var(--text-dim)',fontSize:'0.8rem'}}>Sin misiones registradas.</div>;

  return (
    <div style={{display:'flex',flexDirection:'column',gap:'8px'}}>
      {missions.map(m => (
        <div key={m.mission_id} style={{background:'var(--panel-bg)',border:'1px solid var(--border)',borderRadius:'7px',padding:'12px 16px'}}>
          <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'6px'}}>
            <span style={{fontFamily:'monospace',fontSize:'0.75rem',color:'var(--accent)'}}>{m.mission_id}</span>
            <span className={"badge " + (m.status === 'done' ? 'success' : m.status === 'error' ? 'retrying' : 'running')}>{m.status?.toUpperCase()}</span>
          </div>
          <div style={{display:'flex',gap:'16px',fontSize:'0.7rem',color:'var(--text-dim)'}}>
            <span>Aprobado: <span style={{color: m.aprobado ? 'var(--green)' : 'var(--text-dim)'}}>{m.aprobado ? 'SI' : m.aprobado === false ? 'NO' : '—'}</span></span>
          </div>
          {m.observaciones && <div style={{marginTop:'6px',fontSize:'0.68rem',color:'var(--text-dim)',borderTop:'1px solid var(--border)',paddingTop:'6px'}}>{m.observaciones}</div>}
        </div>
      ))}
    </div>
  );
}

function ConfigView() {
  return (
    <div style={{display:'flex',flexDirection:'column',gap:'12px',maxWidth:'520px'}}>
      {[
        ['Pipeline Version', 'v4.19.0'],
        ['Cloud Run Revision', 'maiie-system-00011-pr4'],
        ['ARCHITECT', 'google/gemini-2.5-flash-lite'],
        ['ENGINEER_BASE', 'google/gemini-2.5-pro'],
        ['AUDITOR', 'google/gemini-2.5-pro'],
        ['GCS Bucket', 'gs://maiie-missions-prod'],
        ['Embeddings', 'text-embedding-004 — 768 dims'],
        ['Seguridad', 'CORS + APP_TOKEN + X-API-Key'],
        ['CORS', 'maiie-systems-graph.vercel.app'],
      ].map(([k, v]) => (
        <div key={k} style={{background:'var(--panel-bg)',border:'1px solid var(--border)',borderRadius:'6px',padding:'10px 14px',display:'flex',justifyContent:'space-between',alignItems:'center'}}>
          <span style={{fontSize:'0.72rem',color:'var(--text-dim)',letterSpacing:'0.05em'}}>{k}</span>
          <span style={{fontSize:'0.72rem',color:'var(--accent)',fontFamily:'monospace'}}>{v}</span>
        </div>
      ))}
    </div>
  );
}

function MemoriaView({ systemStats }) {
  const total = systemStats?.total ?? '...';
  return (
    <div style={{display:'flex',flexDirection:'column',gap:'12px',maxWidth:'520px'}}>
      {[
        ['Misiones indexadas', String(total)],
        ['Dims embedding', '768'],
        ['Modelo embedding', 'text-embedding-004'],
        ['Bucket GCS', 'gs://maiie-missions-prod'],
        ['Busqueda semantica', 'ACTIVA'],
        ['alpha precision', String(systemStats?.alpha ?? '0.6')],
        ['beta recall', String(systemStats?.beta ?? '0.3')],
        ['gamma coverage', String(systemStats?.gamma ?? '0.1')],
      ].map(([k, v]) => (
        <div key={k} style={{background:'var(--panel-bg)',border:'1px solid var(--border)',borderRadius:'6px',padding:'10px 14px',display:'flex',justifyContent:'space-between',alignItems:'center'}}>
          <span style={{fontSize:'0.72rem',color:'var(--text-dim)',letterSpacing:'0.05em'}}>{k}</span>
          <span style={{fontSize:'0.72rem',color:'var(--accent)',fontFamily:'monospace'}}>{v}</span>
        </div>
      ))}
    </div>
  );
}

export default App;