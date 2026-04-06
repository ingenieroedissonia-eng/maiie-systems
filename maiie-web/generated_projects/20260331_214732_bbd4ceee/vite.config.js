/**
 * Modulo: Vite Configuration
 * Capa: Build Tool Configuration
 *
 * Descripcion:
 * Archivo de configuración para Vite. Define el comportamiento del servidor de desarrollo,
 * el proceso de build y los plugins utilizados.
 *
 * Responsabilidades:
 * - Habilitar el plugin de React para la transformación de JSX y Fast Refresh.
 * - Configurar un proxy para las peticiones a la API del backend, evitando problemas de CORS
 *   durante el desarrollo.
 *
 * Version: 1.0.0
 */

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000, // Puerto para el servidor de desarrollo de Vite
    proxy: {
      // Redirige las peticiones que comienzan con /api al backend
      '/api': {
        // URL del backend (ej. FastAPI corriendo en el puerto 8000)
        target: 'http://127.0.0.1:8000',
        // Cambia el origen de la cabecera Host a la URL de destino
        changeOrigin: true,
        // Reescribe la ruta, eliminando el prefijo /api
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  build: {
    outDir: 'dist', // Directorio de salida para los archivos de producción
    sourcemap: true, // Generar sourcemaps para facilitar el debug en producción
  },
  preview: {
    port: 4173, // Puerto para previsualizar el build de producción
    proxy: {
      // Aplica la misma configuración de proxy para la previsualización
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});