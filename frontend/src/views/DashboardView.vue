<template>
  <div class="space-y-6 animate-fade-in">
    <!-- 统计卡片区 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="(stat, i) in stats" :key="stat.label"
           class="stat-glow-card group cursor-pointer"
           :style="{ animationDelay: i * 0.1 + 's' }">
        <div class="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-cyan-400 to-transparent opacity-55"></div>

        <div class="flex items-start justify-between mb-4">
          <div>
            <p class="text-xs text-gray-500 uppercase tracking-wider mb-1">{{ stat.label }}</p>
            <h3 class="text-3xl font-bold font-mono text-white group-hover:text-cyan-200 transition-colors">
              {{ stat.value }}
            </h3>
          </div>
          <div class="w-12 h-12 rounded-xl flex items-center justify-center"
               :class="stat.bgClass">
            <i :class="[stat.icon, 'text-xl', stat.iconClass]"></i>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <div class="flex-1 h-1 bg-dark-200 rounded-full overflow-hidden">
            <div class="h-full rounded-full bg-gradient-to-r from-sky-800 via-cyan-600 to-emerald-400 transition-all duration-1000"
                 :style="{ width: stat.percent + '%' }"></div>
          </div>
          <span class="text-xs text-gray-500">{{ stat.sub }}</span>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 申报趋势 -->
      <div class="lg:col-span-2 glass-panel neon-border p-6">
        <div class="flex items-center justify-between mb-6 flex-wrap gap-3">
          <div>
            <h3 class="text-base font-semibold text-white">{{ trendTitle }}</h3>
            <p class="text-xs text-gray-500 mt-1">{{ trendSubtitle }}</p>
          </div>
          <div class="flex gap-2" role="tablist">
            <button
              v-for="m in trendModes"
              :key="m.id"
              type="button"
              role="tab"
              :aria-selected="trendMode === m.id"
              class="px-3 py-1.5 rounded-lg text-xs border transition-colors"
              :class="trendMode === m.id
                ? 'bg-cyan-500/15 text-cyan-100 border-cyan-500/35'
                : 'bg-dark-200 text-gray-500 border-cyan-500/10 hover:border-cyan-500/30'"
              @click="trendMode = m.id"
            >
              {{ m.label }}
            </button>
          </div>
        </div>

        <!-- 申报趋势：仅柱条，蓝→绿渐变（无折线） -->
        <div class="min-h-[11rem] flex flex-col gap-2">
          <div class="relative h-40 flex gap-2 rounded-xl overflow-hidden bg-dark-200/25 ring-1 ring-cyan-500/15">
            <div
              v-for="bar in trendBars"
              :key="bar.key"
              class="flex-1 min-w-0 max-w-[14%] flex flex-col justify-end h-full relative z-0 group"
            >
              <div
                class="absolute inset-0 flex flex-col justify-end rounded-t overflow-hidden opacity-[0.72]"
              >
                <div
                  class="w-full rounded-t-lg transition-all duration-700 relative shrink-0"
                  :style="{
                    height: bar.pct + '%',
                    minHeight: bar.count > 0 ? '8px' : '2px',
                    background: bar.count > 0 ? trendBarGradient : 'rgba(14,116,144,0.1)',
                    boxShadow: bar.count > 0 ? 'inset 0 1px 0 rgba(255,255,255,0.08), 0 0 12px rgba(34,211,238,0.12)' : 'inset 0 1px 0 rgba(255,255,255,0.04)',
                  }"
                >
                  <div
                    v-if="bar.count > 0"
                    class="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-emerald-200/95 shadow-[0_0_10px_rgba(52,211,153,0.65)] ring-1 ring-cyan-400/50"
                    :style="{ opacity: 0.7 + (bar.pct / 100) * 0.3 }"
                  ></div>
                </div>
              </div>
              <div
                class="absolute -top-8 left-1/2 -translate-x-1/2 px-2 py-1 rounded-lg bg-dark-300/95 backdrop-blur text-xs text-cyan-50 font-mono opacity-0 group-hover:opacity-100 transition-all duration-200 whitespace-nowrap pointer-events-none z-20 shadow-lg border border-cyan-500/30"
              >
                {{ bar.count }} 条
              </div>
            </div>
          </div>
          <div class="flex gap-2 justify-between">
            <span
              v-for="bar in trendBars"
              :key="'lbl-' + bar.key"
              class="flex-1 min-w-0 max-w-[14%] text-[10px] text-gray-500 font-mono text-center leading-tight truncate"
            >{{ bar.label }}</span>
          </div>
        </div>
      </div>

      <!-- 十大重点省行情 -->
      <div class="glass-panel neon-border p-6 flex flex-col">
        <div class="mb-4">
          <h3 class="text-base font-semibold text-white">重点省份行情</h3>
          <p class="text-xs text-gray-500 mt-1">最新交易日均价 · Top 10</p>
        </div>

        <div class="space-y-2 flex-1 overflow-y-auto max-h-80 custom-scrollbar pr-1">
          <div
            v-for="(row, idx) in marketTopRows"
            :key="row.province_code"
            class="flex items-center justify-between p-3 rounded-xl bg-dark-200/50 border border-amber-500/10 hover:border-amber-400/30 transition-colors"
          >
            <div class="flex items-center gap-3 min-w-0">
              <span class="text-xs text-gray-600 w-5 shrink-0 font-mono">{{ String(idx + 1).padStart(2, '0') }}</span>
              <div class="min-w-0">
                <p class="text-xs text-gray-400 truncate">{{ row.province_name }}</p>
                <p class="text-sm font-mono text-white">{{ row.province_code }}</p>
              </div>
            </div>
            <div class="text-right shrink-0">
              <p class="text-sm font-mono text-amber-300">¥{{ row.avg_price?.toFixed(2) }}</p>
              <p class="text-[10px] text-gray-500">{{ latestDate }}</p>
            </div>
          </div>
          <p v-if="!marketTopRows.length" class="text-xs text-gray-500 text-center py-8">暂无市场数据</p>
        </div>

        <!-- 迷你行情：仅柱条，蓝绿渐变（无折线） -->
        <div class="mt-4 h-14 border-t border-cyan-500/15 pt-3 rounded-lg overflow-hidden flex items-stretch gap-1">
          <div
            v-for="(h, i) in sparkline"
            :key="'sp-' + i"
            class="flex-1 min-w-0 flex flex-col justify-end"
          >
            <div
              class="w-full rounded-t shrink-0 transition-opacity hover:opacity-95"
              :style="{
                height: h + '%',
                minHeight: '3px',
                background: sparkBarGradient,
                opacity: 0.62 + (i / Math.max(sparkline.length - 1, 1)) * 0.33,
                boxShadow: '0 0 8px rgba(34,211,238,0.1)',
              }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="glass-panel neon-border p-6">
      <h3 class="text-base font-semibold text-white mb-4">快捷操作</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <button
          v-for="action in quickActions"
          :key="action.label"
          type="button"
          class="flex flex-col items-center gap-2 p-4 rounded-xl bg-dark-200/50 border border-amber-500/10
                 hover:border-amber-400/40 hover:bg-amber-500/5 transition-all duration-300 group"
          @click="runQuickAction(action)"
        >
          <i :class="[action.icon, 'text-xl text-gray-500 group-hover:text-amber-400 transition-colors']"></i>
          <span class="text-xs text-gray-500 group-hover:text-gray-300 transition-colors">{{ action.label }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/utils/api'
import { formatNumber } from '@/utils/format'

const router = useRouter()
const dashboardData = ref(null)
const trendMode = ref('day')

const trendModes = [
  { id: 'day', label: '日' },
  { id: 'week', label: '周' },
  { id: 'month', label: '月' },
]

const stats = computed(() => {
  const d = dashboardData.value || {}
  const decl = d.declarations || {}
  const ctr = d.contracts || {}
  const task = d.reconcile_tasks || {}

  return [
    {
      label: '总申报数',
      value: formatNumber(decl.total),
      sub: decl.submitted_today ? `今日 +${decl.submitted_today}` : '暂无今日',
      icon: 'fas fa-file-alt',
      iconClass: 'text-amber-400',
      bgClass: 'bg-amber-500/10',
      percent: Math.min((decl.total / 50) * 100, 100),
    },
    {
      label: '合同台账',
      value: formatNumber(ctr.total),
      sub: ctr.active ? `活跃 ${ctr.active} 个` : '暂无活跃',
      icon: 'fas fa-file-contract',
      iconClass: 'text-emerald-400',
      bgClass: 'bg-emerald-500/10',
      percent: Math.min((ctr.total / 10) * 100, 100),
    },
    {
      label: '结算任务',
      value: formatNumber(task.total),
      sub: task.pending ? `待处理 ${task.pending} 个` : '暂无待处理',
      icon: 'fas fa-calculator',
      iconClass: 'text-amber-300',
      bgClass: 'bg-amber-500/10',
      percent: Math.min((task.total / 10) * 100, 100),
    },
    {
      label: '审计日志',
      value: formatNumber(d.audit_logs?.total || 0),
      sub: '全量追踪',
      icon: 'fas fa-clipboard-list',
      iconClass: 'text-emerald-300',
      bgClass: 'bg-emerald-500/10',
      percent: Math.min(((d.audit_logs?.total || 0) / 30) * 100, 100),
    },
  ]
})

const latestDate = computed(() => dashboardData.value?.market?.latest_date || '—')

const marketTopRows = computed(() => dashboardData.value?.market_top_provinces || [])

const trendTitle = computed(() => {
  if (trendMode.value === 'day') return '申报趋势（按日）'
  if (trendMode.value === 'week') return '申报趋势（按周）'
  return '申报趋势（按月）'
})

const trendSubtitle = computed(() => {
  if (trendMode.value === 'day') return '近 7 个自然日'
  if (trendMode.value === 'week') return '近约 4 周'
  return '近 6 个月'
})

function buildDailyBars(raw) {
  const map = Object.fromEntries((raw || []).map((t) => [t.date, t.count]))
  const out = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date()
    d.setHours(0, 0, 0, 0)
    d.setDate(d.getDate() - i)
    const key = d.toISOString().slice(0, 10)
    out.push({ key: 'd-' + key, label: key.slice(5), count: map[key] ?? 0 })
  }
  return out
}

