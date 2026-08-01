<script setup>
import { computed, ref } from 'vue'
import HudNav from './HudNav.vue'
import { api } from '../api'
import { store } from '../store'

const emit = defineEmits(['nav'])

const plan = computed(() => store.selectedPlan)
const rec = computed(() => store.recommendation)
const favored = ref(false)

const headerChip = computed(() => {
  if (!plan.value) return ''
  const date = rec.value?.request?.travel_date || ''
  const group = rec.value?.request?.group_size || 1
  return `${plan.value.title} · ${date} 出发 · ${group} 人`
})

const transits = computed(() =>
  (plan.value?.transport_options || []).map((t) => ({
    icon: t.mode.includes('公交') || t.mode.includes('地铁') ? 'metro' : 'train',
    l1: `${t.mode} · ${t.summary}`,
    l2: [t.distance_km != null ? `${t.distance_km}KM` : null, t.duration_min != null ? `约 ${t.duration_min} 分钟` : null]
      .filter(Boolean)
      .join(' · ') || '以高德实时方案为准'
  }))
)

const supplies = computed(() =>
  (plan.value?.supply_points || []).slice(0, 6).map((p, i) => ({
    code: `S${i + 1}`,
    name: p.name,
    meta: `${p.category}${p.distance_m != null ? ` · 距起点 ${Math.round(p.distance_m)}M` : ''}`
  }))
)

const checklist = ref([])
const checkedState = ref({})
const gearItems = computed(() =>
  (plan.value?.equipment_suggestions || []).map((s) => ({
    key: s.equipment_id,
    text: `${s.name} · ${s.reason}`,
    checked: !!checkedState.value[s.equipment_id]
  }))
)
const gapCount = computed(() => gearItems.value.filter((g) => !g.checked).length)

function toggleGear(key) {
  checkedState.value = { ...checkedState.value, [key]: !checkedState.value[key] }
}

async function favoritePlan() {
  if (!store.selectedRouteId) return
  try {
    await api(`/routes/${store.selectedRouteId}/favorite`, { method: 'POST' })
    favored.value = true
  } catch { /* 保持原状态 */ }
}

// 时间线与海拔剖面：后端无轨迹数据源，保留设计稿展示（演示用）
const timeline = [
  { time: '08:30', event: '入口集合' },
  { time: '09:00', event: '出发' },
  { time: '12:00', event: '中途午餐补给' },
  { time: '15:30', event: '到达终点' },
  { time: '17:00', event: '返程' }
]
</script>

<template>
  <section class="screen">
    <HudNav active="plan" @nav="emit('nav', $event)" />

    <header class="screen-head" style="height:120px;">
      <div>
        <div class="sh-title-cn">「04」出行执行助手</div>
        <div class="sh-title-en">EXECUTION PLAN — HOW TO GO</div>
      </div>
      <span v-if="plan" class="sh-chip">{{ headerChip }}</span>
    </header>

    <div v-if="!plan" class="empty panel-d">
      还没有选中的出行方案，请先在「02 智能推荐」选择一条路线。
      <button class="empty-btn" @click="emit('nav', 's2')">去看推荐 →</button>
    </div>

    <template v-else>
      <!-- 三列 1440×412，pad 0 48，gap 24 -->
      <div class="cols">
        <!-- 大交通 -->
        <div class="col panel-d" style="min-height:295px;">
          <div class="ptitle">大交通与接驳 · TRANSIT</div>
          <div v-for="t in transits" :key="t.l1" class="tr-row">
            <svg class="tr-icon" viewBox="0 0 20 20">
              <template v-if="t.icon === 'metro'">
                <rect x="5" y="3" width="10" height="10" fill="#A3E635"/><rect x="7" y="5" width="6" height="3" fill="#0B0B0B"/>
                <rect x="7" y="10" width="2" height="2" fill="#0B0B0B"/><rect x="11" y="10" width="2" height="2" fill="#0B0B0B"/>
                <rect x="6" y="14" width="3" height="2" fill="#A3E635"/><rect x="11" y="14" width="3" height="2" fill="#A3E635"/>
              </template>
              <template v-else>
                <rect x="3" y="4" width="14" height="9" fill="#A3E635"/>
                <rect x="5" y="6" width="3" height="3" fill="#0B0B0B"/><rect x="9" y="6" width="3" height="3" fill="#0B0B0B"/><rect x="13" y="6" width="3" height="3" fill="#0B0B0B"/>
                <rect x="5" y="14" width="3" height="3" fill="#A3E635"/><rect x="12" y="14" width="3" height="2" fill="#A3E635"/>
              </template>
            </svg>
            <div class="tr-text">
              <div class="tr-l1">{{ t.l1 }}</div>
              <div class="tr-l2">{{ t.l2 }}</div>
            </div>
          </div>
          <div v-if="!transits.length" class="tr-l2">暂无交通方案数据</div>
          <div class="col-tip">交通方案来自高德实时规划，请以出行当日查询为准</div>
        </div>

        <!-- 时间线 -->
        <div class="col panel-d" style="min-height:307px;">
          <div class="ptitle">时间安排 · TIMELINE</div>
          <div v-for="t in timeline" :key="t.time" class="tl-row">
            <span class="tl-time">{{ t.time }}</span>
            <span class="tl-event">{{ t.event }}</span>
            <svg class="tl-bell" viewBox="0 0 16 16">
              <rect x="7" y="1" width="2" height="2" fill="#A3E635"/><rect x="5" y="3" width="6" height="2" fill="#A3E635"/>
              <rect x="4" y="5" width="8" height="6" fill="#A3E635"/><rect x="3" y="11" width="10" height="2" fill="#A3E635"/>
              <rect x="7" y="13" width="2" height="2" fill="#A3E635"/>
            </svg>
          </div>
          <div class="col-note">预计耗时 {{ Math.round(plan.estimated_duration_min / 60) }}H · 时间线为演示排期，请按实际情况调整</div>
        </div>

        <!-- 补给与装备 -->
        <div class="col panel-d" style="min-height:412px;">
          <div class="ptitle">沿途补给与装备 · SUPPLY &amp; GEAR</div>
          <div class="supply">
            <template v-for="s in supplies" :key="s.code">
              {{ s.code }} {{ s.name }} · {{ s.meta }}<br />
            </template>
            <template v-if="!supplies.length">起点 3KM 内未查询到补给点，请提前备足饮水。</template>
          </div>
          <div class="gear-label">建议装备清单 · CHECKLIST</div>
          <div v-for="g in gearItems" :key="g.key" class="gk-row" @click="toggleGear(g.key)">
            <span class="gk-box" :class="{ on: g.checked }">
              <svg v-if="g.checked" viewBox="0 0 18 18">
                <rect x="3" y="9" width="3" height="3" fill="#0B0B0B"/><rect x="6" y="12" width="3" height="3" fill="#0B0B0B"/>
                <rect x="9" y="9" width="3" height="3" fill="#0B0B0B"/><rect x="12" y="6" width="3" height="3" fill="#0B0B0B"/>
              </svg>
            </span>
            <span class="gk-text" :class="{ dim: g.checked }">{{ g.text }}</span>
          </div>
          <div v-if="!gearItems.length" class="gk-text">暂无装备建议</div>
          <button class="gap-link" @click="emit('nav', 's6')">缺口 {{ gapCount }} 件 · 去装备比选 →</button>
        </div>
      </div>

      <!-- 海拔剖面 1440×229（演示：后端无轨迹数据源） -->
      <div class="elev-sec">
        <div class="elev panel-d">
          <div class="ptitle">路线海拔剖面 · ELEVATION PROFILE（示意）</div>
          <div class="chart">
            <svg viewBox="0 0 1296 160" preserveAspectRatio="none">
              <path d="M0 140 H100 V120 H220 V130 H360 V92 H500 V102 H660 V62 H800 V80 H960 V46 H1100 V72 H1296 V56 V160 H0 Z"
                    fill="#0B0B0B" stroke="#A3E635" stroke-width="2" />
            </svg>
          </div>
          <div class="elev-cap">累计爬升 {{ plan.elevation_gain_m }}M · 海拔剖面为示意图，非实测轨迹</div>
        </div>
      </div>

      <!-- 操作行 1440×83 -->
      <div class="actions">
        <button class="btn white" @click="favoritePlan">{{ favored ? '已收藏' : '收藏计划' }}</button>
        <button class="btn dark">导出 PDF · 即将上线</button>
        <button class="btn soon">约伴同行 · 即将上线</button>
      </div>
    </template>
  </section>
