<script setup>
/** S6 装备比选（桌面端，对齐设计稿 2:411）
 *  数据来自真实装备目录与评价聚合
 */
import { onMounted, ref, watch } from 'vue'
import HudNav from './HudNav.vue'
import { fetchGapPicks, fetchGearCompare, fetchGearReviews, GEAR_CATEGORIES, state } from '../api/index'

const activeCategory = ref('footwear')
const items = ref([])
const gaps = ref([])
const gearReviews = ref({ totalCount: 0, quote: '' })

const load = async () => {
  try {
    items.value = await fetchGearCompare(activeCategory.value)
    gaps.value = await fetchGapPicks(activeCategory.value, state.budgetCny ?? 500)
  } catch {
    items.value = []
    gaps.value = []
  }
}

watch(activeCategory, load)
onMounted(async () => {
  load()
  try {
    gearReviews.value = await fetchGearReviews()
  } catch { /* 保留默认 */ }
})
</script>

<template>
  <section class="screen">
    <HudNav />

    <header class="screen-head">
      <div>
        <div class="sh-title-cn">「06」装备比选</div>
        <div class="sh-title-en">GEAR COMPARE — EXTENSION MODULE</div>
      </div>
      <span class="sh-chip lime">按装备目录真实数据生成建议</span>
    </header>

    <div class="tabs">
      <button v-for="t in GEAR_CATEGORIES" :key="t.value" class="tab"
              :class="{ on: t.value === activeCategory }"
              @click="activeCategory = t.value">{{ t.label }}</button>
    </div>

    <div v-if="items.length" class="compare">
      <article v-for="g in items" :key="g.id" class="gc" :class="{ best: g.best }">
        <img class="gc-img" :src="g.img" :alt="g.name" />
        <span v-if="g.best" class="gc-badge">最适合本路线 · BEST MATCH</span>
        <h3 class="gc-name">{{ g.name }}</h3>
        <div class="gc-specs">
          <div v-for="s in g.specs" :key="s">{{ s }}</div>
        </div>
        <a v-if="g.sourceUrl" class="gc-link" :href="g.sourceUrl" target="_blank" rel="noopener">迪卡侬官网查看 →</a>
      </article>
    </div>
    <div v-else class="empty panel-d">该品类暂无装备数据，可先通过 API 提交装备。</div>

    <div class="gap-sec">
      <div class="gap-panel panel-d">
        <div class="ptitle">缺口补给建议 · GAP PICKS — 按你的路线与预算生成</div>
        <div v-if="gaps.length" class="gap-row">
          <div v-for="g in gaps" :key="g.name" class="gap-card">
            <div class="gap-name">{{ g.name }}</div>
            <div class="gap-meta">{{ g.meta }}</div>
            <div class="gap-price">{{ g.price }}</div>
          </div>
        </div>
        <div v-else class="gap-meta">预算内暂无其他品类装备可推荐</div>
      </div>
    </div>

    <div class="review-sec">
      <div class="review-bar panel-d">
        <div class="rv-left">
          <span class="rv-label">USER REVIEWS</span>
          <span class="rv-quote">{{ gearReviews.quote }}</span>
        </div>
        <span class="rv-count">已聚合 {{ gearReviews.totalCount.toLocaleString() }} 条真实评价</span>
      </div>
    </div>
  </section>
</template>

<style scoped>
.tabs { padding: 0 var(--content-px) 16px; display: flex; gap: 12px; align-items: flex-start; flex-wrap: wrap; }
.tab { background: var(--panel); color: var(--t1); font-size: 13px; font-weight: 500; padding: 11px 16px; }
.tab.on { background: var(--lime); color: var(--ink); font-weight: 700; }

.compare { padding: 0 var(--content-px); display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--card-gap); align-items: stretch; }
.gc {
  background: #FFFFFF;
  border: 2px solid var(--ink);
  box-shadow: var(--sh-white-4);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.gc.best { box-shadow: var(--sh-lime-4); }
.gc-img { width: 100%; height: 160px; object-fit: contain; display: block; background: #F0F0F0; }
.gc-badge { align-self: flex-start; background: var(--lime); color: var(--ink); font-size: 11px; font-weight: 700; padding: 6px 10px; }
.gc-name { font-size: 16px; font-weight: 700; color: var(--ink); }
.gc-specs { font-size: 13px; color: var(--ink2); line-height: 1.9; flex: 1; }
.gc-link { font-size: 12px; font-weight: 700; color: var(--ink); text-decoration: underline; text-underline-offset: 3px; }

.gap-sec { padding: 24px var(--content-px) 0; }
.gap-panel { padding: 20px; display: flex; flex-direction: column; gap: 14px; }
.gap-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.gap-card { background: var(--bg); border: 1px solid var(--line); padding: 16px; display: flex; flex-direction: column; gap: 6px; }
.gap-name { font-size: 13px; font-weight: 700; color: var(--t1); }
.gap-meta { font-size: 12px; color: var(--t2); }
.gap-price { font-family: var(--vt); font-size: 24px; color: var(--lime); line-height: 1; margin-top: auto; }

.review-sec { padding: 24px var(--content-px) 0; }
.review-bar { padding: 14px 20px; display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.rv-left { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
.rv-label { font-family: var(--silk); font-weight: 700; font-size: 11px; color: var(--lime); }
.rv-quote { font-size: 13px; font-weight: 500; color: var(--t1); }
.rv-count { font-size: 12px; color: var(--t2); }

.empty {
  margin: 24px var(--content-px);
  padding: 40px;
  font-size: 14px;
  color: var(--t1);
}

/* 窄屏桌面：三卡 → 两卡/单卡 */
@media (max-width: 1200px) {
  .compare { grid-template-columns: repeat(2, 1fr); }
  .gap-row { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 900px) {
  .compare { grid-template-columns: 1fr; }
  .gap-row { grid-template-columns: 1fr; }
}
</style>
