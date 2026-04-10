<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-white">市场价格</h2>
        <p class="text-sm text-gray-500 mt-1">Market Prices · Real-time electricity market price data</p>
      </div>
    </div>

    <!-- 查询 -->
    <div class="glass-panel neon-border p-6">
      <div class="grid grid-cols-3 gap-4">
        <div>
          <ProvinceSelect v-model="form.province_code" label="省份" required />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">日期</label>
          <input v-model="form.market_date" type="date" class="input-glow text-sm">
        </div>
        <div class="flex items-end gap-3">
          <button @click="loadPrices" class="btn-neon flex-1" :disabled="loading">
            <i class="fas fa-spinner fa-spin mr-2" v-if="loading"></i>
            {{ loading ? '加载中...' : '查询价格' }}
          </button>
          <button @click="form.market_date = ''; loadPrices()" class="btn-outline">重置</button>
        </div>
      </div>
    </div>

    <!-- 价格概览 -->
    <div v-if="prices.length" class="grid grid-cols-4 gap-4">
      <div class="glass-panel p-4 rounded-xl border border-amber-500/10">
        <p class="text-xs text-gray-500 mb-1">记录总数</p>
        <p class="text-2xl font-bold font-mono text-amber-300">{{ total }}</p>
      </div>
      <div class="glass-panel p-4 rounded-xl border border-amber-500/10">
        <p class="text-xs text-gray-500 mb-1">最高价</p>
        <p class="text-2xl font-bold font-mono text-rose-300">¥{{ maxPrice?.toFixed(2) }}</p>
      </div>
      <div class="glass-panel p-4 rounded-xl border border-amber-500/10">
        <p class="text-xs text-gray-500 mb-1">最低价</p>
        <p class="text-2xl font-bold font-mono text-emerald-300">¥{{ minPrice?.toFixed(2) }}</p>
      </div>
      <div class="glass-panel p-4 rounded-xl border border-amber-500/10">
        <p class="text-xs text-gray-500 mb-1">均价</p>
        <p class="text-2xl font-bold font-mono text-amber-200">¥{{ avgPrice?.toFixed(2) }}</p>
      </div>
    </div>

    <!-- 价格走势：稀疏柱条（抽样）+ 蓝绿渐变 + 折线 -->
    <div v-if="prices.length" class="glass-panel neon-border p-6">
      <h3 class="text-base font-semibold text-white mb-4">价格走势图</h3>
      <div class="relative h-40 rounded-xl overflow-hidden bg-dark-200/25 ring-1 ring-cyan-500/15">
        <!-- grid + minmax 保证无论数据多少，柱条都有足够宽度并均匀铺满 -->
        <div class="absolute inset-0 px-1 opacity-[0.58]" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(18px, 1fr)); gap: 6px; align-items: end;">
          <div
            v-for="(p, i) in chartPrices"
            :key="p.id != null ? p.id : `ch-${i}-${p.timeslot}`"
            class="flex flex-col justify-end group relative z-0 min-h-0"
          >
            <div
              class="w-full rounded-t-md transition-opacity group-hover:opacity-90 shrink-0"
              :style="{
                height: priceHeight(p.price) + '%',
                minHeight: '6px',
                background: chartBarGradient,
                boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.08), 0 0 10px rgba(34,211,238,0.12)',
              }"
            ></div>
            <div
              class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 px-2 py-1 rounded-lg bg-dark-300/95 backdrop-blur text-xs font-mono text-cyan-50 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-20 shadow-lg border border-cyan-500/30 pointer-events-none"
            >
              {{ p.timeslot }} ¥{{ p.price.toFixed(2) }}
            </div>
          </div>
        </div>
        <svg
          class="absolute inset-0 z-10 h-full w-full pointer-events-none"
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          aria-hidden="true"
        >
          <defs>
            <linearGradient id="mvPriceLine" x1="0%" y1="0%" x2="100%" y2="0%" gradientUnits="objectBoundingBox">
              <stop offset="0%" stop-color="#0e7490" />
              <stop offset="50%" stop-color="#22d3ee" />
              <stop offset="100%" stop-color="#a7f3d0" />
            </linearGradient>
            <linearGradient id="mvPriceArea" x1="0" x2="0" y1="0" y2="1" gradientUnits="objectBoundingBox">
              <stop offset="0%" stop-color="#22d3ee" stop-opacity="0.35" />
              <stop offset="65%" stop-color="#0d9488" stop-opacity="0.14" />
              <stop offset="100%" stop-color="#042f2e" stop-opacity="0" />
            </linearGradient>
          </defs>
          <path v-if="chartAreaPath" :d="chartAreaPath" fill="url(#mvPriceArea)" />
          <polyline
            v-if="chartLinePoints"
            fill="none"
            stroke="url(#mvPriceLine)"
            stroke-width="1.4"
            stroke-linecap="round"
            stroke-linejoin="round"
            vector-effect="non-scaling-stroke"
            :points="chartLinePoints"
          />
        </svg>
      </div>
      <div class="flex justify-between text-xs text-gray-500 mt-2">
        <span>00:00</span><span>06:00</span><span>12:00</span><span>18:00</span><span>24:00</span>
      </div>
    </div>

    <!-- 表格 -->
    <div v-if="prices.length" class="glass-panel neon-border overflow-hidden">
      <div class="overflow-x-auto max-h-96">
        <table class="data-table">
          <thead class="sticky top-0 z-10">
            <tr><th>省份</th><th>日期</th><th>时段</th><th>价格(元/MWh)</th><th>来源</th></tr>
          </thead>
          <tbody>
            <tr v-for="p in prices" :key="p.id">
              <td>
                <span class="px-2 py-0.5 rounded text-xs font-semibold" :class="provinceBadgeClass(p.province_code)">
                  {{ p.province_code }}
                </span>
              </td>
              <td class="font-mono text-xs">{{ p.market_date }}</td>
              <td class="font-mono text-xs">{{ p.timeslot }}</td>
              <td class="num text-amber-200">¥{{ p.price.toFixed(2) }}</td>
              <td class="text-xs text-gray-500">{{ p.source || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="px-6 py-3 border-t border-amber-500/10 text-sm text-gray-500">共 {{ total }} 条记录</div>
    </div>

    <div v-if="!prices.length && !loading" class="glass-panel neon-border p-16 text-center">
      <i class="fas fa-chart-bar text-5xl text-gray-600 mb-4"></i>
      <p class="text-gray-500">输入省份查询市场价格数据</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { api } from '@/utils/api'
import ProvinceSelect from '@/components/form/ProvinceSelect.vue'
import { provinceBadgeClass } from '@/utils/provinceStyle'

/** 与看板一致：深青蓝 → 亮青 → 翠绿 */
const chartBarGradient =
  'linear-gradient(to top, rgba(12,74,110,0.92) 0%, rgba(8,145,178,0.82) 42%, rgba(16,185,129,0.78) 100%)'

/** 最多取前 96 点，再按步长抽样，避免柱条过密（约 24 根） */
const CHART_SOURCE_CAP = 96
const CHART_BAR_STRIDE = 4

const loading = ref(false)
const prices = ref([])
const total = ref(0)
const form = ref({ province_code: 'GD', market_date: '2026-04-08' })

const maxPrice = computed(() => prices.value.length ? Math.max(...prices.value.map(p => p.price)) : null)
const minPrice = computed(() => prices.value.length ? Math.min(...prices.value.map(p => p.price)) : null)
const avgPrice = computed(() => prices.value.length ? prices.value.reduce((s, p) => s + p.price, 0) / prices.value.length : null)

const chartPrices = computed(() => {
  const raw = prices.value.slice(0, CHART_SOURCE_CAP)
  return raw.filter((_, i) => i % CHART_BAR_STRIDE === 0)
})

const chartLinePoints = computed(() => {
  const slice = chartPrices.value
  if (!slice.length) return ''
  const n = slice.length
  return slice
    .map((p, i) => {
      const x = ((i + 0.5) / n) * 100
      const y = 100 - priceHeight(p.price)
      return `${x},${y}`
    })
    .join(' ')
})

const chartAreaPath = computed(() => {
  const slice = chartPrices.value
  if (!slice.length) return ''
  const n = slice.length
  const xs = []
  const ys = []
  for (let i = 0; i < n; i++) {
    xs.push(((i + 0.5) / n) * 100)
    ys.push(100 - priceHeight(slice[i].price))
  }
  let d = `M ${xs[0]},100 L ${xs[0]},${ys[0]}`
  for (let i = 1; i < n; i++) d += ` L ${xs[i]},${ys[i]}`
  d += ` L ${xs[n - 1]},100 Z`
  return d
})

function priceHeight(price) {
  const min = minPrice.value
  const max = maxPrice.value
  if (min == null || max == null || !Number.isFinite(min) || !Number.isFinite(max)) return 50
  const range = max - min
  if (range <= 0 || !Number.isFinite(range)) return 55
  const pct = ((Number(price) - min) / range) * 100
  return Math.max(6, Math.min(100, pct))
}

async function loadPrices() {
  if (!form.value.province_code) return
  loading.value = true
  try {
    const params = new URLSearchParams({ province_code: form.value.province_code, page_no: 1, page_size: 200 })
    if (form.value.market_date) params.set('market_date', form.value.market_date)
    const resp = await api.get('/api/v1/market/prices?' + params)
    if (resp.success) {
      prices.value = resp.data.items || []
      total.value = resp.data.total || 0
    }
  } catch (e) { console.warn(e.message) }
  finally { loading.value = false }
}
</script>
