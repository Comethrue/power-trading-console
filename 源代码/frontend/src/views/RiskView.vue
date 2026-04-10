<template>
  <div class="space-y-6 animate-fade-in">
    <!-- 页面标题 -->
    <div>
      <h2 class="text-xl font-bold text-white">风险管理</h2>
      <p class="text-sm text-gray-500 mt-1">Risk Management · Deviation analysis and risk assessment</p>
    </div>

    <!-- 查询表单 -->
    <div class="glass-panel neon-border p-6">
      <h3 class="text-base font-semibold text-white mb-4">偏差风险查询</h3>
      <form @submit.prevent="handleQuery" class="grid grid-cols-3 gap-4">
        <div>
          <ProvinceSelect v-model="form.province_code" label="省份" required />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">交易日期 *</label>
          <input v-model="form.trade_date" type="date" class="input-glow text-sm" required>
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">组织ID *</label>
          <input v-model="form.org_id" type="number" class="input-glow text-sm" required>
        </div>
        <div class="col-span-3 flex gap-3">
          <button type="submit" class="btn-neon" :disabled="loading">
            <i class="fas fa-search mr-2"></i>{{ loading ? '查询中...' : '查询风险' }}
          </button>
          <button type="button" @click="resetForm" class="btn-outline">重置</button>
        </div>
      </form>
    </div>

    <!-- 风险结果 -->
    <div v-if="result" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- 风险等级大卡片 -->
      <div class="lg:col-span-2 stat-glow-card" :class="riskCardClass">
        <div class="flex items-center justify-between mb-4">
          <div>
            <p class="text-xs text-gray-500 uppercase tracking-wider mb-2">风险等级</p>
            <h3 class="text-5xl font-black" :class="riskTextClass">{{ riskLabel }}</h3>
          </div>
          <div class="w-20 h-20 rounded-2xl flex items-center justify-center"
               :class="riskIconBg">
            <i :class="[riskIcon, 'text-3xl']"></i>
          </div>
        </div>
        <div class="text-xs text-gray-400">
          {{ riskDesc }}
        </div>
      </div>

      <!-- 偏差率 -->
      <div class="stat-glow-card">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center">
            <i class="fas fa-percentage text-amber-300"></i>
          </div>
          <div>
            <p class="text-xs text-gray-500">偏差率</p>
            <p class="text-2xl font-bold font-mono text-white">{{ formatPercent(result.deviation_ratio) }}</p>
          </div>
        </div>
        <!-- 偏差率仪表盘 -->
        <div class="relative h-3 bg-dark-200 rounded-full overflow-hidden">
          <div class="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-amber-400 via-amber-400 to-rose-400 transition-all duration-1000"
               :style="{ width: Math.min(result.deviation_ratio * 100 * 2, 100) + '%' }"></div>
          <!-- 阈值线 -->
          <div class="absolute top-0 bottom-0 w-0.5 bg-white/50" 
               :style="{ left: (result.medium_threshold || 0.35) * 100 + '%' }"></div>
          <div class="absolute top-0 bottom-0 w-0.5 bg-white/50"
               :style="{ left: (result.high_threshold || 0.7) * 100 + '%' }"></div>
        </div>
        <div class="flex justify-between text-[10px] text-gray-500 mt-1">
          <span>0%</span>
          <span class="text-amber-300">{{ Math.round((result.medium_threshold || 0.35) * 100) }}%</span>
          <span class="text-rose-300">{{ Math.round((result.high_threshold || 0.7) * 100) }}%</span>
          <span>100%</span>
        </div>
      </div>

      <!-- 预期偏差成本 -->
      <div class="stat-glow-card">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-xl bg-rose-500/10 flex items-center justify-center">
            <i class="fas fa-coins text-rose-300"></i>
          </div>
          <div>
            <p class="text-xs text-gray-500">预期偏差成本</p>
            <p class="text-2xl font-bold font-mono text-rose-300">
              {{ result.expected_deviation_cost != null ? '¥' + Number(result.expected_deviation_cost).toFixed(2) : '—' }}
            </p>
          </div>
        </div>
        <div class="p-3 rounded-lg bg-dark-200/50 border border-amber-500/10">
          <p class="text-xs text-gray-500">规则版本</p>
          <p class="font-mono text-amber-300 text-sm">{{ result.rule_version || '—' }}</p>
        </div>
      </div>
    </div>

    <!-- 成本构成说明（业务语言，非源码） -->
    <div v-if="result" class="glass-panel neon-border p-6">
      <h3 class="text-base font-semibold text-white mb-2">偏差成本构成说明</h3>
      <p class="text-sm text-gray-400 mb-4 leading-relaxed">
        在规则版本 <span class="text-amber-300">{{ result.rule_version || '—' }}</span> 下，
        预期偏差成本由<strong class="text-gray-300">基准成本</strong>、<strong class="text-gray-300">偏差率</strong>与<strong class="text-gray-300">惩罚系数</strong>共同决定，
        数值由后台按省间规则计算，以下为当前查询结果摘要。
      </p>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="p-4 rounded-xl bg-dark-200/50 border border-amber-500/10">
          <p class="text-xs text-gray-500 mb-1">基准成本（元）</p>
          <p class="text-lg text-amber-200 font-semibold">{{ result.base_cost != null ? Number(result.base_cost).toFixed(2) : '—' }}</p>
        </div>
        <div class="p-4 rounded-xl bg-dark-200/50 border border-amber-500/10">
          <p class="text-xs text-gray-500 mb-1">偏差率</p>
          <p class="text-lg text-amber-200 font-semibold">{{ result.deviation_ratio != null ? formatPercent(result.deviation_ratio) : '—' }}</p>
        </div>
        <div class="p-4 rounded-xl bg-dark-200/50 border border-amber-500/10">
          <p class="text-xs text-gray-500 mb-1">惩罚系数</p>
          <p class="text-lg text-amber-200 font-semibold">{{ result.deviation_penalty_coef != null ? Number(result.deviation_penalty_coef).toFixed(4) : '—' }}</p>
        </div>
      </div>
    </div>

    <!-- 无数据提示 -->
    <div v-if="!result && !loading" class="glass-panel neon-border p-16 text-center">
      <i class="fas fa-shield-alt text-5xl text-gray-600 mb-4"></i>
      <p class="text-gray-500">输入查询条件查询偏差风险</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { api } from '@/utils/api'
