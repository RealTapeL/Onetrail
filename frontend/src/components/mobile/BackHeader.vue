<script setup>
/** 下层页返回头（像素箭头 + 返回文字 + 右侧信息位），对齐 M5/M6 设计稿 */
defineProps({
  backText: { type: String, default: '返回' },
  to: { type: String, default: '' }
})
</script>

<template>
  <header class="back-header">
    <button class="back" @click="to ? $router.push(to) : $router.back()">
      <svg viewBox="0 0 16 16" class="arrow">
        <rect x="7" y="2" width="3" height="3"/><rect x="4" y="5" width="3" height="3"/>
        <rect x="1" y="8" width="3" height="3"/><rect x="4" y="11" width="3" height="3"/>
        <rect x="7" y="8" width="8" height="3"/>
      </svg>
      <span>{{ backText }}</span>
    </button>
    <span class="right"><slot /></span>
  </header>
</template>

<style scoped>
.back-header {
  position: fixed;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  z-index: 20;
  height: 48px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--bg);
}
.back { display: flex; align-items: center; gap: 8px; color: var(--lime); font-size: 12px; font-weight: 500; }
.arrow { width: 16px; height: 16px; fill: var(--lime); }
.right { font-size: 10px; font-weight: 700; color: var(--lime); }
</style>
