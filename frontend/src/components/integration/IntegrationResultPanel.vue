<template>
  <div class="rounded-xl border border-amber-500/10 bg-dark-200/50 overflow-hidden">
    <div
      v-if="result.error"
      class="border-b border-red-500/20 bg-red-500/5 px-4 py-3 text-sm text-red-300"
    >
      <i class="fas fa-exclamation-circle mr-2"></i>{{ result.error }}
    </div>
    <template v-else>
      <div class="border-b border-amber-500/10 px-4 py-3 flex flex-wrap items-center gap-2">
        <span class="text-xs text-gray-500">数据来源</span>
        <span class="rounded-md bg-amber-500/10 px-2 py-0.5 font-mono text-xs text-amber-300">
          {{ result.source || '—' }}
        </span>
      </div>
      <div class="divide-y divide-amber-500/10 max-h-72 overflow-y-auto">
        <div
          v-for="(row, idx) in rows"
          :key="idx"
          class="flex gap-3 px-4 py-2.5 text-sm max-md:flex-col"
        >
          <span class="shrink-0 text-xs text-gray-500 md:w-44 font-mono break-all">{{ row.path }}</span>
          <span class="min-w-0 flex-1 text-gray-200 break-words">{{ row.display }}</span>
        </div>
        <p v-if="rows.length === 0" class="px-4 py-6 text-center text-xs text-gray-500">暂无结构化字段可展示</p>
      </div>
      <details class="group border-t border-amber-500/10 bg-dark-300/20">
      <summary
        class="cursor-pointer list-none px-4 py-2 text-xs text-gray-500 hover:text-gray-400 [&::-webkit-details-marker]:hidden"
      >
        <span class="inline-flex items-center gap-2">
          <i class="fas fa-terminal text-[10px] text-amber-500/50"></i>
          原始 JSON（调试用）
          <i class="fas fa-chevron-down text-[9px] transition group-open:rotate-180"></i>
        </span>
      </summary>
      <pre
        class="max-h-40 overflow-auto border-t border-amber-500/10 p-3 font-mono text-[10px] text-gray-500 leading-relaxed"
      >{{ rawJson }}</pre>
      </details>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  result: { type: Object, required: true },
})

const LIMIT = 80

function flattenPayload(obj, prefix = '', out = []) {
  if (out.length >= LIMIT) return out
  if (obj === null || obj === undefined) {
    out.push({ path: prefix || '(root)', display: String(obj) })
    return out
  }
  const t = typeof obj
  if (t !== 'object') {
    out.push({ path: prefix || '(root)', display: String(obj) })
    return out
  }
  if (Array.isArray(obj)) {
    if (obj.length === 0) {
      out.push({ path: prefix, display: '（空列表）' })
      return out
    }
    const allPrimitive = obj.every((x) => x === null || ['string', 'number', 'boolean'].includes(typeof x))
    if (obj.length <= 8 && allPrimitive) {
      out.push({ path: prefix, display: obj.map(String).join('，') })
      return out
    }
    const cap = Math.min(obj.length, 12)
    for (let i = 0; i < cap && out.length < LIMIT; i++) {
      flattenPayload(obj[i], `${prefix}[${i}]`, out)
    }
    if (obj.length > cap) {
      out.push({ path: prefix, display: `… 共 ${obj.length} 条，已折叠展示前 ${cap} 条` })
    }
    return out
  }
  const entries = Object.entries(obj)
  if (entries.length === 0) {
    out.push({ path: prefix || '(object)', display: '（空对象）' })
    return out
  }
  for (const [k, v] of entries) {
    if (out.length >= LIMIT) break
    const p = prefix ? `${prefix}.${k}` : k
    if (v !== null && typeof v === 'object') {
      flattenPayload(v, p, out)
    } else {
      out.push({ path: p, display: v === undefined ? 'undefined' : String(v) })
    }
  }
  return out
}

const rows = computed(() => {
  const r = props.result
  if (!r || r.error) return []
  const payload = r.payload !== undefined ? r.payload : r
  return flattenPayload(payload, 'payload')
})

const rawJson = computed(() => {
  try {
    return JSON.stringify(props.result, null, 2)
  } catch {
    return ''
  }
})
</script>
