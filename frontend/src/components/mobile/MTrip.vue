<script setup>
/** M3 行程 · 执行助手（移动端 Tab 3，对齐设计稿 6:23）
 *  数据来自推荐结果中的真实路线方案（M1/M6 选择后生成）
 */
import { computed, ref } from 'vue'
import MHeader from './MHeader.vue'
import TabBar from './TabBar.vue'
import { buildPlan, state } from '../../api/index'

const plan = computed(() => buildPlan(state.selectedRouteId))
const checked = ref(new Set())
const toggleCheck = (item) => {
  const next = new Set(checked.value)
  next.has(item) ? next.delete(item) : next.add(item)
  checked.value = next
}
const gapCount = computed(() => (plan.value ? plan.value.checklist.length - checked.value.size : 0))

const transitIcons = {
  train: '<rect x="4" y="3" width="12" height="3"/><rect x="3" y="6" width="14" height="7"/><rect x="5" y="8" width="3" height="3" class="cut"/><rect x="9" y="8" width="3" height="3" class="cut"/><rect x="13" y="8" width="3" height="3" class="cut"/><rect x="5" y="14" width="3" height="2"/><rect x="12" y="14" width="3" height="2"/>',
  metro: '<rect x="5" y="3" width="10" height="10"/><rect x="7" y="5" width="6" height="3" class="cut"/><rect x="7" y="10" width="2" height="2" class="cut"/><rect x="11" y="10" width="2" height="2" class="cut"/><rect x="6" y="14" width="3" height="2"/><rect x="11" y="14" width="3" height="2"/>',
  bus: '<rect x="3" y="4" width="14" height="9"/><rect x="5" y="6" width="3" height="3" class="cut"/><rect x="9" y="6" width="3" height="3" class="cut"/><rect x="13" y="6" width="3" height="3" class="cut"/><rect x="5" y="14" width="3" height="3"/><rect x="12" y="14" width="3" height="3"/>'
}
const bell = '<rect x="7" y="1" width="2" height="2"/><rect x="5" y="3" width="6" height="2"/><rect x="4" y="5" width="8" height="6"/><rect x="3" y="11" width="10" height="2"/><rect x="7" y="13" width="2" height="2"/>'
</script>

<template>
  <div class="m-screen">
    <MHeader />
    <div class="m-body">
      <div v-if="!plan" class="empty">
        还没有进行中的行程。请先在「规划」页生成推荐，并选择一条路线。
        <button class="empty-btn" @click="$router.push('/plan')">去规划 →</button>
      </div>
      <template v-else>
      <div class="route-chip">{{ plan.title }}</div>

      <section class="panel">
        <div class="p-title">大交通与接驳 · TRANSIT</div>
        <div v-for="t in plan.transit" :key="t.line" class="tr-row">
          <svg class="tr-icon" viewBox="0 0 20 20" v-html="transitIcons[t.type]" />
          <div class="tr-text">
            <div class="tr-l1">{{ t.line }}</div>
            <div class="tr-l2">{{ t.detail }}</div>
          </div>
        </div>
        <div class="tip">{{ plan.transitTip }}</div>
      </section>

      <section class="panel">
        <div class="p-title">时间安排 · TIMELINE</div>
        <div v-for="t in plan.timeline" :key="t.time" class="tl-row">
          <span class="tl-time">{{ t.time }}</span>
          <span class="tl-event">{{ t.event }}</span>
          <svg class="tl-bell" viewBox="0 0 16 16" v-html="bell" />
        </div>
        <div class="note">{{ plan.timelineNote }}</div>
      </section>

      <section class="panel">
        <div class="p-title">沿途补给与装备 · SUPPLY &amp; GEAR</div>
        <div class="supply">{{ plan.supplyText }}</div>
        <div class="gear-label">建议装备清单 · CHECKLIST</div>
        <div v-for="g in plan.checklist" :key="g.item" class="gk-row" @click="toggleCheck(g.item)">
          <span class="gk-box" :class="{ on: checked.has(g.item) }">
            <svg v-if="checked.has(g.item)" viewBox="0 0 18 18">
              <rect x="3" y="9" width="3" height="3" fill="#0B0B0B"/><rect x="6" y="12" width="3" height="3" fill="#0B0B0B"/>
              <rect x="9" y="9" width="3" height="3" fill="#0B0B0B"/><rect x="12" y="6" width="3" height="3" fill="#0B0B0B"/>
            </svg>
          </span>
          <span class="gk-text" :class="{ dim: checked.has(g.item) }">{{ g.item }}</span>
        </div>
        <button class="gap-link" @click="$router.push('/gear')">缺口 {{ gapCount }} 件 · 去装备比选 →</button>
      </section>

      <section class="panel">
        <div class="p-title">路线海拔剖面 · ELEVATION</div>
        <svg class="chart" viewBox="0 0 315 64" preserveAspectRatio="none">
          <path d="M0 52 H28 V44 H60 V50 H100 V34 H140 V40 H180 V24 H220 V32 H260 V18 H315 V26 V64 H0 Z"
                fill="#0B0B0B" stroke="#A3E635" stroke-width="1.5"/>
          <rect x="96" y="30" width="4" height="4" fill="#FFD028"/><rect x="176" y="20" width="4" height="4" fill="#FFD028"/>
          <rect x="256" y="14" width="4" height="4" fill="#FFD028"/>
        </svg>
        <div class="p-dim">{{ plan.elevation.caption }}</div>
      </section>
      </template>
    </div>
    <TabBar />
  </div>
