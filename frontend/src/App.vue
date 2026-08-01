<script setup>
import { onMounted, ref } from 'vue'
import HudNav from './components/HudNav.vue'
import S1Home from './components/S1Home.vue'
import S2Routes from './components/S2Routes.vue'
import S3Detail from './components/S3Detail.vue'
import S4Exec from './components/S4Exec.vue'
import S5Library from './components/S5Library.vue'
import S6Gear from './components/S6Gear.vue'
import { ensureSession } from './store'

onMounted(ensureSession)

const screens = [
  { id: 's1', label: '01 需求输入', comp: S1Home },
  { id: 's2', label: '02 智能推荐', comp: S2Routes },
  { id: 's3', label: '03 路线详情', comp: S3Detail },
  { id: 's4', label: '04 执行助手', comp: S4Exec },
  { id: 's5', label: '05 路线库',   comp: S5Library },
  { id: 's6', label: '06 装备比选', comp: S6Gear }
]
const active = ref(new URLSearchParams(location.search).get('screen') || 's1')
const go = (id) => { if (screens.some(s => s.id === id)) active.value = id }
</script>

<template>
  <div class="proto">
    <!-- 原型切换条（不属于设计稿） -->
    <div class="switcher">
      <span class="sw-brand">ONE TRAIL PROTOTYPE</span>
      <button v-for="s in screens" :key="s.id"
              class="sw-tab" :class="{ on: active === s.id }"
              @click="go(s.id)">{{ s.label }}</button>
    </div>

    <div class="stage">
      <component :is="screens.find(s => s.id === active).comp" @nav="go" />
    </div>
  </div>
</template>

<style scoped>
.proto { min-height: 100vh; background: #000; }
.switcher {
  position: sticky;
  top: 0;
  z-index: 99;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #111111;
  border-bottom: 1px solid #222222;
}
.sw-brand {
  font-family: var(--silk);
  font-size: 10px;
  color: #555555;
  letter-spacing: 1px;
  margin-right: 12px;
}
.sw-tab {
  font-size: 12px;
  color: #8E8E8E;
  padding: 4px 10px;
  border: 1px solid transparent;
}
.sw-tab:hover { color: #F5F5F5; }
.sw-tab.on { color: #0B0B0B; background: var(--lime); font-weight: 700; }
.stage {
  min-height: calc(100vh - 37px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 24px 0 48px;
}
</style>
