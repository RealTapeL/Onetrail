<script setup>
/** M2 路线库 · 搜索发现（移动端 Tab 2，对齐设计稿 6:22） */
import MHeader from './MHeader.vue'
import TabBar from './TabBar.vue'
import { routeLibrary, weatherTip } from '../../api/mock'
</script>

<template>
  <div class="m-screen">
    <MHeader />
    <div class="m-body">
      <div class="search-row">
        <div class="search-input"><span class="ph">搜索路线、山峰、地名…</span></div>
        <button class="search-btn" aria-label="搜索">
          <svg viewBox="0 0 20 20" width="20" height="20">
            <circle cx="9" cy="9" r="5" fill="none" stroke="#0B0B0B" stroke-width="2.5"/>
            <line x1="13" y1="13" x2="17" y2="17" stroke="#0B0B0B" stroke-width="2.5"/>
          </svg>
        </button>
      </div>
      <div class="weather">{{ weatherTip.text }}</div>
      <div class="f-label">景观 SCENE</div>
      <div class="chips">
        <span v-for="s in routeLibrary.scenes" :key="s" class="chip"
              :class="{ on: s === routeLibrary.activeScene }">{{ s }}</span>
      </div>

      <article v-for="c in routeLibrary.items" :key="c.id" class="card"
               @click="$router.push(`/routes/${c.id}`)">
        <img class="card-img" :src="c.img" :alt="c.name" />
        <div class="card-name">{{ c.name }}</div>
        <div class="card-meta">{{ c.meta }}</div>
      </article>
    </div>
    <TabBar />
  </div>
</template>

<style scoped>
.search-row { display: flex; gap: 10px; }
.search-input {
  flex: 1; height: 44px;
  background: #FFF; border: 2px solid var(--ink); box-shadow: var(--sh-lime-4);
  display: flex; align-items: center; padding: 0 12px;
}
.ph { font-size: 12px; color: #9A9A9A; }
.search-btn {
  width: 44px; height: 44px; flex: none;
  background: var(--lime); border: 2px solid var(--ink);
  display: grid; place-items: center;
}
.weather { font-size: 10px; font-weight: 700; color: var(--lime); }
.f-label { font-family: var(--silk); font-size: 9px; color: var(--t2); }
.chips { display: flex; gap: 8px; flex-wrap: wrap; }
.chip { background: var(--panel); border: 1px solid var(--line); color: var(--t1); font-size: 11px; font-weight: 500; padding: 6px 10px; }
.chip.on { background: var(--lime); border-color: var(--lime); color: var(--ink); font-weight: 700; }
.card {
  background: var(--panel); border: 1px solid var(--line);
  padding: 12px; display: flex; flex-direction: column; gap: 8px; cursor: pointer;
}
.card-img { width: 100%; height: 120px; object-fit: cover; }
.card-name { font-size: 14px; font-weight: 700; color: #FFF; }
.card-meta { font-size: 11px; color: var(--t2); }
</style>
