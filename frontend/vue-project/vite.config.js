import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueDevTools from 'vite-plugin-vue-devtools';

export default defineConfig(({ mode }) => {
  return {
    plugins: [
      vue(),
      vueDevTools(),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    base: mode === 'production' ? '/static/' : '/', // Use / in development, /static/ in production
    build: {
      outDir: 'dist', // Output directly to Django's static directory
      assetsDir: 'assets',
      manifest: true,
      rollupOptions: {
        output: {
          entryFileNames: 'assets/[name].js',
          chunkFileNames: 'assets/[name].js',
          assetFileNames: 'assets/[name].[ext]',
        },
      },
    },
    server: {
      port: 5173,
      historyApiFallback: true,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
        '/static': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
        '/login': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
        '/register': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
        '/logout': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
        '/admin-page/login': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
        '/admin-page/register': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
        '/admin-page/dashboard': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
        '/admin-page/profile': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
      },
    },
  };
});
