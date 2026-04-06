content = '''import React, { useState, useEffect } from 'react';
import { getMissions } from '../services/apiService';

const Sidebar = ({ onNewMission, missionStatus, activeView, onViewChange, systemStats }) => {
  const [missions, setMissions] = useState([]);
  const [loadingMissions, setLoadingMissions] = useState(false);

  useEffect(() => {
    if (activeView === 'historial') {
      setLoadingMissions(true);
      getMissions()
        .then(data => setMissions(data.missions || []))
        .catch(() => setMissions([]))
        .finally(() => setLoadingMissions(false));
    }
  }, [activeView]);

  const alpha = systemStats?.alpha ?? '0.5977';
  const beta = systemStats?.beta ?? '0.3023';
  const gamma = systemStats?.gamma ?? '0.100';
  const totalMissions = systemStats?.total ?? '...';

  return (
    <div className="sidebar">
      <button className="new-mission-btn" onClick={onNewMission}>+ Nueva Mision</button>
      <nav>
        <div className={"nav-item" + (activeView === "panel" ? " active" : "")} onClick={() => onViewChange("panel")}>
          <span className="nav-icon">⊞</span>Panel de Control
        </div>
        <div className={"nav-item" + (activeView === "historial" ? " active" : "")} onClick={() => onViewChange("historial")}>
          <span className="nav-icon">↻</span>Historial de Misiones
        </div>
        <div className={"nav-item" + (activeView === "memoria" ? " active" : "")} onClick={() => onViewChange("memoria")}>
          <span className="nav-icon">◈</span>Memoria Semantica
        </div>
      </nav>

      {activeView === "panel" && (
        <>
          <div className="sb-section">
            <div className="sb-section-title">Misiones Indexadas</div>
            <div className="sb-stat"><span className="lbl">Total</span><span className="val">{totalMissions}</span></div>
          </div>
          <div className="sb-section">
            <div className="sb-section-title">LearningEngine Pesos</div>
            <div className="sb-stat"><span className="lbl">α (precision)</span><span className="val">{alpha}</span></div>
            <div className="sb-stat"><span className="lbl">β (recall)</span><span className="val">{beta}</span></div>
            <div className="sb-stat"><span className="lbl">γ (coverage)</span><span className="val">{gamma}</span></div>
          </div>
          <div className="sb-section">
            <div className="sb-section-title">Estado del Sistema</div>
            <div className="sb-stat"><span className="lbl">Interventoria</span><span className="val g">ACTIVA</span></div>
            <div className="sb-stat"><span className="lbl">Mision Store</span><span className="val g">GCS</span></div>
            <div className="sb-stat"><span className="lbl">LearningEngine</span><span className="val g">100%</span></div>
            <div className="sb-stat"><span className="lbl">Configuracion</span><span className="val g">100%</span></div>
          </div>
        </>
      )}

      {activeView === "historial" && (
        <div className="sb-section" style={{flex:1,overflowY:"auto"}}>
          <div className="sb-section-title">Historial de Misiones</div>
          {loadingMissions && <div style={{color:"var(--text-dim)",fontSize:"0.7rem",padding:"8px 0"}}>Cargando...</div>}
          {!loadingMissions && missions.length === 0 && (
            <div style={{color:"var(--text-dim)",fontSize:"0.7rem",padding:"8px 0"}}>Sin misiones registradas.</div>
          )}
          {!loadingMissions && missions.map(m => (
            <div key={m.mission_id} style={{padding:"8px 0",borderBottom:"1px solid var(--border)"}}>
              <div style={{fontFamily:"monospace",fontSize:"0.68rem",color:"var(--accent)"}}>{m.mission_id}</div>
              <div style={{display:"flex",justifyContent:"space-between",marginTop:"3px"}}>
                <span style={{fontSize:"0.65rem",color: m.status === "done" ? "var(--green)" : m.status === "error" ? "var(--red)" : "var(--yellow)"}}>{m.status?.toUpperCase()}</span>
                <span style={{fontSize:"0.65rem",color: m.aprobado ? "var(--green)" : "var(--text-dim)"}}>{m.aprobado ? "APROBADO" : m.aprobado === false ? "RECHAZADO" : "—"}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {activeView === "memoria" && (
        <div className="sb-section" style={{flex:1,overflowY:"auto"}}>
          <div className="sb-section-title">Memoria Semantica</div>
          <div className="sb-stat"><span className="lbl">Misiones indexadas</span><span className="val">{totalMissions}</span></div>
          <div className="sb-stat"><span className="lbl">Dims embedding</span><span className="val">768</span></div>
          <div className="sb-stat"><span className="lbl">Modelo</span><span className="val" style={{fontSize:"0.62rem"}}>text-embedding-004</span></div>
          <div className="sb-stat"><span className="lbl">Bucket GCS</span><span className="val g">ACTIVO</span></div>
          <div style={{marginTop:"12px"}}>
            <div className="sb-section-title">LearningEngine</div>
            <div className="sb-stat"><span className="lbl">α precision</span><span className="val">{alpha}</span></div>
            <div className="sb-stat"><span className="lbl">β recall</span><span className="val">{beta}</span></div>
            <div className="sb-stat"><span className="lbl">γ coverage</span><span className="val">{gamma}</span></div>
            <div className="sb-stat"><span className="lbl">Busqueda</span><span className="val g">SEMANTICA</span></div>
          </div>
        </div>
      )}

      <div style={{marginTop:"auto"}}>
        <div className={"nav-item" + (activeView === "config" ? " active" : "")} onClick={() => onViewChange("config")}>
          <span className="nav-icon">⚙</span>Configuracion
        </div>
      </div>
    </div>
  );
};
export default Sidebar;'''
open('maiie-web/src/components/Sidebar.jsx', 'w', encoding='utf-8').write(content)
print('OK')
