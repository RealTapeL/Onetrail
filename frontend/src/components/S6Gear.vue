<script setup>
import HudNav from './HudNav.vue'
const emit = defineEmits(['nav'])

const tabs = ['背包', '徒步鞋', '帐篷', '睡袋']
const gears = [
  {
    img: '/images/2_448.webp', name: 'CRISPI Monaco GTX', best: false,
    specs: ['价格 ¥1,899', '重量 1.4KG（单只）', '防水 GTX 全袜套', '适合 轻装 · 古道', '用户评分 4.8']
  },
  {
    img: '/images/2_452.webp', name: 'SCARPA 冈仁波齐', best: true,
    specs: ['价格 ¥1,299', '重量 1.2KG（单只）', '防水 GTX 全袜套', '适合 溪谷 · 涉水路线', '用户评分 4.7']
  },
  {
    img: '/images/2_458.webp', name: '凯乐石 征途', best: false,
    specs: ['价格 ¥699', '重量 1.1KG（单只）', '防水 防泼水涂层', '适合 新手 · 轻徒步', '用户评分 4.5']
  }
]
const gaps = [
  { name: '雨具 · 三峰出 15D 雨衣', meta: '防暴雨 · 仅 180G · 收纳巴掌大', price: '¥129' },
  { name: '头灯 · 奈特科尔 NU25',   meta: '400 流明 · 仅 56G · USB-C 充电', price: '¥168' },
  { name: '饮水 · 驼峰 2L 水袋',     meta: '快拆吸嘴 · 适配 20L 背包',       price: '¥149' }
]
</script>

<template>
  <section class="screen">
    <HudNav active="gear" @nav="emit('nav', $event)" />

    <header class="screen-head" style="height:116px;">
      <div>
        <div class="sh-title-cn">「06」装备比选</div>
        <div class="sh-title-en">GEAR COMPARE — EXTENSION MODULE</div>
      </div>
      <span class="sh-chip lime">已按「九溪环线 · 溪谷涉水」生成建议</span>
    </header>

    <!-- Tabs 1440×63 -->
    <div class="tabs">
      <button v-for="t in tabs" :key="t" class="tab" :class="{ on: t === '徒步鞋' }">{{ t }}</button>
    </div>

    <!-- 对比卡 1440×420 -->
    <div class="compare">
      <article v-for="g in gears" :key="g.name" class="gc" :class="{ best: g.best }">
        <img class="gc-img" :src="g.img" :alt="g.name" />
        <span v-if="g.best" class="gc-badge">最适合本路线 · BEST MATCH</span>
        <h3 class="gc-name">{{ g.name }}</h3>
        <div class="gc-specs">
          <div v-for="s in g.specs" :key="s">{{ s }}</div>
        </div>
      </article>
    </div>

    <!-- GAP PICKS 1440×212 -->
    <div class="gap-sec">
      <div class="gap-panel panel-d">
        <div class="ptitle">缺口补给建议 · GAP PICKS — 按你的路线与预算生成</div>
        <div class="gap-row">
          <div v-for="g in gaps" :key="g.name" class="gap-card">
            <div class="gap-name">{{ g.name }}</div>
            <div class="gap-meta">{{ g.meta }}</div>
            <div class="gap-price">{{ g.price }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 评价条 1440×79 -->
    <div class="review-sec">
      <div class="review-bar panel-d">
        <div class="rv-left">
          <span class="rv-label">USER REVIEWS</span>
          <span class="rv-quote">「冈仁波齐走溪谷两天，鞋里没进水。」—— 来自真实用户评价</span>
        </div>
        <span class="rv-count">已聚合 1,203 条真实评价</span>
      </div>
    </div>

    <!-- 底部说明 1440×85 -->
    <div class="note-sec">
      聚合分散装备信息 · 按场景、品牌、价格、重量、防护能力比较 · 与出发方案联动
    </div>
  </section>
</template>

<style scoped>
.tabs { height: 63px; padding: 0 48px; display: flex; gap: 12px; align-items: flex-start; }
.tab {
  background: var(--panel);
  color: var(--t1);
  font-size: 13px; font-weight: 500;
  padding: 11px 16px;
}
.tab.on { background: var(--lime); color: var(--ink); font-weight: 700; }

.compare {
  height: 420px;
  padding: 0 48px;
  display: flex;
  gap: 16px;
}
.gc {
  width: 437px;
  background: #FFFFFF;
  border: 2px solid var(--ink);
  box-shadow: var(--sh-white-4);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.gc.best { box-shadow: var(--sh-lime-4); }
.gc-img { width: 397px; height: 160px; object-fit: cover; display: block; background: #F0F0F0; }
.gc-badge {
  align-self: flex-start;
  background: var(--lime);
  color: var(--ink);
  font-size: 11px; font-weight: 700;
  padding: 6px 10px;
}
.gc-name { font-size: 16px; font-weight: 700; color: var(--ink); }
.gc-specs { font-size: 13px; color: var(--ink2); line-height: 1.9; }

.gap-sec { height: 212px; padding: 16px 48px 0; }
.gap-panel { height: 180px; padding: 20px; display: flex; flex-direction: column; gap: 14px; }
.gap-row { display: flex; gap: 16px; }
.gap-card {
  width: 424px; height: 104px;
  background: var(--bg);
  border: 1px solid var(--line);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.gap-name { font-size: 13px; font-weight: 700; color: var(--t1); }
.gap-meta { font-size: 12px; color: var(--t2); }
.gap-price { font-family: var(--vt); font-size: 24px; color: var(--lime); line-height: 1; margin-top: auto; }

.review-sec { height: 79px; padding: 16px 48px 0; }
.review-bar {
  height: 47px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.rv-left { display: flex; align-items: center; gap: 14px; }
.rv-label { font-family: var(--silk); font-weight: 700; font-size: 11px; color: var(--lime); }
.rv-quote { font-size: 13px; font-weight: 500; color: var(--t1); }
.rv-count { font-size: 12px; color: var(--t2); }

.note-sec {
  height: 85px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--t2);
}
</style>
