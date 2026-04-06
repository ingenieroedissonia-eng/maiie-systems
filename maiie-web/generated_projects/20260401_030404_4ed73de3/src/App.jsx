"""
Module: App
Layer: Presentation (View)

Description:
Main application component for the Mission Control dashboard.
This component orchestrates the user interface, manages application state,
and handles communication with the backend service through polling.
It defines the API constants for use in service calls.

Responsibilities:
- Define API connection constants (URL, Key).
- Render the main application layout.
- Manage state for mission ID, mission status, loading, and errors.
- Handle submission of new mission orders.
- Periodically poll for mission status updates.

Version: 1.3.0
"""

import React, { useState, useEffect, useCallback } from 'react';
import MissionForm from './components/MissionForm';
import MissionStatusPanel from './components/MissionStatusPanel';
import { getMissionStatus, sendMissionOrder } from './services/apiService';

const API_URL = "http://localhost:8000/api/v1/missions";
const API_KEY = "a_secure_and_well_managed_api_key";

function App() {
    const [missionId, setMissionId] = useState(null);
    const [missionStatus, setMissionStatus] = useState(null);
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleSendOrder = async (order) => {
        setIsLoading(true);
        setError(null);
        setMissionStatus(null);
        setMissionId(null);
        try {
            const newMission = await sendMissionOrder(order, API_URL, API_KEY);
            if (newMission && newMission.mission_id) {
                setMissionId(newMission.mission_id);
                setMissionStatus(newMission);
            } else {
                throw new Error("Failed to create mission: Invalid response from server.");
            }
        } catch (err) {
            console.error("Error sending mission order:", err);
            setError(err.message || "An unexpected error occurred while sending the order.");
        } finally {
            setIsLoading(false);
        }
    };

    const fetchStatus = useCallback(async () => {
        if (!missionId) return;

        try {
            const status = await getMissionStatus(missionId, API_URL, API_KEY);
            setMissionStatus(status);
            if (error) setError(null); 
        } catch (err) {
            console.error(`Error fetching status for mission ${missionId}:`, err);
            setError(err.message || `Failed to fetch status for mission ${missionId}.`);
        }
    }, [missionId, error]);

    useEffect(() => {
        if (!missionId) {
            return;
        }

        const isTerminalState = missionStatus?.status === 'SUCCESS' || missionStatus?.status === 'FAILURE';
        if (isTerminalState) {
            return;
        }
        
        const intervalId = setInterval(() => {
            fetchStatus();
        }, 3000);

        return () => clearInterval(intervalId);
    }, [missionId, fetchStatus, missionStatus]);

    return (
        <div className="app-container">
            <header className="app-header">
                <h1>ARES-V Mission Control</h1>
                <p>Real-time command and telemetry dashboard.</p>
            </header>
            <main>
                <MissionForm onSubmit={handleSendOrder} isLoading={isLoading} />
                {error && <div className="error-panel">{`Error: ${error}`}</div>}
                <MissionStatusPanel 
                    status={missionStatus} 
                    isLoading={isLoading && !missionStatus} 
                />
            </main>
            <footer className="app-footer">
                <p>&copy; 2024 ARES-V Program. All rights reserved.</p>
            </footer>
        </div>
    );
}

export default App;