import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    isolate: false,
    include: ['tests/**/*.{test,spec}.{js,jsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['html', 'json-summary', 'json'],
      reportsDirectory: 'tests/coverage/js'
    }
  },
  build: {
    rollupOptions: {
      output: {
        entryFileNames: `assets/[name].js`,
        chunkFileNames: `assets/[name].js`,
        assetFileNames: `assets/[name].[ext]`
      }
    }
  }
})
