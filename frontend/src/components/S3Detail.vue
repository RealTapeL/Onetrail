<script setup>
import { computed, onMounted, ref } from 'vue'
import HudNav from './HudNav.vue'
import { api } from '../api'
import { store } from '../store'

const emit = defineEmits(['nav'])

const route = ref(null)
const reviews = ref([])
const loadError = ref('')
const favored = ref(false)

onMounted(async () => {
  if (!store.selectedRouteId) return
  try {
    const [detail, reviewList] = await Promise.all([
      api(`/routes/${store.selectedRouteId}`, { auth: false }),
      api(`/routes/${store.selectedRouteId}/reviews`, { auth: false })
    ])
    route.value = detail
    reviews.value = reviewList
  } catch (err) {
    loadError.value = err.message || '路线加载失败'
  }
})

const stats = computed(() => {
  if (!route.value) return []
  return [
    { label: '距离 · DIST', value: `${route.value.distance_km}KM` },
    { label: '爬升 · ELEV', value: `${route.value.elevation_gain_m}M` },
    { label: '耗时 · TIME', value: `${Math.round(route.value.estimated_duration_min / 60)}H` },
    { label: '难度 · LEVEL', value: `Lv.${route.value.level}` }
  ]
})
const terrains = computed(() =>
  (route.value?.tags || []).map((t) => ({ label: t.name, warn: t.category === 'safety' }))
)
const safetyTip = computed(() => {
  const note = (route.value?.tags || []).find((t) => t.safety_note)?.safety_note
  return note ? `安全提示：${note}` : '安全提示：暂无标签化安全提示，请出发前确认现场状况。'
})
const votes = computed(() => {
  const total = route.value?.review_count || 0
  return (route.value?.impression_stats || []).map((s) => {
    const pct = total ? Math.min(100, Math.round((s.count / total) * 100)) : 0
    return { label: s.tag, pct, lime: pct >= 60 }
  })
})
const verdict = computed(() => {
  const avg = route.value?.average_rating
  const count = route.value?.review_count || 0
  if (!count) return { text: '暂无评价', sub: '等待第一条真实评价' }
  return {
    text: avg >= 4 ? '值得去' : '再想想',
    sub: `基于 ${count} 条真实评价 · 平均 ${avg} 分`
  }
})

async function toggleFavorite() {
  if (!store.selectedRouteId) return
  try {
    if (favored.value) {
      await api(`/routes/${store.selectedRouteId}/favorite`, { method: 'DELETE' })
      favored.value = false
    } else {
      await api(`/routes/${store.selectedRouteId}/favorite`, { method: 'POST' })
      favored.value = true
    }
  } catch { /* 未登录或网络错误时保持原状态 */ }
}
</script>

<template>
  <section class="screen">
    <HudNav active="lib" @nav="emit('nav', $event)" />

    <div v-if="!store.selectedRouteId" class="empty panel-d">
      还没有选中的路线，请先到路线库或推荐页选择一条路线。
      <button class="empty-btn" @click="emit('nav', 's5')">去路线库 →</button>
    </div>
    <div v-else-if="loadError" class="empty panel-d">{{ loadError }}</div>

    <template v-else-if="route">
      <header class="screen-head" style="height:120px;">
        <div>
          <div class="sh-title-cn">「03」{{ route.title }}</div>
          <div class="sh-title-en">ROUTE DETAIL — TRUSTED ARCHIVE</div>
        </div>
        <span class="sh-chip lime">社区共识：{{ verdict.text }} · {{ route.review_count }} 条评价</span>
      </header>

      <div class="main-row">
        <!-- 左列 904 -->
        <div class="left-col">
          <div class="preview">
            <img class="preview-img" src="/images/2_206.webp" :alt="route.title" />
            <span v-if="route.video_url" class="video-chip">视频预览</span>
            <span v-if="route.video_url" class="play-btn">
              <svg viewBox="0 0 16 20" width="15" height="20"><polygon points="0,0 16,10 0,20" fill="#0B0B0B" /></svg>
            </span>
          </div>

          <div class="stats-bar panel-d">
            <div v-for="s in stats" :key="s.label" class="stat">
              <div class="stat-label">{{ s.label }}</div>
              <div class="stat-value">{{ s.value }}</div>
            </div>
          </div>

          <div class="terrain panel-d">
            <div class="ptitle">地形与安全标签 · TERRAIN &amp; SAFETY</div>
            <div class="t-chips">
              <span v-for="t in terrains" :key="t.label" class="t-chip" :class="{ warn: t.warn }">{{ t.label }}</span>
              <span v-if="!terrains.length" class="t-chip">暂无标签</span>
            </div>
            <div class="t-tip">{{ safetyTip }}</div>
          </div>

          <div class="reviews panel-d">
            <div class="ptitle">徒步者评价 · REVIEWS</div>
            <template v-for="r in reviews" :key="r.id">
              <div class="rv-meta">评分 {{ r.rating }}/5</div>
              <div class="rv-text">{{ r.content || '（未填写评价内容）' }}</div>
            </template>
            <div v-if="!reviews.length" class="rv-text">暂无评价，走过这条路线后欢迎留下第一条反馈。</div>
          </div>
        </div>

        <!-- 右栏 416 白卡 -->
        <aside class="rail">
          <div class="vote-g">
            <div class="rail-title">路线气质投票 · VIBE VOTE</div>
            <div v-for="v in votes" :key="v.label" class="vote">
              <div class="vote-label">{{ v.label }} · {{ v.pct }}%</div>
              <div class="vote-track">
                <div class="vote-fill" :class="{ lime: v.lime }" :style="{ width: v.pct + '%' }" />
              </div>
            </div>
            <div v-if="!votes.length" class="who-text">暂无投票数据</div>
          </div>

          <div class="who-g">
            <div class="who-label">适合人群 · WHO</div>
            <div class="who-text">{{ route.suitable_for || '暂无标注' }}</div>
          </div>

          <div class="verdict">
            <div class="v-q">值不值得去？</div>
            <div class="v-a">{{ verdict.text }}</div>
            <div class="v-sub">{{ verdict.sub }}</div>
          </div>

          <div class="rail-cta">
            <button class="cta-main" @click="emit('nav', 's4')">加入出行计划</button>
            <button class="cta-sub" @click="toggleFavorite">{{ favored ? '已收藏' : '收藏' }}</button>
          </div>
        </aside>
      </div>
    </template>
  </section>
