<script setup>
/** S3 路线详情（桌面端，对齐设计稿 2:178）
 *  数据来自真实后端 GET /api/v1/routes/{id}（含评价、气质投票、评分聚合）
 */
import { ref, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import HudNav from './HudNav.vue'
import { fetchRouteDetail, IMPRESSION_OPTIONS, postRouteReview, setFavorite } from '../api/index'

const route = useRoute()
const routeDetail = ref(null)
const loadError = ref('')
const favored = ref(false)

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

// ---- 写评价 / 气质投票 ----
const reviewRating = ref(5)
const reviewTags = ref([])
const reviewContent = ref('')
const reviewSubmitting = ref(false)
const reviewMsg = ref('')

const toggleTag = (tag) => {
  const i = reviewTags.value.indexOf(tag)
  i >= 0 ? reviewTags.value.splice(i, 1) : reviewTags.value.push(tag)
}

const submitReview = async () => {
  if (reviewSubmitting.value) return
  reviewSubmitting.value = true
  reviewMsg.value = ''
  try {
    await postRouteReview(route.params.id, {
      rating: reviewRating.value,
      content: reviewContent.value.trim(),
      impressionTags: reviewTags.value
    })
    reviewContent.value = ''
    reviewTags.value = []
    reviewMsg.value = '评价已提交，感谢分享'
    await load(route.params.id)
  } catch (err) {
    reviewMsg.value = err.message || '提交失败，请稍后重试'
  } finally {
    reviewSubmitting.value = false
  }
}
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
        <span class="sh-chip lime">社区共识：{{ routeDetail.verdict.text }} · {{ routeDetail.verdict.voteCount }} 条评价</span>
      </header>

      <div class="main-row">
        <div class="left-col">
          <div class="preview">
            <img class="preview-img" :src="routeDetail.coverImage" :alt="routeDetail.name" />
          </div>

          <div class="stats-bar panel-d">
            <div v-for="s in routeDetail.stats" :key="s.label" class="stat">
              <div class="stat-label">{{ s.label }}</div>
              <div class="stat-value">{{ s.value }}</div>
            </div>
          </div>

          <div class="terrain panel-d">
            <div class="ptitle">地形与安全标签 · TERRAIN &amp; SAFETY</div>
            <div class="t-chips">
              <span v-for="t in routeDetail.terrain.tags" :key="t.label" class="t-chip" :class="{ warn: t.warning }">{{ t.label }}</span>
              <span v-if="!routeDetail.terrain.tags.length" class="t-chip">暂无标签</span>
            </div>
            <div class="t-tip">{{ routeDetail.terrain.safetyTip }}</div>
          </div>

          <div class="reviews panel-d">
            <div class="ptitle">徒步者评价 · REVIEWS</div>
            <template v-for="r in routeDetail.reviews" :key="r.author + r.visitedAt">
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
            <div class="wr-foot">
              <span v-if="reviewMsg" class="wr-msg">{{ reviewMsg }}</span>
              <button class="wr-submit" :disabled="reviewSubmitting" @click="submitReview">
                {{ reviewSubmitting ? '提交中…' : '提交评价' }}
              </button>
            </div>
          </div>
        </div>

        <aside class="rail">
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

          <div class="verdict">
            <div class="v-q">值不值得去？</div>
            <div class="v-a">{{ routeDetail.verdict.text }}</div>
            <div class="v-sub">基于 {{ routeDetail.verdict.voteCount }} 条真实评价聚合</div>
          </div>

          <div class="rail-cta">
            <button class="cta-main" @click="$router.push('/trip/current')">加入出行计划</button>
            <button class="cta-sub" @click="toggleFavorite">{{ favored ? '已收藏' : '收藏' }}</button>
          </div>
        </aside>
      </div>
    </template>
  </section>
</template>

<style scoped>
.main-row { min-height: 768px; padding: 0 48px; display: flex; gap: 24px; align-items: flex-start; }
.left-col { width: 904px; display: flex; flex-direction: column; gap: 20px; }

.preview { position: relative; width: 904px; height: 300px; flex: none; }
.preview-img { width: 100%; height: 100%; object-fit: cover; display: block; }

.stats-bar { height: 91px; display: flex; align-items: center; gap: 24px; padding: 0 20px; flex: none; }
.stat { width: 198px; display: flex; flex-direction: column; gap: 6px; }
.stat-label { font-family: var(--silk); font-size: 10px; color: var(--t2); }
.stat-value { font-family: var(--vt); font-size: 32px; color: var(--lime); line-height: 1; }

.terrain { padding: 18px 20px; display: flex; flex-direction: column; gap: 14px; flex: none; }
.t-chips { display: flex; gap: 10px; }
.t-chip { background: var(--bg); border: 1px solid var(--line); color: var(--t1); font-size: 12px; font-weight: 500; padding: 7px 12px; }
.t-chip.warn { border-color: var(--amber); color: var(--amber); }
.t-tip { font-size: 12px; color: var(--t2); }

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
.cta-main { width: 280px; height: 44px; background: var(--lime); border: 2px solid var(--ink); font-size: 14px; font-weight: 700; color: var(--ink); }
.cta-sub { width: 68px; height: 44px; background: #FFFFFF; border: 2px solid var(--ink); font-size: 14px; font-weight: 700; color: var(--ink); }

.empty {
  margin: 24px 48px;
  padding: 40px;
  font-size: 14px;
  color: var(--t1);
}
</style>
