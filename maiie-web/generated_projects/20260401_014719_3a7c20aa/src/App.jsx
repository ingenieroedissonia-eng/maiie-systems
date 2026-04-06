/**
 * Modulo: App
 * Capa: Presentacion (Componente Principal)
 *
 * @description
 * Componente raíz de la aplicación React. Orquesta la interfaz de usuario,
 * gestiona el estado global de la misión y coordina la comunicación entre
 * los componentes hijos.
 *
 * @responsabilidades
 * - Mantener el estado de la orden de misión actual.
 * - Mantener el estado del progreso de la misión.
 * - Renderizar los componentes de formulario y panel de estado.
 * - Proveer manejadores de eventos para actualizar el estado.
 *
 * @version 1.0.0
 */
import React, { useState, useCallback } from 'react';
import MissionForm from './components/MissionForm';
import MissionStatusPanel from './components/MissionStatusPanel';
// Importar servicios que se usarán en futuras implementaciones
// import { sendMissionOrder } from './services/apiService';
// import { startMissionPolling } from './services/pollingService';

const App = () => {
  const [missionId, setMissionId] = useState(null);
  const [missionStatus, setMissionStatus] = useState({
    status: 'IDLE',
    message: 'Awaiting new mission order.',
    details: [],
    timestamp: new Date().toISOString(),
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * @function handleSendOrder
   * @description
   * Manejador para enviar una nueva orden de misión.
   * Esta función será pasada como prop al componente MissionForm.
   * En esta fase, simula el inicio de una misión.
   * @param {string} orderText - La orden de la misión ingresada por el usuario.
   */
  const handleSendOrder = useCallback(async (orderText) => {
    setIsLoading(true);
    setError(null);
    setMissionStatus({
      status: 'SENDING',
      message: `Sending new mission order: "${orderText}"`,
      details: [],
      timestamp: new Date().toISOString(),
    });

    // Simulación de llamada a API en esta fase inicial
    // La lógica real se implementará en capas de servicio
    try {
      // const response = await sendMissionOrder(orderText);
      // setMissionId(response.mission_id);
      const simulatedMissionId = `mission_${Date.now()}`;
      setMissionId(simulatedMissionId);

      setMissionStatus({
        status: 'PENDING',
        message: `Mission order received. ID: ${simulatedMissionId}. Awaiting execution...`,
        details: [],
        timestamp: new Date().toISOString(),
      });
      // startMissionPolling(simulatedMissionId, handleStatusUpdate, handleError);
    } catch (apiError) {
      const errorMessage = apiError.message || 'Failed to send mission order.';
      setError(errorMessage);
      setMissionStatus({
        status: 'ERROR',
        message: errorMessage,
        details: [],
        timestamp: new Date().toISOString(),
      });
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * @function handleStatusUpdate
   * @description
   * Callback para actualizar el estado de la misión.
   * Será utilizado por el servicio de polling en futuras implementaciones.
   * @param {object} newStatus - El nuevo objeto de estado de la misión.
   */
  const handleStatusUpdate = useCallback((newStatus) => {
    setMissionStatus(newStatus);
  }, []);

  /**
   * @function handleError
   * @description
   * Callback para manejar errores provenientes de los servicios.
   * @param {Error} errorObject - El objeto de error.
   */
  const handleError = useCallback((errorObject) => {
    setError(errorObject.message || 'An unexpected error occurred.');
    setMissionStatus((prevStatus) => ({
      ...prevStatus,
      status: 'ERROR',
      message: errorObject.message || 'Polling failed.',
    }));
  }, []);


  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>M.A.I.I.E. Control System</h1>
        <p style={styles.subtitle}>Mission & Artificial Intelligence Integration Engine</p>
      </header>
      <main style={styles.main}>
        <div style={styles.panel}>
          <MissionForm onSendOrder={handleSendOrder} isLoading={isLoading} />
        </div>
        <div style={styles.panel}>
          <MissionStatusPanel
            status={missionStatus.status}
            message={missionStatus.message}
            details={missionStatus.details}
            timestamp={missionStatus.timestamp}
            error={error}
          />
        </div>
      </main>
      <footer style={styles.footer}>
        <p>System Status: Online | Version: 1.0.0</p>
      </footer>
    </div>
  );
};

const styles = {
  container: {
    fontFamily: '"Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    backgroundColor: '#1a1a1a',
    color: '#e0e0e0',
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '20px',
  },
  header: {
    textAlign: 'center',
    marginBottom: '40px',
    borderBottom: '1px solid #444',
    paddingBottom: '20px',
    width: '100%',
    maxWidth: '960px',
  },
  title: {
    margin: 0,
    fontSize: '2.5rem',
    color: '#00aaff',
    fontWeight: '300',
    letterSpacing: '2px',
  },
  subtitle: {
    margin: '5px 0 0',
    fontSize: '1rem',
    color: '#aaa',
    fontWeight: 'normal',
  },
  main: {
    display: 'flex',
    flexDirection: 'row',
    gap: '20px',
    width: '100%',
    maxWidth: '960px',
  },
  panel: {
    backgroundColor: '#242424',
    borderRadius: '8px',
    padding: '20px',
    flex: 1,
    boxShadow: '0 4px 8px rgba(0,0,0,0.2)',
  },
  footer: {
    marginTop: '40px',
    paddingTop: '20px',
    borderTop: '1px solid #444',
    width: '100%',
    maxWidth: '960px',
    textAlign: 'center',
    fontSize: '0.8rem',
    color: '#777',
  }
};

export default App;