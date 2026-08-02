<script setup>
/** M4 装备 · 装备比选（移动端 Tab 4，对齐设计稿 6:24）
 *  数据来自真实装备目录与评价聚合
 */
import { onMounted, ref, watch } from 'vue'
import MHeader from './MHeader.vue'
import TabBar from './TabBar.vue'
import { fetchGapPicks, fetchGearCompare, fetchGearReviews, GEAR_CATEGORIES, state } from '../../api/index'

const activeCategory = ref('footwear')
const items = ref([])
const gapPicks = ref([])
const gearReviews = ref({ totalCount: 0, quote: '' })

const load = async () => {
  try {
    items.value = await fetchGearCompare(activeCategory.value)
    gapPicks.value = await fetchGapPicks(activeCategory.value, state.budgetCny ?? 500)
  } catch {
    items.value = []
    gapPicks.value = []
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
  <div class="m-screen">
    <MHeader />
    <div class="m-body">
      <div class="link-chip">按装备目录真实数据生成建议</div>

      <div class="tabs">
        <button v-for="t in GEAR_CATEGORIES" :key="t.value" class="tab"
                :class="{ on: t.value === activeCategory }" @click="activeCategory = t.value">{{ t.label }}</button>
      </div>

      <article v-for="g in items" :key="g.id" class="gc" :class="{ best: g.best }">
        <img class="gc-img" :src="g.img" :alt="g.name" />
        <span v-if="g.best" class="gc-badge">最适合本路线 · BEST MATCH</span>
        <h3 class="gc-name">{{ g.name }}</h3>
        <div class="gc-specs">
          <div>{{ g.specs[0] }} · {{ g.specs[1] }}</div>
          <div>{{ g.specs[2] }} · {{ g.specs[3] }}</div>
          <div>{{ g.specs[4] }}</div>
          <div v-if="g.specs[5]">{{ g.specs[5] }}</div>
        </div>
        <a v-if="g.sourceUrl" class="gc-link" :href="g.sourceUrl" target="_blank" rel="noopener">官网查看 →</a>
      </article>

      <section class="gap">
        <div class="gap-title">缺口补给建议 · GAP PICKS</div>
        <div v-for="g in gapPicks" :key="g.name" class="gap-row">
          <div class="gap-text">
            <div class="gap-name">{{ g.name }}</div>
            <div class="gap-meta">{{ g.meta }}</div>
          </div>
          <span class="gap-price">{{ g.price }}</span>
        </div>
        <div v-if="!items.length" class="empty">该品类暂无装备数据。</div>
        <div class="gap-review">{{ gearReviews.quote }} · 已聚合 {{ gearReviews.totalCount.toLocaleString() }} 条真实评价</div>
      </section>
    </div>
    <TabBar />
  </div>
</template>

<style scoped>
.link-chip { background: var(--bg); border: 1px solid var(--lime); color: var(--lime); font-size: 11px; font-weight: 700; padding: 9px 12px; }
.tabs { display: flex; gap: 8px; }
.tab { background: var(--panel); color: var(--t1); font-size: 11px; font-weight: 500; padding: 8px 12px; }
.tab.on { background: var(--lime); color: var(--ink); font-weight: 700; }
.gc {
  background: #FFF; border: 2px solid var(--ink); box-shadow: var(--sh-white-4);
  padding: 12px; display: flex; flex-direction: column; gap: 8px;
}
.gc.best { box-shadow: var(--sh-lime-4); }
.gc-img { width: 100%; height: 110px; object-fit: cover; background: #F0F0F0; }
.gc-badge { align-self: flex-start; background: var(--lime); color: var(--ink); font-size: 9px; font-weight: 700; padding: 4px 8px; }
.gc-name { font-size: 14px; font-weight: 700; color: var(--ink); }
.gc-specs { font-size: 10px; color: var(--ink2); line-height: 1.7; }
.gc-link { font-size: 10px; font-weight: 700; color: var(--ink); text-decoration: underline; text-underline-offset: 2px; }
.gap { background: var(--panel); border: 1px solid var(--line); padding: 14px; display: flex; flex-direction: column; gap: 10px; }
.gap-title { font-size: 13px; font-weight: 700; color: #FFF; }
.gap-row { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.gap-name { font-size: 11px; font-weight: 700; color: var(--t1); }
.gap-meta { font-size: 9px; color: var(--t2); margin-top: 2px; }
.gap-price { font-family: var(--vt); font-size: 16px; color: var(--lime); flex: none; }
.gap-review { font-size: 9px; color: var(--t2); border-top: 1px dashed var(--line); padding-top: 10px; line-height: 1.6; }
.empty { font-size: 11px; color: var(--t2); }
</style>
