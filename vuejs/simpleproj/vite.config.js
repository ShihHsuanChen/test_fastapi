import { fileURLToPath, URL } from 'url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  build: {
    outDir:  '../frontend',
    rollupOptions: {
      output: {
        assetFileNames: 'asset/[name]-[hash][extname]',
        chunkFileNames: 'scripts/[name]-[hash].js',
        entryFileNames: 'scripts/[name]-[hash].js',
      },
    },
  },
})
