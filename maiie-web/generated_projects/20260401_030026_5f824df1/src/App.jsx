"""
Modulo: App
Capa: Componente Principal (Frontend)

Descripcion:
Componente principal de la aplicación React. Gestiona el estado global de la misión,
implementa el polling para obtener actualizaciones y renderiza los subcomponentes.

Responsabilidades:
- Definir constantes de configuración para la API.
- Mantener el estado del `missionStatus`.
- Iniciar un intervalo de polling para actualizar el estado de la misión cada 3 segundos.
- Manejar el ciclo de vida del polling (inicio y limpieza).
- Renderizar los componentes de la interfaz de usuario: MissionForm y MissionStatusPanel.

Version: 1.2.0
"""
import React, { useState, useEffect } from 'react';
import MissionForm from './components/MissionForm';
import MissionStatusPanel from './components/MissionStatusPanel';
import { getMissionStatus, sendMissionOrder } from './services/apiService';

const API_URL = 'http://localhost:8000/api/mission';
const API_KEY = 'your_super_secret_api_key';

function App() {
  const [missionStatus, setMissionStatus] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchMissionStatus = async () => {
      try {
        const status = await getMissionStatus(`${API_URL}/status`, API_KEY);
        setMissionStatus(status);
        if (error) setError(''); 
      } catch (err) {
        const errorMessage = `Error fetching mission status: ${err.message}`;
        console.error(errorMessage);
        setError(errorMessage);
        setMissionStatus({ state: 'ERROR', details: 'Failed to connect to the mission server.' });
      }
    };

    fetchMissionStatus();

    const intervalId = setInterval(fetchMissionStatus, 3000);

    return () => clearInterval(intervalId);
  }, [error]);

  const handleSendOrder = async (order) => {
    try {
      const result = await sendMissionOrder(`${API_URL}/order`, API_KEY, order);
      console.log('Order sent successfully:', result);
      const immediateStatus = await getMissionStatus(`${API_URL}/status`, API_KEY);
      setMissionStatus(immediateStatus);
    } catch (err) {
      const errorMessage = `Error sending mission order: ${err.message}`;
      console.error(errorMessage);
      setError(errorMessage);
    }
  };


  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Orion Mission Control</h1>
        <p>Real-time monitoring of deep space missions.</p>
      </header>
      <main className="app-main">
        <MissionForm onSubmitOrder={handleSendOrder} />
        <MissionStatusPanel status={missionStatus} error={error} />
      </main>
      <footer className="app-footer">
        <p>&copy; 2024 Galactic Federation. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;