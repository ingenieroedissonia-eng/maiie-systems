/**
 * @module vite.config
 * @description
 * Archivo de configuración para Vite.
 *
 * @responsibilities
 * - Definir la configuración base para el proyecto React.
 * - Configurar plugins, como el de React.
 * - Establecer opciones para el servidor de desarrollo (puerto, host).
 * - Definir la configuración del proceso de build para producción.
 *
 * @version 1.0.0
 */

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  /**
   * Lista de plugins a utilizar.
   * @property {Array} plugins - @vitejs/plugin-react es esencial para proyectos React.
   */
  plugins: [react()],

  /**
   * Configuración del servidor de desarrollo.
   */
  server: {
    // Puerto en el que se ejecutará el servidor de desarrollo.
    port: 5173,
    // Permite que el servidor sea accesible desde la red local.
    // Útil para probar en dispositivos móviles.
    host: true,
    // Abre automáticamente el navegador al iniciar el servidor.
    open: true,
  },

  /**
   * Configuración del proceso de construcción (build).
   */
  build: {
    // Directorio de salida para los archivos de producción.
    outDir: 'dist',
    // Genera sourcemaps para facilitar la depuración en producción.
    sourcemap: true,
    // Umbral de advertencia para el tamaño de los chunks en kB.
    chunkSizeWarningLimit: 1000,
  },

  /**
   * Configuración del servidor de previsualización (preview).
   * Este servidor se usa para probar la build de producción localmente.
   */
  preview: {
    // Puerto para el servidor de previsualización.
    port: 4173,
    // Permite que el servidor sea accesible desde la red local.
    host: true,
    // Abre automáticamente el navegador al iniciar el servidor de previsualización.
    open: true,
  },

  /**
   * Resolución de alias para rutas de importación.
   * Simplifica las importaciones en proyectos grandes.
   */
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@services': path.resolve(__dirname, './src/services'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@assets': path.resolve(__dirname, './src/assets'),
    },
  },
});