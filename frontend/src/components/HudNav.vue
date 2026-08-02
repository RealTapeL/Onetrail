<script setup>
/**
 * HUD Nav · Web 顶部导航（对齐 Ardot 组件 6:4）
 * 菜单对齐束状 IA：开始规划 / 路线库 / 我的行程 / 装备
 * 激活态由路由 meta.bundle 决定
 */
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { session, logout } from '../api/http'

const route = useRoute()
const router = useRouter()
const active = computed(() => route.meta.bundle || 'plan')

function onLogout() {
  logout()
  router.push('/login')
}

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
      <span class="user">
        <i class="dot" :class="{ off: !session.user }" />{{ session.user ? session.user.display_name : '连接中…' }}
      </span>
      <button v-if="session.user" class="logout" @click="onLogout">退出</button>
    </div>
  </nav>
</template>

<style scoped>
.hud-nav {
  width: 100%;
  height: 72px;
  padding: 0 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  background: var(--bg);
  flex: none;
}
.logo { display: flex; align-items: center; gap: 12px; cursor: pointer; text-decoration: none; }
.logo-mark { position: relative; width: 28px; height: 28px; background: #2F5B2A; flex: none; }
.logo-mark i { position: absolute; width: 4px; height: 4px; background: #FFFFFF; }
.logo-cn { font-size: 20px; font-weight: 900; color: #FFFFFF; }
.logo-en { font-family: var(--p8); font-size: 11px; color: var(--lime); }

.menu { display: flex; align-items: center; gap: 32px; flex: none; }
.mi { font-size: 14px; font-weight: 500; color: var(--t2); text-decoration: none; }
.mi.on { color: var(--lime); font-weight: 700; }
.mi:hover { color: var(--t1); }
.mi.on:hover { color: var(--lime); }

.right { display: flex; align-items: center; gap: 10px; }
.logout {
  background: none;
  border: 1px solid var(--line);
  padding: 8px 12px;
  font-family: var(--silk);
  font-size: 11px;
  color: var(--t3);
  cursor: pointer;
}
.logout:hover { color: var(--red); border-color: var(--red); }
.user {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--panel);
  border: 1px solid var(--line);
  padding: 8px 14px;
  font-family: var(--silk);
  font-size: 11px;
  color: var(--lime);
}
.dot { width: 8px; height: 8px; background: var(--lime); flex: none; }
.dot.off { background: var(--t4); }

/* 小屏（如移动端进发布路线页）：收缩菜单间距，隐藏英文标与用户 chip 防溢出 */
@media (max-width: 860px) {
  .hud-nav { padding: 0 16px; }
  .menu { gap: 16px; }
  .logo-en, .user { display: none; }
}
@media (max-width: 520px) {
  .menu { gap: 10px; }
  .mi { font-size: 12px; }
}
</style>
