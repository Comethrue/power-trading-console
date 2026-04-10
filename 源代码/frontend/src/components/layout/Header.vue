<template>
  <header class="h-16 flex items-center justify-between px-6 border-b border-cyan-500/10 relative z-20 glass-panel">
    <div class="flex items-center gap-4">
      <div>
        <h2 class="text-base font-bold text-white">{{ currentPageTitle }}</h2>
        <p class="text-xs text-gray-500">{{ currentTime }}</p>
      </div>
    </div>

    <div class="flex items-center gap-4">
      <!-- 全局搜索 -->
      <div class="relative" ref="searchRootRef">
        <div class="relative">
          <input
            v-model="searchQuery"
            type="search"
            placeholder="搜索页面、功能…"
            autocomplete="off"
            class="input-glow w-52 md:w-64 pl-10 pr-4 py-2 text-sm rounded-xl"
            @keydown.enter.prevent="goFirstResult"
            @focus="searchOpen = true"
            @click.stop
          />
          <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-xs pointer-events-none"></i>
        </div>
        <Transition name="dropdown-fade">
          <div
            v-show="searchOpen && filteredSearch.length"
            class="absolute right-0 mt-1 w-72 max-h-64 overflow-y-auto rounded-xl border border-cyan-500/25 bg-dark-100/97 backdrop-blur-xl shadow-xl z-[10050] py-1"
          >
            <button
              v-for="item in filteredSearch"
              :key="item.path"
              type="button"
              class="w-full text-left px-3 py-2 text-sm hover:bg-cyan-500/10 text-gray-300 flex flex-col gap-0.5"
              @click.stop="navigateSearch(item.path)"
            >
              <span class="text-white">{{ item.label }}</span>
              <span class="text-[10px] text-gray-500">{{ item.hint }}</span>
            </button>
          </div>
        </Transition>
      </div>

      <!-- 系统状态 -->
      <div
        class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-dark-200/60 border border-cyan-500/10"
        :title="statusTitle"
      >
        <span class="relative flex h-2.5 w-2.5">
          <span
            v-if="health.status === 'ok'"
            class="absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75 animate-ping"
          ></span>
          <span class="relative inline-flex rounded-full h-2.5 w-2.5" :class="statusDotClass"></span>
        </span>
        <span class="text-[11px] text-gray-400 hidden sm:inline max-w-[8rem] truncate">{{ statusLabel }}</span>
      </div>

      <!-- 用户信息（专业组织展示） -->
      <div class="flex items-center gap-3 pl-4 border-l border-cyan-500/10">
        <div class="text-right">
          <p class="text-sm font-semibold text-gray-200">{{ authStore.user?.username || '未登录' }}</p>
          <p class="text-xs text-gray-500">{{ orgDisplayText }}</p>
        </div>
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-sky-600 to-cyan-600 flex items-center justify-center text-white font-bold text-sm shadow-lg" style="box-shadow: 0 2px 12px rgba(14,165,233,0.28)">
          {{ (authStore.user?.username || 'G')[0].toUpperCase() }}
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSystemHealth } from '@/composables/useSystemHealth'
import { formatOrgLine } from '@/utils/orgDisplay'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const health = useSystemHealth(20000)

const searchQuery = ref('')
const searchOpen = ref(false)
const searchRootRef = ref(null)

const searchIndex = [
  { path: '/dashboard', label: '数据看板', hint: '统计、趋势、各省均价', keywords: '看板 首页 统计 dashboard' },
  { path: '/auth', label: '认证管理', hint: '登录、注册、令牌', keywords: '登录 注册 token 认证' },
  { path: '/contracts', label: '合同台账', hint: '合同列表与新建', keywords: '合同 contract' },
  { path: '/trades', label: '交易申报', hint: '现货申报', keywords: '交易 申报 trade' },
  { path: '/risk', label: '风险管理', hint: '偏差风险', keywords: '风险 risk' },
  { path: '/settlement', label: '结算对账', hint: '结算任务', keywords: '结算 settlement' },
  { path: '/market', label: '市场价格', hint: '现货电价曲线', keywords: '市场 价格 电价 market' },
  { path: '/external', label: '外部数据', hint: '交易中心、计量', keywords: '外部 集成 integration' },
  { path: '/rules', label: '规则配置', hint: '省份交易规则', keywords: '规则 rule' },
  { path: '/audit', label: '审计日志', hint: '操作记录', keywords: '审计 audit 日志' },
]

const filteredSearch = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return searchIndex
  return searchIndex.filter(
    (item) =>
      item.label.toLowerCase().includes(q) ||
      item.hint.toLowerCase().includes(q) ||
      item.keywords.toLowerCase().includes(q) ||
      item.path.includes(q)
  )
})

const orgDisplayText = computed(() => {
  if (!authStore.user?.org_id) return '游客'
  return formatOrgLine(authStore.user.org_id)
})

function navigateSearch(path) {
  router.push(path)
  searchOpen.value = false
  searchQuery.value = ''
}

function goFirstResult() {
  const list = filteredSearch.value
  if (list.length) navigateSearch(list[0].path)
}

function onDocClick(e) {
  if (!searchRootRef.value?.contains(e.target)) searchOpen.value = false
}

const pageTitles = {
  '/dashboard': '数据看板',
  '/auth': '认证管理',
  '/contracts': '合同台账',
  '/trades': '交易申报',
  '/risk': '风险管理',
  '/settlement': '结算对账',
  '/market': '市场价格',
  '/external': '外部数据',
  '/rules': '规则配置',
  '/audit': '审计日志',
}

const currentPageTitle = computed(() => pageTitles[route.path] || '控制台')

const currentTime = ref('')
let timer = null

function updateTime() {
  const now = new Date()
  currentTime.value = now
    .toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    })
    .replace(/\//g, '-')
}

const statusDotClass = computed(() => {
  if (health.status === 'ok') return 'bg-emerald-400'
  if (health.status === 'error') return 'bg-rose-400'
  return 'bg-sky-400'
})

const statusLabel = computed(() => {
  if (health.status === 'ok') return 'API 正常'
  if (health.status === 'error') return 'API 异常'
  return '检测中…'
})

const statusTitle = computed(() => {
  const parts = [health.detail, health.checkedAt && `上次检测 ${health.checkedAt}`].filter(Boolean)
  return parts.join(' · ') || '系统状态'
})

watch(
  () => route.path,
  () => {
    searchOpen.value = false
  }
)

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
  document.addEventListener('click', onDocClick)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  document.removeEventListener('click', onDocClick)
})
</script>

<style scoped>
.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity 0.12s ease, transform 0.12s ease;
}
.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