</template>

<style scoped>
.route-chip { background: var(--panel); border: 1px solid var(--line); padding: 9px 12px; font-size: 11px; font-weight: 500; color: var(--t1); }
.panel { background: var(--panel); border: 1px solid var(--line); padding: 14px; display: flex; flex-direction: column; gap: 10px; }
.p-title { font-size: 13px; font-weight: 700; color: #FFF; }
.p-dim { font-size: 9px; color: var(--t2); }
.tr-row { display: flex; gap: 10px; align-items: center; }
.tr-icon { width: 16px; height: 16px; fill: var(--lime); flex: none; }
.tr-icon :deep(.cut) { fill: #0B0B0B; }
.tr-l1 { font-size: 11px; font-weight: 700; color: var(--t1); }
.tr-l2 { font-size: 10px; color: var(--t2); margin-top: 2px; }
.tip { background: var(--bg); border: 1px solid var(--lime); color: var(--lime); font-size: 10px; font-weight: 500; padding: 8px 10px; }
.tl-row { display: flex; align-items: center; gap: 10px; }
.tl-time { font-family: var(--vt); font-size: 16px; color: var(--lime); width: 52px; flex: none; }
.tl-event { flex: 1; font-size: 11px; font-weight: 500; color: var(--t1); }
.tl-bell { width: 14px; height: 14px; fill: var(--lime); flex: none; }
.note { background: var(--bg); color: var(--t2); font-size: 10px; font-weight: 500; padding: 8px 10px; }
.supply { font-size: 10px; color: var(--t1); line-height: 1.8; white-space: pre-line; }
.gear-label { font-size: 11px; font-weight: 700; color: #FFF; }
.gk-row { display: flex; align-items: center; gap: 8px; }
.gk-box { width: 14px; height: 14px; border: 2px solid var(--t4); display: grid; place-items: center; flex: none; }
.gk-box.on { background: var(--lime); border: none; }
.gk-box svg { width: 14px; height: 14px; }
.gk-text { font-size: 11px; font-weight: 500; color: var(--t1); }
.gk-text.dim { color: var(--t2); }
.gap-link { font-size: 10px; font-weight: 700; color: var(--lime); text-align: left; padding: 0; }
.chart { width: 100%; height: 64px; }
.empty { font-size: 11px; color: var(--t2); line-height: 1.8; display: flex; flex-direction: column; gap: 10px; }
.empty-btn { align-self: flex-start; font-size: 11px; font-weight: 700; color: var(--lime); padding: 0; }
</style>
