import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// GitHub Pages 部署时使用环境变量或默认值 '/仓库名/'
// 本地开发环境会使用相对路径
const base = process.env.VITE_BASE_URL || (process.env.NODE_ENV === 'production' ? '/power-trading-console/' : '/')

export default defineConfig({
  plugins: [vue()],
  base: base,
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', '@vueuse/core']
  },
  server: {
    port: 5173,
    warmup: {
      clientFiles: [
        './src/main.js',
        './src/App.vue',
        './src/router/index.js',
        './src/components/layout/AppLayout.vue',
        './src/components/background/PowerFlowBackground.vue'
      ]
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia']
        }
      }
    }
  }
})