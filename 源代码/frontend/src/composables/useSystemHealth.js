import { reactive, onMounted, onUnmounted } from 'vue'

/**
 * 轮询 /api/v1/health，供顶栏红点与侧栏「系统状态」共用。
 * 返回 reactive 对象，字段：status / detail / checkedAt
 */
export function useSystemHealth(intervalMs = 20000) {
  const state = reactive({
    status: 'checking',
    detail: '',
    checkedAt: '',
  })
  let timer = null

  async function ping() {
    try {
      // 使用运行时配置的 API 地址（window.APP_CONFIG 在 index.html 中优先加载）
      const apiBase =
        (typeof window !== 'undefined' && window.APP_CONFIG?.API_BASE) ||
        'https://power-trading-console.onrender.com';
      const resp = await fetch(`${apiBase}/api/v1/health`, { method: 'GET' })
      const data = await resp.json().catch(() => ({}))
      if (resp.ok && data.success && data.data?.status === 'healthy') {
        state.status = 'ok'
        state.detail = data.data?.app || 'API 正常'
      } else {
        state.status = 'error'
        state.detail = data.message || `HTTP ${resp.status}`
      }
    } catch (e) {
      state.status = 'error'
      state.detail = e.message || '无法连接'
    }
    state.checkedAt = new Date().toLocaleTimeString('zh-CN', { hour12: false })
  }

  onMounted(() => {
    ping()
    timer = setInterval(ping, intervalMs)
  })

  onUnmounted(() => {
    if (timer) clearInterval(timer)
  })

  return state
}
