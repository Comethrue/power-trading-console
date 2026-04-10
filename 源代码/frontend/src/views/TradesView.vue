<template>
  <div class="space-y-6 animate-fade-in">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-white">交易申报</h2>
        <p class="text-sm text-gray-500 mt-1">Trade Declarations · Submit and manage power trade declarations</p>
      </div>
      <button @click="showSubmit = !showSubmit" class="btn-neon">
        <i class="fas fa-paper-plane mr-2"></i>提交申报
      </button>
    </div>

    <!-- 提交表单 -->
    <transition name="slide">
      <div v-if="showSubmit" id="declaration-form-anchor" class="glass-panel neon-border p-6">
        <h3 class="text-base font-semibold text-white mb-4">新建交易申报</h3>
        <form @submit.prevent="handleSubmit" class="grid grid-cols-2 gap-4">
          <div>
            <ProvinceSelect v-model="form.province_code" label="省份" required />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">交易日期 *</label>
            <input v-model="form.trade_date" type="date" class="input-glow text-sm" required>
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">市场类型 *</label>
            <input v-model="form.market_type" class="input-glow text-sm" placeholder="SPOT_DA" required>
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">幂等键 *</label>
            <input v-model="form.idempotency_key" class="input-glow text-sm font-mono" required>
          </div>
          <div class="col-span-2">
            <div class="flex items-center justify-between mb-2">
              <label class="text-xs text-gray-500">申报时段</label>
              <button type="button" @click="addTimeslot" class="text-xs text-amber-300 hover:text-amber-200">
                <i class="fas fa-plus mr-1"></i>添加时段
              </button>
            </div>
            <div class="space-y-2 max-h-48 overflow-y-auto custom-scrollbar">
              <div v-for="(ts, i) in form.timeslots" :key="i" class="flex gap-2 items-center">
                <input v-model="ts.slot" class="input-glow text-sm flex-1" placeholder="09:00-09:15">
                <input v-model="ts.volume_mwh" type="number" step="0.01" class="input-glow text-sm w-24" placeholder="电量">
                <input v-model="ts.price" type="number" step="0.01" class="input-glow text-sm w-24" placeholder="价格">
                <button type="button" @click="form.timeslots.splice(i, 1)" class="text-rose-500/60 hover:text-rose-300">
                  <i class="fas fa-trash-alt text-sm"></i>
                </button>
              </div>
            </div>
          </div>
          <div class="col-span-2 flex gap-3">
            <button type="button" @click="showSubmit = false" class="btn-outline flex-1">取消</button>
            <button type="submit" class="btn-neon flex-1" :disabled="submitting">
              <i class="fas fa-spinner fa-spin mr-2" v-if="submitting"></i>
              {{ submitting ? '提交中...' : '提交申报' }}
            </button>
          </div>
        </form>
      </div>
    </transition>

    <!-- 列表 -->
    <div class="glass-panel neon-border overflow-hidden">
      <div class="overflow-x-auto">
        <table class="data-table">
          <thead>
            <tr>
              <th>申报ID</th>
              <th>组织</th>
              <th>省份</th>
              <th>规则版本</th>
              <th>交易日期</th>
              <th>市场类型</th>
              <th>状态</th>
              <th>创建时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="8" class="text-center py-12">
                <i class="fas fa-spinner fa-spin text-amber-300 text-2xl"></i>
              </td>
            </tr>
            <tr v-else-if="!items.length">
              <td colspan="8">
                <div class="empty-state">
                  <i class="fas fa-exchange-alt"></i>
                  <p>暂无申报数据</p>
                </div>
              </td>
            </tr>
            <tr v-for="item in items" :key="item.declaration_id">
              <td class="font-mono text-xs text-amber-300">{{ item.declaration_id }}</td>
              <td>{{ item.org_id }}</td>
              <td>
                <span class="px-2 py-0.5 rounded text-xs font-semibold" :class="provinceBadgeClass(item.province_code)">
                  {{ item.province_code }}
                </span>
              </td>
              <td class="font-mono text-xs">{{ item.rule_version }}</td>
              <td>{{ item.trade_date }}</td>
              <td class="text-xs">{{ item.market_type }}</td>
              <td><span :class="statusClass(item.status)">{{ statusLabel(item.status) }}</span></td>
              <td class="text-xs text-gray-500">{{ item.created_at?.slice(0, 19) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="flex items-center justify-between px-6 py-4 border-t border-amber-500/10">
        <p class="text-sm text-gray-500">共 <span class="text-amber-300 font-semibold">{{ total }}</span> 条</p>
        <div class="flex gap-2">
          <button class="btn-outline px-4 py-2 text-xs" :disabled="page <= 1" @click="changePage(-1)">
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M14.5 6.5 8 12l6.5 5.5"/></svg>
          </button>
          <span class="min-w-[2.5rem] h-9 inline-flex items-center justify-center rounded-lg text-sm font-semibold font-mono bg-gradient-to-b from-dark-200 to-dark-300/90 text-amber-200 border border-amber-500/25 shadow-inner">{{ page }}</span>
          <button class="btn-outline px-4 py-2 text-xs" @click="changePage(1)">
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M9.5 6.5 16 12l-6.5 5.5"/></svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { api } from '@/utils/api'
import { statusClass, statusLabel } from '@/utils/format'
import ProvinceSelect from '@/components/form/ProvinceSelect.vue'
import { provinceBadgeClass } from '@/utils/provinceStyle'

const loading = ref(false)
const submitting = ref(false)
const showSubmit = ref(false)
const page = ref(1)
const total = ref(0)
const items = ref([])

const form = ref({
  province_code: 'GD',
  trade_date: '2026-04-09',
  market_type: 'SPOT_DA',
  idempotency_key: `dec-${new Date().toISOString().slice(0,10).replace(/-/g,'')}-ui-${Date.now().toString().slice(-6)}`,
  timeslots: [
    { slot: '09:00-09:15', volume_mwh: 12.5, price: 420 },
    { slot: '09:15-09:30', volume_mwh: 14.2, price: 425 },
    { slot: '09:30-09:45', volume_mwh: 15.0, price: 430 },
  ],
})

function addTimeslot() {
  form.value.timeslots.push({ slot: '10:00-10:15', volume_mwh: 10, price: 420 })
}

async function loadTrades() {
  loading.value = true
  try {
    const resp = await api.get(`/api/v1/trades/declarations?page_no=${page.value}&page_size=20`)
    if (resp.success) {
      items.value = resp.data.items || []
      total.value = resp.data.total || 0
    }
  } catch (e) {
    console.warn(e.message)
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  submitting.value = true
  try {
    const f = { ...form.value }
    f.timeslots = f.timeslots.map(ts => ({
      ...ts,
      volume_mwh: Number(ts.volume_mwh),
      price: Number(ts.price),
    }))
    const resp = await api.post('/api/v1/trades/declarations', f)
    if (resp.success) {
      showSubmit.value = false
      form.value.idempotency_key = `dec-${new Date().toISOString().slice(0,10).replace(/-/g,'')}-ui-${Date.now().toString().slice(-6)}`
      loadTrades()
    }
  } catch (e) {
    alert('提交失败: ' + e.message)
  } finally {
    submitting.value = false
  }
}

function changePage(delta) {
  page.value = Math.max(1, page.value + delta)
  loadTrades()
}

onMounted(async () => {
  await loadTrades()
  if (typeof sessionStorage !== 'undefined' && sessionStorage.getItem('focus_declaration_form') === '1') {
    showSubmit.value = true
    sessionStorage.removeItem('focus_declaration_form')
    await nextTick()
    document.getElementById('declaration-form-anchor')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
})
</script>

<style scoped>
.slide-enter-active, .slide-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}
.slide-enter-from, .slide-leave-to {
  opacity: 0;
  max-height: 0;
  transform: translateY(-10px);
}
.slide-enter-to, .slide-leave-from {
  opacity: 1;
  max-height: 500px;
}
</style>
