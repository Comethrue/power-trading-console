<template>
  <div class="space-y-6 animate-fade-in">
    <div>
      <h2 class="text-xl font-bold text-white">规则配置</h2>
      <p class="text-sm text-gray-500 mt-1">Rule Configuration · Province trading rules and parameters</p>
    </div>

    <!-- 查询规则 -->
    <div class="glass-panel neon-border p-6">
      <h3 class="text-base font-semibold text-white mb-4">查询省份规则</h3>
      <div class="grid grid-cols-3 gap-4">
        <div>
          <ProvinceSelect v-model="form.province_code" label="省份" required />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">交易日期</label>
          <input v-model="form.trade_date" type="date" class="input-glow text-sm">
        </div>
        <div class="flex items-end gap-3">
          <button @click="queryRule" class="btn-neon flex-1" :disabled="loading">
            <i class="fas fa-search mr-2"></i>{{ loading ? '查询中...' : '查询规则' }}
          </button>
          <button @click="queryVersions" class="btn-outline flex-1" :disabled="loading">
            <i class="fas fa-list mr-2"></i>版本列表
          </button>
        </div>
      </div>
    </div>

    <!-- 规则详情 -->
    <div v-if="ruleData" class="glass-panel neon-border p-6">
      <h3 class="text-base font-semibold text-white mb-4">
        {{ ruleData.province_code }} 省规则 · {{ ruleData.version }}
      </h3>
      <div class="grid grid-cols-3 gap-4">
        <!-- 交易规则 -->
        <div class="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20">
          <div class="flex items-center gap-2 mb-3">
            <i class="fas fa-exchange-alt text-amber-300"></i>
            <span class="text-sm font-semibold text-amber-300">交易规则</span>
          </div>
          <div class="space-y-2 text-xs">
            <div class="flex justify-between"><span class="text-gray-500">价格区间</span><span class="font-mono text-amber-200">¥{{ ruleData.trade?.price_min }} ~ ¥{{ ruleData.trade?.price_max }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">电量区间</span><span class="font-mono text-amber-200">{{ ruleData.trade?.volume_min }} ~ {{ ruleData.trade?.volume_max }} MWh</span></div>
            <div class="flex justify-between"><span class="text-gray-500">最大时段数</span><span class="font-mono text-amber-200">{{ ruleData.trade?.timeslot_max_count }}</span></div>
          </div>
        </div>
        <!-- 风险规则 -->
        <div class="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20">
          <div class="flex items-center gap-2 mb-3">
            <i class="fas fa-exclamation-triangle text-amber-300"></i>
            <span class="text-sm font-semibold text-amber-300">风险规则</span>
          </div>
          <div class="space-y-2 text-xs">
            <div class="flex justify-between"><span class="text-gray-500">基础成本</span><span class="font-mono text-amber-200">¥{{ ruleData.risk?.base_cost?.toLocaleString() }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">中等阈值</span><span class="font-mono text-amber-200">{{ Math.round((ruleData.risk?.medium_threshold || 0) * 100) }}%</span></div>
            <div class="flex justify-between"><span class="text-gray-500">高风险阈值</span><span class="font-mono text-amber-200">{{ Math.round((ruleData.risk?.high_threshold || 0) * 100) }}%</span></div>
          </div>
        </div>
        <!-- 结算规则 -->
        <div class="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20">
          <div class="flex items-center gap-2 mb-3">
            <i class="fas fa-calculator text-emerald-300"></i>
            <span class="text-sm font-semibold text-emerald-300">结算规则</span>
          </div>
          <div class="space-y-2 text-xs">
            <div class="flex justify-between"><span class="text-gray-500">最大周期天数</span><span class="font-mono text-amber-200">{{ ruleData.settlement?.max_cycle_days }} 天</span></div>
            <div class="flex justify-between"><span class="text-gray-500">偏差惩罚系数</span><span class="font-mono text-amber-200">×{{ ruleData.settlement?.deviation_penalty_coef }}</span></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 版本列表 -->
    <div v-if="versions.length" class="glass-panel neon-border p-6">
      <h3 class="text-base font-semibold text-white mb-4">规则版本列表</h3>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="v in versions"
          :key="v"
          type="button"
          @click="queryRuleByVersion(v)"
          class="px-4 py-2 rounded-xl bg-dark-200 border border-amber-500/20 text-amber-300 hover:border-amber-400/50 hover:bg-amber-500/5 transition-all font-mono text-sm"
        >
          {{ v }}
        </button>
      </div>
    </div>

    <!-- 无数据 -->
    <div v-if="!ruleData && !versions.length && !loading" class="glass-panel neon-border p-16 text-center">
      <i class="fas fa-cogs text-5xl text-gray-600 mb-4"></i>
      <p class="text-gray-500">输入省份查询规则配置</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { api } from '@/utils/api'
import ProvinceSelect from '@/components/form/ProvinceSelect.vue'

const loading = ref(false)
const ruleData = ref(null)
const versions = ref([])
const form = ref({ province_code: 'GD', trade_date: '2026-04-09' })

async function queryRule() {
  loading.value = true
  try {
    const params = new URLSearchParams({ province_code: form.value.province_code })
    if (form.value.trade_date) params.set('trade_date', form.value.trade_date)
    const resp = await api.get('/api/v1/rules?' + params)
    if (resp.success) ruleData.value = resp.data
  } catch (e) { alert(e.message) }
  finally { loading.value = false }
}

async function queryVersions() {
  loading.value = true
  try {
    const resp = await api.get('/api/v1/rules/versions?province_code=' + form.value.province_code)
    if (resp.success) versions.value = resp.data?.versions || []
  } catch (e) { alert(e.message) }
  finally { loading.value = false }
}

async function queryRuleByVersion(version) {
  loading.value = true
  try {
    const params = new URLSearchParams({
      province_code: form.value.province_code,
      version,
    })
    const resp = await api.get('/api/v1/rules?' + params)
    if (resp.success) ruleData.value = resp.data
  } catch (e) {
    alert(e.message)
  } finally {
    loading.value = false
  }
}
</script>
