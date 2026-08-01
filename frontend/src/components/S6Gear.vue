<script setup>
import { computed, onMounted, ref } from 'vue'
import HudNav from './HudNav.vue'
import { api } from '../api'
import { store } from '../store'

const emit = defineEmits(['nav'])

const CATEGORIES = [
  { label: '背包', value: 'backpack' },
  { label: '徒步鞋', value: 'footwear' },
  { label: '帐篷', value: 'tent' },
  { label: '睡袋', value: 'sleeping_bag' }
]
const COVERS = ['/images/2_448.webp', '/images/2_452.webp', '/images/2_458.webp']

const activeCategory = ref('footwear')
const catalog = ref([])
const reviewSummary = ref(null)

const categoryLabel = (v) => CATEGORIES.find((c) => c.value === v)?.label || v

const gears = computed(() => {
  const items = catalog.value.filter((g) => g.category === activeCategory.value)
  const bestId = items.reduce(
    (best, g) => (g.average_rating != null && (best == null || g.average_rating > best.average_rating) ? g : best),
    null
  )?.id
  return items.slice(0, 3).map((g, i) => ({
    id: g.id,
    img: COVERS[i % COVERS.length],
    name: g.name,
    best: g.id === bestId && g.average_rating != null,
    specs: [
      g.price_cny != null ? `价格 ¥${g.price_cny}` : '价格 暂无',
      g.weight_g != null ? `重量 ${(g.weight_g / 1000).toFixed(1)}KG` : '重量 暂无',
      `防水 ${g.specifications?.防水 ?? '暂无参数'}`,
      `适合 ${g.suitable_scenarios.join(' · ') || '通用'}`,
      g.average_rating != null ? `用户评分 ${g.average_rating}` : '暂无评分'
    ]
  }))
})

const gaps = computed(() => {
  const budget = store.gearContext.budget ?? 500
  return catalog.value
    .filter((g) => g.category !== activeCategory.value && g.price_cny != null && g.price_cny <= budget)
    .sort((a, b) => a.price_cny - b.price_cny)
    .slice(0, 3)
    .map((g) => ({
      name: `${categoryLabel(g.category)} · ${g.name}`,
      meta: g.suitable_scenarios.join(' · ') || (g.weight_g != null ? `约 ${(g.weight_g / 1000).toFixed(1)}KG` : '通用场景'),
      price: `¥${g.price_cny}`
    }))
})

const contextSummary = computed(() =>
  store.gearContext.routeTitle
    ? `已按「${store.gearContext.routeTitle} · ${store.gearContext.tags.slice(0, 2).join('')}」生成建议`
    : '按装备目录真实数据生成建议'
)

async function load() {
  try {
    catalog.value = await api('/equipment', { auth: false })
  } catch {
    catalog.value = []
  }
  try {
    reviewSummary.value = await api('/equipment/reviews/summary', { auth: false })
  } catch {
    reviewSummary.value = null
  }
}

onMounted(load)
</script>

<template>
  <section class="screen">
    <HudNav active="gear" @nav="emit('nav', $event)" />

    <header class="screen-head" style="height:116px;">
      <div>
        <div class="sh-title-cn">「06」装备比选</div>
        <div class="sh-title-en">GEAR COMPARE — EXTENSION MODULE</div>
      </div>
      <span class="sh-chip lime">{{ contextSummary }}</span>
    </header>

    <!-- Tabs 1440×63 -->
    <div class="tabs">
      <button v-for="t in CATEGORIES" :key="t.value" class="tab"
              :class="{ on: t.value === activeCategory }"
              @click="activeCategory = t.value">{{ t.label }}</button>
    </div>

    <!-- 对比卡 1440×420 -->
    <div v-if="gears.length" class="compare">
      <article v-for="g in gears" :key="g.id" class="gc" :class="{ best: g.best }">
        <img class="gc-img" :src="g.img" :alt="g.name" />
        <span v-if="g.best" class="gc-badge">最适合本路线 · BEST MATCH</span>
        <h3 class="gc-name">{{ g.name }}</h3>
        <div class="gc-specs">
          <div v-for="s in g.specs" :key="s">{{ s }}</div>
        </div>
      </article>
    </div>
    <div v-else class="empty panel-d">该品类暂无装备数据，可先通过 API 提交装备。</div>

    <!-- GAP PICKS 1440×212 -->
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

    <!-- 评价条 1440×79 -->
    <div class="review-sec">
      <div class="review-bar panel-d">
        <div class="rv-left">
          <span class="rv-label">USER REVIEWS</span>
          <span class="rv-quote" v-if="reviewSummary?.sample">
            「{{ reviewSummary.sample.quote }}」—— {{ reviewSummary.sample.equipment_name }} 的真实评价
          </span>
          <span class="rv-quote" v-else>暂无真实评价，欢迎提交第一条装备反馈</span>
        </div>
        <span class="rv-count">已聚合 {{ reviewSummary?.total_count ?? 0 }} 条真实评价</span>
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
  min-height: 420px;
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

.gap-sec { min-height: 212px; padding: 16px 48px 0; }
.gap-panel { min-height: 180px; padding: 20px; display: flex; flex-direction: column; gap: 14px; }
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

.empty {
  margin: 24px 48px;
  padding: 40px;
  font-size: 14px;
  color: var(--t1);
}
</style>
