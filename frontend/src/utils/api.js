/**
 * 获取 API 基础地址
 *
 * 优先级：
 * 1. 运行时配置 window.APP_CONFIG.API_BASE（由 GitHub Actions 构建时注入）
 * 2. 构建时环境变量 VITE_API_BASE（备选）
 * 3. 默认值（兜底）
 */
function getApiBase() {
  if (typeof window !== 'undefined' && window.APP_CONFIG && window.APP_CONFIG.API_BASE) {
    return window.APP_CONFIG.API_BASE;
  }
  if (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_BASE) {
    return import.meta.env.VITE_API_BASE;
  }
  return 'https://power-trading-console.onrender.com';
}

const BASE_URL = getApiBase();

function getHeaders() {
  const token = localStorage.getItem('auth_token')
  return token ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' }
}

async function request(method, path, body) {
  const url = BASE_URL + path
  const options = {
    method,
    headers: getHeaders(),
  }
  if (body && method !== 'GET') {
    options.body = JSON.stringify(body)
  }

  try {
    const resp = await fetch(url, options)
    const data = await resp.json()
    if (!resp.ok) {
      throw new Error(data.message || data.detail || `请求失败: ${resp.status}`)
    }
    return data
  } catch (e) {
    if (e.name === 'TypeError' && e.message.includes('fetch')) {
      throw new Error('无法连接后端服务，请确保后端已启动')
    }
    throw e
  }
}

export const api = {
  get: (path) => request('GET', path),
  post: (path, body) => request('POST', path, body),
  patch: (path, body) => request('PATCH', path, body),
  delete: (path) => request('DELETE', path),
}
