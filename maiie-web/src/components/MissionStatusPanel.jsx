import React from 'react';
import PropTypes from 'prop-types';

const MissionStatusPanel = ({ missionStatus = null }) => {
  const status = typeof missionStatus === "object" && missionStatus !== null
    ? (missionStatus.status || "")
    : (missionStatus || "");

  const getStatusStyle = (s) => {
    if (!s) return styles.statusLoading;
    if (s === 'done') return styles.statusSuccess;
    if (s === 'error') return styles.statusError;
    if (s === 'running') return styles.statusInProgress;
    return styles.statusLoading;
  };

  const getStatusText = (s, data) => {
    if (!s) return "Esperando datos de la mision...";
    if (s === 'running') return "Mision en proceso...";
    if (s === 'done') return `Mision completada. Aprobado: ${data?.aprobado ? 'SI' : 'NO'} | Iteracion: ${data?.iteracion || 1}`;
    if (s === 'error') return `Error: ${data?.observaciones || 'Error desconocido'}`;
    return s;
  };

  const currentStyle = getStatusStyle(status);
  const statusText = getStatusText(status, missionStatus);

  return (
    <div style={styles.panel}>
      <h2 style={styles.header}>Estado Actual de la Mision</h2>
      <div style={styles.statusContainer}>
        <p style={{ ...styles.statusText, ...currentStyle }}>
          {statusText}
        </p>
      </div>
    </div>
  );
};

const styles = {
  panel: {
    border: '1px solid #444',
    borderRadius: '8px',
    padding: '20px',
    margin: '20px 0',
    backgroundColor: '#282c34',
    color: 'white',
    fontFamily: 'Arial, sans-serif',
    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
  },
  header: {
    marginTop: 0,
    marginBottom: '15px',
    borderBottom: '1px solid #444',
    paddingBottom: '10px',
    color: '#61dafb',
    fontSize: '1.5em',
  },
  statusContainer: {
    padding: '15px',
    backgroundColor: '#3a3f47',
    borderRadius: '4px',
    textAlign: 'center',
  },
  statusText: {
    margin: 0,
    fontSize: '1.2em',
    fontWeight: 'bold',
  },
  statusLoading: { color: '#aaa', fontStyle: 'italic' },
  statusInProgress: { color: '#f0ad4e' },
  statusSuccess: { color: '#5cb85c' },
  statusError: { color: '#d9534f' },
};

MissionStatusPanel.propTypes = {
  missionStatus: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
};

export default MissionStatusPanel;
