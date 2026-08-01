<script setup>
import HudNav from './HudNav.vue'
const emit = defineEmits(['nav'])

const cards = [
  {
    img: '/images/2_469.webp', top: 'TOP 1', hot: true, score: '96%',
    name: '九溪十八涧 · 环线',
    meta: '9.5KM · 爬升 320M · 耗时 4H · 晴 18°C',
    why: ['体能 Lv.3 匹配，爬升平缓友好', '竹林溪谷景观，命中你的兴趣', '沿途 3 处补给点，风险可控'],
    risk: '风险提示：雨后溪石湿滑，建议防滑徒步鞋',
    tags: '溪谷 · 竹林 · 新手友好'
  },
  {
    img: '/images/2_470.webp', top: 'TOP 2', hot: false, score: '89%',
    name: '徽杭古道 · 精华段',
    meta: '12.5KM · 爬升 480M · 耗时 5.5H · 多云 16°C',
    why: ['古道人文加山景，故事性强', '难度 Lv.3 与体能刚好匹配', '民宿补给完善，适合 2 人同行'],
    risk: '风险提示：部分路段手机信号弱，提前下载离线地图',
    tags: '古道 · 人文 · 进阶'
  },
  {
    img: '/images/2_471.webp', top: 'TOP 3', hot: false, score: '82%',
    name: '大明山 · 云海线',
    meta: '8.2KM · 爬升 650M · 耗时 4.5H · 晴 15°C',
    why: ['云海概率 78%，出片率高', '爬升偏大，接近体能上限', '山顶补给少，需自带路餐'],
    risk: '风险提示：山顶风大，昼夜温差达 10°C',
    tags: '云海 · 出片 · 体能挑战'
  }
]

const alts = [
  { img: '/images/2_472.webp', name: '鸬鸟山温泉线', meta: '轻松休闲 · 6.0KM · 温泉补给' },
  { img: '/images/2_473.webp', name: '径山古道',     meta: '文化禅意 · 7.8KM · 新手友好' }
]
</script>

<template>
  <section class="screen">
    <HudNav active="plan" @nav="emit('nav', $event)" />

    <header class="screen-head" style="height:132px;">
      <div>
        <div class="sh-title-cn">「02」智能线路推荐</div>
        <div class="sh-title-en">TOP 3 ROUTES FOR YOU</div>
      </div>
      <span class="sh-chip">本周末 · 杭州 · 2 人 · ¥500 · 体能 Lv.3</span>
    </header>

    <!-- 三卡 1440×505，pad 0 48，gap 24 -->
    <div class="cards">
      <article v-for="c in cards" :key="c.name" class="rc" @click="c.hot && emit('nav', 's3')">
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

    <!-- 备选 1440×246 -->
    <div class="alt-sec">
      <div class="alt-panel panel-d">
        <div class="alt-head">
          <span class="ptitle">备选路线 · ALTERNATIVES</span>
          <span class="alt-note">适配引擎已综合距离、爬升、天气、泥泞风险与体能偏好计算匹配度</span>
        </div>
        <div v-for="a in alts" :key="a.name" class="alt-row">
          <img class="alt-thumb" :src="a.img" :alt="a.name" />
          <span class="alt-name">{{ a.name }}</span>
          <span class="alt-meta">{{ a.meta }}</span>
          <span class="alt-view">查看详情</span>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.cards {
  height: 505px;
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

.alt-sec { height: 246px; padding: 34px 48px 0; }
.alt-panel { height: 178px; padding: 20px 24px; display: flex; flex-direction: column; gap: 14px; }
.alt-head { display: flex; align-items: center; justify-content: space-between; }
.alt-note { font-size: 12px; color: var(--t2); }
.alt-row { display: flex; align-items: center; gap: 16px; height: 40px; }
.alt-thumb { width: 40px; height: 40px; object-fit: cover; flex: none; }
.alt-name { font-size: 14px; font-weight: 700; color: var(--t1); }
.alt-meta { font-size: 12px; color: var(--t2); }
.alt-view { margin-left: auto; font-size: 12px; font-weight: 700; color: var(--lime); cursor: pointer; }
</style>
