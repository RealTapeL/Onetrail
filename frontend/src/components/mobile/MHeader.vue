<script setup>
/** 移动端 slim 头部（logo + 用户 chip），对齐 M1-M4 设计稿 */
import { useRouter } from 'vue-router'
import { session, logout } from '../../api/http'

const router = useRouter()

function onLogout() {
  logout()
  router.push('/login')
}
</script>

<template>
  <header class="m-header">
    <router-link class="logo" to="/plan">
      <svg class="mark" viewBox="0 0 20 20">
        <rect width="20" height="20" fill="#2F5B2A"/>
        <rect x="9" y="4" width="3" height="3" fill="#FFF"/><rect x="6" y="7" width="3" height="3" fill="#FFF"/>
        <rect x="12" y="7" width="3" height="3" fill="#FFF"/><rect x="3" y="10" width="3" height="3" fill="#FFF"/>
        <rect x="9" y="10" width="3" height="3" fill="#FFF"/><rect x="15" y="10" width="3" height="3" fill="#FFF"/>
      </svg>
      <span class="en">ONE TRAIL</span>
    </router-link>
    <button v-if="session.user" class="lv as-btn" title="退出登录" @click="onLogout">
      {{ session.user.display_name }} ⏻
    </button>
    <span v-else class="lv">HIKER</span>
  </header>
</template>

<style scoped>
.m-header {
  position: fixed;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  z-index: 20;
  height: calc(48px + var(--sat));
  padding: var(--sat) 16px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--bg);
}
.logo { display: flex; align-items: center; gap: 8px; text-decoration: none; }
.mark { width: 20px; height: 20px; }
.en { font-family: var(--p8); font-size: 9px; color: var(--lime); }
.lv {
  background: var(--panel);
  border: 1px solid var(--line);
  padding: 4px 8px;
  font-family: var(--silk);
  font-size: 9px;
  color: var(--lime);
}
.as-btn { cursor: pointer; }
.as-btn:active { color: var(--red); border-color: var(--red); }
</style>
