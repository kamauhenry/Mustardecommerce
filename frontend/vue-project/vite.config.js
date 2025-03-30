import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueDevTools from 'vite-plugin-vue-devtools';

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  base: '/static/', // Vite-generated assets use Django's static URL
  build: {
    outDir: '../vue-project/dist', // The output goes into frontend/dist
    assetsDir: 'assets',
    manifest: true, // Generates manifest.json for Django
    rollupOptions: {
      output: {
        entryFileNames: 'assets/[name].js',
        chunkFileNames: 'assets/[name].js',
        assetFileNames: 'assets/[name].[ext]',
      },
    },
  },
  server: {
    port: 5173, // Vite’s dev server port (avoid conflict with Django)
    strictPort: true,
    proxy: {
      '/api': {
        // target: 'http://127.0.0.1:8000', // Fixed to include 'http:'
        target: 'http://127.0.0.1:8080',  // Use Nginx as the backend gateway
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
      },
    },
  },
});