const trendBars = computed(() => {
  const d = dashboardData.value
  if (!d) return []

  let rows = []
  if (trendMode.value === 'day') {
    rows = buildDailyBars(d.declaration_trend_7d)
  } else if (trendMode.value === 'week') {
    rows = (d.declaration_trend_weeks || []).map((t, i) => ({
      key: 'w-' + (t.period || i),
      label: (t.period || '').replace(/^(\d{4})-W(\d+)$/, '$1-W$2') || 'W' + (i + 1),
      count: t.count ?? 0,
    }))
  } else {
    rows = (d.declaration_trend_months || []).map((t, i) => ({
      key: 'm-' + (t.period || i),
      label: t.period || '—',
      count: t.count ?? 0,
    }))
  }

  if (!rows.length) {
    return [{ key: 'empty', label: '—', count: 0, pct: 0 }]
  }

  const max = Math.max(...rows.map((r) => r.count), 1)
  return rows.map((r) => ({
    ...r,
    pct: Math.max((r.count / max) * 100, r.count > 0 ? 8 : 0),
  }))
})

/** 底部深蓝青 → 中部亮青 → 顶部翠绿（蓝绿渐变） */
const trendBarGradient =
  'linear-gradient(to top, rgba(12,74,110,0.92) 0%, rgba(8,145,178,0.82) 42%, rgba(16,185,129,0.78) 100%)'

