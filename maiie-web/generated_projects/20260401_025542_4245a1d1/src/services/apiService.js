/**
 * Modulo: apiService
 * Capa: Infrastructure (Services)
 *
 * Descripcion:
 * Proporciona funciones para interactuar con la API de control de misiones.
 * Se encarga de encapsular la logica de las llamadas HTTP, el manejo de
 * cabeceras de autenticacion y la gestion de errores de red o de la API.
 *
 * Responsabilidades:
 * - Enviar nuevas ordenes de mision.
 * - Obtener el estado actualizado de una mision.
 * - Lanzar errores especificos para problemas de API o de red.
 *
 * Version: 1.1.0
 */

/**
 * Error personalizado para problemas relacionados con la respuesta de la API.
 */
export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

/**
 * Error personalizado para problemas de red.
 */
export class NetworkError extends Error {
  constructor(message) {
    super(message);
    this.name = 'NetworkError';
  }
}

/**
 * Envia una orden de mision a la API.
 * @param {object} order - El objeto de la orden a enviar.
 * @param {string} apiUrl - La URL base de la API.
 * @param {string} apiKey - La clave de API para la autenticacion.
 * @returns {Promise<object>} La respuesta de la API con los detalles de la mision creada.
 * @throws {ApiError} Si la API retorna un error.
 * @throws {NetworkError} Si hay un problema de red.
 */
export const sendMissionOrder = async (order, apiUrl, apiKey) => {
  const endpoint = `${apiUrl}/missions`;

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': apiKey,
      },
      body: JSON.stringify(order),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Failed to parse error response' }));
      throw new ApiError(errorData.message || `API Error: ${response.statusText}`, response.status);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new NetworkError('Network request failed. Please check your connection and API configuration.');
  }
};

/**
 * Obtiene el estado de una mision especifica desde la API.
 * @param {string} missionId - El ID de la mision a consultar.
 * @param {string} apiUrl - La URL base de la