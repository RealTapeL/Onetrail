<script setup>
/**
 * 共享标签 · 对齐 Ardot 组件 Chip / Dark | Lime | LimeFill | Warn
 * variant: dark（深底灰边）| lime（荧光绿描边）| limeFill（荧光绿底）| warn（街机黄描边）
 */
defineProps({
  variant: { type: String, default: 'dark' },
  bold: { type: Boolean, default: false }
})
</script>

<template>
  <span class="chip" :class="[variant, { bold }]"><slot /></span>
</template>

<style scoped>
.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}
.chip.bold { font-weight: 700; }
.dark { background: var(--panel); border: 1px solid var(--line); color: var(--t1); }
.lime { background: var(--bg); border: 1px solid var(--lime); color: var(--lime); }
.limeFill { background: var(--lime); border: 1px solid var(--lime); color: var(--ink); font-weight: 700; }
.warn { background: var(--bg); border: 1px solid var(--amber); color: var(--amber); }
</style>