const sparkBarGradient =
  'linear-gradient(to top, rgba(14,116,144,0.88) 0%, rgba(6,182,212,0.75) 48%, rgba(52,211,153,0.72) 100%)'

const sparkline = ref([40, 55, 45, 60, 58, 65, 70, 68, 75, 72, 80, 78, 85])

watch(marketTopRows, (rows) => {
  if (rows?.length) {
    const vals = rows.slice(0, 12).map((r) => Math.min(100, 20 + (r.avg_price % 120)))
    if (vals.length) sparkline.value = vals
  }
}, { immediate: true })

const quickActions = [
  { label: '新建申报', icon: 'fas fa-plus-circle', path: '/trades', hint: 'declaration' },
  { label: '创建合同', icon: 'fas fa-file-signature', path: '/contracts', hint: 'create' },
  { label: '结算任务', icon: 'fas fa-calculator', path: '/settlement', hint: 'scroll' },
  { label: '偏差分析', icon: 'fas fa-chart-pie', path: '/risk', hint: 'risk' },
  { label: '市场行情', icon: 'fas fa-chart-line', path: '/market', hint: 'market' },
  { label: '审计日志', icon: 'fas fa-history', path: '/audit', hint: 'audit' },
]

function runQuickAction(action) {
  if (action.path) {
    router.push(action.path)
  }
  if (action.hint === 'create') {
    sessionStorage.setItem('open_contract_create', '1')
  }
  if (action.hint === 'declaration') {
    sessionStorage.setItem('focus_declaration_form', '1')
  }
  if (action.hint === 'scroll') {
    sessionStorage.setItem('focus_settlement', '1')
  }
}

async function loadDashboard() {
  try {
    const resp = await api.get('/api/v1/dashboard/stats')
    if (resp.success) {
      dashboardData.value = resp.data
    }
  } catch (e) {
    console.warn('看板数据加载失败:', e.message)
  }
}

onMounted(() => {
  loadDashboard()
})
</script>
