<script setup>
import { computed } from 'vue'
import HudNav from './HudNav.vue'
import { selectRoute, store } from '../store'

const emit = defineEmits(['nav'])

const COVERS = ['/images/2_469.webp', '/images/2_470.webp', '/images/2_471.webp']
const ALT_THUMBS = ['/images/2_472.webp', '/images/2_473.webp']

const rec = computed(() => store.recommendation)
const weatherMeta = computed(() => {
  const w = rec.value?.response?.weather
  if (!w) return ''
  const temp = w.temperature_max_c != null ? ` ${w.temperature_max_c}°C` : ''
  return `${w.weather}${temp}`
})
const cards = computed(() =>
  (rec.value?.response?.routes || []).slice(0, 3).map((r, i) => ({
    routeId: r.route_id,
    plan: r,
    img: COVERS[i % COVERS.length],
    top: `TOP ${i + 1}`,
    hot: i === 0,
    score: `${Math.round(r.score)}%`,
    name: r.title,
    meta: `${r.distance_km}KM · 爬升 ${r.elevation_gain_m}M · 耗时 ${Math.round(r.estimated_duration_min / 60)}H · ${weatherMeta.value}`,
    why: r.reasons.slice(0, 3),
    risk: r.risk_notes.length ? `风险提示：${r.risk_notes[0]}` : '风险提示：暂无特别提示，出发前请确认现场状况',
    tags: r.scene_tags.join(' · ')
  }))
)
const alts = computed(() =>
  (rec.value?.response?.alternates || []).slice(0, 2).map((r, i) => ({
    routeId: r.route_id,
    img: ALT_THUMBS[i % ALT_THUMBS.length],
    name: r.title,
    meta: `${r.region} · ${r.distance_km}KM · 匹配度 ${Math.round(r.score)}%`
  }))
)
const notice = computed(() => rec.value?.response?.notice || '')

function open(card) {
  selectRoute(card.routeId, card.plan)
  emit('nav', 's3')
}
</script>

<template>
  <section class="screen">
    <HudNav active="plan" @nav="emit('nav', $event)" />

    <header class="screen-head" style="height:132px;">
      <div>
        <div class="sh-title-cn">「02」智能线路推荐</div>
        <div class="sh-title-en">TOP 3 ROUTES FOR YOU</div>
      </div>
      <span v-if="rec" class="sh-chip">{{ rec.summary }}</span>
    </header>

    <div v-if="!rec" class="empty panel-d">
      还没有推荐结果，请先到「01 需求输入」提交出行条件。
      <button class="empty-btn" @click="emit('nav', 's1')">去填写 →</button>
    </div>

    <template v-else>
      <div v-if="notice" class="notice">{{ notice }}</div>

      <!-- 三卡 1440×505，pad 0 48，gap 24 -->
      <div v-if="cards.length" class="cards">
        <article v-for="c in cards" :key="c.routeId" class="rc" @click="open(c)">
          <img class="rc-photo" :src="c.img" :alt="c.name" />
          <div class="rc-top">
            <span class="rc-rank" :class="{ hot: c.hot }">{{ c.top }}</span>
            <span class="rc-score">
              <span class="rc-score-label">匹配度</span>
              <span class="rc-score-num">{{ c.score }}</span>
            </span>
          </div>
          <h3 class="rc-name">{{ c.name }}</h3>
          <div class="rc-meta">{{ c.meta }}</div>
          <div class="rc-why-label">推荐理由 · WHY</div>
          <ul class="rc-bullets">
            <li v-for="b in c.why" :key="b">· {{ b }}</li>
          </ul>
          <div class="rc-risk">{{ c.risk }}</div>
          <div class="rc-tags">{{ c.tags }}</div>
        </article>
      </div>
      <div v-else class="empty panel-d">当前条件下没有满足限制的路线，请调整条件后重试。</div>

      <!-- 备选 1440×246 -->
      <div v-if="alts.length" class="alt-sec">
        <div class="alt-panel panel-d">
          <div class="alt-head">
            <span class="ptitle">备选路线 · ALTERNATIVES</span>
            <span class="alt-note">适配引擎已综合距离、爬升、天气、泥泞风险与体能偏好计算匹配度</span>
          </div>
          <div v-for="a in alts" :key="a.routeId" class="alt-row">
            <img class="alt-thumb" :src="a.img" :alt="a.name" />
            <span class="alt-name">{{ a.name }}</span>
            <span class="alt-meta">{{ a.meta }}</span>
            <span class="alt-view" @click="selectRoute(a.routeId); emit('nav', 's3')">查看详情</span>
          </div>
        </div>
      </div>
    </template>
  </section>
</template>

<style scoped>
.cards {
  min-height: 505px;
  padding: 0 48px;
  display: flex;
  gap: 24px;
}
.rc {
  width: 432px;
  background: #FFFFFF;
  border: 2px solid var(--ink);
  box-shadow: var(--sh-lime-6);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  cursor: pointer;
}
.rc-photo { width: 384px; height: 140px; object-fit: cover; display: block; }
.rc-top { display: flex; align-items: flex-end; justify-content: space-between; height: 40px; }
.rc-rank {
  background: var(--panel);
  padding: 6px 10px;
  font-family: var(--p8);
  font-size: 10px;
  color: var(--lime);
}
.rc-rank.hot { background: var(--lime); color: var(--ink); }
.rc-score { display: inline-flex; align-items: baseline; gap: 8px; }
.rc-score-label { font-size: 12px; font-weight: 500; color: var(--t3); }
.rc-score-num { font-family: var(--vt); font-size: 40px; color: var(--ink); line-height: 1; }
.rc-name { font-size: 20px; font-weight: 900; color: var(--ink); }
.rc-meta { font-size: 12px; font-weight: 500; color: var(--t3); }
.rc-why-label { font-size: 12px; font-weight: 700; color: var(--ink); }
.rc-bullets { list-style: none; font-size: 13px; color: var(--ink2); line-height: 1.8; }
.rc-risk {
  background: var(--red-bg);
  border: 1px solid var(--red-line);
  color: var(--red);
  font-size: 12px;
  font-weight: 500;
  padding: 8px 10px;
}
.rc-tags { font-size: 12px; font-weight: 500; color: var(--t3); }

.alt-sec { min-height: 246px; padding: 34px 48px 0; }
.alt-panel { min-height: 178px; padding: 20px 24px; display: flex; flex-direction: column; gap: 14px; }
.alt-head { display: flex; align-items: center; justify-content: space-between; }
.alt-note { font-size: 12px; color: var(--t2); }
.alt-row { display: flex; align-items: center; gap: 16px; height: 40px; }
.alt-thumb { width: 40px; height: 40px; object-fit: cover; flex: none; }
.alt-name { font-size: 14px; font-weight: 700; color: var(--t1); }
.alt-meta { font-size: 12px; color: var(--t2); }
.alt-view { margin-left: auto; font-size: 12px; font-weight: 700; color: var(--lime); cursor: pointer; }

.empty {
  margin: 24px 48px;
  padding: 40px;
  font-size: 14px;
  color: var(--t1);
  display: flex;
  align-items: center;
  gap: 16px;
}
.empty-btn { background: var(--lime); color: var(--ink); font-weight: 700; padding: 8px 16px; }
.notice {
  margin: 0 48px 16px;
  padding: 10px 14px;
  border: 1px solid var(--amber);
  color: var(--amber);
  font-size: 13px;
}
</style>