</template>

<style scoped>
.cols {
  min-height: 412px;
  padding: 0 48px;
  display: flex;
  gap: 24px;
  align-items: flex-start;
}
.col { width: 432px; padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; }

.tr-row { display: flex; gap: 12px; align-items: flex-start; }
.tr-icon { width: 20px; height: 20px; flex: none; margin-top: 10px; }
.tr-text { display: flex; flex-direction: column; gap: 4px; }
.tr-l1 { font-size: 13px; font-weight: 700; color: var(--t1); }
.tr-l2 { font-size: 12px; color: var(--t2); }
.col-tip {
  margin-top: auto;
  background: var(--bg);
  border: 1px solid var(--lime);
  color: var(--lime);
  font-size: 12px; font-weight: 500;
  padding: 11px 12px;
}

.tl-row { display: flex; align-items: center; gap: 12px; height: 20px; }
.tl-time { font-family: var(--vt); font-size: 20px; color: var(--lime); width: 62px; flex: none; }
.tl-event { font-size: 13px; font-weight: 500; color: var(--t1); }
.tl-bell { width: 16px; height: 16px; margin-left: auto; flex: none; }
.col-note {
  margin-top: auto;
  background: var(--bg);
  color: var(--t2);
  font-size: 12px; font-weight: 500;
  padding: 11px 12px;
}

.supply { font-size: 13px; color: var(--t1); line-height: 1.9; }
.gear-label { font-size: 13px; font-weight: 700; color: #FFFFFF; }
.gk-row { display: flex; align-items: center; gap: 10px; min-height: 19px; cursor: pointer; }
.gk-box {
  width: 18px; height: 18px; flex: none;
  border: 2px solid var(--t4);
  display: grid; place-items: center;
}
.gk-box.on { background: var(--lime); border: none; }
.gk-box svg { width: 18px; height: 18px; }
.gk-text { font-size: 13px; font-weight: 500; color: var(--t1); }
.gk-text.dim { color: var(--t2); }
.gap-link { font-size: 12px; font-weight: 700; color: var(--lime); text-align: left; }

.elev-sec { min-height: 229px; padding: 12px 48px 0; }
.elev { min-height: 217px; padding: 20px 24px; display: flex; flex-direction: column; gap: 14px; }
.chart { position: relative; height: 110px; }
.chart svg { position: absolute; inset: 0; width: 100%; height: 100%; }
.elev-cap { font-size: 12px; color: var(--t2); }

.actions { height: 83px; padding: 20px 48px 0; display: flex; gap: 16px; }
.btn { height: 43px; padding: 0 18px; font-size: 13px; font-weight: 700; }
.btn.white { background: #FFFFFF; color: var(--ink); }
.btn.dark { background: var(--bg); color: var(--t4); border: 1px solid var(--line); cursor: not-allowed; }
.btn.soon { background: var(--panel); color: var(--t4); border: 1px solid var(--line); font-weight: 500; cursor: not-allowed; }

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
</style>
