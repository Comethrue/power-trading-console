<template>
  <aside class="w-64 flex-shrink-0 flex flex-col h-full relative z-20">
    <!-- Logo区域 -->
    <div class="px-6 py-6 border-b border-cyan-500/10">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-sky-600 to-cyan-600 flex items-center justify-center shadow-lg" style="box-shadow: 0 4px 16px rgba(14,165,233,0.28)">
          <svg class="w-6 h-6 text-white" viewBox="0 0 24 24" fill="currentColor">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
          </svg>
        </div>
        <div>
          <h1 class="text-sm font-bold text-gradient">PowerGrid</h1>
          <p class="text-[10px] text-gray-500 tracking-widest uppercase">Trading Console</p>
        </div>
      </div>
    </div>

    <!-- 菜单 -->
    <nav class="flex-1 px-3 py-4 overflow-y-auto custom-scrollbar">
      <div class="space-y-1">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="menu-item"
          :class="{ active: $route.path === item.path }"
        >
          <div class="menu-indicator" v-if="$route.path === item.path"></div>
          <i :class="[item.icon, 'menu-icon']"></i>
          <span class="menu-text">{{ item.label }}</span>
          <span v-if="item.badge" class="menu-badge">{{ item.badge }}</span>
        </router-link>
      </div>
    </nav>

    <!-- 底部状态 -->
    <div class="px-4 py-4 border-t border-cyan-500/10">
      <div class="glass-panel p-3 rounded-xl">
        <div class="flex items-center gap-2 mb-2">
          <span class="relative flex h-2 w-2">
            <span
              v-if="health.status === 'ok'"
              class="absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75 animate-ping"
            ></span>
            <span class="relative inline-flex rounded-full h-2 w-2" :class="health.status === 'ok' ? 'bg-emerald-400' : health.status === 'error' ? 'bg-rose-400' : 'bg-amber-400'"></span>
          </span>
          <span class="text-[10px] text-gray-500 font-medium">系统状态</span>
          <span class="text-[10px] text-gray-600 ml-auto">{{ health.status === 'ok' ? '正常' : health.status === 'error' ? '异常' : '检测中' }}</span>
        </div>
        <div class="flex items-center gap-2 text-[9px] text-gray-600">
          <i class="fas fa-clock w-3 text-center"></i>
          <span class="shrink-0">{{ health.checkedAt }}</span>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { useSystemHealth } from '@/composables/useSystemHealth'

const health = useSystemHealth(20000)

const menuItems = [
  { path: '/dashboard', label: '数据看板', icon: 'fas fa-chart-line', badge: null },
  { path: '/auth', label: '认证管理', icon: 'fas fa-shield-alt', badge: null },
  { path: '/contracts', label: '合同台账', icon: 'fas fa-file-contract', badge: null },
  { path: '/trades', label: '交易申报', icon: 'fas fa-exchange-alt', badge: null },
  { path: '/risk', label: '风险管理', icon: 'fas fa-exclamation-triangle', badge: null },
  { path: '/settlement', label: '结算对账', icon: 'fas fa-calculator', badge: null },
  { path: '/market', label: '市场价格', icon: 'fas fa-chart-bar', badge: null },
  { path: '/external', label: '外部数据', icon: 'fas fa-plug', badge: null },
  { path: '/rules', label: '规则配置', icon: 'fas fa-cogs', badge: null },
  { path: '/audit', label: '审计日志', icon: 'fas fa-clipboard-list', badge: null },
]
</script>

<style scoped>
.menu-item {
  @apply relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm
         text-gray-400 transition-all duration-300;
  @apply hover:bg-cyan-500/10 hover:text-cyan-200;
}

.menu-item.active {
  @apply bg-cyan-500/10 text-cyan-200;
}

.menu-indicator {
  @apply absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 rounded-r-full;
  @apply bg-gradient-to-b from-cyan-400 to-sky-600;
  box-shadow: 0 0 10px rgba(34, 211, 238, 0.45);
}

.menu-icon {
  @apply w-5 text-center text-sm;
}

.menu-text {
  @apply flex-1 font-medium;
}

.menu-badge {
  @apply px-2 py-0.5 rounded-full text-[10px] font-bold
         bg-cyan-500/20 text-cyan-200;
}

.router-link-active.menu-item {
  @apply bg-cyan-500/10 text-cyan-200;
}
</style>
