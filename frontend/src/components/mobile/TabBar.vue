<script setup>
/** 移动端底部 Tab · 对齐 Ardot 组件 6:28（4 等分格，激活按束高亮） */
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const active = computed(() => route.meta.bundle || 'plan')

const tabs = [
  {
    key: 'plan', label: '规划', to: '/plan',
    icon: '<rect x="8" y="2" width="2" height="16"/><rect x="10" y="2" width="8" height="3"/><rect x="10" y="5" width="6" height="3"/><rect x="10" y="8" width="4" height="3"/>'
  },
  {
    key: 'library', label: '路线库', to: '/routes',
    icon: '<rect x="2" y="3" width="16" height="3"/><rect x="2" y="8" width="16" height="3"/><rect x="2" y="13" width="10" height="3"/>'
  },
  {
    key: 'trip', label: '行程', to: '/trip/current',
    icon: '<rect x="7" y="2" width="6" height="3"/><rect x="5" y="5" width="10" height="11"/><rect x="7" y="8" width="6" height="3" class="cut"/><rect x="7" y="12" width="6" height="4" class="cut"/>'
  },
  {
    key: 'gear', label: '装备', to: '/gear',
    icon: '<rect x="2" y="13" width="16" height="3"/><rect x="4" y="8" width="9" height="5"/><rect x="13" y="10" width="5" height="3"/><rect x="6" y="6" width="2" height="2"/><rect x="9" y="7" width="2" height="2"/>'
  },
  {
    key: 'me', label: '我的', to: '/me',
    icon: '<rect x="7" y="2" width="6" height="6"/><rect x="4" y="11" width="12" height="3"/><rect x="6" y="14" width="8" height="4"/>'
  }
]
</script>

<template>
  <div class="tab-spacer" />
  <nav class="tab-bar">
    <router-link v-for="t in tabs" :key="t.key" class="tab" :class="{ on: active === t.key }" :to="t.to">
      <svg viewBox="0 0 20 20" class="ti" v-html="t.icon" />
      <span class="tl">{{ t.label }}</span>
    </router-link>
  </nav>
</template>

<style scoped>
/* 占位块：在文档流中撑起固定导航的高度，防止内容被遮挡 */
.tab-spacer { height: calc(56px + var(--sab)); flex: none; }
.tab-bar {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  z-index: 20;
  display: flex;
  height: calc(56px + var(--sab));
  padding-bottom: var(--sab);
  background: var(--bg);
  border-top: 1px solid var(--line);
}
.tab {
  width: 20%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  text-decoration: none;
}
.ti { width: 20px; height: 20px; fill: var(--t2); }
.ti :deep(.cut) { fill: #0B0B0B; }
.tl { font-size: 10px; font-weight: 500; color: var(--t2); }
.tab.on .ti { fill: var(--lime); }
.tab.on .tl { color: var(--lime); }
</style>
