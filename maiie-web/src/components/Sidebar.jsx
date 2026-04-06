import React from 'react';

const Sidebar = ({ onNewMission, missionStatus }) => (
  <div className="sidebar">
    <button className="new-mission-btn" onClick={onNewMission}>+ Nueva Mision</button>
    <nav>
      <div className="nav-item active"><span className="nav-icon">⊞</span>Panel de Control</div>
      <div className="nav-item"><span className="nav-icon">↻</span>Historial de Misiones</div>
      <div className="nav-item"><span className="nav-icon">◈</span>Memoria Semantica</div>
    </nav>
    <div className="sb-section">
      <div className="sb-section-title">Misiones Indexadas: 24+</div>
      <div className="sb-stat"><span className="lbl">Status</span><span className="val">24+</span></div>
    </div>
    <div className="sb-section">
      <div className="sb-section-title">LearningEngine Pesos</div>
      <div className="sb-stat"><span className="lbl">α (precision)</span><span className="val">0.5997</span></div>
      <div className="sb-stat"><span className="lbl">β (recall)</span><span className="val">0.3003</span></div>
      <div className="sb-stat"><span className="lbl">γ (coverage)</span><span className="val">0.100</span></div>
    </div>
    <div className="sb-section">
      <div className="sb-section-title">Estado del Sistema</div>
      <div className="sb-stat"><span className="lbl">Inleinadoria</span><span className="val">24+</span></div>
      <div className="sb-stat"><span className="lbl">Mision Store</span><span className="val g">100%</span></div>
      <div className="sb-stat"><span className="lbl">LearningEngine</span><span className="val g">100%</span></div>
      <div className="sb-stat"><span className="lbl">Configuracion</span><span className="val g">100%</span></div>
    </div>
    <div style={{marginTop:'auto'}}>
      <div className="nav-item"><span className="nav-icon">⚙</span>Configuracion</div>
    </div>
  </div>
);

export default Sidebar;
