<template>
  <div class="relative min-h-screen bg-[#020308] overflow-hidden">
    <!-- 电力流动画背景 -->
    <PowerFlowBackground />
    
    <!-- 主应用内容 -->
    <div class="relative z-10">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<script setup>
import PowerFlowBackground from '@/components/background/PowerFlowBackground.vue'
</script>

<style>
.page-enter-active,
.page-leave-active {
  transition: all 0.3s ease;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
