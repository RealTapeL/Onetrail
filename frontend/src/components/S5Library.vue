<script setup>
/** S5 路线库 · 搜索发现（桌面端，对齐设计稿 2:338） */
import HudNav from './HudNav.vue'
import { routeLibrary, weatherTip } from '../api/mock'
</script>

<template>
  <section class="screen">
    <HudNav />

    <header class="screen-head" style="height:116px;">
      <div>
        <div class="sh-title-cn">「05」路线库 · 搜索发现</div>
        <div class="sh-title-en">ROUTE LIBRARY — SEARCH &amp; DISCOVER</div>
      </div>
    </header>

    <div class="search-row">
      <div class="search-input">
        <span class="ph">搜索路线、山峰、地名…</span>
      </div>
      <button class="search-btn" aria-label="搜索">
        <svg viewBox="0 0 24 24" width="24" height="24">
          <circle cx="10" cy="10" r="6" fill="none" stroke="#0B0B0B" stroke-width="3" />
          <line x1="15" y1="15" x2="21" y2="21" stroke="#0B0B0B" stroke-width="3" />
        </svg>
      </button>
      <span class="weather-chip">{{ weatherTip.text }}</span>
    </div>

    <div class="filter-sec">
      <div class="f-row1">
        <span class="f-label">景观 SCENE</span>
        <span v-for="s in routeLibrary.scenes" :key="s" class="f-chip"
              :class="{ on: s === routeLibrary.activeScene }">{{ s }}</span>
      </div>
      <div class="f-row2">{{ routeLibrary.filterSummary }}</div>
    </div>

    <div class="grid">
      <article v-for="c in routeLibrary.items" :key="c.id" class="lib-card panel-d"
               @click="$router.push(`/routes/${c.id}`)">
        <img class="lc-img" :src="c.img" :alt="c.name" />
        <div class="lc-name">{{ c.name }}</div>
        <div class="lc-meta">{{ c.meta }}</div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.search-row { height: 68px; padding: 0 48px; display: flex; align-items: center; gap: 16px; }
.search-input {
  width: 1070px; height: 48px;
  background: #FFFFFF; border: 2px solid var(--ink); box-shadow: var(--sh-lime-4);
  display: flex; align-items: center; padding: 0 16px;
}
.ph { font-size: 14px; color: #9A9A9A; }
.search-btn { width: 48px; height: 48px; flex: none; background: var(--lime); border: 2px solid var(--ink); display: grid; place-items: center; }
.weather-chip { background: var(--bg); border: 1px solid var(--lime); color: var(--lime); font-size: 13px; font-weight: 700; padding: 12px 16px; white-space: nowrap; }

.filter-sec { height: 84px; padding: 12px 48px 0; display: flex; flex-direction: column; gap: 12px; }
.f-row1 { display: flex; align-items: center; gap: 10px; }
.f-label { font-family: var(--silk); font-size: 11px; color: var(--t2); margin-right: 2px; }
.f-chip { background: var(--panel); border: 1px solid var(--line); color: var(--t1); font-size: 12px; font-weight: 500; padding: 7px 12px; }
.f-chip.on { background: var(--lime); border-color: var(--lime); color: var(--ink); font-weight: 700; }
.f-row2 { font-size: 12px; color: var(--t2); }

.grid { height: 546px; padding: 20px 48px 0; display: grid; grid-template-columns: repeat(3, 432px); gap: 24px; align-content: start; }
.lib-card { width: 432px; height: 241px; padding: 16px; display: flex; flex-direction: column; gap: 10px; cursor: pointer; }
.lc-img { width: 400px; height: 150px; object-fit: cover; display: block; }
.lc-name { font-size: 15px; font-weight: 700; color: #FFFFFF; }
.lc-meta { font-size: 12px; color: var(--t2); }
</style>
