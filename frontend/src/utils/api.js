const BASE_URL = import.meta.env.VITE_API_BASE || ''

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
