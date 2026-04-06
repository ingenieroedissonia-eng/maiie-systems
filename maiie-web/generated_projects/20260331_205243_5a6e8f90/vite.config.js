/**
 * @module vite.config
 * @description Configuration file for Vite.
 *
 * This file configures Vite for the React frontend application. It includes settings
 * for the development server, build process, and necessary plugins. The primary
 * plugin is `@vitejs/plugin-react` for React support.
 *
 * A key feature of this configuration is the development server proxy. It forwards
 * API requests made from the frontend to the backend server, which is assumed
 * to be running on `http://127.0.0.1:8000`. This avoids CORS issues during
 * local development when the frontend and backend are on different ports.
 *
 * @see https://vitejs.dev/config/
 * @version 1.0.0
 */

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// The defineConfig helper provides type-checking and autocompletion for the config.
export default defineConfig({
  /**
   * An array of plugins to use.
   * @see https://vitejs.dev/plugins/
   */
  plugins: [
    // The @vitejs/plugin-react plugin provides React-specific functionalities,
    // such as JSX transformation and React Fast Refresh (HMR).
    react(),
  ],

  /**
   * Configuration for the development server.
   * @see https://vitejs.dev/config/server-options.html
   */
  server: {
    // The port the development server will listen on.
    port: 5173, // This is the default Vite port.

    // Specifies whether to open the browser automatically when the server starts.
    open: true,

    /**
     * Configure custom proxy rules for the dev server.
     * This is useful for forwarding API requests to a backend server.
     */
    proxy: {
      // Any request starting with '/mission' will be proxied.
      // e.g., /mission, /mission/some-id/status
      '/mission': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true, // Needed for virtual-hosted sites.
        secure: false,      // Set to false if your backend is HTTP.
      },
      // Any request starting with '/publish' will be proxied.
      '/publish': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },

  /**
   * Configuration for the production build.
   * @see https://vitejs.dev/config/build-options.html
   */
  build: {
    // The directory where build output will be placed.
    outDir: 'dist',
    // Generate source maps for debugging production issues.
    sourcemap: true,
  },

  /**
   * Preview server configuration.
   * This is for previewing the production build locally.
   * @see https://vitejs.dev/config/preview-options.html
   */
  preview: {
    port: 4173, // Port to run the preview server on.
  },
});