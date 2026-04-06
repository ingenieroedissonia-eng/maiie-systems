import React, { useState } from 'react';

/**
 * Un formulario para crear y enviar órdenes de misión.
 * @param {object} props - Propiedades del componente.
 * @param {function({name: string, description: string}): void} props.onSendOrder - Callback que se ejecuta al enviar el formulario con éxito.
 */
const MissionForm = ({ onSendOrder }) => {
    const [missionName, setMissionName] = useState('');
    const [missionDescription, setMissionDescription] = useState('');
    const [error, setError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    /**
     * Maneja el envío del formulario.
     * Valida los campos y, si son válidos, llama al callback onSendOrder.
     * @param {React.FormEvent<HTMLFormElement>} event - El evento del formulario.
     */
    const handleSubmit = async (event) => {
        event.preventDefault();
        if (isSubmitting) return;
        setError('');

        if (!missionName.trim() || !missionDescription.trim()) {
            setError('Both mission name and description are required.');
            return;
        }

        setIsSubmitting(true);

        try {
            await onSendOrder({
                name: missionName,
                description: missionDescription,
            });
            
            setMissionName('');
            setMissionDescription('');
        } catch (e) {
            setError('Failed to send the mission order. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="mission-form-container">
            <h2>New Mission</h2>
            <form onSubmit={handleSubmit} noValidate>
                <div className="form-group">
                    <label htmlFor="missionName">Mission Name</label>
                    <input
                        id="missionName"
                        type="text"
                        value={missionName}
                        onChange={(e) => setMissionName(e.target.value)}
                        placeholder="e.g., Reconnaissance Alpha"
                        required
                        disabled={isSubmitting}
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="missionDescription">Mission Description</label>
                    <textarea
                        id="missionDescription"
                        value={missionDescription}
                        onChange={(e) => setMissionDescription(e.target.value)}
                        placeholder="Describe the mission objectives, target, and any special instructions."
                        rows={4}
                        required
                        disabled={isSubmitting}
                    />
                </div>

                {error && <p className="error-message">{error}</p>}

                <button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Sending Order...' : 'Send Mission Order'}
                </button>
            </form>
        </div>
    );
};

export default MissionForm;



