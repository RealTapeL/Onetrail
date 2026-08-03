<script setup>
/** S3 路线详情（桌面端，对齐设计稿 2:178）
 *  数据来自真实后端 GET /api/v1/routes/{id}（含评价、气质投票、评分聚合）
 */
import { computed, ref, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import HudNav from './HudNav.vue'
import RouteMarkModal from './RouteMarkModal.vue'
import ReviewMediaPicker from './ReviewMediaPicker.vue'
import SharePoster from './SharePoster.vue'
import { fetchRouteDetail, IMPRESSION_OPTIONS, setFavorite } from '../api/index'
import { useRouteReview } from '../composables/useRouteReview'
import { buildRatingPanel } from '../composables/ratingPanel'

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
    loadError.value = err.message || '路线加载失败'
  }
}

watchEffect(() => {
  if (route.params.id) load(route.params.id)
})

const toggleFavorite = async () => {
  try {
    await setFavorite(route.params.id, !favored.value)
    favored.value = !favored.value
  } catch { /* 未连接后端时保持原状态 */ }
}

// ---- 想去 / 去过 记录弹窗 ----
const markOpen = ref(false)
const markTab = ref('wish')
const openMark = (tab) => {
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
  useRouteReview(() => route.params.id, {
    successText: '评价已提交，感谢分享',
    onSubmitted: () => load(route.params.id)
  })
// 评价附件（图片/视频，当前前端暂存）
const reviewMedia = ref([])
const submitWithMedia = async () => {
  await submitReview()
  if (reviewMsg.value === '评价已提交，感谢分享') reviewMedia.value = []
}

// ---- 评分面板（参考豆瓣/香水时代详情页）：大分数 + 星级 + 分布条，纯展示计算 ----
const ratingPanel = computed(() => buildRatingPanel(routeDetail.value?.reviews))
</script>

<template>
  <section class="screen">
    <HudNav />

    <div v-if="loadError" class="empty panel-d">{{ loadError }}</div>
    <div v-else-if="!routeDetail" class="empty panel-d">加载中…</div>

    <template v-else>
      <header class="screen-head">
        <div>
          <div class="sh-title-cn">「03」{{ routeDetail.name }}</div>
          <div class="sh-title-en">ROUTE DETAIL — TRUSTED ARCHIVE</div>
        </div>
        <div class="head-right">
          <span class="sh-chip lime">社区共识：{{ routeDetail.verdict.text }} · {{ routeDetail.verdict.voteCount }} 条评价</span>
          <button class="share-btn" @click="share">分享</button>
          <span v-if="shareMsg" class="share-msg">{{ shareMsg }}</span>
        </div>
      </header>

      <div class="main-row">
        <div class="left-col">
          <div class="preview">
            <img class="preview-img" :src="routeDetail.coverImage" :alt="routeDetail.name" />
            <a v-if="routeDetail.videoUrl" class="video-link" :href="routeDetail.videoUrl"
               target="_blank" rel="noopener">▶ 视频预览</a>
          </div>

          <div class="stats-bar panel-d">
            <div v-for="s in routeDetail.stats" :key="s.label" class="stat">
              <div class="stat-label">{{ s.label }}</div>
              <div class="stat-value">{{ s.value }}</div>
            </div>
          </div>

          <!-- 评分面板：大分数 + 星级 + 分布条（对齐主流详情页结构） -->
          <div class="rating-panel panel-d">
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
            <div v-else class="rp-empty">暂无评分 —— 走完这条路线后欢迎留下第一条评价</div>
          </div>

          <div class="terrain panel-d">
            <div class="ptitle">地形与安全标签 · TERRAIN &amp; SAFETY</div>
            <div class="t-chips">
              <span v-for="t in routeDetail.terrain.tags" :key="t.label" class="t-chip" :class="{ warn: t.warning }">{{ t.label }}</span>
              <span v-if="!routeDetail.terrain.tags.length" class="t-chip">暂无标签</span>
            </div>
            <div v-for="n in routeDetail.terrain.safetyNotes" :key="n.label" class="t-note">
              <b>{{ n.label }}</b>：{{ n.note }}
            </div>
            <div v-if="!routeDetail.terrain.safetyNotes.length" class="t-tip">{{ routeDetail.terrain.safetyTip }}</div>
          </div>

          <div class="reviews panel-d">
            <div class="ptitle">徒步者评价 · REVIEWS</div>
            <template v-for="r in routeDetail.reviews" :key="r.id">
              <div class="rv-meta">{{ r.author }} · 评分 {{ r.rating }}/5 · {{ r.visitedAt }}</div>
              <div class="rv-text">{{ r.content }}</div>
            </template>
            <div v-if="!routeDetail.reviews.length" class="rv-text">暂无评价，走过这条路线后欢迎留下第一条反馈。</div>
          </div>

          <div class="write-review panel-d">
            <div class="ptitle">写评价 · 投一票</div>
            <div class="wr-row">
              <span class="wr-label">评分</span>
              <button v-for="n in 5" :key="n" class="wr-star" :class="{ on: n <= reviewRating }"
                      @click="reviewRating = n">{{ n <= reviewRating ? '★' : '☆' }}</button>
            </div>
            <div class="wr-row">
              <span class="wr-label">气质</span>
              <button v-for="t in IMPRESSION_OPTIONS" :key="t" class="wr-chip"
                      :class="{ on: reviewTags.includes(t) }" @click="toggleTag(t)">{{ t }}</button>
            </div>
            <textarea v-model="reviewContent" class="wr-text" rows="3"
                      placeholder="说说这条路线的真实体验（路况、风景、注意事项…）" />
            <ReviewMediaPicker v-model:files="reviewMedia" />
            <div class="wr-foot">
              <span v-if="reviewMsg" class="wr-msg">{{ reviewMsg }}</span>
              <button class="wr-submit" :disabled="reviewSubmitting" @click="submitWithMedia">
                {{ reviewSubmitting ? '提交中…' : '提交评价' }}
              </button>
            </div>
          </div>
        </div>

        <aside class="rail">
          <!-- 决策区置顶：值不值得去 + 核心操作，视线第一落点 -->
          <div class="verdict">
            <div class="v-q">值不值得去？</div>
            <div class="v-a">{{ routeDetail.verdict.text }}</div>
            <div class="v-sub">基于 {{ routeDetail.verdict.voteCount }} 条真实评价聚合</div>
          </div>

          <div class="rail-cta">
            <button class="cta-main" @click="$router.push('/trip/current')">加入出行计划</button>
            <button class="cta-sub" :class="{ on: favored }" @click="openMark('wish')">{{ favored ? '已想去' : '想去' }}</button>
            <button class="cta-sub" @click="openMark('done')">去过</button>
          </div>

          <div class="vote-g">
            <div class="rail-title">路线气质投票 · VIBE VOTE</div>
            <div v-for="v in routeDetail.vibeVote" :key="v.label" class="vote">
              <div class="vote-label">{{ v.label }} · {{ v.percent }}%</div>
              <div class="vote-track">
                <div class="vote-fill" :class="{ amber: !v.lime }" :style="{ width: v.percent + '%' }" />
              </div>
            </div>
            <div v-if="!routeDetail.vibeVote.length" class="who-text">暂无投票数据</div>
          </div>

          <div class="who-g">
            <div class="who-label">适合人群 · WHO</div>
            <div class="who-text">{{ routeDetail.suitableFor }}</div>
          </div>
        </aside>
      </div>
    </template>
    <RouteMarkModal v-if="markOpen && routeDetail" :route-id="route.params.id"
                    :initial-tab="markTab"
                    @close="markOpen = false" @marked="onMarked" />
    <SharePoster v-if="posterOpen && routeDetail" :route="routeDetail" @close="posterOpen = false" />
  </section>
</template>

<style scoped>
.head-right { display: flex; align-items: center; gap: 10px; }
.share-btn {
  background: none; border: 1px solid var(--lime); color: var(--lime);
  padding: 8px 14px; font-size: 12px; cursor: pointer;
}
.share-btn:hover { background: var(--lime); color: var(--ink); }
.share-msg { font-size: 11px; color: var(--lime); }
.main-row { padding: 0 var(--content-px) 40px; display: flex; gap: 24px; align-items: flex-start; }
.left-col { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 20px; }

.preview { position: relative; width: 100%; height: 300px; flex: none; }
.preview-img { width: 100%; height: 100%; object-fit: cover; display: block; }
.video-link {
  position: absolute;
  left: 16px;
  bottom: 16px;
  background: var(--bg);
  color: var(--lime);
  border: 1px solid var(--lime);
  padding: 8px 14px;
  font-family: var(--silk);
  font-size: 11px;
  text-decoration: none;
}
.video-link:hover { background: var(--lime); color: var(--ink); }

.stats-bar { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; padding: 18px 20px; flex: none; }
.stat { display: flex; flex-direction: column; gap: 6px; }
.stat-label { font-family: var(--silk); font-size: 10px; color: var(--t2); }
.stat-value { font-family: var(--vt); font-size: 32px; color: var(--lime); line-height: 1; }

/* ---- 评分面板 ---- */
.rating-panel { padding: 20px; display: flex; gap: 32px; align-items: center; flex-wrap: wrap; }
.rp-left { display: flex; flex-direction: column; gap: 6px; flex: none; }
.rp-label { font-family: var(--silk); font-size: 10px; color: var(--t2); }
.rp-score { font-family: var(--vt); font-size: 56px; color: var(--lime); line-height: 1; }
.rp-stars { font-size: 18px; color: var(--t4); letter-spacing: 2px; }
.rp-stars .on { color: var(--amber); }
.rp-right { flex: 1; min-width: 220px; display: flex; flex-direction: column; gap: 6px; }
.rp-row { display: flex; align-items: center; gap: 10px; }
.rp-star-label { font-size: 11px; color: var(--t2); width: 34px; flex: none; }
.rp-track { flex: 1; height: 8px; background: var(--track); }
.rp-fill { display: block; height: 100%; background: var(--amber); }
.rp-count { font-size: 11px; color: var(--t3); width: 20px; text-align: right; flex: none; }
.rp-total { font-size: 11px; color: var(--t3); text-align: right; }
.rp-empty { font-size: 13px; color: var(--t2); }

.terrain { padding: 18px 20px; display: flex; flex-direction: column; gap: 14px; flex: none; }
.t-chips { display: flex; gap: 10px; }
.t-chip { background: var(--bg); border: 1px solid var(--line); color: var(--t1); font-size: 12px; font-weight: 500; padding: 7px 12px; }
.t-chip.warn { border-color: var(--amber); color: var(--amber); }
.t-tip { font-size: 12px; color: var(--t2); }
.t-note { font-size: 12px; color: var(--t2); line-height: 1.6; }
.t-note b { color: var(--red); font-weight: 700; }

.reviews { padding: 18px 20px; display: flex; flex-direction: column; gap: 10px; }
.rv-meta { font-size: 12px; font-weight: 700; color: var(--lime); }
.rv-text { font-size: 12px; color: var(--t2); }

.write-review { padding: 18px 20px; display: flex; flex-direction: column; gap: 14px; }
.wr-row { display: flex; align-items: center; gap: 8px; }
.wr-label { font-size: 12px; font-weight: 700; color: var(--t1); width: 36px; flex: none; }
.wr-star { font-size: 22px; color: var(--t4); padding: 0 2px; line-height: 1; }
.wr-star.on { color: var(--amber); }
.wr-chip { font-size: 12px; font-weight: 500; color: var(--t1); background: var(--bg); border: 1px solid var(--line); padding: 6px 12px; }
.wr-chip.on { background: var(--lime); border-color: var(--lime); color: var(--ink); font-weight: 700; }
.wr-text {
  background: var(--bg); border: 1px solid var(--line); color: var(--t1);
  font-size: 13px; padding: 10px 12px; resize: vertical; font-family: inherit;
}
.wr-text:focus { outline: none; border-color: var(--lime); }
.wr-foot { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.wr-msg { font-size: 12px; color: var(--lime); }
.wr-submit { background: var(--lime); border: 2px solid var(--ink); color: var(--ink); font-size: 13px; font-weight: 700; padding: 8px 20px; }
.wr-submit:disabled { opacity: 0.6; }

.rail {
  width: 360px;
  flex: none;
  position: sticky;
  top: 24px;
  background: #FFFFFF;
  border: 2px solid var(--ink);
  box-shadow: var(--sh-lime-6);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.rail-title { font-size: 16px; font-weight: 900; color: var(--ink); }
.vote-g { display: flex; flex-direction: column; gap: 10px; }
.vote-label { font-size: 13px; font-weight: 500; color: var(--ink); margin-bottom: 6px; }
.vote-track { width: 100%; height: 10px; background: var(--track); }
.vote-fill { height: 100%; background: var(--lime); }
.vote-fill.amber { background: var(--amber); }

.who-g { display: flex; flex-direction: column; gap: 8px; }
.who-label { font-size: 13px; font-weight: 700; color: var(--ink); }
.who-text { font-size: 13px; font-weight: 500; color: var(--ink2); }

.verdict { background: var(--bg); padding: 16px; display: flex; flex-direction: column; gap: 6px; }
.v-q { font-size: 12px; font-weight: 500; color: var(--t2); }
.v-a { font-size: 26px; font-weight: 900; color: var(--lime); }
.v-sub { font-size: 11px; color: var(--t2); }

.rail-cta { display: flex; gap: 12px; }
.cta-main { flex: 1; height: 44px; background: var(--lime); border: 2px solid var(--ink); font-size: 14px; font-weight: 700; color: var(--ink); }
.cta-sub { width: 68px; flex: none; height: 44px; background: #FFFFFF; border: 2px solid var(--ink); font-size: 14px; font-weight: 700; color: var(--ink); }
.cta-sub.on { background: var(--lime); }

.empty {
  margin: 24px var(--content-px);
  padding: 40px;
  font-size: 14px;
  color: var(--t1);
}

/* 窄屏桌面：右栏取消吸顶并与主列上下堆叠 */
@media (max-width: 1100px) {
  .main-row { flex-direction: column; }
  .rail { width: 100%; position: static; }
  .left-col { width: 100%; }
}
</style>
