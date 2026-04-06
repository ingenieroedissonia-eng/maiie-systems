"""
Módulo: App
Capa: Presentación (Componente Principal)

Descripción:
Componente principal de la aplicación React. Orquesta la interacción entre el formulario de misión y el panel de estado.
Maneja el estado central de la aplicación, incluyendo el estado de la misión y los posibles errores.

Responsabilidades:
- Renderizar los componentes principales de la UI (`MissionForm`, `MissionStatusPanel`).
- Mantener el estado de la misión actual.
- Proporcionar una función para manejar el envío de nuevas misiones.
- Gestionar y mostrar errores a nivel de aplicación.

Versión: 1.0.0
"""

import React, { useState, useEffect } from 'react';
import MissionForm from './components/MissionForm';
import MissionStatusPanel from './components/MissionStatusPanel';
import './App.css';

function App() {
  const [missionStatus, setMissionStatus] = useState(null);
  const [currentMissionId, setCurrentMissionId] = useState(null);
  const [error, setError] = useState('');

  const handleNewMission = (missionId) => {
    console.log(`New mission submitted with ID: ${missionId}`);
    setMissionStatus(null);
    setError('');
    setCurrentMissionId(missionId);
  };

  const handleStatusUpdate = (status) => {
    setMissionStatus(status);
    setError('');
  };

  const handleError = (errorMessage) => {
    console.error("An error occurred:", errorMessage);
    setError(errorMessage);
    setMissionStatus(null);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>M.A.R.S. Mission Control</h1>
        <p>Mission Administration & Remote Supervision</p>
      </header>
      <main className="app-main">
        <section className="form-section">
          <h2>New Mission Order</h2>
          <MissionForm 
            onMissionSubmit={handleNewMission}
            onError={handleError}
          />
        </section>
        <section className="status-section">
          <h2>Mission Status</h2>
          <MissionStatusPanel
            missionId={currentMissionId}
            status={missionStatus}
            error={error}
            onStatusUpdate={handleStatusUpdate}
            onError={handleError}
          />
        </section>
      </main>
      <footer className="app-footer">
        <p>&copy; 2024 Galactic Ventures Inc. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;