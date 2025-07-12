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
    // Fix: Use relative path for assets in production
    base: mode === 'production' ? '/' : '/',
    build: {
      outDir: 'dist',
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
          target: 'https://mustardimports.co.ke',
          changeOrigin: true,
          secure: true, // Set to true for HTTPS
        },
        '/static': {
          target: 'https://mustardimports.co.ke',
          changeOrigin: true,
          secure: true,
        },
        '/login': {
          target: 'https://mustardimports.co.ke',
          changeOrigin: true,
          secure: true,
        },
        '/register': {
          target: 'https://mustardimports.co.ke',
          changeOrigin: true,
          secure: true,
        },
        '/logout': {
          target: 'https://mustardimports.co.ke',
          changeOrigin: true,
          secure: true,
        },
        '/admin-page/login': {
          target: 'https://mustardimports.co.ke',
          changeOrigin: true,
          secure: true,
        },
        '/admin-page/register': {
          target: 'https://mustardimports.co.ke',
          changeOrigin: true,
          secure: true,
        },
        '/admin-page/dashboard': {
          target: 'https://mustardimports.co.ke',
          changeOrigin: true,
          secure: true,
        },
        '/admin-page/profile': {
          target: 'https://mustardimports.co.ke',
          changeOrigin: true,
          secure: true,
        },
      },
    },
  };
});