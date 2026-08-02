<script setup>
/** M6 推荐结果（下层页，对齐设计稿 6:26）
 *  数据来自真实推荐结果（M1 提交后写入共享状态）
 */
import { computed } from 'vue'
import BackHeader from './BackHeader.vue'
import { state } from '../../api/index'

const recommendation = computed(() => state.recommendation)
</script>

<template>
  <div class="m-screen">
    <BackHeader back-text="返回规划" to="/plan">
      <span class="silk">TOP 3 ROUTES FOR YOU</span>
    </BackHeader>
    <div class="m-body">
      <div v-if="!recommendation" class="empty">
        还没有推荐结果。请先在「规划」页提交出行需求。
        <button class="empty-btn" @click="$router.push('/plan')">去规划 →</button>
      </div>
      <template v-else>
      <div class="cond">{{ recommendation.conditionSummary }}</div>
      <div v-if="recommendation.notice" class="notice">{{ recommendation.notice }}</div>

      <article v-for="c in recommendation.top" :key="c.routeId" class="rc" :class="{ top1: c.rank === 1 }"
               @click="$router.push(`/routes/${c.routeId}`)">
        <img class="rc-img" :src="c.img" :alt="c.name" />
        <div class="rc-top">
          <span class="rank" :class="{ hot: c.rank === 1 }">TOP {{ c.rank }}</span>
          <span class="score">{{ c.matchScore }}%</span>
        </div>
        <h3 class="rc-name">{{ c.name }}</h3>
        <div class="rc-meta">{{ c.meta }}</div>
        <div class="rc-why">
          <b>推荐理由 · WHY</b>
          <div v-for="r in c.reasons" :key="r">· {{ r }}</div>
        </div>
        <div class="rc-risk">{{ c.risk }}</div>
        <div class="rc-tags">{{ c.tags }}</div>
        <div class="rc-cta">查看详情 · 加入行程 →</div>
      </article>
      <div v-if="!recommendation.top.length" class="empty">当前条件下没有匹配的已发布路线，可调整限制后重试。</div>

      <section v-if="recommendation.alternatives.length" class="alt">
        <div class="alt-title">备选路线 · ALTERNATIVES</div>
        <div v-for="a in recommendation.alternatives" :key="a.routeId" class="alt-row"
             @click="$router.push(`/routes/${a.routeId}`)">
          <img class="alt-thumb" :src="a.thumb" :alt="a.name" />
          <div class="alt-text">
            <div class="alt-name">{{ a.name }}</div>
            <div class="alt-meta">{{ a.summary }}</div>
          </div>
        </div>
      </section>

      <section v-if="recommendation.hikingSpots.length" class="alt">
        <div class="alt-title">周边徒步地 · 来自高德地图</div>
        <div v-for="s in recommendation.hikingSpots" :key="s.name" class="spot-row">
          <div class="alt-name">{{ s.name }}</div>
          <div class="alt-meta">{{ s.meta }}</div>
        </div>
      </section>
      </template>
    </div>
  </div>
</template>

<style scoped>
.silk { font-family: var(--silk); font-weight: 400; font-size: 9px; }
.cond {
  background: var(--panel); border: 1px solid var(--line);
  padding: 9px 12px; font-size: 10px; font-weight: 500; color: var(--t1);
}
.rc {
  background: #FFF; border: 2px solid var(--ink); box-shadow: var(--sh-lime-4);
  padding: 12px; display: flex; flex-direction: column; gap: 8px; cursor: pointer;
}
.rc-img { width: 100%; height: 140px; object-fit: cover; }
.rc-top { display: flex; align-items: center; justify-content: space-between; }
.rank { background: var(--panel); padding: 4px 8px; font-family: var(--p8); font-size: 8px; color: var(--lime); }
.rank.hot { background: var(--lime); color: var(--ink); }
.score { font-family: var(--vt); font-size: 28px; color: var(--ink); line-height: 1; }
.rc-name { font-size: 15px; font-weight: 900; color: var(--ink); }
.rc-meta { font-size: 10px; font-weight: 500; color: var(--t3); }
.rc-why { font-size: 10px; color: var(--ink2); line-height: 1.6; }
.rc-why b { color: var(--ink); }
.rc-risk {
  background: var(--red-bg); border: 1px solid var(--red-line);
  color: var(--red); font-size: 9px; font-weight: 500; padding: 8px;
}
.rc-tags { font-size: 9px; font-weight: 500; color: var(--t3); }
/* 显式操作入口 + TOP1 强调（与桌面 S2 同一策略） */
.rc-cta {
  background: var(--ink); color: var(--lime);
  font-size: 12px; font-weight: 700; text-align: center; padding: 9px;
}
.rc.top1 { border-color: var(--lime); box-shadow: 6px 6px 0 var(--lime); }
.rc.top1 .rc-cta { background: var(--lime); color: var(--ink); }
.alt { background: var(--panel); border: 1px solid var(--line); padding: 14px; display: flex; flex-direction: column; gap: 10px; }
.alt-title { font-size: 13px; font-weight: 700; color: #FFF; }
.alt-row { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.alt-thumb { width: 36px; height: 36px; object-fit: cover; flex: none; }
.alt-name { font-size: 11px; font-weight: 700; color: var(--t1); }
.alt-meta { font-size: 9px; color: var(--t2); margin-top: 2px; }
.spot-row { padding: 6px 0; border-top: 1px dashed var(--line); }
.notice { font-size: 10px; font-weight: 500; color: var(--amber); }
.empty { font-size: 11px; color: var(--t2); line-height: 1.8; display: flex; flex-direction: column; gap: 10px; }
.empty-btn { align-self: flex-start; font-size: 11px; font-weight: 700; color: var(--lime); padding: 0; }
</style>