</template>

<style scoped>
.main-row {
  min-height: 768px;
  padding: 0 48px;
  display: flex;
  gap: 24px;
  align-items: flex-start;
}
.left-col { width: 904px; display: flex; flex-direction: column; gap: 20px; }

.preview { position: relative; width: 904px; height: 300px; flex: none; }
.preview-img { width: 100%; height: 100%; object-fit: cover; display: block; }
.video-chip {
  position: absolute; left: 16px; top: 16px;
  background: var(--bg);
  color: #FFFFFF;
  font-size: 12px; font-weight: 500;
  padding: 6px 12px;
}
.play-btn {
  position: absolute; left: 50%; top: 50%;
  transform: translate(-50%, -50%);
  width: 43px; height: 53px;
  background: var(--lime);
  display: grid; place-items: center;
}

.stats-bar { height: 91px; display: flex; align-items: center; gap: 24px; padding: 0 20px; flex: none; }
.stat { width: 198px; display: flex; flex-direction: column; gap: 6px; }
.stat-label { font-family: var(--silk); font-size: 10px; color: var(--t2); }
.stat-value { font-family: var(--vt); font-size: 32px; color: var(--lime); line-height: 1; }

.terrain { padding: 18px 20px; display: flex; flex-direction: column; gap: 14px; flex: none; }
.t-chips { display: flex; gap: 10px; }
.t-chip {
  background: var(--bg);
  border: 1px solid var(--line);
  color: var(--t1);
  font-size: 12px; font-weight: 500;
  padding: 7px 12px;
}
.t-chip.warn { border-color: var(--amber); color: var(--amber); }
.t-tip { font-size: 12px; color: var(--t2); }

.reviews { padding: 18px 20px; display: flex; flex-direction: column; gap: 10px; }
.rv-meta { font-size: 12px; font-weight: 700; color: var(--lime); }
.rv-text { font-size: 12px; color: var(--t2); }

/* 右栏白卡：2px 黑边 + 6px 荧光绿实体投影 */
.rail {
  width: 416px;
  min-height: 728px;
  background: #FFFFFF;
  border: 2px solid var(--ink);
  box-shadow: var(--sh-lime-6);
  padding: 28px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 20px;
}
.rail-title { font-size: 16px; font-weight: 900; color: var(--ink); }
.vote-g { display: flex; flex-direction: column; gap: 10px; }
.vote-label { font-size: 13px; font-weight: 500; color: var(--ink); margin-bottom: 6px; }
.vote-track { width: 360px; height: 10px; background: var(--track); }
.vote-fill { height: 100%; background: var(--amber); }
.vote-fill.lime { background: var(--lime); }

.who-g { display: flex; flex-direction: column; gap: 8px; }
.who-label { font-size: 13px; font-weight: 700; color: var(--ink); }
.who-text { font-size: 13px; font-weight: 500; color: var(--ink2); }

.verdict {
  background: var(--bg);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.v-q { font-size: 12px; font-weight: 500; color: var(--t2); }
.v-a { font-size: 26px; font-weight: 900; color: var(--lime); }
.v-sub { font-size: 11px; color: var(--t2); }

.rail-cta { display: flex; gap: 12px; }
.cta-main {
  width: 280px; height: 44px;
  background: var(--lime);
  border: 2px solid var(--ink);
  font-size: 14px; font-weight: 700; color: var(--ink);
}
.cta-sub {
  width: 68px; height: 44px;
  background: #FFFFFF;
  border: 2px solid var(--ink);
  font-size: 14px; font-weight: 700; color: var(--ink);
}

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
</style>
