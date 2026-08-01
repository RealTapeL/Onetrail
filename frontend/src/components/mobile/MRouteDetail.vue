<script setup>
/** M5 路线详情（下层页，对齐设计稿 6:25）
 *  数据来自真实后端 GET /api/v1/routes/{id}
 */
import { ref, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import BackHeader from './BackHeader.vue'
import { fetchRouteDetail, setFavorite } from '../../api/index'

const route = useRoute()
const routeDetail = ref(null)
const favored = ref(false)

watchEffect(async () => {
  const id = Number(route.params.id)
  if (!id) return
  routeDetail.value = null
  try {
    routeDetail.value = await fetchRouteDetail(id)
  } catch {
    routeDetail.value = null
  }
})

const toggleFavorite = async () => {
  if (!routeDetail.value) return
  try {
    await setFavorite(routeDetail.value.id, !favored.value)
    favored.value = !favored.value
  } catch { /* 保持原状态 */ }
}
</script>

<template>
  <div class="m-screen">
    <BackHeader back-text="返回路线库" to="/routes">
      <span v-if="routeDetail">社区共识：{{ routeDetail.verdict.text }} · {{ routeDetail.verdict.voteCount.toLocaleString() }} 票</span>
      <span v-else>路线详情</span>
    </BackHeader>

    <div v-if="!routeDetail" class="m-body"><div class="loading">加载中…</div></div>
    <template v-else>
    <div class="hero">
      <img class="hero-img" :src="routeDetail.coverImage" :alt="routeDetail.name" />
      <span class="video-chip">视频预览 · 00:42</span>
      <span class="play">
        <svg viewBox="0 0 16 20" width="14" height="18"><polygon points="0,0 16,10 0,20" fill="#0B0B0B" /></svg>
      </span>
    </div>

    <div class="m-body">
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
        <div class="p-dim">{{ routeDetail.terrain.safetyTip }}</div>
      </section>

      <section class="vote">
        <div class="v-title">路线气质投票 · VIBE VOTE</div>
        <div v-for="v in routeDetail.vibeVote" :key="v.label" class="v-row">
          <div class="v-label">{{ v.label }} · {{ v.percent }}%</div>
          <div class="v-track"><div class="v-fill" :class="{ amber: !v.lime }" :style="{ width: v.percent + '%' }" /></div>
        </div>
        <div class="verdict">
          <div class="vd-q">值不值得去？</div>
          <div class="vd-a">{{ routeDetail.verdict.text }}</div>
          <div class="vd-s">基于 {{ routeDetail.verdict.voteCount.toLocaleString() }} 票社区共识投票</div>
        </div>
      </section>

      <section class="panel">
        <div class="p-title">徒步者评价 · REVIEWS</div>
        <template v-for="r in routeDetail.reviews" :key="r.author">
          <div class="r-meta">{{ r.author }} · 评分 {{ r.rating }}/5 · {{ r.visitedAt }}</div>
          <div class="p-dim">{{ r.content }}</div>
        </template>
        <div class="p-dim who">适合人群 · WHO：{{ routeDetail.suitableFor }}</div>
      </section>
    </div>

    <div class="cta-bar">
      <button class="cta-main" @click="$router.push('/trip/current')">加入出行计划</button>
      <button class="cta-sub" :class="{ on: favored }" @click="toggleFavorite">{{ favored ? '已收藏' : '收藏' }}</button>
    </div>
    </template>
  </div>
</template>

<style scoped>
.hero { position: relative; height: 190px; flex: none; }
.hero-img { width: 100%; height: 100%; object-fit: cover; display: block; }
.video-chip { position: absolute; left: 12px; top: 12px; background: var(--bg); color: #FFF; font-size: 10px; padding: 5px 10px; }
.play {
  position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%);
  width: 38px; height: 46px; background: var(--lime); display: grid; place-items: center;
}
.stats {
  background: var(--panel); border: 1px solid var(--line); padding: 14px;
  display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
}
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
.verdict { background: var(--bg); padding: 12px; display: flex; flex-direction: column; gap: 4px; }
.vd-q { font-size: 10px; font-weight: 500; color: var(--t2); }
.vd-a { font-size: 20px; font-weight: 900; color: var(--lime); }
.vd-s { font-size: 9px; color: var(--t2); }
.r-meta { font-size: 10px; font-weight: 700; color: var(--lime); }
.who { border-top: 1px dashed var(--line); padding-top: 8px; }
.cta-bar {
  position: sticky; bottom: 0; z-index: 20;
  display: flex; gap: 10px; padding: 10px 16px;
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
</style>
