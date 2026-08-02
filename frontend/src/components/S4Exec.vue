<script setup>
/** S4 出行执行助手（桌面端，对齐设计稿 2:280）
 *  交通/补给/装备清单来自推荐引擎的真实结果（不落库）
 */
import { computed, ref } from 'vue'
import HudNav from './HudNav.vue'
import { buildPlan, setFavorite, state } from '../api/index'
import { useCheckin } from '../composables/useCheckin'

const plan = computed(() => buildPlan(state.selectedRouteId))
const favored = ref(false)

const transitIcons = {
  metro: '<rect x="5" y="3" width="10" height="10"/><rect x="7" y="5" width="6" height="3" class="cut"/><rect x="7" y="10" width="2" height="2" class="cut"/><rect x="11" y="10" width="2" height="2" class="cut"/><rect x="6" y="14" width="3" height="2"/><rect x="11" y="14" width="3" height="2"/>',
  bus: '<rect x="3" y="4" width="14" height="9"/><rect x="5" y="6" width="3" height="3" class="cut"/><rect x="9" y="6" width="3" height="3" class="cut"/><rect x="13" y="6" width="3" height="3" class="cut"/><rect x="5" y="14" width="3" height="3"/><rect x="12" y="14" width="3" height="3"/>'
}
const bell = '<rect x="7" y="1" width="2" height="2"/><rect x="5" y="3" width="6" height="2"/><rect x="4" y="5" width="8" height="6"/><rect x="3" y="11" width="10" height="2"/><rect x="7" y="13" width="2" height="2"/>'

const checked = ref({})
const toggleGear = (item) => { checked.value = { ...checked.value, [item]: !checked.value[item] } }
const gapCount = computed(() => (plan.value?.checklist || []).filter((g) => !checked.value[g.item]).length)

const favoritePlan = async () => {
  try {
    await setFavorite(state.selectedRouteId, true)
    favored.value = true
  } catch { /* 保持原状态 */ }
}

// ---- 完成徒步 · 打卡（反哺推荐能力画像） ----
const { checkinRating, checkinSubmitting, checkinMsg, checkin } = useCheckin()
</script>

<template>
  <section class="screen">
    <HudNav />

    <header class="screen-head">
      <div>
        <div class="sh-title-cn">「04」出行执行助手</div>
        <div class="sh-title-en">EXECUTION PLAN — HOW TO GO</div>
      </div>
      <span v-if="plan" class="sh-chip">{{ plan.title }}</span>
    </header>

    <div v-if="!plan" class="empty panel-d">
      还没有选中的出行方案，请先在「智能推荐」选择一条路线。
      <button class="empty-btn" @click="$router.push('/plan/results')">去看推荐 →</button>
    </div>

    <template v-else>
      <div class="cols">
        <div class="col panel-d">
          <div class="ptitle">大交通与接驳 · TRANSIT</div>
          <div v-for="t in plan.transit" :key="t.line" class="tr-row">
            <svg class="tr-icon" viewBox="0 0 20 20" v-html="transitIcons[t.type]" />
            <div class="tr-text">
              <div class="tr-l1">{{ t.line }}</div>
              <div class="tr-l2">{{ t.detail }}</div>
              <div v-for="(s, i) in t.steps" :key="i" class="tr-step">{{ i + 1 }}. {{ s }}</div>
            </div>
          </div>
          <div v-if="!plan.transit.length" class="tr-l2">暂无交通方案数据</div>
          <div class="col-tip">{{ plan.transitTip }}</div>
        </div>

        <div class="col panel-d">
          <div class="ptitle">时间安排 · TIMELINE</div>
          <div v-for="t in plan.timeline" :key="t.time" class="tl-row">
            <span class="tl-time">{{ t.time }}</span>
            <span class="tl-event">{{ t.event }}</span>
            <svg class="tl-bell" viewBox="0 0 16 16" v-html="bell" />
          </div>
          <div class="col-note">{{ plan.timelineNote }}</div>
        </div>

        <div class="col panel-d">
          <div class="ptitle">沿途补给与装备 · SUPPLY &amp; GEAR</div>
          <div class="supply">{{ plan.supplyText }}</div>
          <div class="gear-label">建议装备清单 · CHECKLIST</div>
          <div v-for="g in plan.checklist" :key="g.item" class="gk-row" @click="toggleGear(g.item)">
            <span class="gk-box" :class="{ on: checked[g.item] }">
              <svg v-if="checked[g.item]" viewBox="0 0 18 18">
                <rect x="3" y="9" width="3" height="3" fill="#0B0B0B"/><rect x="6" y="12" width="3" height="3" fill="#0B0B0B"/>
                <rect x="9" y="9" width="3" height="3" fill="#0B0B0B"/><rect x="12" y="6" width="3" height="3" fill="#0B0B0B"/>
              </svg>
            </span>
            <span class="gk-text" :class="{ dim: checked[g.item] }">{{ g.item }}</span>
          </div>
          <div v-if="!plan.checklist.length" class="gk-text">暂无装备建议</div>
          <button class="gap-link" @click="$router.push('/gear')">缺口 {{ gapCount }} 件 · 去装备比选 →</button>
        </div>
      </div>

      <div class="elev-sec">
        <div class="elev panel-d">
          <div class="ptitle">路线海拔剖面 · ELEVATION PROFILE（示意）</div>
          <div class="chart">
            <svg viewBox="0 0 1296 160" preserveAspectRatio="none">
              <path d="M0 140 H100 V120 H220 V130 H360 V92 H500 V102 H660 V62 H800 V80 H960 V46 H1100 V72 H1296 V56 V160 H0 Z"
                    fill="#0B0B0B" stroke="#A3E635" stroke-width="2" />
            </svg>
          </div>
          <div class="elev-cap">{{ plan.elevation.caption }}</div>
        </div>
      </div>

      <div class="actions">
        <div class="checkin">
          <span class="ck-stars">
            <button v-for="n in 5" :key="n" class="ck-star" :class="{ on: n <= checkinRating }"
                    @click="checkinRating = n">{{ n <= checkinRating ? '★' : '☆' }}</button>
          </span>
          <button class="btn lime" :disabled="checkinSubmitting" @click="checkin">
            {{ checkinSubmitting ? '打卡中…' : '完成徒步 · 打卡' }}
          </button>
          <span v-if="checkinMsg" class="ck-msg">{{ checkinMsg }}</span>
        </div>
        <button class="btn white" @click="favoritePlan">{{ favored ? '已收藏' : '收藏计划' }}</button>
        <button class="btn dark">导出 PDF · 即将上线</button>
        <button class="btn soon">约伴同行 · 即将上线</button>
      </div>
    </template>
  </section>
