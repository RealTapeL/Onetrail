<script setup>
/**
 * 共享按钮 · 对齐 Ardot 组件 Button / Primary | Secondary | Dark
 * variant: primary（荧光绿+投影）| secondary（白）| dark（深色描边）| ghost（暗灰禁用）
 */
defineProps({
  variant: { type: String, default: 'primary' },
  block: { type: Boolean, default: false }
})
</script>

<template>
  <button class="btn" :class="[variant, { block }]"><slot /></button>
</template>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}
.btn.block { width: 100%; }
.primary { background: var(--lime); color: var(--ink); border: 2px solid var(--ink); box-shadow: var(--sh-ink-4); }
.primary:active { transform: translate(2px, 2px); box-shadow: 2px 2px 0 #0A0A0A; }
.secondary { background: #FFFFFF; color: var(--ink); border: 2px solid var(--ink); }
.dark { background: var(--bg); color: var(--t1); border: 1px solid var(--t1); }
.ghost { background: var(--panel); color: var(--t4); border: 1px solid var(--line); font-weight: 500; cursor: not-allowed; }
</style>
