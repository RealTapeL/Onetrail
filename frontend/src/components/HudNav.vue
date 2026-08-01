<script setup>
/**
 * HUD Nav · Web 顶部导航（对齐 Ardot 组件 6:4）
 * 菜单对齐束状 IA：开始规划 / 路线库 / 我的行程 / 装备
 * 激活态由路由 meta.bundle 决定
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { me } from '../api/mock'

const route = useRoute()
const active = computed(() => route.meta.bundle || 'plan')

const menus = [
  { key: 'plan', label: '开始规划', to: '/plan' },
  { key: 'library', label: '路线库', to: '/routes' },
  { key: 'trip', label: '我的行程', to: '/trip/current' },
  { key: 'gear', label: '装备', to: '/gear' }
]
</script>

<template>
  <nav class="hud-nav">
    <router-link class="logo" to="/plan">
      <span class="logo-mark">
        <i v-for="p in [[12,6],[8,10],[16,10],[4,14],[12,14],[20,14]]"
           :key="p.join(',')" :style="{ left: p[0]+'px', top: p[1]+'px' }" />
      </span>
      <span class="logo-cn">一径</span>
      <span class="logo-en">ONE TRAIL</span>
    </router-link>

    <div class="menu">
      <router-link v-for="m in menus" :key="m.key"
                   class="mi" :class="{ on: active === m.key }"
                   :to="m.to">{{ m.label }}</router-link>
    </div>

    <div class="right">
      <span class="hud-chip">LV.{{ me.level }} {{ me.levelTitle }}</span>
      <button class="login">登录 / 注册</button>
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
.logo { display: flex; align-items: center; gap: 12px; cursor: pointer; text-decoration: none; }
.logo-mark { position: relative; width: 28px; height: 28px; background: #2F5B2A; flex: none; }
.logo-mark i { position: absolute; width: 4px; height: 4px; background: #FFFFFF; }
.logo-cn { font-size: 20px; font-weight: 900; color: #FFFFFF; }
.logo-en { font-family: var(--p8); font-size: 11px; color: var(--lime); }

.menu { display: flex; align-items: center; gap: 32px; }
.mi { font-size: 14px; font-weight: 500; color: var(--t2); text-decoration: none; }
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
.login { background: var(--lime); padding: 10px 20px; font-size: 13px; font-weight: 700; color: var(--ink); }
</style>
