<script setup>
/** S2 推荐结果 · Top N（桌面端，对齐设计稿 2:94）
 *  数据来自 S1 提交后写入的共享状态（真实推荐引擎结果）
 */
import { computed } from 'vue'
import HudNav from './HudNav.vue'
import { state } from '../api/index'

const recommendation = computed(() => state.recommendation)
</script>

<template>
  <section class="screen">
    <HudNav />

    <header class="screen-head">
      <div>
        <div class="sh-title-cn">「02」智能线路推荐</div>
        <div class="sh-title-en">TOP 3 ROUTES FOR YOU</div>
      </div>
      <span v-if="recommendation" class="sh-chip">{{ recommendation.conditionSummary }}</span>
    </header>

    <div v-if="!recommendation" class="empty panel-d">
      还没有推荐结果，请先到「开始规划」提交出行条件。
      <button class="empty-btn" @click="$router.push('/plan')">去填写 →</button>
    </div>

    <template v-else>
      <div v-if="recommendation.notice" class="notice">{{ recommendation.notice }}</div>

      <div v-if="recommendation.top.length" class="cards">
        <article v-for="c in recommendation.top" :key="c.routeId" class="rc"
                 @click="$router.push(`/routes/${c.routeId}`)">
          <img class="rc-photo" :src="c.img" :alt="c.name" />
          <div class="rc-top">
            <span class="rc-rank" :class="{ hot: c.rank === 1 }">TOP {{ c.rank }}</span>
            <span class="rc-score">
              <span class="rc-score-label">匹配度</span>
              <span class="rc-score-num">{{ c.matchScore }}%</span>
            </span>
          </div>
          <h3 class="rc-name">{{ c.name }}</h3>
          <div class="rc-meta">{{ c.meta }}</div>
          <div class="rc-why-label">推荐理由 · WHY</div>
          <ul class="rc-bullets">
            <li v-for="b in c.reasons" :key="b">· {{ b }}</li>
          </ul>
          <div class="rc-risk">{{ c.risk }}</div>
          <div class="rc-tags">{{ c.tags }}</div>
        </article>
      </div>
      <div v-else class="empty panel-d">当前条件下没有满足限制的路线，请调整条件后重试。</div>

      <div v-if="recommendation.alternatives.length" class="alt-sec">
        <div class="alt-panel panel-d">
          <div class="alt-head">
            <span class="ptitle">备选路线 · ALTERNATIVES</span>
            <span class="alt-note">适配引擎已综合距离、爬升、天气、泥泞风险与体能偏好计算匹配度</span>
          </div>
          <div v-for="a in recommendation.alternatives" :key="a.routeId" class="alt-row"
               @click="$router.push(`/routes/${a.routeId}`)">
            <img class="alt-thumb" :src="a.thumb" :alt="a.name" />
            <span class="alt-name">{{ a.name }}</span>
            <span class="alt-meta">{{ a.summary }}</span>
            <span class="alt-view">查看详情</span>
          </div>
        </div>
      </div>

      <div v-if="recommendation.hikingSpots.length" class="alt-sec">
        <div class="alt-panel panel-d">
          <div class="alt-head">
            <span class="ptitle">目的地周边徒步地 · 来自高德地图</span>
            <span class="alt-note">路线库尚未收录这些地点的详细路线，仅展示真实位置信息</span>
          </div>
          <div v-for="s in recommendation.hikingSpots" :key="s.name" class="alt-row spot-row">
            <span class="alt-name">{{ s.name }}</span>
            <span class="alt-meta">{{ s.meta }}</span>
          </div>
        </div>
      </div>
    </template>
  </section>
</template>

<style scoped>
.cards { min-height: 505px; padding: 0 48px; display: flex; gap: 24px; }
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
.rc-rank { background: var(--panel); padding: 6px 10px; font-family: var(--p8); font-size: 10px; color: var(--lime); }
.rc-rank.hot { background: var(--lime); color: var(--ink); }
.rc-score { display: inline-flex; align-items: baseline; gap: 8px; }
.rc-score-label { font-size: 12px; font-weight: 500; color: var(--t3); }
.rc-score-num { font-family: var(--vt); font-size: 40px; color: var(--ink); line-height: 1; }
.rc-name { font-size: 20px; font-weight: 900; color: var(--ink); }
.rc-meta { font-size: 12px; font-weight: 500; color: var(--t3); }
.rc-why-label { font-size: 12px; font-weight: 700; color: var(--ink); }
.rc-bullets { list-style: none; font-size: 13px; color: var(--ink2); line-height: 1.8; }
.rc-risk { background: var(--red-bg); border: 1px solid var(--red-line); color: var(--red); font-size: 12px; font-weight: 500; padding: 8px 10px; }
.rc-tags { font-size: 12px; font-weight: 500; color: var(--t3); }

.alt-sec { min-height: 246px; padding: 34px 48px 0; }
.alt-panel { min-height: 178px; padding: 20px 24px; display: flex; flex-direction: column; gap: 14px; }
.alt-head { display: flex; align-items: center; justify-content: space-between; }
.alt-note { font-size: 12px; color: var(--t2); }
.alt-row { display: flex; align-items: center; gap: 16px; height: 40px; cursor: pointer; }
.alt-thumb { width: 40px; height: 40px; object-fit: cover; flex: none; }
.alt-name { font-size: 14px; font-weight: 700; color: var(--t1); }
.alt-meta { font-size: 12px; color: var(--t2); }
.alt-view { margin-left: auto; font-size: 12px; font-weight: 700; color: var(--lime); }
.spot-row { height: auto; min-height: 32px; cursor: default; }

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
