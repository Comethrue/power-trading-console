<template>
  <div class="space-y-6 animate-fade-in">
    <div>
      <h2 class="text-xl font-bold text-white">外部数据源</h2>
      <p class="text-sm text-gray-500 mt-1">External Integrations · Trading center and metering system data</p>
    </div>

    <!-- 连接状态 -->
    <div class="glass-panel neon-border p-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center">
            <i class="fas fa-server text-amber-300 text-xl"></i>
          </div>
          <div>
            <h3 class="text-base font-semibold text-white">系统连接状态</h3>
            <p class="text-xs text-gray-500">检查交易中心、计量系统连通性</p>
          </div>
        </div>
        <button type="button" @click="checkStatus" class="btn-outline" :disabled="loading">
          <i class="fas fa-spinner fa-spin mr-2" v-if="loading"></i>
          <i class="fas fa-sync-alt mr-2" v-else></i>
          检测连接
        </button>
      </div>

      <div v-if="status" class="mt-4 space-y-3">
        <div
          v-if="status.error"
          class="rounded-xl border border-red-500/30 bg-red-500/5 px-4 py-3 text-sm text-red-300"
        >
          <i class="fas fa-exclamation-circle mr-2"></i>{{ status.error }}
        </div>
        <div v-else class="grid gap-3 md:grid-cols-2">
          <div
            v-for="block in statusBlocks"
            :key="block.key"
            class="rounded-xl border border-amber-500/15 bg-dark-200/40 p-4"
          >
            <div class="flex items-center justify-between gap-2">
              <span class="text-sm font-medium text-white">{{ block.label }}</span>
              <span
                class="rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide"
                :class="block.configured ? 'bg-emerald-500/15 text-emerald-300' : 'bg-amber-500/15 text-amber-300'"
              >
                {{ block.configured ? '已配置' : '未配置' }}
              </span>
            </div>
            <p class="mt-2 text-xs text-gray-500">
              请求超时：<span class="font-mono text-gray-400">{{ block.timeout_sec }}s</span>
            </p>
            <p class="mt-1 text-[11px] leading-relaxed text-gray-600">
              {{ block.hint }}
            </p>
          </div>
        </div>
        <details v-if="statusRaw" class="group rounded-xl border border-amber-500/10 bg-dark-300/30">
          <summary
            class="cursor-pointer list-none px-4 py-2 text-xs text-gray-500 hover:text-gray-400 [&::-webkit-details-marker]:hidden"
          >
            <span class="inline-flex items-center gap-2">
              <i class="fas fa-code text-[10px] text-amber-500/60"></i>
              查看原始响应（调试）
              <i class="fas fa-chevron-down text-[9px] transition group-open:rotate-180"></i>
            </span>
          </summary>
          <pre
            class="max-h-48 overflow-auto border-t border-amber-500/10 p-3 font-mono text-[10px] leading-relaxed text-gray-500"
          >{{ statusRaw }}</pre>
        </details>
      </div>
    </div>

    <!-- 交易中心 -->
    <div class="glass-panel neon-border p-6">
      <div class="flex items-center gap-4 mb-4">
        <div class="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center">
          <i class="fas fa-landmark text-emerald-300"></i>
        </div>
        <div>
          <h3 class="text-base font-semibold text-white">交易中心</h3>
          <p class="text-xs text-gray-500">从交易中心拉取清算快照和电价数据</p>
        </div>
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs text-gray-500 mb-1">交易日</label>
          <input v-model="tcForm.trade_date" type="date" class="input-glow text-sm" />
        </div>
        <div>
          <ProvinceSelect v-model="tcForm.province_code" label="电价省份" required />
        </div>
        <button type="button" @click="fetchClearing" class="btn-neon" :disabled="loading">
          <i class="fas fa-download mr-2"></i>拉取清算快照
        </button>
        <button type="button" @click="fetchExternalPrices" class="btn-outline" :disabled="loading">
          <i class="fas fa-chart-line mr-2"></i>拉取外部电价
        </button>
      </div>
      <integration-result-panel v-if="tcResult" :result="tcResult" class="mt-4" />
    </div>

    <!-- 计量系统 -->
    <div class="glass-panel neon-border p-6">
      <div class="flex items-center gap-4 mb-4">
        <div class="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center">
          <i class="fas fa-tachometer-alt text-emerald-300"></i>
        </div>
        <div>
          <h3 class="text-base font-semibold text-white">计量系统</h3>
          <p class="text-xs text-gray-500">从计量系统拉取抄表数据</p>
        </div>
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs text-gray-500 mb-1">计量点ID</label>
          <input v-model="meterForm.meter_point_id" class="input-glow text-sm" placeholder="MP-GD-001" />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">抄表日</label>
          <input v-model="meterForm.reading_date" type="date" class="input-glow text-sm" />
        </div>
        <div class="col-span-2">
          <button type="button" @click="fetchMetering" class="btn-neon" :disabled="loading">
            <i class="fas fa-bolt mr-2"></i>拉取抄表数据
          </button>
        </div>
      </div>
      <integration-result-panel v-if="meterResult" :result="meterResult" class="mt-4" />
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { api } from '@/utils/api'
import IntegrationResultPanel from '@/components/integration/IntegrationResultPanel.vue'
import ProvinceSelect from '@/components/form/ProvinceSelect.vue'

