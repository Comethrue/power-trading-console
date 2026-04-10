<template>
  <div class="space-y-6 animate-fade-in">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-white">结算对账</h2>
        <p class="text-sm text-gray-500 mt-1">Settlement & Reconciliation · Manage billing and settlement tasks</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 左侧：任务列表 -->
      <div class="space-y-4">
        <div id="settlement-task-list" class="glass-panel neon-border overflow-hidden">
          <div class="px-6 py-4 border-b border-amber-500/10 flex items-center justify-between">
            <h3 class="text-base font-semibold text-white">结算任务列表</h3>
            <button @click="loadTasks" class="btn-outline px-3 py-1.5 text-xs">
              <i class="fas fa-sync-alt mr-1"></i>刷新
            </button>
          </div>
          <div class="overflow-x-auto">
            <table class="data-table">
              <thead>
                <tr>
                  <th>任务ID</th>
                  <th>省份</th>
                  <th>周期</th>
                  <th>状态</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="taskLoading">
                  <td colspan="5" class="text-center py-8"><i class="fas fa-spinner fa-spin text-amber-300"></i></td>
                </tr>
                <tr v-else-if="!tasks.length">
                  <td colspan="5"><div class="empty-state py-8"><i class="fas fa-tasks"></i><p>暂无结算任务</p></div></td>
                </tr>
                <tr v-for="task in tasks" :key="task.task_id" class="cursor-pointer hover:bg-amber-500/5"
                    :class="{ 'bg-amber-500/5': selectedTask?.task_id === task.task_id }"
                    @click="selectTask(task)">
                  <td class="font-mono text-xs text-amber-300">{{ task.task_id }}</td>
                  <td>
                    <span class="px-2 py-0.5 rounded text-xs font-semibold" :class="provinceBadgeClass(task.province_code)">
                      {{ task.province_code }}
                    </span>
                  </td>
                  <td class="text-xs text-gray-400">{{ task.cycle_start }} ~ {{ task.cycle_end }}</td>
                  <td><span :class="statusClass(task.status)">{{ statusLabel(task.status) }}</span></td>
                  <td>
                    <button @click.stop="selectTask(task)" class="text-xs text-amber-300 hover:text-amber-200">
                      <i class="fas fa-chart-pie mr-1"></i>查看
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 新建任务 -->
        <div class="glass-panel neon-border p-6">
          <h3 class="text-base font-semibold text-white mb-4">创建结算任务</h3>
          <form @submit.prevent="handleCreateTask" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs text-gray-500 mb-1">组织ID</label>
                <input v-model="createForm.org_id" type="number" class="input-glow text-sm" required>
              </div>
              <div>
                <ProvinceSelect v-model="createForm.province_code" label="省份" required />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs text-gray-500 mb-1">周期开始</label>
                <input v-model="createForm.cycle_start" type="date" class="input-glow text-sm" required>
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">周期结束</label>
                <input v-model="createForm.cycle_end" type="date" class="input-glow text-sm" required>
              </div>
            </div>
            <button type="submit" class="btn-neon w-full" :disabled="creating">
              <i class="fas fa-spinner fa-spin mr-2" v-if="creating"></i>
              {{ creating ? '创建中...' : '创建结算任务' }}
            </button>
          </form>
        </div>
      </div>

      <!-- 右侧：汇总报告 -->
      <div class="glass-panel neon-border p-6">
        <h3 class="text-base font-semibold text-white mb-4">结算汇总报告</h3>
        
        <div v-if="!selectedTask" class="flex flex-col items-center justify-center py-16 text-gray-500">
          <i class="fas fa-chart-pie text-4xl opacity-20 mb-4"></i>
          <p class="text-sm">请从左侧选择一个结算任务查看报告</p>
        </div>

        <div v-else class="space-y-4">
          <!-- 任务基本信息 -->
          <div class="p-4 rounded-xl bg-dark-200/50 border border-amber-500/10">
            <div class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p class="text-xs text-gray-500">任务ID</p>
                <p class="font-mono text-amber-300 text-xs">{{ selectedTask.task_id }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">省份</p>
                <p class="text-white">{{ selectedTask.province_code }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">周期</p>
                <p class="text-gray-300 text-xs">{{ selectedTask.cycle_start }} ~ {{ selectedTask.cycle_end }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">状态</p>
                <span :class="statusClass(selectedTask.status)">{{ statusLabel(selectedTask.status) }}</span>
              </div>
            </div>
          </div>

          <!-- 核心指标 -->
          <div class="grid grid-cols-2 gap-3">
            <div class="p-4 rounded-xl bg-amber-500/5 border border-amber-500/10">
              <p class="text-xs text-gray-500 mb-1">总申报数</p>
              <p class="text-2xl font-bold font-mono text-amber-300">{{ summary.total_declarations ?? '—' }}</p>
            </div>
            <div class="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/10">
              <p class="text-xs text-gray-500 mb-1">总电量</p>
              <p class="text-2xl font-bold font-mono text-emerald-300">{{ formatNum(summary.total_volume_mwh) }}<span class="text-xs ml-1">MWh</span></p>
            </div>
            <div class="p-4 rounded-xl bg-amber-500/5 border border-amber-500/10">
              <p class="text-xs text-gray-500 mb-1">均价</p>
              <p class="text-2xl font-bold font-mono text-amber-300">{{ formatPrice(summary.avg_price) }}</p>
            </div>
            <div class="p-4 rounded-xl bg-rose-500/5 border border-rose-500/10">
              <p class="text-xs text-gray-500 mb-1">偏差电量</p>
              <p class="text-2xl font-bold font-mono" :class="deviationColor">{{ formatDev(summary.deviation_mwh) }}</p>
            </div>
          </div>

          <!-- 日汇总表格 -->
          <div>
            <p class="text-sm font-semibold text-gray-300 mb-2">日汇总明细</p>
            <div class="overflow-x-auto rounded-xl border border-amber-500/10">
              <table class="data-table text-xs">
                <thead>
                  <tr>
                    <th>日期</th>
                    <th>申报次数</th>
                    <th>总电量</th>
                    <th>均价</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="!summary.daily_summary?.length">
                    <td colspan="4"><div class="empty-state py-6"><i class="fas fa-table"></i><p>暂无数据</p></div></td>
                  </tr>
                  <tr v-for="day in summary.daily_summary" :key="day.trade_date">
                    <td class="font-mono">{{ day.trade_date }}</td>
                    <td>{{ day.declarations }}</td>
                    <td class="num">{{ formatNum(day.volume_mwh) }}</td>
                    <td class="num">{{ formatPrice(day.avg_price) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <button @click="loadSummary" class="btn-outline w-full" :disabled="summaryLoading">
            <i class="fas fa-spinner fa-spin mr-2" v-if="summaryLoading"></i>
            <i class="fas fa-redo mr-2" v-else></i>
            刷新报告
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { api } from '@/utils/api'
import { statusClass, statusLabel, formatPrice } from '@/utils/format'
import ProvinceSelect from '@/components/form/ProvinceSelect.vue'
import { provinceBadgeClass } from '@/utils/provinceStyle'

const taskLoading = ref(false)
const summaryLoading = ref(false)
const creating = ref(false)
const tasks = ref([])
const selectedTask = ref(null)
const summary = ref({})

const createForm = ref({
  org_id: 1001,
  province_code: 'GD',
  cycle_start: '2026-04-01',
  cycle_end: '2026-04-08',
})

const deviationColor = computed(() => {
  const v = summary.value.deviation_mwh
  if (v > 0) return 'text-rose-300'
  if (v < 0) return 'text-amber-300'
  return 'text-emerald-300'
})

function formatNum(v) {
  return v != null ? Number(v).toFixed(2) : '—'
}

function formatDev(v) {
  if (v == null) return '—'
  if (v === 0) return '无偏差'
  return (v > 0 ? '+' : '') + Number(v).toFixed(2) + ' MWh'
}

async function loadTasks() {
  taskLoading.value = true
  try {
    const resp = await api.get('/api/v1/settlement/reconcile/tasks?page_no=1&page_size=20')
    if (resp.success) tasks.value = resp.data.items || []
  } catch (e) { console.warn(e.message) }
  finally { taskLoading.value = false }
}

function selectTask(task) {
  selectedTask.value = task
  loadSummary()
}

async function loadSummary() {
  if (!selectedTask.value) return
  summaryLoading.value = true
  try {
    const resp = await api.get(`/api/v1/settlement/reconcile/tasks/${selectedTask.value.task_id}/summary`)
    if (resp.success) summary.value = resp.data || {}
  } catch (e) { console.warn(e.message) }
  finally { summaryLoading.value = false }
}

async function handleCreateTask() {
  creating.value = true
  try {
    const f = { ...createForm.value }
    const resp = await api.post('/api/v1/settlement/reconcile/tasks', f)
    if (resp.success) {
      loadTasks()
    }
  } catch (e) { alert('创建失败: ' + e.message) }
  finally { creating.value = false }
}

onMounted(async () => {
  await loadTasks()
  if (typeof sessionStorage !== 'undefined' && sessionStorage.getItem('focus_settlement') === '1') {
    sessionStorage.removeItem('focus_settlement')
    await nextTick()
    document.getElementById('settlement-task-list')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
})
</script>
