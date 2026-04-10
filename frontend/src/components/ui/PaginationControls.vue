<template>
  <div class="flex items-center gap-2" :class="wrapperClass">
    <button
      type="button"
      class="pagination-arrow"
      :disabled="prevDisabled"
      :aria-label="prevLabel"
      @click="$emit('prev')"
    >
      <svg class="pagination-arrow__svg" viewBox="0 0 24 24" aria-hidden="true">
        <path
          d="M14.5 6.5 8 12l6.5 5.5"
          fill="none"
          stroke="currentColor"
          stroke-width="2.2"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
    </button>
    <span class="pagination-page">{{ page }}</span>
    <button
      type="button"
      class="pagination-arrow"
      :disabled="nextDisabled"
      :aria-label="nextLabel"
      @click="$emit('next')"
    >
      <svg class="pagination-arrow__svg" viewBox="0 0 24 24" aria-hidden="true">
        <path
          d="M9.5 6.5 16 12l-6.5 5.5"
          fill="none"
          stroke="currentColor"
          stroke-width="2.2"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
    </button>
  </div>
</template>

<script setup>
defineProps({
  page: { type: [Number, String], required: true },
  prevDisabled: { type: Boolean, default: false },
  nextDisabled: { type: Boolean, default: false },
  wrapperClass: { type: String, default: '' },
  prevLabel: { type: String, default: '上一页' },
  nextLabel: { type: String, default: '下一页' },
})

defineEmits(['prev', 'next'])
</script>

<style scoped>
.pagination-arrow {
  @apply inline-flex items-center justify-center min-w-[2.5rem] h-9 rounded-lg transition-all duration-200;
  @apply border border-amber-500/35 text-amber-200/95 bg-dark-200/40;
  @apply hover:border-amber-400/55 hover:bg-amber-500/10 hover:text-amber-100;
  @apply disabled:opacity-35 disabled:pointer-events-none disabled:hover:bg-dark-200/40;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.pagination-arrow__svg {
  width: 1.1rem;
  height: 1.1rem;
}

.pagination-page {
  @apply min-w-[2.5rem] h-9 inline-flex items-center justify-center rounded-lg text-sm font-semibold font-mono;
  @apply bg-gradient-to-b from-dark-200 to-dark-300/90 text-amber-200 border border-amber-500/25;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
}
</style>
