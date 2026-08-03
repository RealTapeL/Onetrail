<script setup>
/** M5 路线详情（下层页，对齐设计稿 6:25）
 *  数据来自真实后端 GET /api/v1/routes/{id}
 */
import { computed, ref, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import BackHeader from './BackHeader.vue'
import RouteMarkModal from '../RouteMarkModal.vue'
import ReviewMediaPicker from '../ReviewMediaPicker.vue'
import SharePoster from '../SharePoster.vue'
import { fetchRouteDetail, IMPRESSION_OPTIONS, setFavorite } from '../../api/index'
import { useRouteReview } from '../../composables/useRouteReview'
import { buildRatingPanel } from '../../composables/ratingPanel'

const route = useRoute()
const routeDetail = ref(null)
const loadError = ref('')
const favored = ref(false)
const shareMsg = ref('')
// 分享海报弹层
const posterOpen = ref(false)
const share = () => { posterOpen.value = true }

const load = async (id) => {
  routeDetail.value = null
  loadError.value = ''
  try {
    routeDetail.value = await fetchRouteDetail(id)
  } catch (err) {
    loadError.value = err.message || '路线详情加载失败，请稍后重试'
  }
}

watchEffect(() => {
  if (route.params.id) load(route.params.id)
})

const toggleFavorite = async () => {
  if (!routeDetail.value) return
  try {
    await setFavorite(routeDetail.value.id, !favored.value)
    favored.value = !favored.value
  } catch { /* 保持原状态 */ }
}

// ---- 想去 / 去过 记录弹窗 ----
const markOpen = ref(false)
const markTab = ref('wish')
const openMark = (tab) => {
  if (!routeDetail.value) return
  // 已想去时直接点「想去」= 取消想去，不再开弹窗
  if (tab === 'wish' && favored.value) { toggleFavorite(); return }
  markTab.value = tab
  markOpen.value = true
}
const onMarked = ({ tab }) => {
  if (tab === 'wish') favored.value = true
  else load(route.params.id)
}

// ---- 写评价 / 气质投票 ----
const { reviewRating, reviewTags, reviewContent, reviewSubmitting, reviewMsg, toggleTag, submitReview } =
  useRouteReview(() => route.params.id, { onSubmitted: () => load(route.params.id) })
// 评价附件（图片/视频，当前前端暂存）
const reviewMedia = ref([])
const submitWithMedia = async () => {
  await submitReview()
  if (reviewMsg.value === '评价已提交') reviewMedia.value = []
}

// ---- 评分面板（与桌面 S3 同一套计算） ----
const ratingPanel = computed(() => buildRatingPanel(routeDetail.value?.reviews))
</script>

<template>
  <div class="m-screen">
    <BackHeader back-text="返回路线库" to="/routes">
      <span v-if="routeDetail">社区共识：{{ routeDetail.verdict.text }} · {{ routeDetail.verdict.voteCount.toLocaleString() }} 票</span>
      <span v-else>路线详情</span>
      <button class="share-btn" @click="share">{{ shareMsg || '分享' }}</button>
    </BackHeader>

    <div v-if="loadError" class="m-body">
      <div class="loading">{{ loadError }}</div>
      <button class="share-btn retry" @click="load(route.params.id)">重试</button>
    </div>
    <div v-else-if="!routeDetail" class="m-body"><div class="loading">加载中…</div></div>
    <template v-else>
    <div class="hero">
      <img class="hero-img" :src="routeDetail.coverImage" :alt="routeDetail.name" />
      <template v-if="routeDetail.videoUrl">
        <a class="video-chip" :href="routeDetail.videoUrl" target="_blank" rel="noopener">视频预览 ▶</a>
        <span class="play">
          <svg viewBox="0 0 16 20" width="14" height="18"><polygon points="0,0 16,10 0,20" fill="#0B0B0B" /></svg>
        </span>
      </template>
    </div>

    <div class="m-body">
      <div class="d-title">{{ routeDetail.name }}</div>

      <!-- 决策条：本页最重要的问题，放在标题正下方 -->
      <section class="decide">
        <div class="dc-q">值不值得去？</div>
        <div class="dc-a">{{ routeDetail.verdict.text }}</div>
        <div class="dc-s">基于 {{ routeDetail.verdict.voteCount.toLocaleString() }} 票社区共识</div>
      </section>

      <!-- 评分面板：大分数 + 星级 + 分布条 -->
      <section class="rating">
        <template v-if="ratingPanel">
          <div class="rp-left">
            <div class="rp-label">社区评分 · RATING</div>
            <div class="rp-score">{{ ratingPanel.avg }}</div>
            <div class="rp-stars">
              <span v-for="n in 5" :key="n" :class="{ on: n <= ratingPanel.fullStars }">★</span>
            </div>
          </div>
          <div class="rp-right">
            <div v-for="d in ratingPanel.dist" :key="d.star" class="rp-row">
              <span class="rp-star-label">{{ d.star }} 星</span>
              <span class="rp-track"><span class="rp-fill" :style="{ width: d.percent + '%' }" /></span>
              <span class="rp-count">{{ d.count }}</span>
            </div>
            <div class="rp-total">{{ ratingPanel.total }} 条真实评价</div>
          </div>
        </template>
        <div v-else class="p-dim">暂无评分 —— 走完这条路线后欢迎留下第一条评价</div>
      </section>

      <section class="stats">
        <div v-for="s in routeDetail.stats" :key="s.label" class="stat">
          <div class="s-label">{{ s.label }}</div>
          <div class="s-value">{{ s.value }}</div>
        </div>
      </section>

      <section class="panel">
        <div class="p-title">地形与安全 · TERRAIN &amp; SAFETY</div>
        <div class="t-chips">
          <span v-for="t in routeDetail.terrain.tags" :key="t.label" class="t-chip" :class="{ warn: t.warning }">{{ t.label }}</span>
        </div>
        <div v-for="n in routeDetail.terrain.safetyNotes" :key="n.label" class="p-dim t-note">
          <b>{{ n.label }}</b>：{{ n.note }}
        </div>
        <div v-if="!routeDetail.terrain.safetyNotes.length" class="p-dim">{{ routeDetail.terrain.safetyTip }}</div>
      </section>

      <section class="vote">
        <div class="v-title">路线气质投票 · VIBE VOTE</div>
        <div v-for="v in routeDetail.vibeVote" :key="v.label" class="v-row">
          <div class="v-label">{{ v.label }} · {{ v.percent }}%</div>
          <div class="v-track"><div class="v-fill" :class="{ amber: !v.lime }" :style="{ width: v.percent + '%' }" /></div>
        </div>
      </section>

      <section class="panel">
        <div class="p-title">徒步者评价 · REVIEWS</div>
        <template v-for="r in routeDetail.reviews" :key="r.id">
          <div class="r-meta">{{ r.author }} · 评分 {{ r.rating }}/5 · {{ r.visitedAt }}</div>
          <div class="p-dim">{{ r.content }}</div>
        </template>
        <div class="p-dim who">适合人群 · WHO：{{ routeDetail.suitableFor }}</div>
      </section>

      <section class="panel">
        <div class="p-title">写评价 · 投一票</div>
        <div class="wr-row">
          <button v-for="n in 5" :key="n" class="wr-star" :class="{ on: n <= reviewRating }"
                  @click="reviewRating = n">{{ n <= reviewRating ? '★' : '☆' }}</button>
        </div>
        <div class="wr-row">
          <button v-for="t in IMPRESSION_OPTIONS" :key="t" class="wr-chip"
                  :class="{ on: reviewTags.includes(t) }" @click="toggleTag(t)">{{ t }}</button>
        </div>
        <textarea v-model="reviewContent" class="wr-text" rows="3" placeholder="说说真实体验（路况、风景、注意事项…）" />
        <ReviewMediaPicker v-model:files="reviewMedia" />
        <div class="wr-foot">
          <span v-if="reviewMsg" class="wr-msg">{{ reviewMsg }}</span>
          <button class="wr-submit" :disabled="reviewSubmitting" @click="submitWithMedia">
            {{ reviewSubmitting ? '提交中…' : '提交' }}
          </button>
        </div>
      </section>
    </div>

    <div class="cta-spacer" />
    <div class="cta-bar">
      <button class="cta-main" @click="$router.push('/trip/current')">加入出行计划</button>
      <button class="cta-sub" :class="{ on: favored }" @click="openMark('wish')">{{ favored ? '已想去' : '想去' }}</button>
      <button class="cta-sub" @click="openMark('done')">去过</button>
    </div>
    </template>
    <SharePoster v-if="posterOpen && routeDetail" :route="routeDetail" @close="posterOpen = false" />
    <RouteMarkModal v-if="markOpen && routeDetail" :route-id="routeDetail.id"
                    :initial-tab="markTab"
                    @close="markOpen = false" @marked="onMarked" />
  </div>
</template>

<style scoped>
.hero { position: relative; height: 190px; flex: none; }
.hero-img { width: 100%; height: 100%; object-fit: cover; display: block; }
.video-chip { position: absolute; left: 12px; top: 12px; background: var(--bg); color: #FFF; font-size: 10px; padding: 5px 10px; text-decoration: none; }
.t-note { line-height: 1.6; }
.t-note b { color: var(--red); font-weight: 700; }
.share-btn {
  background: none; border: 1px solid var(--lime); color: var(--lime);
  font-size: 9px; padding: 3px 8px; cursor: pointer;
}
.play {
  position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%);
  width: 38px; height: 46px; background: var(--lime); display: grid; place-items: center;
}
.stats {
  background: var(--panel); border: 1px solid var(--line); padding: 14px;
  display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
}
.d-title { font-size: 20px; font-weight: 900; color: #FFF; line-height: 1.3; }
/* ---- 评分面板 ---- */
.rating {
  background: var(--panel); border: 1px solid var(--line); padding: 14px;
  display: flex; align-items: center; gap: 20px; flex-wrap: wrap;
}
.rp-left { display: flex; flex-direction: column; gap: 4px; flex: none; }
.rp-label { font-family: var(--silk); font-size: 8px; color: var(--t2); }
.rp-score { font-family: var(--vt); font-size: 44px; color: var(--lime); line-height: 1; }
.rp-stars { font-size: 14px; color: var(--t4); letter-spacing: 1px; }
.rp-stars .on { color: var(--amber); }
.rp-right { flex: 1; min-width: 180px; display: flex; flex-direction: column; gap: 5px; }
.rp-row { display: flex; align-items: center; gap: 8px; }
.rp-star-label { font-size: 10px; color: var(--t2); width: 30px; flex: none; }
.rp-track { flex: 1; height: 6px; background: var(--track); }
.rp-fill { display: block; height: 100%; background: var(--amber); }
.rp-count { font-size: 10px; color: var(--t3); width: 16px; text-align: right; flex: none; }
.rp-total { font-size: 9px; color: var(--t3); text-align: right; }
.s-label { font-family: var(--silk); font-size: 8px; color: var(--t2); }
.s-value { font-family: var(--vt); font-size: 22px; color: var(--lime); line-height: 1; margin-top: 2px; }
.panel { background: var(--panel); border: 1px solid var(--line); padding: 14px; display: flex; flex-direction: column; gap: 8px; }
.p-title { font-size: 13px; font-weight: 700; color: #FFF; }
.p-dim { font-size: 10px; color: var(--t2); line-height: 1.6; }
.t-chips { display: flex; gap: 6px; flex-wrap: wrap; }
.t-chip { background: var(--bg); border: 1px solid var(--line); color: var(--t1); font-size: 10px; font-weight: 500; padding: 4px 8px; }
.t-chip.warn { border-color: var(--amber); color: var(--amber); }
.vote {
  background: #FFF; border: 2px solid var(--ink); box-shadow: var(--sh-lime-4);
  padding: 14px; display: flex; flex-direction: column; gap: 10px;
}
.v-title { font-size: 13px; font-weight: 900; color: var(--ink); }
.v-label { font-size: 11px; font-weight: 500; color: var(--ink); margin-bottom: 4px; }
.v-track { height: 8px; background: var(--track); }
.v-fill { height: 100%; background: var(--lime); }
.v-fill.amber { background: var(--amber); }
/* 决策条：标题正下方的视觉焦点（荧光底 + 大字号结论） */
.decide {
  background: var(--lime); border: 2px solid var(--ink); box-shadow: var(--sh-ink-3);
  padding: 14px 16px; display: flex; flex-direction: column; gap: 4px;
}
.dc-q { font-size: 11px; font-weight: 500; color: var(--ink2); }
.dc-a { font-size: 24px; font-weight: 900; color: var(--ink); }
.dc-s { font-size: 10px; font-weight: 500; color: var(--ink2); }
.r-meta { font-size: 10px; font-weight: 700; color: var(--lime); }
.wr-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.wr-star { font-size: 20px; color: var(--t4); padding: 0 2px; line-height: 1; }
.wr-star.on { color: var(--amber); }
.wr-chip { font-size: 11px; font-weight: 500; color: var(--t1); background: var(--bg); border: 1px solid var(--line); padding: 5px 10px; }
.wr-chip.on { background: var(--lime); border-color: var(--lime); color: var(--ink); font-weight: 700; }
.wr-text {
  background: var(--bg); border: 1px solid var(--line); color: var(--t1);
  font-size: 12px; padding: 8px 10px; resize: vertical; font-family: inherit;
}
.wr-text:focus { outline: none; border-color: var(--lime); }
.wr-foot { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.wr-msg { font-size: 11px; color: var(--lime); }
.wr-submit { background: var(--lime); border: 2px solid var(--ink); color: var(--ink); font-size: 12px; font-weight: 700; padding: 7px 18px; }
.wr-submit:disabled { opacity: 0.6; }
.who { border-top: 1px dashed var(--line); padding-top: 8px; }
.cta-spacer { height: calc(64px + var(--sab)); flex: none; }
.cta-bar {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  z-index: 20;
  display: flex; gap: 10px; padding: 10px 16px calc(10px + var(--sab));
  background: var(--bg); border-top: 1px solid var(--line);
}
.cta-main {
  flex: 1; height: 44px;
  background: var(--lime); border: 2px solid var(--ink);
  font-size: 13px; font-weight: 700; color: var(--ink);
}
.cta-sub { width: 76px; height: 44px; background: #FFF; border: 2px solid var(--ink); font-size: 13px; font-weight: 700; color: var(--ink); }
.cta-sub.on { background: var(--lime); }
.loading { font-size: 11px; color: var(--t2); }
.retry { margin-top: 10px; align-self: flex-start; }
</style>
