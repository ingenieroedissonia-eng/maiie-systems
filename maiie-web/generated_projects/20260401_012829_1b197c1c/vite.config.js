/**
 * @fileoverview
 * Modulo: vite.config.js
 * Capa: Build Configuration
 *
 * @description
 * Archivo de configuracion para Vite.js. Define el entorno de desarrollo,
 * el proceso de construccion y los plugins utilizados para el proyecto React.
 *
 * @responsabilidades
 * - Configurar el servidor de desarrollo (puerto, apertura automatica).
 * - Integrar el plugin de React para habilitar Fast Refresh (HMR) y transformaciones JSX.
 * - Definir la configuracion para la construccion de produccion (build).
 * - Configurar el servidor de previsualizacion de la build de produccion.
 *
 * @version 1.0.0
 */

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react({
      // Opciones especificas del plugin de React si son necesarias
      // Por ejemplo, para habilitar/deshabilitar fast refresh
      fastRefresh: true,
    }),
  ],
  server: {
    // Puerto para el servidor de desarrollo
    port: 5173,
    // Abrir el navegador automaticamente al iniciar el servidor
    open: true,
    // Configuracion del proxy para peticiones a la API (si es necesario)
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // Asumiendo que el backend corre en el puerto 8000
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    // Directorio de salida para los archivos de produccion
    outDir: 'dist',
    // Generar sourcemaps para la depuracion en produccion
    sourcemap: true,
    // Advertir si el tamano del chunk supera este limite (en kB)
    chunkSizeWarningLimit: 1024,
  },
  preview: {
    // Puerto para previsualizar la build de produccion
    port: 4173,
    // Abrir el navegador automaticamente al iniciar la previsualizacion
    open: true,
  },
  // Configuracion para resolver alias de rutas (opcional pero recomendado)
  resolve: {
    alias: {
      '@': '/src',
      '@components': '/src/components',
      '@services': '/src/services',
      '@assets': '/src/assets',
    },
  },
});