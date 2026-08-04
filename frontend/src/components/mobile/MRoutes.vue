<script setup>
/** M2 路线库 · 搜索发现（移动端 Tab 2，对齐设计稿 6:22）
 *  数据来自真实后端 GET /api/v1/routes
 */
import { onMounted, ref } from 'vue'
import MHeader from './MHeader.vue'
import TabBar from './TabBar.vue'
import { fetchRouteLibrary, fetchWeatherTip, fetchCommunityPulse } from '../../api/index'

const scenes = ['瀑布', '古道', '竹林', '云海', '星空']
const keyword = ref('')
const activeScene = ref('')
const items = ref([])
const weatherText = ref('')
const pulse = ref({ hot_routes: [], latest_reviews: [] })

const load = async () => {
  try {
    const data = await fetchRouteLibrary({ query: keyword.value, tag: activeScene.value })
    items.value = data.items
  } catch {
    items.value = []
  }
}
const toggleScene = (s) => {
  activeScene.value = activeScene.value === s ? '' : s
  load()
}

onMounted(() => {
  load()
  fetchCommunityPulse().then((p) => { pulse.value = p }).catch(() => {})
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(async (pos) => {
      const tip = await fetchWeatherTip(pos.coords.latitude, pos.coords.longitude)
      if (tip) weatherText.value = tip.text
    })
  }
})
</script>

<template>
  <div class="m-screen">
    <MHeader />
    <div class="m-body">
      <div class="search-row">
        <div class="search-input">
          <input v-model="keyword" class="search-real" placeholder="搜索路线、山峰、地名…" @keyup.enter="load" />
        </div>
        <button class="search-btn" aria-label="搜索" @click="load">
          <svg viewBox="0 0 20 20" width="20" height="20">
            <circle cx="9" cy="9" r="5" fill="none" stroke="#0B0B0B" stroke-width="2.5"/>
            <line x1="13" y1="13" x2="17" y2="17" stroke="#0B0B0B" stroke-width="2.5"/>
          </svg>
        </button>
      </div>
      <div v-if="weatherText" class="weather">{{ weatherText }}</div>
      <div class="f-label">景观 SCENE</div>
      <div class="chips">
        <span v-for="s in scenes" :key="s" class="chip"
              :class="{ on: s === activeScene }" @click="toggleScene(s)">{{ s }}</span>
      </div>

      <button class="pub-btn" @click="$router.push('/routes/new')">+ 发布我的路线</button>

      <article v-for="c in items" :key="c.id" class="card"
               @click="$router.push(`/routes/${c.id}`)">
        <img class="card-img" :src="c.img" :alt="c.name" />
        <div class="card-name">{{ c.name }}</div>
        <div class="card-meta">{{ c.meta }}</div>
      </article>
      <div v-if="!items.length" class="empty">暂无符合条件的已发布路线。</div>

      <section class="pulse">
        <div class="p-title">热门路线 · TOP</div>
        <div v-for="(r, i) in pulse.hot_routes" :key="r.id" class="pr-row"
             @click="$router.push(`/routes/${r.id}`)">
          <span class="pr-rank" :class="{ hot: i === 0 }">{{ i + 1 }}</span>
          <span class="pr-name">{{ r.title }}</span>
          <span class="pr-meta">{{ r.review_count }} 评价 · {{ r.favorite_count }} 收藏</span>
        </div>
      </section>

      <section class="pulse">
        <div class="p-title">最新评价 · REVIEWS</div>
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
      </section>
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
.search-real { width: 100%; border: none; background: none; font-size: 12px; color: var(--ink); }
.search-real:focus { outline: none; }
.empty { font-size: 11px; color: var(--t2); }
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

.pub-btn {
  align-self: flex-start;
  background: transparent; border: 1px dashed var(--t3);
  padding: 8px 14px; font-size: 11px; font-weight: 500; color: var(--t2); cursor: pointer;
}

.pulse {
  background: var(--panel); border: 1px solid var(--line);
  padding: 12px; display: flex; flex-direction: column; gap: 6px;
}
.p-title { font-family: var(--silk); font-size: 9px; color: var(--t2); }
.pr-row { display: flex; align-items: baseline; gap: 8px; cursor: pointer; padding: 4px 0; border-bottom: 1px solid var(--line); }
.pr-row:last-child { border-bottom: none; }
.pr-rank { font-family: var(--silk); font-size: 10px; color: var(--t3); width: 14px; flex: none; }
.pr-rank.hot { color: var(--lime); font-weight: 700; }
.pr-name { font-size: 12px; font-weight: 700; color: #FFF; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.pr-meta { margin-left: auto; font-size: 9px; color: var(--t3); white-space: nowrap; }
.prv { cursor: pointer; padding: 4px 0; border-bottom: 1px solid var(--line); }
.prv:last-child { border-bottom: none; }
.prv-meta { font-size: 9px; color: var(--t2); }
.prv-tags { color: var(--lime); margin-left: 4px; }
.prv-text { font-size: 11px; color: var(--t1); margin-top: 2px; }
</style>
