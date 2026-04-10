<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-white">审计日志</h2>
        <p class="text-sm text-gray-500 mt-1">Audit Logs · Complete operation history tracking</p>
      </div>
      <button @click="loadLogs" class="btn-outline">
        <i class="fas fa-sync-alt mr-2"></i>刷新
      </button>
    </div>

    <!-- 筛选 -->
    <div class="glass-panel neon-border p-4">
      <div class="flex items-center gap-4">
        <label class="text-sm text-gray-500">操作类型</label>
        <select v-model="actionFilter" @change="loadLogs" class="input-glow text-sm w-48">
          <option value="">全部操作</option>
          <option value="trade_declaration_create">交易申报</option>
          <option value="reconcile_task_create">结算任务创建</option>
          <option value="reconcile_task_status_update">结算状态更新</option>
          <option value="contract_create">合同创建</option>
          <option value="contract_status_update">合同状态更新</option>
        </select>
        <span class="text-sm text-gray-500">共 <span class="text-amber-300 font-semibold">{{ total }}</span> 条记录</span>
      </div>
    </div>

    <!-- 表格 -->
    <div class="glass-panel neon-border overflow-hidden">
      <div class="overflow-x-auto max-h-[60vh]">
        <table class="data-table">
          <thead class="sticky top-0 z-10">
            <tr>
              <th>ID</th>
              <th>组织</th>
              <th>操作类型</th>
              <th>资源类型</th>
              <th>资源ID</th>
              <th>详情</th>
              <th>时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="7" class="text-center py-12"><i class="fas fa-spinner fa-spin text-amber-300 text-2xl"></i></td>
            </tr>
            <tr v-else-if="!logs.length">
              <td colspan="7"><div class="empty-state"><i class="fas fa-clipboard-list"></i><p>暂无审计日志</p></div></td>
            </tr>
            <tr v-for="log in logs" :key="log.id" class="group">
              <td class="text-gray-500 text-xs">{{ log.id }}</td>
              <td>
                <span class="px-2 py-0.5 rounded text-xs font-semibold bg-amber-500/10 text-amber-300">org {{ log.org_id }}</span>
              </td>
              <td><span class="tag-info">{{ actionLabel(log.action) }}</span></td>
              <td class="text-xs text-gray-400">{{ log.resource_type }}</td>
              <td class="font-mono text-xs text-amber-300">{{ log.resource_id || '—' }}</td>
              <td class="text-xs text-gray-300 max-w-md">
                <span class="line-clamp-2">{{ formatDetails(log.details_json) }}</span>
              </td>
              <td class="text-xs text-gray-500 font-mono whitespace-nowrap">{{ log.created_at?.slice(0, 19) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/utils/api'

const loading = ref(false)
const logs = ref([])
const total = ref(0)
const actionFilter = ref('')

const actionLabels = {
  trade_declaration_create: '交易申报',
  reconcile_task_create: '结算任务创建',
  reconcile_task_status_update: '结算状态更新',
  contract_create: '合同创建',
  contract_status_update: '合同状态更新',
}

function actionLabel(a) { return actionLabels[a] || a || '—' }

const DETAIL_LABELS = {
  org_id: '组织',
  province_code: '省份',
  rule_version: '规则版本',
  contract_type: '合同类型',
  duplicate: '重复申报',
  status: '状态',
}

function formatDetails(json) {
  if (!json) return '—'
  try {
    const o = typeof json === 'string' ? JSON.parse(json) : json
    if (!o || typeof o !== 'object') return String(json)
    return Object.entries(o)
      .map(([k, v]) => {
        const lk = DETAIL_LABELS[k] || k
        let vv = v
        if (typeof v === 'boolean') vv = v ? '是' : '否'
        return `${lk}：${vv}`
      })
      .join('；')
  } catch {
    return '（详情已记录）'
  }
}

async function loadLogs() {
  loading.value = true
  try {
    const params = new URLSearchParams({ page_no: 1, page_size: 50 })
    if (actionFilter.value) params.set('action', actionFilter.value)
    const resp = await api.get('/api/v1/audit/logs?' + params)
    if (resp.success) {
      logs.value = resp.data.items || []
      total.value = resp.data.total || 0
    }
  } catch (e) { console.warn(e.message) }
  finally { loading.value = false }
}

onMounted(() => { loadLogs() })
</script>
