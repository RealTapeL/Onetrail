<script setup>
import HudNav from './HudNav.vue'
const emit = defineEmits(['nav'])

const transits = [
  {
    icon: 'train',
    l1: '高铁 · 上海虹桥 → 杭州东',
    l2: '07:15 – 08:06 · 二等座 ¥73'
  },
  {
    icon: 'metro',
    l1: '地铁 1 号线 · 杭州东 → 龙翔桥',
    l2: '25 分钟 · ¥4'
  },
  {
    icon: 'bus',
    l1: '公交 4 路 · 龙翔桥 → 九溪站',
    l2: '30 分钟 · ¥2 · 步行 800M 至入口'
  }
]
const timeline = [
  { time: '08:30', event: '九溪入口集合' },
  { time: '09:00', event: '出发 · 溪谷竹林段' },
  { time: '12:00', event: '龙井村 · 午餐补给' },
  { time: '15:30', event: '杨梅岭 · 到达终点' },
  { time: '17:00', event: '返程' }
]
const gears = [
  { text: '登山鞋 · 已有', checked: true },
  { text: '背包 20L · 已有', checked: true },
  { text: '2L 饮水', checked: false },
  { text: '雨具', checked: false },
  { text: '头灯', checked: false },
  { text: '能量食品', checked: false }
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
      <span class="sh-chip">九溪十八涧环线 · 5月2日出发 · 2 人</span>
    </header>

    <!-- 三列 1440×412，pad 0 48，gap 24 -->
    <div class="cols">
      <!-- 大交通 -->
      <div class="col panel-d" style="height:295px;">
        <div class="ptitle">大交通与接驳 · TRANSIT</div>
        <div v-for="t in transits" :key="t.l1" class="tr-row">
          <svg class="tr-icon" viewBox="0 0 20 20">
            <template v-if="t.icon === 'train'">
              <rect x="4" y="3" width="12" height="3" fill="#A3E635"/><rect x="3" y="6" width="14" height="7" fill="#A3E635"/>
              <rect x="5" y="8" width="3" height="3" fill="#0B0B0B"/><rect x="9" y="8" width="3" height="3" fill="#0B0B0B"/><rect x="13" y="8" width="3" height="3" fill="#0B0B0B"/>
              <rect x="5" y="14" width="3" height="2" fill="#A3E635"/><rect x="12" y="14" width="3" height="2" fill="#A3E635"/>
            </template>
            <template v-else-if="t.icon === 'metro'">
              <rect x="5" y="3" width="10" height="10" fill="#A3E635"/><rect x="7" y="5" width="6" height="3" fill="#0B0B0B"/>
              <rect x="7" y="10" width="2" height="2" fill="#0B0B0B"/><rect x="11" y="10" width="2" height="2" fill="#0B0B0B"/>
              <rect x="6" y="14" width="3" height="2" fill="#A3E635"/><rect x="11" y="14" width="3" height="2" fill="#A3E635"/>
            </template>
            <template v-else>
              <rect x="3" y="4" width="14" height="9" fill="#A3E635"/>
              <rect x="5" y="6" width="3" height="3" fill="#0B0B0B"/><rect x="9" y="6" width="3" height="3" fill="#0B0B0B"/><rect x="13" y="6" width="3" height="3" fill="#0B0B0B"/>
              <rect x="5" y="14" width="3" height="3" fill="#A3E635"/><rect x="12" y="14" width="3" height="3" fill="#A3E635"/>
            </template>
          </svg>
          <div class="tr-text">
            <div class="tr-l1">{{ t.l1 }}</div>
            <div class="tr-l2">{{ t.l2 }}</div>
          </div>
        </div>
        <div class="col-tip">接驳提示：返程末班公交 18:30，注意下山时间</div>
      </div>

      <!-- 时间线 -->
      <div class="col panel-d" style="height:307px;">
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
        <div class="col-note">全程约 4H · 点击铃铛设置出发提醒</div>
      </div>

      <!-- 补给与装备 -->
      <div class="col panel-d" style="height:412px;">
        <div class="ptitle">沿途补给与装备 · SUPPLY &amp; GEAR</div>
        <div class="supply">
          S1 龙井村 · 午餐/补水 · 4.2KM 处<br />
          S2 理安寺 · 补水/休息 · 6.8KM 处<br />
          S3 杨梅岭 · 终点补给 · 9.5KM 处
        </div>
        <div class="gear-label">建议装备清单 · CHECKLIST</div>
        <div v-for="g in gears" :key="g.text" class="gk-row">
          <span class="gk-box" :class="{ on: g.checked }">
            <svg v-if="g.checked" viewBox="0 0 18 18">
              <rect x="3" y="9" width="3" height="3" fill="#0B0B0B"/><rect x="6" y="12" width="3" height="3" fill="#0B0B0B"/>
              <rect x="9" y="9" width="3" height="3" fill="#0B0B0B"/><rect x="12" y="6" width="3" height="3" fill="#0B0B0B"/>
            </svg>
          </span>
          <span class="gk-text" :class="{ dim: g.checked }">{{ g.text }}</span>
        </div>
        <button class="gap-link" @click="emit('nav', 's6')">缺口 4 件 · 去装备比选 →</button>
      </div>
    </div>

    <!-- 海拔剖面 1440×229 -->
    <div class="elev-sec">
      <div class="elev panel-d">
        <div class="ptitle">路线海拔剖面 · ELEVATION PROFILE</div>
        <div class="chart">
          <svg viewBox="0 0 1296 160" preserveAspectRatio="none">
            <path d="M0 140 H100 V120 H220 V130 H360 V92 H500 V102 H660 V62 H800 V80 H960 V46 H1100 V72 H1296 V56 V160 H0 Z"
                  fill="#0B0B0B" stroke="#A3E635" stroke-width="2" />
            <rect x="496" y="94" width="8" height="8" fill="#FFD028" />
            <rect x="796" y="72" width="8" height="8" fill="#FFD028" />
            <rect x="1096" y="64" width="8" height="8" fill="#FFD028" />
          </svg>
          <span class="cl" style="left:0.3%;  top:82.5%; color:#8E8E8E;">入口 45M</span>
          <span class="cl" style="left:34.9%; top:53.75%; color:#FFD028;">S1 龙井村</span>
          <span class="cl" style="left:58.8%; top:40%;  color:#FFD028;">S2 理安寺</span>
          <span class="cl" style="left:81.2%; top:35%;  color:#FFD028;">S3 杨梅岭</span>
          <span class="cl" style="left:92.4%; top:27.5%; color:#8E8E8E;">最高 420M</span>
        </div>
        <div class="elev-cap">最高海拔 420M · 累计爬升 320M · 涉水点 2 处 · 补给点 3 处</div>
      </div>
    </div>

    <!-- 操作行 1440×83 -->
    <div class="actions">
      <button class="btn white">收藏计划</button>
      <button class="btn lime">分享给同伴</button>
      <button class="btn dark">导出 PDF</button>
      <button class="btn soon">约伴同行 · 即将上线</button>
    </div>
  </section>
</template>

<style scoped>
.cols {
  height: 412px;
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
.gk-row { display: flex; align-items: center; gap: 10px; height: 19px; }
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

.elev-sec { height: 229px; padding: 12px 48px 0; }
.elev { height: 217px; padding: 20px 24px; display: flex; flex-direction: column; gap: 14px; }
.chart { position: relative; height: 110px; }
.chart svg { position: absolute; inset: 0; width: 100%; height: 100%; }
.cl { position: absolute; font-size: 12px; transform: translateY(-100%); white-space: nowrap; }
.elev-cap { font-size: 12px; color: var(--t2); }

.actions { height: 83px; padding: 20px 48px 0; display: flex; gap: 16px; }
.btn { height: 43px; padding: 0 18px; font-size: 13px; font-weight: 700; }
.btn.white { background: #FFFFFF; color: var(--ink); }
.btn.lime { background: var(--lime); color: var(--ink); }
.btn.dark { background: var(--bg); color: var(--t1); border: 1px solid var(--t1); }
.btn.soon { background: var(--panel); color: var(--t4); border: 1px solid var(--line); font-weight: 500; cursor: not-allowed; }
</style>
