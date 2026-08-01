<script setup>
import { onMounted, ref } from 'vue'
import HudNav from './HudNav.vue'
import { api } from '../api'
import { selectRoute } from '../store'

const emit = defineEmits(['nav'])

const COVERS = ['/images/2_388.webp', '/images/2_392.webp', '/images/2_396.webp', '/images/2_400.webp', '/images/2_404.webp', '/images/2_408.webp']
const scenes = ['瀑布', '古道', '竹林', '云海', '星空']

const keyword = ref('')
const scene = ref('')
const maxDistance = ref(null)
const cards = ref([])
const total = ref(0)
const weatherTip = ref('')

async function load() {
  const params = new URLSearchParams({ page: '1', page_size: '12' })
  if (keyword.value) params.set('query', keyword.value)
  if (scene.value) params.set('tag', scene.value)
  if (maxDistance.value) params.set('max_distance_km', String(maxDistance.value))
  try {
    const data = await api(`/routes?${params}`, { auth: false })
    total.value = data.total
    cards.value = data.items.map((r, i) => ({
      id: r.id,
      img: COVERS[i % COVERS.length],
      name: r.title,
      meta: `${r.distance_km}KM · 爬升 ${r.elevation_gain_m}M · Lv.${r.level} · ${r.average_rating != null ? `评分 ${r.average_rating}` : '暂无评分'}`
    }))
  } catch {
    cards.value = []
    total.value = 0
  }
}

function toggleScene(s) {
  scene.value = scene.value === s ? '' : s
  load()
}

function toggleDistance() {
  maxDistance.value = maxDistance.value ? null : 15
  load()
}

function open(id) {
  selectRoute(id)
  emit('nav', 's3')
}

onMounted(() => {
  load()
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(async (pos) => {
      try {
        const data = await api(
          `/meta/weather-tip?latitude=${pos.coords.latitude}&longitude=${pos.coords.longitude}`,
          { auth: false }
        )
        weatherTip.value = data.text
      } catch { /* 未配置天气服务时隐藏胶囊 */ }
    })
  }
})
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
        <input v-model="keyword" class="search-real" placeholder="搜索路线、山峰、地名…" @keyup.enter="load" />
      </div>
      <button class="search-btn" aria-label="搜索" @click="load">
        <svg viewBox="0 0 24 24" width="24" height="24">
          <circle cx="10" cy="10" r="6" fill="none" stroke="#0B0B0B" stroke-width="3" />
          <line x1="15" y1="15" x2="21" y2="21" stroke="#0B0B0B" stroke-width="3" />
        </svg>
      </button>
      <span v-if="weatherTip" class="weather-chip">{{ weatherTip }}</span>
    </div>

    <!-- 筛选 1440×84 -->
    <div class="filter-sec">
      <div class="f-row1">
        <span class="f-label">景观 SCENE</span>
        <span v-for="s in scenes" :key="s" class="f-chip" :class="{ on: s === scene }" @click="toggleScene(s)">{{ s }}</span>
      </div>
      <div class="f-row2">
        距离 <span class="f-chip inline" :class="{ on: maxDistance === 15 }" @click="toggleDistance">≤ 15KM</span>
        · 共 {{ total }} 条路线
      </div>
    </div>

    <!-- 卡片区 1440×546 -->
    <div v-if="cards.length" class="grid">
      <article v-for="c in cards" :key="c.id" class="lib-card panel-d" @click="open(c.id)">
        <img class="lc-img" :src="c.img" :alt="c.name" />
        <div class="lc-name">{{ c.name }}</div>
        <div class="lc-meta">{{ c.meta }}</div>
      </article>
    </div>
    <div v-else class="empty panel-d">暂无符合条件的路线，可先通过 API 创建路线内容。</div>
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
.search-real { width: 100%; font-size: 14px; color: #0B0B0B; border: none; outline: none; }
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
  cursor: pointer;
}
.f-chip.inline { padding: 2px 8px; }
.f-chip.on { background: var(--lime); border-color: var(--lime); color: var(--ink); font-weight: 700; }
.f-row2 { font-size: 12px; color: var(--t2); }

.grid {
  min-height: 546px;
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

.empty {
  margin: 24px 48px;
  padding: 40px;
  font-size: 14px;
  color: var(--t1);
}
</style>
