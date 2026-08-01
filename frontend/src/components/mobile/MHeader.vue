<script setup>
/** 移动端 slim 头部（logo + 用户 chip），对齐 M1-M4 设计稿 */
import { session } from '../../api/http'
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
    <span class="lv">{{ session.user?.display_name || 'HIKER' }}</span>
  </header>
</template>

<style scoped>
.m-header {
  height: 48px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--bg);
  flex: none;
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
</style>
