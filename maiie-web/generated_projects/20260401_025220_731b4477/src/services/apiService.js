/**
 * Modulo: ApiService
 * Capa: Services
 *
 * Descripcion:
 * Este módulo centraliza todas las interacciones con la API externa de la misión.
 * Proporciona funciones para enviar datos y solicitar información, encapsulando
 * la lógica de las peticiones HTTP, manejo de cabeceras y errores de red.
 *
 * Responsabilidades:
 * - Enviar órdenes de misión a la API.
 * - Gestionar la autenticación a través de la X-API-Key.
 * - Manejar respuestas y errores de la API de forma consistente.
 *
 * Version: 1.0.0
 */

/**
 * Envía una nueva orden de misión a la API.
 *
 * Realiza una petición POST al endpoint de órdenes, incluyendo los datos
 * de la orden en el cuerpo y la clave de API en las cabeceras.
 *
 * @param {object} orderData - Los datos de la orden a enviar.
 * @param {string} apiUrl - La URL base de la API.
 * @param {string} apiKey - La clave de API para la autenticación.
 * @returns {Promise<object>} Una promesa que se resuelve con los datos de la respuesta de la API.
 * @throws {Error} Si la petición de red falla o si la API devuelve un estado de error (no 2xx).
 */
export const sendOrder = async (orderData, apiUrl, apiKey) => {
  const endpoint = `${apiUrl}/orders`;

  console.log(`Sending order to: ${endpoint}`);

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': apiKey,
      },
      body: JSON.stringify(orderData),
    });

    if (!response.ok) {
      // Intentamos leer el cuerpo del error para dar más contexto
      const errorBody = await response.text();
      const errorMessage = `API Error: ${response.status} ${response.statusText}. Response: ${errorBody}`;
      console.error(errorMessage);
      throw new Error(errorMessage);
    }

    const responseData = await response.json();
    console.log('API response received successfully:', responseData);
    return responseData;

  } catch (error) {
    // Captura errores de red (e.g., no se puede conectar) o errores del bloque 'if (!response.ok)'
    console.error('Failed to execute sendOrder:', error.message);
    // Re-lanzamos el error para que el componente que llama (UI) pueda manejarlo
    // y actualizar su estado, por ejemplo, mostrando un mensaje de error al usuario.
    throw new Error(`Failed to send mission order. Please check network connection or API status.`);
  }
};