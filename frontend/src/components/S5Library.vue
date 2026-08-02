<script setup>
/** S5 路线库 · 搜索发现（桌面端，对齐设计稿 2:338）
 *  数据来自真实后端 GET /api/v1/routes（搜索/筛选/分页）
 */
import { onMounted, ref } from 'vue'
import HudNav from './HudNav.vue'
import { fetchRouteLibrary, fetchWeatherTip, fetchCommunityPulse } from '../api/index'

const scenes = ['瀑布', '古道', '竹林', '云海', '星空']
const keyword = ref('')
const activeScene = ref('')
const limitDistance = ref(false)
const items = ref([])
const total = ref(0)
const weatherTip = ref('')
const pulse = ref({ hot_routes: [], latest_reviews: [] })

const load = async () => {
  try {
    const data = await fetchRouteLibrary({
      query: keyword.value,
      tag: activeScene.value,
      maxDistanceKm: limitDistance.value ? 15 : null
    })
    items.value = data.items
    total.value = data.total
  } catch {
    items.value = []
    total.value = 0
  }
}

const toggleScene = (s) => {
  activeScene.value = activeScene.value === s ? '' : s
  load()
}
const toggleDistance = () => {
  limitDistance.value = !limitDistance.value
  load()
}

onMounted(() => {
  load()
  fetchCommunityPulse().then((p) => { pulse.value = p }).catch(() => {})
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(async (pos) => {
      const tip = await fetchWeatherTip(pos.coords.latitude, pos.coords.longitude)
      if (tip) weatherTip.value = tip.text
    })
  }
})
</script>

<template>
  <section class="screen">
    <HudNav />

    <header class="screen-head">
      <div>
        <div class="sh-title-cn">「05」路线库 · 搜索发现</div>
        <div class="sh-title-en">ROUTE LIBRARY — SEARCH &amp; DISCOVER</div>
      </div>
      <button class="pub-btn" @click="$router.push('/routes/new')">+ 发布路线</button>
    </header>

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

    <div class="filter-sec">
      <div class="f-row1">
        <span class="f-label">景观 SCENE</span>
        <span v-for="s in scenes" :key="s" class="f-chip"
              :class="{ on: s === activeScene }" @click="toggleScene(s)">{{ s }}</span>
      </div>
      <div class="f-row2">
        距离 <span class="f-chip inline" :class="{ on: limitDistance }" @click="toggleDistance">≤ 15KM</span>
        · 共 {{ total }} 条路线
      </div>
    </div>

    <div v-if="items.length" class="grid">
      <article v-for="c in items" :key="c.id" class="lib-card panel-d"
               @click="$router.push(`/routes/${c.id}`)">
        <img class="lc-img" :src="c.img" :alt="c.name" />
        <div class="lc-name">{{ c.name }}</div>
        <div class="lc-meta">{{ c.meta }}</div>
      </article>
    </div>
    <div v-else class="empty panel-d">暂无符合条件的路线，可先通过 API 创建路线内容。</div>

    <div class="pulse-sec">
      <div class="pulse panel-d">
        <div class="ptitle">热门路线 · TOP ROUTES</div>
        <div v-for="(r, i) in pulse.hot_routes" :key="r.id" class="pr-row"
             @click="$router.push(`/routes/${r.id}`)">
          <span class="pr-rank" :class="{ hot: i === 0 }">{{ i + 1 }}</span>
          <span class="pr-name">{{ r.title }}</span>
          <span class="pr-meta">
            {{ r.review_count }} 评价 · {{ r.favorite_count }} 收藏{{ r.average_rating != null ? ` · 评分 ${r.average_rating}` : '' }}
          </span>
        </div>
      </div>
      <div class="pulse panel-d">
        <div class="ptitle">最新评价 · LATEST REVIEWS</div>
        <template v-if="pulse.latest_reviews.length">
          <div v-for="rv in pulse.latest_reviews" :key="rv.id" class="prv"
               @click="$router.push(`/routes/${rv.route_id}`)">
            <div class="prv-meta">
              {{ rv.author }} · 《{{ rv.route_title }}》 · {{ rv.rating }}/5
              <span v-if="rv.impression_tags.length" class="prv-tags">{{ rv.impression_tags.join(' · ') }}</span>
            </div>
            <div class="prv-text">{{ rv.content || '（未填写评价内容）' }}</div>
          </div>
        </template>
        <div v-else class="prv-text">还没有社区评价，走完一条路线后欢迎留下第一条。</div>
      </div>
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
.search-real { width: 100%; font-size: 14px; color: #0B0B0B; border: none; outline: none; }
.search-btn { width: 48px; height: 48px; flex: none; background: var(--lime); border: 2px solid var(--ink); display: grid; place-items: center; }
.weather-chip { background: var(--bg); border: 1px solid var(--lime); color: var(--lime); font-size: 13px; font-weight: 700; padding: 12px 16px; white-space: nowrap; }

.filter-sec { height: 84px; padding: 12px 48px 0; display: flex; flex-direction: column; gap: 12px; }
.f-row1 { display: flex; align-items: center; gap: 10px; }
.f-label { font-family: var(--silk); font-size: 11px; color: var(--t2); margin-right: 2px; }
.f-chip { background: var(--panel); border: 1px solid var(--line); color: var(--t1); font-size: 12px; font-weight: 500; padding: 7px 12px; cursor: pointer; }
.f-chip.inline { padding: 2px 8px; }
.f-chip.on { background: var(--lime); border-color: var(--lime); color: var(--ink); font-weight: 700; }
.f-row2 { font-size: 12px; color: var(--t2); }

.grid { min-height: 546px; padding: 20px 48px 0; display: grid; grid-template-columns: repeat(3, 432px); gap: 24px; align-content: start; }
.lib-card { width: 432px; height: 241px; padding: 16px; display: flex; flex-direction: column; gap: 10px; cursor: pointer; }
.lc-img { width: 400px; height: 150px; object-fit: cover; display: block; }
.lc-name { font-size: 15px; font-weight: 700; color: #FFFFFF; }
.lc-meta { font-size: 12px; color: var(--t2); }

.empty {
  margin: 24px 48px;
  padding: 40px;
  font-size: 14px;
  color: var(--t1);
}

.pub-btn {
  background: var(--lime); border: 2px solid var(--ink); box-shadow: var(--sh-lime-4);
  padding: 10px 18px; font-size: 13px; font-weight: 700; color: var(--ink); cursor: pointer;
}

.pulse-sec { padding: 28px 48px 40px; display: flex; gap: 24px; align-items: flex-start; }
.pulse { flex: 1; padding: 18px 20px; display: flex; flex-direction: column; gap: 10px; }
.pr-row { display: flex; align-items: baseline; gap: 10px; cursor: pointer; padding: 6px 0; border-bottom: 1px solid var(--line); }
.pr-row:last-child { border-bottom: none; }
.pr-rank { font-family: var(--silk); font-size: 12px; color: var(--t3); width: 16px; flex: none; }
.pr-rank.hot { color: var(--lime); font-weight: 700; }
.pr-name { font-size: 13px; font-weight: 700; color: #FFFFFF; }
.pr-meta { margin-left: auto; font-size: 11px; color: var(--t3); white-space: nowrap; }
.prv { cursor: pointer; padding: 6px 0; border-bottom: 1px solid var(--line); }
.prv:last-child { border-bottom: none; }
.prv-meta { font-size: 11px; color: var(--t2); }
.prv-tags { color: var(--lime); margin-left: 6px; }
.prv-text { font-size: 12px; color: var(--t1); margin-top: 3px; }
</style>
