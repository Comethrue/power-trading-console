<template>
  <div class="max-w-2xl mx-auto space-y-6 animate-fade-in">
    <!-- 登录 / 注册 -->
    <div class="glass-panel neon-border p-8">
      <div class="text-center mb-6">
        <div class="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-amber-600 to-amber-700 flex items-center justify-center mb-4 shadow-lg" style="box-shadow: 0 4px 24px rgba(245,158,11,0.3)">
          <i class="fas fa-shield-alt text-2xl text-white"></i>
        </div>
        <h2 class="text-xl font-bold text-white">身份认证</h2>
        <p class="text-sm text-gray-500 mt-1">Authentication Portal</p>
      </div>

      <div class="flex rounded-xl bg-dark-200/60 p-1 mb-6 border border-amber-500/10">
        <button
          type="button"
          class="flex-1 rounded-lg py-2.5 text-sm font-medium transition-all"
          :class="authTab === 'login' ? 'bg-amber-500/20 text-amber-300 shadow-inner' : 'text-gray-500 hover:text-gray-300'"
          @click="authTab = 'login'"
        >
          登录
        </button>
        <button
          type="button"
          class="flex-1 rounded-lg py-2.5 text-sm font-medium transition-all"
          :class="authTab === 'register' ? 'bg-emerald-500/20 text-emerald-300 shadow-inner' : 'text-gray-500 hover:text-gray-300'"
          @click="authTab = 'register'"
        >
          注册
        </button>
      </div>

      <!-- 登录 -->
      <form v-show="authTab === 'login'" @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-xs text-gray-500 mb-2 uppercase tracking-wider">用户名</label>
          <input v-model="loginForm.username" type="text" placeholder="请输入用户名" class="input-glow" required />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-2 uppercase tracking-wider">密码</label>
          <input v-model="loginForm.password" type="password" placeholder="请输入密码" class="input-glow" required />
        </div>
        <button type="submit" class="btn-neon w-full py-3" :disabled="loading">
          <i class="fas fa-sign-in-alt mr-2"></i>
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <!-- 注册 -->
      <form v-show="authTab === 'register'" @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label class="block text-xs text-gray-500 mb-2 uppercase tracking-wider">用户名</label>
          <input
            v-model="registerForm.username"
            type="text"
            autocomplete="username"
            placeholder="3–32 位，字母数字下划线"
            class="input-glow"
            required
          />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-2 uppercase tracking-wider">密码</label>
          <input
            v-model="registerForm.password"
            type="password"
            autocomplete="new-password"
            placeholder="至少 8 位"
            class="input-glow"
            required
          />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-2 uppercase tracking-wider">确认密码</label>
          <input
            v-model="registerForm.password2"
            type="password"
            autocomplete="new-password"
            placeholder="再次输入密码"
            class="input-glow"
            required
          />
        </div>
        <label class="flex items-start gap-2 text-xs text-gray-500 cursor-pointer select-none">
          <input v-model="registerForm.agree" type="checkbox" class="mt-0.5 rounded border-amber-500/30" />
          <span>我已阅读并同意平台服务条款与隐私说明（演示环境）</span>
        </label>
        <p v-if="registerError" class="text-xs text-rose-400">{{ registerError }}</p>
        <button type="submit" class="btn-neon w-full py-3" :disabled="loading">
          <i class="fas fa-user-plus mr-2"></i>
          {{ loading ? '提交中...' : '注册并登录' }}
        </button>
        <p class="text-[11px] text-gray-600 text-center">注册成功后将自动写入令牌，与登录使用同一套会话机制。</p>
      </form>

      <!-- 测试账号（专业展示） -->
      <div v-if="authTab === 'login'" class="mt-6 p-4 rounded-xl bg-dark-200/50 border border-amber-500/10">
        <p class="text-xs text-gray-500 mb-3">演示账号（点击快速登录）</p>
        <div class="grid grid-cols-3 gap-2">
          <button
            v-for="acc in testAccounts"
            :key="acc.username"
            type="button"
            @click="fillAccount(acc)"
            class="p-2.5 rounded-lg bg-dark-300 border border-amber-500/10 hover:border-amber-400/30 transition-all text-left"
          >
            <p class="text-xs font-semibold text-amber-300 mb-0.5">{{ acc.name }}</p>
            <p class="text-[10px] text-gray-500 leading-tight">{{ acc.orgDisplay }}</p>
            <p class="text-[9px] text-gray-600 font-mono mt-0.5">{{ acc.username }}</p>
          </button>
        </div>
      </div>

      <!-- 登录结果（专业组织信息） -->
      <div v-if="loginResult" class="mt-6">
        <div class="p-4 rounded-xl bg-dark-200/50 border border-emerald-500/20">
          <div class="flex items-center gap-2 mb-3">
            <i class="fas fa-check-circle text-emerald-400 text-sm"></i>
            <span class="text-sm text-emerald-400 font-semibold">登录成功</span>
          </div>
          <ul class="space-y-2 text-sm text-gray-300">
            <li class="flex justify-between gap-4"><span class="text-gray-500">交易单元</span><span>{{ loginResult.orgDisplay }}</span></li>
            <li class="flex justify-between gap-4"><span class="text-gray-500">单元编号</span><span class="font-mono text-amber-300">{{ loginResult.orgCode }}</span></li>
            <li class="flex justify-between gap-4"><span class="text-gray-500">角色</span><span>{{ loginResult.role }}</span></li>
            <li class="flex justify-between gap-4">
              <span class="text-gray-500">访问凭证</span><span class="text-amber-300">已安全保存在本机</span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Token 管理 -->
    <div class="glass-panel neon-border p-6">
      <h3 class="text-base font-semibold text-white mb-2">会话与安全</h3>
      <p class="text-xs text-gray-500 mb-4">访问令牌不会完整显示在页面上，可通过下方按钮复制到剪贴板（请妥善保管）。</p>
      <div class="space-y-4">
        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="text-xs text-gray-500">访问令牌 Access Token</label>
            <button type="button" class="text-xs text-amber-300 hover:text-amber-200" @click="revealAccess = !revealAccess">
              {{ revealAccess ? '隐藏' : '临时查看' }}
            </button>
          </div>
          <div
            class="input-glow text-sm font-mono break-all min-h-[2.75rem] flex items-center"
            :class="revealAccess ? 'text-gray-200' : 'text-gray-500'"
          >
            {{ maskedAccess }}
          </div>
          <div class="flex gap-2 mt-2">
            <button type="button" class="btn-outline text-xs flex-1 py-2" @click="copyText(tokenForm.accessToken, 'Access Token')">
              <i class="fas fa-copy mr-1"></i>复制 Access Token
            </button>
          </div>
        </div>
        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="text-xs text-gray-500">刷新令牌 Refresh Token</label>
            <button type="button" class="text-xs text-amber-300 hover:text-amber-200" @click="revealRefresh = !revealRefresh">
              {{ revealRefresh ? '隐藏' : '临时查看' }}
            </button>
          </div>
          <div
            class="input-glow text-sm font-mono break-all min-h-[2.75rem] flex items-center"
            :class="revealRefresh ? 'text-gray-200' : 'text-gray-500'"
          >
            {{ maskedRefresh }}
          </div>
          <div class="flex gap-2 mt-2">
            <button type="button" class="btn-outline text-xs flex-1 py-2" @click="copyText(tokenForm.refreshToken, 'Refresh Token')">
              <i class="fas fa-copy mr-1"></i>复制 Refresh Token
            </button>
          </div>
        </div>
        <div class="flex gap-3 flex-wrap">
          <button type="button" @click="handleRefresh" class="btn-outline flex-1 min-w-[8rem]" :disabled="loading">
            <i class="fas fa-redo mr-2"></i>刷新Token
          </button>
          <button type="button" @click="handleWhoami" class="btn-outline flex-1 min-w-[8rem]" :disabled="loading">
            <i class="fas fa-user-check mr-2"></i>验证身份
          </button>
          <button type="button" @click="handleLogout" class="btn-outline flex-1 min-w-[8rem]" :disabled="loading">
            <i class="fas fa-sign-out-alt mr-2"></i>退出登录
          </button>
        </div>
        <div v-if="whoamiResult" class="p-4 rounded-xl border border-emerald-500/15 bg-emerald-500/5 space-y-2">
          <p class="text-xs text-emerald-400 font-semibold">当前会话</p>
          <ul class="text-sm text-gray-300 space-y-1">
            <li
              v-for="(val, key) in whoamiFlat"
              :key="key"
              class="flex justify-between gap-4 border-b border-amber-500/10 pb-1 last:border-0"
            >
              <span class="text-gray-500">{{ key }}</span>
              <span class="text-right font-mono text-xs">{{ val }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { api } from '@/utils/api'
import { useAuthStore } from '@/stores/auth'
import { formatOrgLine, formatOrgCodeOnly } from '@/utils/orgDisplay'

const authStore = useAuthStore()
const loading = ref(false)
const authTab = ref('login')
const loginResult = ref(null)
const whoamiResult = ref(null)
const revealAccess = ref(false)
const revealRefresh = ref(false)
const registerError = ref('')

// 登录表单（保留原用户名）
const loginForm = ref({ username: 'admin', password: 'admin123' })
const registerForm = ref({
  username: '',
  password: '',
  password2: '',
  agree: false,
})

const tokenForm = ref({
  accessToken: typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') || '' : '',
  refreshToken: typeof localStorage !== 'undefined' ? localStorage.getItem('refresh_token') || '' : '',
})

// 专业化的测试账号展示（登录仍使用原用户名）
const testAccounts = [
  {
    username: 'admin',
    password: 'admin123',
    name: '系统管理员',
    role: 'admin',
    orgId: 0,
    orgDisplay: '体系运营管理中心',
    orgCode: 'SYS-ROOT',
  },
  {
    username: 'user1001',
    password: 'pass1001',
    name: '华南交易单元',
    role: 'trader',
    orgId: 1001,
    orgDisplay: '华南电力交易单元',
    orgCode: 'ORG-SPS-2026-001',
  },
  {
    username: 'user1002',
    password: 'pass1002',
    name: '华东交易单元',
    role: 'trader',
    orgId: 1002,
    orgDisplay: '华东电力交易单元',
    orgCode: 'ORG-EPS-2026-002',
  },
]

watch(authTab, () => {
  registerError.value = ''
})

function maskToken(t) {
  if (!t || t.length < 16) return t ? '••••••••（长度过短）' : '（未持有）'
  return `${t.slice(0, 10)} … ${t.slice(-6)}`
}

const maskedAccess = computed(() => {
  const t = tokenForm.value.accessToken
  if (!t) return '（未登录或已清除）'
  return revealAccess.value ? t : maskToken(t)
})

const maskedRefresh = computed(() => {
  const t = tokenForm.value.refreshToken
  if (!t) return '（未持有刷新令牌）'
  return revealRefresh.value ? t : maskToken(t)
})

const whoamiFlat = computed(() => {
  const o = whoamiResult.value
  if (!o || typeof o !== 'object') return {}
  const out = {}
  const label = {
    username: '用户名',
    org_id: '交易单元',
    org_code: '单元编号',
    role: '角色',
    sub: '主体标识',
  }
  for (const [k, v] of Object.entries(o)) {
    if (v === null || v === undefined) continue
    if (k === 'org_id') {
      out[label[k] || k] = formatOrgLine(v)
    } else if (k === 'org_id') {
      out['交易单元'] = formatOrgLine(v)
      out['单元编号'] = formatOrgCodeOnly(v)
    } else {
      out[label[k] || k] = typeof v === 'object' ? '—' : String(v)
    }
  }
  return out
})

function fillAccount(acc) {
  loginForm.value.username = acc.username
  loginForm.value.password = acc.password
}

function applyAuthPayload(data) {
  // 展示专业化的组织信息
  const orgId = data.org_id
  loginResult.value = {
    ...data,
    orgDisplay: formatOrgLine(orgId),
    orgCode: formatOrgCodeOnly(orgId),
  }
  authStore.setAuth(data)
  tokenForm.value.accessToken = data.access_token
  tokenForm.value.refreshToken = data.refresh_token
  revealAccess.value = false
  revealRefresh.value = false
}

async function copyText(text, label) {
  if (!text) {
    alert('没有可复制的内容')
    return
  }
  try {
    await navigator.clipboard.writeText(text)
    alert(`${label} 已复制到剪贴板`)
  } catch {
    alert('复制失败，请手动选择文本复制')
  }
}

async function handleLogin() {
  loading.value = true
  try {
    const resp = await api.post('/api/v1/auth/login', loginForm.value)
    if (resp.success) {
      applyAuthPayload(resp.data)
    }
  } catch (e) {
    alert('登录失败: ' + e.message)
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  registerError.value = ''
  if (!registerForm.value.agree) {
    registerError.value = '请勾选同意条款后继续'
    return
  }
  if (registerForm.value.password !== registerForm.value.password2) {
    registerError.value = '两次输入的密码不一致'
    return
  }
  if (registerForm.value.password.length < 8) {
    registerError.value = '密码至少 8 位'
    return
  }
  loading.value = true
  try {
    const resp = await api.post('/api/v1/auth/register', {
      username: registerForm.value.username.trim(),
      password: registerForm.value.password,
    })
    if (resp.success && resp.data) {
      applyAuthPayload(resp.data)
      loginForm.value.username = resp.data.username || registerForm.value.username.trim()
      loginForm.value.password = ''
      registerForm.value.password = ''
      registerForm.value.password2 = ''
      authTab.value = 'login'
      alert('注册成功，已自动登录。也可使用同一账号密码在「登录」页签再次登录。')
    }
  } catch (e) {
    registerError.value = e.message || '注册失败'
  } finally {
    loading.value = false
  }
}

async function handleRefresh() {
  if (!tokenForm.value.refreshToken) return
  loading.value = true
  try {
    const resp = await api.post('/api/v1/auth/refresh', { refresh_token: tokenForm.value.refreshToken })
    if (resp.success) {
      authStore.setAuth(resp.data)
      tokenForm.value.accessToken = resp.data.access_token
      tokenForm.value.refreshToken = resp.data.refresh_token
      revealAccess.value = false
      revealRefresh.value = false
      alert('Token 刷新成功')
    }
  } catch (e) {
    alert('刷新失败: ' + e.message)
  } finally {
    loading.value = false
  }
}

async function handleWhoami() {
  if (!tokenForm.value.accessToken) {
    alert('请先登录或注册以获取访问令牌')
    return
  }
  loading.value = true
  try {
    const resp = await api.get('/api/v1/auth/whoami')
    whoamiResult.value = resp.data
  } catch (e) {
    alert('验证失败: ' + e.message)
  } finally {
    loading.value = false
  }
}

async function handleLogout() {
  loading.value = true
  try {
    if (tokenForm.value.refreshToken) {
      await api.post('/api/v1/auth/logout', { refresh_token: tokenForm.value.refreshToken })
    }
    authStore.clearAuth()
    loginResult.value = null
    whoamiResult.value = null
    tokenForm.value = { accessToken: '', refreshToken: '' }
    revealAccess.value = false
    revealRefresh.value = false
  } catch (e) {
    console.warn('退出失败:', e.message)
  } finally {
    loading.value = false
  }
}
</script>
