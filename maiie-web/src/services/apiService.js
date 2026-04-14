export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}
export class NetworkError extends Error {
  constructor(message) {
    super(message);
    this.name = 'NetworkError';
  }
}
const APP_TOKEN = import.meta.env.VITE_APP_TOKEN;
export const sendMissionOrder = async (order) => {
  try {
    const response = await fetch('/api/mission', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-app-token': APP_TOKEN,
      },
      body: JSON.stringify(order),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Error' }));
      throw new ApiError(errorData.message || `API Error: ${response.statusText}`, response.status);
    }
    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new NetworkError('Network request failed.');
  }
};
export const getMissionStatus = async (missionId) => {
  try {
    const response = await fetch(`/api/status?id=${missionId}`, {
      headers: { 'x-app-token': APP_TOKEN },
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Error' }));
      throw new ApiError(errorData.message || `API Error: ${response.statusText}`, response.status);
    }
    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new NetworkError('Network request failed.');
  }
};

export const getMissions = async () => {
  try {
    const response = await fetch('/api/missions', {
      headers: { 'x-app-token': APP_TOKEN },
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Error' }));
      throw new ApiError(errorData.message || 'API Error: ' + response.statusText, response.status);
    }
    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new NetworkError('Network request failed.');
  }
};
export const getSubmissions = async (missionId) => {
  try {
    const response = await fetch('/api/submissions?id=' + missionId, {
      headers: { 'x-app-token': APP_TOKEN },
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Error' }));
      throw new ApiError(errorData.message || 'API Error: ' + response.statusText, response.status);
    }
    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new NetworkError('Network request failed.');
  }
};
export const getMetrics = async () => {
  try {
    const response = await fetch('/api/metrics', {
      headers: { 'x-app-token': APP_TOKEN },
    });
    if (!response.ok) throw new ApiError('API Error', response.status);
    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new NetworkError('Network request failed.');
  }
};
export const getGraph = async (missionId) => {
  try {
    const response = await fetch(`/api/mission/${missionId}/graph`, {
      headers: { 'x-app-token': APP_TOKEN },
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Error' }));
      throw new ApiError(errorData.message || 'API Error: ' + response.statusText, response.status);
    }
    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new NetworkError('Network request failed.');
  }
};

export const getSubmissionDetail = async (missionId, subId) => {
  try {
    const response = await fetch(`/api/mission/${missionId}/submission/${subId}`, {
      headers: { 'x-app-token': APP_TOKEN },
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Error' }));
      throw new ApiError(errorData.message || 'API Error: ' + response.statusText, response.status);
    }
    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new NetworkError('Network request failed.');
  }
};
