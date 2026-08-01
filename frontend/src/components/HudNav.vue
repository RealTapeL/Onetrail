<script setup>
/* HUD Nav — 6 屏共用，1440×72，pad 0 40，space-between */
import { store } from '../store'

defineProps({
  active: { type: String, default: 'plan' } // plan | lib | gear | community | none
})
const emit = defineEmits(['nav'])

const menus = [
  { key: 'plan', label: '开始规划', to: 's1' },
  { key: 'lib', label: '路线库', to: 's5' },
  { key: 'gear', label: '装备比选', to: 's6' },
  { key: 'community', label: '社区', to: 's3' }
]
</script>

<template>
  <nav class="hud-nav">
    <div class="logo" @click="emit('nav', 's1')">
      <span class="logo-mark">
        <i v-for="p in [[12,6],[8,10],[16,10],[4,14],[12,14],[20,14]]"
           :key="p.join(',')" :style="{ left: p[0]+'px', top: p[1]+'px' }" />
      </span>
      <span class="logo-cn">一径</span>
      <span class="logo-en">ONE TRAIL</span>
    </div>

    <div class="menu">
      <button v-for="m in menus" :key="m.key"
              class="mi" :class="{ on: active === m.key }"
              @click="emit('nav', m.to)">{{ m.label }}</button>
    </div>

    <div class="right">
      <span class="hud-chip">{{ store.session.user ? store.session.user.display_name : '未连接' }}</span>
      <span class="login">{{ store.session.user ? '已登录' : '连接中…' }}</span>
    </div>
  </nav>
</template>

<style scoped>
.hud-nav {
  width: 1440px;
  height: 72px;
  padding: 0 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--bg);
  flex: none;
}
.logo { display: flex; align-items: center; gap: 12px; cursor: pointer; }
.logo-mark {
  position: relative;
  width: 28px; height: 28px;
  background: #2F5B2A;
  flex: none;
}
.logo-mark i {
  position: absolute;
  width: 4px; height: 4px;
  background: #FFFFFF;
}
.logo-cn { font-size: 20px; font-weight: 900; color: #FFFFFF; }
.logo-en { font-family: var(--p8); font-size: 11px; color: var(--lime); }

.menu { display: flex; align-items: center; gap: 32px; }
.mi { font-size: 14px; font-weight: 500; color: var(--t2); }
.mi.on { color: var(--lime); font-weight: 700; }
.mi:hover { color: var(--t1); }
.mi.on:hover { color: var(--lime); }

.right { display: flex; align-items: center; gap: 16px; }
.hud-chip {
  background: var(--panel);
  border: 1px solid var(--line);
  padding: 6px 12px;
  font-family: var(--silk);
  font-size: 11px;
  color: var(--lime);
}
.login {
  background: var(--lime);
  padding: 10px 20px;
  font-size: 13px;
  font-weight: 700;
  color: var(--ink);
}
</style>
