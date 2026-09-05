import { resolve } from 'path'
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        register: resolve(__dirname, 'register.html'),
        dashboard: resolve(__dirname, 'dashboard.html'),
        currentPrice: resolve(__dirname, 'current-price.html'),
        resalePrice: resolve(__dirname, 'resale-price.html'),
      },
    },
  },
})
