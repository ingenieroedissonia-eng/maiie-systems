"""
Modulo: MissionForm
Capa: Component (UI)

Descripcion: Un componente React que renderiza un formulario para enviar nuevas órdenes de misión.

Responsabilidades:
- Mostrar campos de entrada para los detalles de la misión (objetivo, destino, carga útil).
- Gestionar el estado de las entradas del formulario.
- Manejar el envío del formulario y pasar los datos a un componente padre.

Version: 1.0.0
"""
import React, { useState } from 'react';
import PropTypes from 'prop-types';

const MissionForm = ({ onMissionSubmit, isSubmitting }) => {
    const [objective, setObjective] = useState('');
    const [target, setTarget] = useState('');
    const [payload, setPayload] = useState('');

    const handleSubmit = (event) => {
        event.preventDefault();
        if (!objective.trim() || !target.trim()) {
            alert('Objective and Target are required fields.');
            return;
        }
        onMissionSubmit({ objective, target, payload });
        setObjective('');
        setTarget('');
        setPayload('');
    };

    const formStyles = {
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
        padding: '1.5rem',
        border: '1px solid #444',
        borderRadius: '8px',
        backgroundColor: '#2a2a2e',
        maxWidth: '600px',
        margin: '2rem auto',
        boxShadow: '0 4px 8px rgba(0,0,0,0.3)',
    };

    const headerStyles = {
        color: '#00aaff',
        textAlign: 'center',
        margin: '0 0 1rem 0',
        borderBottom: '1px solid #444',
        paddingBottom: '1rem',
    };

    const inputGroupStyles = {
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem',
    };

    const labelStyles = {
        fontWeight: 'bold',
        fontSize: '0.9rem',
        color: '#ccc',
    };

    const inputStyles = {
        padding: '0.75rem',
        border: '1px solid #555',
        borderRadius: '4px',
        fontSize: '1rem',
        backgroundColor: '#333',
        color: '#eee',
    };

    const buttonStyles = {
        padding: '0.75rem 1.5rem',
        border: 'none',
        borderRadius: '4px',
        backgroundColor: '#007bff',
        color: 'white',
        fontSize: '1rem',
        cursor: 'pointer',
        transition: 'background-color 0.2s',
        marginTop: '1rem',
    };

    const disabledButtonStyles = {
        ...buttonStyles,
        backgroundColor: '#555',
        cursor: 'not-allowed',
    };

    return (
        <form onSubmit={handleSubmit} style={formStyles}>
            <h2 style={headerStyles}>New Mission Order</h2>
            <div style={inputGroupStyles}>
                <label htmlFor="objective" style={labelStyles}>Mission Objective:</label>
                <input
                    id="objective"
                    type="text"
                    value={objective}
                    onChange={(e) => setObjective(e.target.value)}
                    style={inputStyles}
                    placeholder="e.g., Deploy Communications Satellite"
                    required
                    disabled={isSubmitting}
                />
            </div>
            <div style={inputGroupStyles}>
                <label htmlFor="target" style={labelStyles}>Target:</label>
                <input
                    id="target"
                    type="text"
                    value={target}
                    onChange={(e) => setTarget(e.target.value)}
                    style={inputStyles}
                    placeholder="e.g., Geostationary Orbit 113.1°W"
                    required
                    disabled={isSubmitting}
                />
            </div>
            <div style={inputGroupStyles}>
                <label htmlFor="payload" style={labelStyles}>Payload Details:</label>
                <textarea
                    id="payload"
                    value={payload}
                    onChange={(e) => setPayload(e.target.value)}
                    style={{ ...inputStyles, minHeight: '100px', resize: 'vertical' }}
                    placeholder="e.g., 1x SAT-COM-XG-v2, 2x Micro-Sensors"
                    disabled={isSubmitting}
                />
            </div>
            <button type="submit" style={isSubmitting ? disabledButtonStyles : buttonStyles} disabled={isSubmitting}>
                {isSubmitting ? 'Transmitting Order...' : 'Submit Mission Order'}
            </button>
        </form>
    );
};

MissionForm.propTypes = {
    /**
     * Function to call when the form is submitted with valid data.
     * It receives an object with the mission details.
     */
    onMissionSubmit: PropTypes.func.isRequired,
    /**
     * Boolean flag to indicate if a submission is currently in progress.
     * Disables the form fields and button when true.
     */
    isSubmitting: PropTypes.bool,
};

MissionForm.defaultProps = {
    isSubmitting: false,
};

export default MissionForm;