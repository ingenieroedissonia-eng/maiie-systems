/**
 * Modulo: MissionStatusPanel
 * Capa: Presentation (Components)
 *
 * Descripcion:
 * Componente de React para visualizar el estado actual de la misión.
 * Muestra un mensaje de carga si el estado no está disponible, o el
 * estado actual si se ha recibido. Aplica estilos dinámicos según el estado.
 *
 * Responsabilidades:
 * - Renderizar el título del panel de estado.
 * - Mostrar el estado de la misión recibido a través de props.
 * - Mostrar un mensaje de "cargando" cuando el estado no está definido.
 *
 * Version: 1.0.0
 */

import React from 'react';
import PropTypes from 'prop-types';

/**
 * Componente para mostrar el estado de la misión.
 * @param {object} props - Propiedades del componente.
 * @param {string|null} props.missionStatus - El estado actual de la misión.
 * @returns {JSX.Element} El panel de estado de la misión.
 */
const MissionStatusPanel = ({ missionStatus }) => {

  const getStatusStyle = (status) => {
    if (!status) {
      return styles.statusLoading;
    }
    if (status.includes('ERROR')) {
      return styles.statusError;
    }
    if (status.includes('COMPLETADA')) {
      return styles.statusSuccess;
    }
    return styles.statusInProgress;
  };

  const statusText = missionStatus || 'Esperando datos de la misión...';
  const currentStatusStyle = getStatusStyle(missionStatus);

  return (
    <div style={styles.panel}>
      <h2 style={styles.header}>Estado Actual de la Misión</h2>
      <div style={styles.statusContainer}>
        <p style={{ ...styles.statusText, ...currentStatusStyle }}>
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
  statusLoading: {
    color: '#aaa',
    fontStyle: 'italic',
  },
  statusInProgress: {
    color: '#f0ad4e',
  },
  statusSuccess: {
    color: '#5cb85c',
  },
  statusError: {
    color: '#d9534f',
  },
};

MissionStatusPanel.propTypes = {
  /**
   * El estado actual de la misión como una cadena de texto.
   * Si es null o undefined, se mostrará un mensaje de carga.
   */
  missionStatus: PropTypes.string,
};

MissionStatusPanel.defaultProps = {
  missionStatus: null,
};

export default MissionStatusPanel;