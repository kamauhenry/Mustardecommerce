import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  base: '/static/',  // Ensure Vite-generated assets use Django's static URL
  build: {
    outDir: '../vue-project/dist',  // Ensures the output goes into frontend/dist
    assetsDir: 'assets',
    manifest: true,  // Generates manifest.json for Django
    rollupOptions: {
      output: {
        entryFileNames: 'assets/[name].js',
        chunkFileNames: 'assets/[name].js',
        assetFileNames: 'assets/[name].[ext]',
      }
    }
  },
  server: {
    port: 5173,  // Vite's dev server port
    strictPort: true
  }
})
