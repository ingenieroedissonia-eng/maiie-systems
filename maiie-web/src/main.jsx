import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';

// Se busca el elemento raÃ­z en el DOM.
// Este elemento estÃ¡ definido en `index.html` y sirve como contenedor para toda la aplicaciÃ³n.
const rootElement = document.getElementById('root');

// Se realiza una validaciÃ³n para asegurar que el elemento raÃ­z existe.
// Si no se encuentra, se lanza un error para detener la ejecuciÃ³n y notificar el problema.
if (!rootElement) {
    // Este error es crÃ­tico, ya que la aplicaciÃ³n no puede iniciarse sin un punto de montaje.
    throw new Error(
        "Error CrÃ­tico: No se pudo encontrar el elemento raÃ­z con id 'root'. " +
        "AsegÃºrese de que su archivo public/index.html contiene un `div` con este identificador."
    );
}

// Se crea la raÃ­z de la aplicaciÃ³n utilizando el API moderno de React 18.
// Esto habilita caracterÃ­sticas concurrentes y mejoras de rendimiento.
const root = ReactDOM.createRoot(rootElement);

// Se renderiza la aplicaciÃ³n en el DOM.
// React.StrictMode es un componente de envoltura que ayuda a identificar
// prÃ¡cticas inseguras, efectos secundarios inesperados y APIs obsoletas durante el desarrollo.
// No tiene impacto en el build de producciÃ³n.
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
