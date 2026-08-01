<script setup>
import HudNav from './HudNav.vue'
const emit = defineEmits(['nav'])

const scenes = ['瀑布', '古道', '竹林', '云海', '星空']
const cards = [
  { img: '/images/2_388.webp', name: '九溪十八涧 · 环线', meta: '9.5KM · 爬升 320M · Lv.2 · 评分 4.8' },
  { img: '/images/2_392.webp', name: '徽杭古道 · 精华段', meta: '12.5KM · 爬升 480M · Lv.3 · 评分 4.7' },
  { img: '/images/2_396.webp', name: '大明山 · 云海线',   meta: '8.2KM · 爬升 650M · Lv.4 · 评分 4.6' },
  { img: '/images/2_400.webp', name: '鸬鸟山温泉线',     meta: '6.0KM · 爬升 180M · Lv.1 · 评分 4.5' },
  { img: '/images/2_404.webp', name: '径山古道',         meta: '7.8KM · 爬升 260M · Lv.2 · 评分 4.7' },
  { img: '/images/2_408.webp', name: '清凉峰 · 星空线',   meta: '14.0KM · 爬升 920M · Lv.5 · 评分 4.9' }
]
</script>

<template>
  <section class="screen">
    <HudNav active="lib" @nav="emit('nav', $event)" />

    <header class="screen-head" style="height:116px;">
      <div>
        <div class="sh-title-cn">「05」路线库 · 搜索发现</div>
        <div class="sh-title-en">ROUTE LIBRARY — SEARCH &amp; DISCOVER</div>
      </div>
    </header>

    <!-- 搜索 1440×68 -->
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
      <span class="weather-chip">本周晴好 · 适合溪谷竹林线</span>
    </div>

    <!-- 筛选 1440×84 -->
    <div class="filter-sec">
      <div class="f-row1">
        <span class="f-label">景观 SCENE</span>
        <span v-for="s in scenes" :key="s" class="f-chip" :class="{ on: s === '竹林' }">{{ s }}</span>
      </div>
      <div class="f-row2">难度 Lv.1 – Lv.5 · 距离 ≤ 15KM · 新手 / 亲子 / 硬核 · 更多筛选 →</div>
    </div>

    <!-- 卡片区 1440×546 -->
    <div class="grid">
      <article v-for="c in cards" :key="c.name" class="lib-card panel-d" @click="emit('nav', 's3')">
        <img class="lc-img" :src="c.img" :alt="c.name" />
        <div class="lc-name">{{ c.name }}</div>
        <div class="lc-meta">{{ c.meta }}</div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.search-row {
  height: 68px;
  padding: 0 48px;
  display: flex;
  align-items: center;
  gap: 16px;
}
.search-input {
  width: 1070px;
  height: 48px;
  background: #FFFFFF;
  border: 2px solid var(--ink);
  box-shadow: var(--sh-lime-4);
  display: flex;
  align-items: center;
  padding: 0 16px;
}
.ph { font-size: 14px; color: #9A9A9A; }
.search-btn {
  width: 48px; height: 48px; flex: none;
  background: var(--lime);
  border: 2px solid var(--ink);
  display: grid; place-items: center;
}
.weather-chip {
  background: var(--bg);
  border: 1px solid var(--lime);
  color: var(--lime);
  font-size: 13px; font-weight: 700;
  padding: 12px 16px;
  white-space: nowrap;
}

.filter-sec {
  height: 84px;
  padding: 12px 48px 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.f-row1 { display: flex; align-items: center; gap: 10px; }
.f-label { font-family: var(--silk); font-size: 11px; color: var(--t2); margin-right: 2px; }
.f-chip {
  background: var(--panel);
  border: 1px solid var(--line);
  color: var(--t1);
  font-size: 12px; font-weight: 500;
  padding: 7px 12px;
}
.f-chip.on { background: var(--lime); border-color: var(--lime); color: var(--ink); font-weight: 700; }
.f-row2 { font-size: 12px; color: var(--t2); }

.grid {
  height: 546px;
  padding: 20px 48px 0;
  display: grid;
  grid-template-columns: repeat(3, 432px);
  gap: 24px;
  align-content: start;
}
.lib-card {
  width: 432px;
  height: 241px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  cursor: pointer;
}
.lc-img { width: 400px; height: 150px; object-fit: cover; display: block; }
.lc-name { font-size: 15px; font-weight: 700; color: #FFFFFF; }
.lc-meta { font-size: 12px; color: var(--t2); }
</style>
