<template>
  <div class="space-y-6 animate-fade-in">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-white">合同台账</h2>
        <p class="text-sm text-gray-500 mt-1">Contract Management · Manage your power trading contracts</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="relative">
          <input v-model="filters.status" @change="loadContracts" placeholder="状态筛选" class="input-glow w-40 pl-10 text-sm">
          <i class="fas fa-filter absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-xs"></i>
        </div>
        <button type="button" @click="showCreate = true" class="btn-neon">
          <i class="fas fa-plus mr-2"></i>新建合同
        </button>
        <button @click="loadContracts" class="btn-outline">
          <i class="fas fa-sync-alt mr-2"></i>刷新
        </button>
      </div>
    </div>

    <!-- 统计概览 -->
    <div class="grid grid-cols-4 gap-4">
      <div v-for="stat in overviewStats" :key="stat.label"
           class="glass-panel p-4 rounded-xl border border-amber-500/10">
        <p class="text-xs text-gray-500 mb-1">{{ stat.label }}</p>
        <p class="text-2xl font-bold font-mono" :class="stat.color">{{ stat.value }}</p>
      </div>
    </div>

    <!-- 表格 -->
    <div class="glass-panel neon-border overflow-hidden">
      <div class="overflow-x-auto">
        <table class="data-table">
          <thead>
            <tr>
              <th>合同ID</th>
              <th>组织</th>
              <th>省份</th>
              <th>类型</th>
              <th>对手方</th>
              <th>电量(MWh)</th>
              <th>价格</th>
              <th>有效期</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="9" class="text-center py-12">
                <i class="fas fa-spinner fa-spin text-electric-400 text-2xl"></i>
              </td>
            </tr>
            <tr v-else-if="!items.length">
              <td colspan="9">
                <div class="empty-state">
                  <i class="fas fa-file-contract"></i>
                  <p>暂无合同数据</p>
                </div>
              </td>
            </tr>
            <tr v-for="item in items" :key="item.contract_id" class="group">
              <td class="font-mono text-xs text-amber-300">{{ item.contract_id }}</td>
              <td>{{ formatOrgCell(item.org_id) }}</td>
              <td>
                <span class="px-2 py-0.5 rounded text-xs font-semibold" :class="provinceBadgeClass(item.province_code)">
                  {{ provinceLabel(item.province_code) }}
                </span>
              </td>
              <td>
                <span class="tag-info">{{ contractTypeLabel(item.contract_type) }}</span>
              </td>
              <td class="text-gray-400">{{ item.counterpart || '—' }}</td>
              <td class="num">{{ formatNum(item.volume_mwh) }}</td>
              <td class="num">{{ formatPrice(item.price) }}</td>
              <td class="text-xs text-gray-500">{{ item.start_date }} ~ {{ item.end_date }}</td>
              <td>
                <span :class="statusClass(item.status)">{{ statusLabel(item.status) }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 分页 -->
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

    <!-- 新建合同抽屉 -->
    <div v-if="showCreate" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div class="glass-panel neon-border w-full max-w-lg p-6 m-4">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-bold text-white">新建合同</h3>
          <button @click="showCreate = false" class="text-gray-500 hover:text-white">
            <i class="fas fa-times text-lg"></i>
          </button>
        </div>
        <form @submit.prevent="handleCreate" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs text-gray-500 mb-1">组织ID *</label>
              <input v-model="createForm.org_id" type="number" class="input-glow text-sm" required>
            </div>
            <div>
              <ProvinceSelect v-model="createForm.province_code" label="省份" required />
            </div>
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">合同类型 *</label>
            <select v-model="createForm.contract_type" class="input-glow text-sm" required>
              <option value="MEDIUM_LONG">中长期合同</option>
              <option value="SPOT_DA">现货日前</option>
              <option value="SPOT_RT">现货实时</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs text-gray-500 mb-1">电量(MWh)</label>
              <input v-model="createForm.volume_mwh" type="number" step="0.01" class="input-glow text-sm" required>
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">价格(元/MWh)</label>
              <input v-model="createForm.price" type="number" step="0.01" class="input-glow text-sm" required>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs text-gray-500 mb-1">开始日期</label>
              <input v-model="createForm.start_date" type="date" class="input-glow text-sm" required>
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">结束日期</label>
              <input v-model="createForm.end_date" type="date" class="input-glow text-sm" required>
            </div>
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">对手方</label>
            <input v-model="createForm.counterpart" class="input-glow text-sm" placeholder="对手方名称（可选）">
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">备注</label>
            <input v-model="createForm.remark" class="input-glow text-sm" placeholder="备注信息（可选）">
          </div>
          <div class="flex gap-3 pt-2">
            <button type="button" @click="showCreate = false" class="btn-outline flex-1">取消</button>
            <button type="submit" class="btn-neon flex-1" :disabled="creating">
              <i class="fas fa-spinner fa-spin mr-2" v-if="creating"></i>
              {{ creating ? '创建中...' : '创建合同' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/utils/api'
import { formatNumber, formatPrice, statusClass, statusLabel } from '@/utils/format'
import { provinceLabel } from '@/constants/provinces'
import ProvinceSelect from '@/components/form/ProvinceSelect.vue'
import { formatOrgLine, formatOrgCodeOnly } from '@/utils/orgDisplay'
import { provinceBadgeClass } from '@/utils/provinceStyle'

const loading = ref(false)
const showCreate = ref(false)
const creating = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)
const items = ref([])
const filters = ref({ status: '', contract_type: '' })

const createForm = ref({
  org_id: 1001,
  province_code: 'GD',
  contract_type: 'MEDIUM_LONG',
  counterpart: '',
  volume_mwh: 1000,
  price: 450,
  start_date: '2026-04-01',
  end_date: '2026-04-30',
  remark: '',
})

const overviewStats = computed(() => {
  const active = items.value.filter(i => i.status === 'active').length
  const expired = items.value.filter(i => i.status === 'expired').length
  const totalVol = items.value.reduce((s, i) => s + (i.volume_mwh || 0), 0)
  const avgPrice = items.value.length ? items.value.reduce((s, i) => s + (i.price || 0), 0) / items.value.length : 0
  return [
    { label: '总合同数', value: total.value, color: 'text-white' },
    { label: '生效中', value: active, color: 'text-emerald-300' },
    { label: '已到期', value: expired, color: 'text-gray-400' },
    { label: '总电量', value: formatNumber(totalVol) + ' MWh', color: 'text-amber-300' },
  ]
})

function formatOrgCell(orgId) {
  if (!orgId) return '—'
  return formatOrgLine(orgId)
}

function contractTypeLabel(t) {
  const m = { MEDIUM_LONG: '中长期', SPOT_DA: '现货日前', SPOT_RT: '现货实时' }
  return m[t] || t
}

function formatNum(v) {
  return v != null ? Number(v).toFixed(2) : '—'
}

async function loadContracts() {
  loading.value = true
  try {
    const params = new URLSearchParams({ page_no: page.value, page_size: pageSize })
    if (filters.value.status) params.set('status', filters.value.status)
    if (filters.value.contract_type) params.set('contract_type', filters.value.contract_type)
    const resp = await api.get('/api/v1/contracts/contracts?' + params)
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

async function handleCreate() {
  creating.value = true
  try {
    const form = { ...createForm.value }
    form.volume_mwh = Number(form.volume_mwh)
    form.price = Number(form.price)
    const resp = await api.post('/api/v1/contracts/contracts', form)
    if (resp.success) {
      showCreate.value = false
      loadContracts()
    }
  } catch (e) {
    alert('创建失败: ' + e.message)
  } finally {
    creating.value = false
  }
}

function changePage(delta) {
  page.value = Math.max(1, page.value + delta)
  loadContracts()
}

onMounted(() => {
  loadContracts()
  if (typeof sessionStorage !== 'undefined' && sessionStorage.getItem('open_contract_create') === '1') {
    showCreate.value = true
    sessionStorage.removeItem('open_contract_create')
  }
})
</script>
