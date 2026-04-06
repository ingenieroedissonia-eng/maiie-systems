/**
 * @module MissionStatusPanel
 * @description Componente de React para mostrar el estado actual de la misión.
 *
 * @responsibilities
 * - Renderizar el título del panel de estado.
 * - Mostrar el estado de la misión recibido a través de las props.
 * - Mostrar un mensaje de espera si el estado de la misión aún no está disponible.
 * - Validar las props recibidas utilizando PropTypes.
 * - Aplicar estilos dinámicos según el estado de la misión (e.g., error, éxito).
 *
 * @version 1.0.0
 */

import React from 'react';
import PropTypes from 'prop-types';

/**
 * Componente funcional que muestra el estado de una misión.
 *
 * @param {object} props - Las props del componente.
 * @param {string|null} props.missionStatus - El estado actual de la misión. Puede ser nulo si no hay estado disponible.
 * @returns {JSX.Element} El elemento JSX que representa el panel de estado.
 */
function MissionStatusPanel({ missionStatus }) {
  /**
   * Determina el color del texto del estado basado en su contenido.
   * @param {string} status - El estado de la misión.
   * @returns {string} La clase CSS para el color (simulando TailwindCSS).
   */
  const getStatusStyle = (status) => {
    if (!status) {
      return { color: '#6B7280' }; // text-gray-500
    }
    const lowerCaseStatus = status.toLowerCase();
    if (lowerCaseStatus.includes('error') || lowerCaseStatus.includes('fallo')) {
      return { color: '#EF4444', fontWeight: 'bold' }; // text-red-500
    }
    if (lowerCaseStatus.includes('completada') || lowerCaseStatus.includes('éxito')) {
      return { color: '#22C55E', fontWeight: 'bold' }; // text-green-500
    }
    if (lowerCaseStatus.includes('progreso') || lowerCaseStatus.includes('ejecutando')) {
      return { color: '#3B82F6' }; // text-blue-500
    }
    return { color: '#374151' }; // text-gray-700
  };

  const panelStyle = {
    padding: '1rem',
    border: '1px solid #E5E7EB',
    borderRadius: '0.5rem',
    boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    backgroundColor: '#F9FAFB',
    marginTop: '1rem',
  };

  const headerStyle = {
    fontSize: '1.25rem',
    fontWeight: 'bold',
    marginBottom: '0.5rem',
    borderBottom: '1px solid #E5E7EB',
    paddingBottom: '0.5rem',
  };

  return (
    <div style={panelStyle}>
      <h2 style={headerStyle}>Estado de la Misión</h2>
      {missionStatus ? (
        <div>
          <p style={{ color: '#4B5563', fontSize: '0.875rem' }}>Última actualización:</p>
          <p style={{ fontSize: '1.125rem', ...getStatusStyle(missionStatus) }}>
            {missionStatus}
          </p>
        </div>
      ) : (
        <p style={{ color: '#6B7280', fontStyle: 'italic' }}>
          Esperando inicio de la misión para mostrar el estado...
        </p>
      )}
    </div>
  );
}

MissionStatusPanel.propTypes = {
  /**
   * El estado actual de la misión que se mostrará en el panel.
   * Si es nulo, se mostrará un mensaje de espera.
   */
  missionStatus: PropTypes.string,
};

MissionStatusPanel.defaultProps = {
  missionStatus: null,
};

export default MissionStatusPanel;