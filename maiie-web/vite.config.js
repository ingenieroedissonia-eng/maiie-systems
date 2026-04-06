/**
 * @module vite.config
 * @description
 * Archivo de configuraciÃ³n para Vite.
 *
 * @responsibilities
 * - Definir la configuraciÃ³n base para el proyecto React.
 * - Configurar plugins, como el de React.
 * - Establecer opciones para el servidor de desarrollo (puerto, host).
 * - Definir la configuraciÃ³n del proceso de build para producciÃ³n.
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
   * ConfiguraciÃ³n del servidor de desarrollo.
   */
  server: {
    // Puerto en el que se ejecutarÃ¡ el servidor de desarrollo.
    port: 5173,
    strictPort: true,
    // Permite que el servidor sea accesible desde la red local.
    // Ãštil para probar en dispositivos mÃ³viles.
    host: true,
    // Abre automÃ¡ticamente el navegador al iniciar el servidor.
    open: true,
  },

  /**
   * ConfiguraciÃ³n del proceso de construcciÃ³n (build).
   */
  build: {
    // Directorio de salida para los archivos de producciÃ³n.
    outDir: 'dist',
    // Genera sourcemaps para facilitar la depuraciÃ³n en producciÃ³n.
    sourcemap: true,
    // Umbral de advertencia para el tamaÃ±o de los chunks en kB.
    chunkSizeWarningLimit: 1000,
  },

  /**
   * ConfiguraciÃ³n del servidor de previsualizaciÃ³n (preview).
   * Este servidor se usa para probar la build de producciÃ³n localmente.
   */
  preview: {
    // Puerto para el servidor de previsualizaciÃ³n.
    port: 4173,
    // Permite que el servidor sea accesible desde la red local.
    host: true,
    // Abre automÃ¡ticamente el navegador al iniciar el servidor de previsualizaciÃ³n.
    open: true,
  },

  /**
   * ResoluciÃ³n de alias para rutas de importaciÃ³n.
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
