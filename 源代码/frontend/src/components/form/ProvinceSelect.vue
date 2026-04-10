<template>
  <div class="relative">
    <label v-if="label" class="block text-xs text-gray-500 mb-1">{{ label }}<span v-if="required" class="text-cyan-400"> *</span></label>
    <button
      ref="triggerRef"
      type="button"
      class="input-glow w-full flex items-center justify-between gap-2 text-left text-sm py-2.5 px-3 rounded-xl"
      :class="open ? 'ring-1 ring-cyan-400/40' : ''"
      @click.stop="toggle"
    >
      <span class="text-white truncate">
        {{ currentName }} <span class="font-mono text-cyan-400/90">{{ modelValue }}</span>
      </span>
      <svg class="w-3.5 h-3.5 text-gray-500 transition shrink-0" :class="{ 'rotate-180': open }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
        <path d="M6 9l6 6 6-6"/>
      </svg>
    </button>

    <Teleport to="body">
      <Transition name="dropdown-fade">
        <div
          v-show="open"
          ref="panelRef"
          class="fixed max-h-72 overflow-y-auto rounded-xl border border-cyan-500/30 bg-dark-100/[0.97] backdrop-blur-xl shadow-xl shadow-cyan-950/40 py-1 custom-scrollbar z-[10050]"
          :style="dropdownStyle"
        >
          <button
            v-for="p in provinces"
            :key="p.code"
            type="button"
            class="w-full text-left px-3 py-2.5 hover:bg-cyan-500/10 transition flex flex-col gap-0.5 border-b border-cyan-500/10 last:border-0"
            :class="modelValue === p.code ? 'bg-cyan-500/15' : ''"
            @click.stop="select(p.code)"
          >
            <div class="flex items-center justify-between gap-2">
              <span class="text-sm text-white font-medium">{{ p.name }}</span>
              <span class="font-mono text-xs text-cyan-400">{{ p.code }}</span>
            </div>
            <div v-if="metricLine(p.code)" class="text-[10px] text-gray-500 leading-snug">
              {{ metricLine(p.code) }}
            </div>
          </button>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { TOP10_POWER_PROVINCES } from '@/constants/provinces'
import { api } from '@/utils/api'

const props = defineProps({
  modelValue: { type: String, required: true },
  label: { type: String, default: '' },
  required: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const triggerRef = ref(null)
const panelRef = ref(null)
const dropdownPos = ref({ top: 0, left: 0, width: 0 })
const metricsMap = ref({})

const dropdownStyle = computed(() => ({
  top: `${dropdownPos.value.top}px`,
  left: `${dropdownPos.value.left}px`,
  width: `${dropdownPos.value.width}px`,
}))

function updateDropdownPosition() {
  const el = triggerRef.value
  if (!el) return
  const r = el.getBoundingClientRect()
  const gap = 4
  const maxH = 288
  let top = r.bottom + gap
  if (top + maxH > window.innerHeight && r.top > maxH + gap) {
    top = r.top - maxH - gap
  }
  dropdownPos.value = {
    top,
    left: r.left,
    width: r.width,
  }
}
const metricsLoaded = ref(false)

const provinces = TOP10_POWER_PROVINCES

const currentName = computed(() => {
  const f = provinces.find((x) => x.code === props.modelValue)
  return f ? f.name : '请选择'
})

function metricLine(code) {
  const m = metricsMap.value[code]
  if (!m) return ''
  return `最新交易日 ${m.market_date} · 均价 ${m.avg_price} 元/MWh · 最低 ${m.min_price} · 最高 ${m.max_price} · ${m.point_count} 时点`
}

async function loadMetrics() {
  try {
    const resp = await api.get('/api/v1/market/province-metrics')
    if (resp.success && Array.isArray(resp.data?.provinces)) {
      const map = {}
      for (const row of resp.data.provinces) {
        map[row.province_code] = row
      }
      metricsMap.value = map
    }
  } catch {
    metricsMap.value = {}
  } finally {
    metricsLoaded.value = true
  }
}

function toggle() {
  open.value = !open.value
  if (open.value && !metricsLoaded.value) {
    loadMetrics()
  }
}

function select(code) {
  emit('update:modelValue', code)
  open.value = false
}

function onDocClick(e) {
  if (!open.value) return
  const el = e.target
  if (triggerRef.value?.contains(el)) return
  if (panelRef.value?.contains(el)) return
  open.value = false
}

function onReposition() {
  if (open.value) updateDropdownPosition()
}

watch(open, async (isOpen) => {
  if (isOpen) {
    await nextTick()
    updateDropdownPosition()
    window.addEventListener('scroll', onReposition, true)
    window.addEventListener('resize', onReposition)
  } else {
    window.removeEventListener('scroll', onReposition, true)
    window.removeEventListener('resize', onReposition)
  }
})

onMounted(() => document.addEventListener('click', onDocClick))
onUnmounted(() => {
  document.removeEventListener('click', onDocClick)
  window.removeEventListener('scroll', onReposition, true)
  window.removeEventListener('resize', onReposition)
})
</script>

<style scoped>
.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity 0.12s ease, transform 0.12s ease;
}
.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-3px);
}
</style>