</template>

<style scoped>
.cols { padding: 0 var(--content-px); display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--card-gap); align-items: stretch; }
.col { padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; }

.tr-row { display: flex; gap: 12px; align-items: flex-start; }
.tr-icon { width: 20px; height: 20px; fill: var(--lime); flex: none; margin-top: 10px; }
.tr-icon :deep(.cut) { fill: #161616; }
.tr-text { display: flex; flex-direction: column; gap: 4px; }
.tr-l1 { font-size: 13px; font-weight: 700; color: var(--t1); }
.tr-l2 { font-size: 12px; color: var(--t2); }
.tr-step { font-size: 11px; color: var(--t3); padding-left: 8px; border-left: 2px solid var(--line); margin-top: 2px; }
.col-tip { margin-top: auto; background: var(--bg); border: 1px solid var(--lime); color: var(--lime); font-size: 12px; font-weight: 500; padding: 11px 12px; }

.tl-row { display: flex; align-items: center; gap: 12px; height: 20px; }
.tl-time { font-family: var(--vt); font-size: 20px; color: var(--lime); width: 62px; flex: none; }
.tl-event { font-size: 13px; font-weight: 500; color: var(--t1); flex: 1; }
.tl-bell { width: 16px; height: 16px; fill: var(--lime); flex: none; }
.col-note { margin-top: auto; background: var(--bg); color: var(--t2); font-size: 12px; font-weight: 500; padding: 11px 12px; }

.supply { font-size: 13px; color: var(--t1); line-height: 1.9; white-space: pre-line; }
.gear-label { font-size: 13px; font-weight: 700; color: #FFFFFF; }
.gk-row { display: flex; align-items: center; gap: 10px; min-height: 19px; cursor: pointer; }
.gk-box { width: 18px; height: 18px; flex: none; border: 2px solid var(--t4); display: grid; place-items: center; }
.gk-box.on { background: var(--lime); border: none; }
.gk-box svg { width: 18px; height: 18px; }
.gk-text { font-size: 13px; font-weight: 500; color: var(--t1); }
.gk-text.dim { color: var(--t2); }
.gap-link { font-size: 12px; font-weight: 700; color: var(--lime); text-align: left; padding: 0; }

.elev-sec { padding: 24px var(--content-px) 0; }
.elev { padding: 20px 24px; display: flex; flex-direction: column; gap: 14px; }
.chart { position: relative; height: 110px; }
.chart svg { position: absolute; inset: 0; width: 100%; height: 100%; }
.elev-cap { font-size: 12px; color: var(--t2); }

.actions { padding: 24px var(--content-px) 40px; display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }
.btn { height: 43px; padding: 0 18px; font-size: 13px; font-weight: 700; }
.btn.white { background: #FFFFFF; color: var(--ink); margin-left: auto; }
/* 主操作：完成打卡，全场最大最亮 */
.btn.lime { background: var(--lime); border: 2px solid var(--ink); color: var(--ink); height: 52px; padding: 0 26px; font-size: 15px; }
.btn.lime:disabled { opacity: 0.6; }
/* 未上线功能：缩小弱化，不与主操作抢注意力 */
.btn.dark { background: var(--bg); color: var(--t4); border: 1px solid var(--line); cursor: not-allowed; height: 34px; padding: 0 12px; font-size: 11px; font-weight: 500; }
.btn.soon { background: var(--panel); color: var(--t4); border: 1px solid var(--line); cursor: not-allowed; height: 34px; padding: 0 12px; font-size: 11px; font-weight: 500; }
.checkin { display: flex; align-items: center; gap: 12px; }
.ck-stars { display: inline-flex; }
.ck-star { font-size: 20px; color: var(--t4); padding: 0 2px; line-height: 1; }
.ck-star.on { color: var(--amber); }
.ck-msg { font-size: 12px; color: var(--lime); max-width: 220px; }

.empty {
  margin: 24px var(--content-px);
  padding: 40px;
  font-size: 14px;
  color: var(--t1);
  display: flex;
  align-items: center;
  gap: 16px;
}
.empty-btn { background: var(--lime); color: var(--ink); font-weight: 700; padding: 8px 16px; }

/* 窄屏桌面：三栏 → 单栏堆叠 */
@media (max-width: 1100px) {
  .cols { grid-template-columns: 1fr; }
}
</style>
