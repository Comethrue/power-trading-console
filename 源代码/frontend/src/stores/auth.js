import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('auth_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user_info') || 'null'))

  const isLoggedIn = computed(() => !!token.value)

  function setAuth(data) {
    token.value = data.access_token || ''
    refreshToken.value = data.refresh_token || ''
    user.value = {
      username: data.username,
      org_id: data.org_id,
      role: data.role,
    }
    localStorage.setItem('auth_token', token.value)
    localStorage.setItem('refresh_token', refreshToken.value)
    localStorage.setItem('user_info', JSON.stringify(user.value))
  }

  function clearAuth() {
    token.value = ''
    refreshToken.value = ''
    user.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_info')
  }

  return { token, refreshToken, user, isLoggedIn, setAuth, clearAuth }
})