import { formatPercent } from '@/utils/format'
import ProvinceSelect from '@/components/form/ProvinceSelect.vue'

const loading = ref(false)
const result = ref(null)

const form = ref({
  province_code: 'GD',
  trade_date: '2026-04-09',
  org_id: 1001,
})

const riskLabel = computed(() => {
  const m = { low: '低风险', medium: '中风险', high: '高风险' }
  return m[result.value?.deviation_risk_level] || '—'
})

const riskCardClass = computed(() => {
  const m = {
    low: 'border-emerald-500/30',
    medium: 'border-amber-500/30',
    high: 'border-rose-500/30',
  }
  return m[result.value?.deviation_risk_level] || ''
})

const riskTextClass = computed(() => {
  const m = { low: 'text-emerald-300', medium: 'text-amber-300', high: 'text-rose-300' }
  return m[result.value?.deviation_risk_level] || 'text-gray-400'
})

const riskIconBg = computed(() => {
  const m = {
    low: 'bg-emerald-500/10',
    medium: 'bg-amber-500/10',
    high: 'bg-rose-500/10',
  }
  return m[result.value?.deviation_risk_level] || 'bg-gray-500/10'
})

const riskIcon = computed(() => {
  const m = { low: 'fas fa-check-circle', medium: 'fas fa-exclamation-circle', high: 'fas fa-exclamation-triangle' }
  return m[result.value?.deviation_risk_level] || 'fas fa-question'
})

const riskDesc = computed(() => {
  const m = {
    low: '申报价格稳定，偏差风险较低，建议继续保持当前策略。',
    medium: '存在一定偏差风险，建议关注市场动态，适当调整申报策略。',
    high: '偏差风险较高，建议立即分析原因并采取风险控制措施。',
  }
  return m[result.value?.deviation_risk_level] || ''
})

async function handleQuery() {
  loading.value = true
  try {
    const params = new URLSearchParams(form.value)
    const resp = await api.get('/api/v1/risk/deviation?' + params)
    if (resp.success) result.value = resp.data
  } catch (e) { alert('查询失败: ' + e.message) }
  finally { loading.value = false }
}

function resetForm() {
  result.value = null
  form.value = { province_code: 'GD', trade_date: '2026-04-09', org_id: 1001 }
}
</script>