const loading = ref(false)
const status = ref(null)
const tcResult = ref(null)
const meterResult = ref(null)

const tcForm = ref({ trade_date: '2026-04-09', province_code: 'GD' })
const meterForm = ref({ meter_point_id: 'MP-GD-001', reading_date: '2026-04-09' })

const statusRaw = computed(() => {
  if (!status.value || status.value.error) return ''
  try {
    return JSON.stringify(status.value, null, 2)
  } catch {
    return ''
  }
})

const statusBlocks = computed(() => {
  const s = status.value
  if (!s || s.error || typeof s !== 'object') return []
  const tc = s.trading_center || {}
  const mt = s.metering || {}
  return [
    {
      key: 'tc',
      label: '交易中心 API',
      configured: !!tc.configured,
      timeout_sec: tc.timeout_sec ?? '—',
      hint: tc.configured
        ? '已设置 APP_TRADING_CENTER_BASE_URL，可拉取外部数据。'
        : '未配置环境变量 APP_TRADING_CENTER_BASE_URL，接口将返回「未配置」。',
    },
    {
      key: 'meter',
      label: '计量系统 API',
      configured: !!mt.configured,
      timeout_sec: mt.timeout_sec ?? '—',
      hint: mt.configured
        ? '已设置 APP_METERING_BASE_URL，可拉取抄表数据。'
        : '未配置 APP_METERING_BASE_URL，接口将返回「未配置」。',
    },
  ]
})

async function checkStatus() {
  loading.value = true
  try {
    const r = await api.get('/api/v1/integrations/status')
    status.value = r.data
  } catch (e) {
    status.value = { error: e.message }
  } finally {
    loading.value = false
  }
}

async function fetchClearing() {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (tcForm.value.trade_date) params.set('trade_date', tcForm.value.trade_date)
    const r = await api.get('/api/v1/integrations/trading-center/clearing-snapshot?' + params)
    tcResult.value = r.data || r
  } catch (e) {
    tcResult.value = { error: e.message }
  } finally {
    loading.value = false
  }
}

async function fetchExternalPrices() {
  loading.value = true
  try {
    const params = new URLSearchParams({ province_code: tcForm.value.province_code || 'GD' })
    const r = await api.get('/api/v1/integrations/trading-center/market-prices?' + params)
    tcResult.value = r.data || r
  } catch (e) {
    tcResult.value = { error: e.message }
  } finally {
    loading.value = false
  }
}

async function fetchMetering() {
  loading.value = true
  try {
    const params = new URLSearchParams({ meter_point_id: meterForm.value.meter_point_id })
    if (meterForm.value.reading_date) params.set('reading_date', meterForm.value.reading_date)
    const r = await api.get('/api/v1/integrations/metering/readings?' + params)
    meterResult.value = r.data || r
  } catch (e) {
    meterResult.value = { error: e.message }
  } finally {
    loading.value = false
  }
}
</script>
