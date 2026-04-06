/**
 * Modulo: main
 * Capa: Punto de Entrada (Entry Point)
 *
 * @description
 * Este archivo es el punto de entrada principal para la aplicación React.
 * Su responsabilidad es inicializar la aplicación y montarla en el DOM,
 * utilizando el API concurrente de React 18.
 *
 * @responsabilidades
 * - Importar las bibliotecas fundamentales: React y ReactDOM/client.
 * - Importar el componente raíz de la aplicación (`App`).
 * - Localizar el elemento del DOM donde se montará la aplicación, que por convención es un `div` con `id='root'`.
 * - Crear una raíz de renderizado concurrente usando `ReactDOM.createRoot()`.
 * - Renderizar el componente `App` dentro de la raíz creada.
 * - Envolver el componente `App` en `<React.StrictMode>` para activar verificaciones y advertencias adicionales en el modo de desarrollo, ayudando a detectar problemas potenciales.
 *
 * @version 1.0.0
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';

// Se busca el elemento raíz en el DOM.
// Este elemento está definido en `index.html` y sirve como contenedor para toda la aplicación.
const rootElement = document.getElementById('root');

// Se realiza una validación para asegurar que el elemento raíz existe.
// Si no se encuentra, se lanza un error para detener la ejecución y notificar el problema.
if (!rootElement) {
    // Este error es crítico, ya que la aplicación no puede iniciarse sin un punto de montaje.
    throw new Error(
        "Error Crítico: No se pudo encontrar el elemento raíz con id 'root'. " +
        "Asegúrese de que su archivo public/index.html contiene un `div` con este identificador."
    );
}

// Se crea la raíz de la aplicación utilizando el API moderno de React 18.
// Esto habilita características concurrentes y mejoras de rendimiento.
const root = ReactDOM.createRoot(rootElement);

// Se renderiza la aplicación en el DOM.
// React.StrictMode es un componente de envoltura que ayuda a identificar
// prácticas inseguras, efectos secundarios inesperados y APIs obsoletas durante el desarrollo.
// No tiene impacto en el build de producción.
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);