import { fileURLToPath, URL } from 'node:url';
import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueDevTools from 'vite-plugin-vue-devtools';

export default defineConfig(({ mode }) => {
  // Load env file based on mode
  const env = loadEnv(mode, process.cwd(), '');

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
    // Build optimization
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      manifest: true,

      // Code splitting
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor': ['vue', 'vue-router', 'pinia'],
            'axios': ['axios'],
            'charts': ['chart.js', 'vue-chartjs'],
          },
          entryFileNames: 'assets/[name].[hash].js',
          chunkFileNames: 'assets/[name].[hash].js',
          assetFileNames: 'assets/[name].[hash].[ext]',
        }
      },

      // Source maps only in development
      sourcemap: mode === 'development',

      // Minification
      minify: mode === 'production' ? 'terser' : false,

      // Performance warnings
      chunkSizeWarningLimit: 1000,
    },
    server: {
      port: 5173,
      historyApiFallback: true,
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL?.replace('/api', '') || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
      },
    },

    // Preview server (for production builds)
    preview: {
      port: 4173,
    },
  };
});