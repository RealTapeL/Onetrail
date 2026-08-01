<script setup>
import HudNav from './HudNav.vue'
const emit = defineEmits(['nav'])

const fields1 = [
  { label: '出行日期 · DATE',      value: '5月2日 – 5月4日 · 3天2晚' },
  { label: '目的地 · LOCATION',    value: '杭州 · 西湖区（当前定位）' },
  { label: '同行人数 · PARTY',     value: '2 人 · 朋友同行' },
  { label: '预算 · BUDGET',        value: '¥300 – 500 / 人' }
]
const fields2 = [
  { label: '体能 · FITNESS',       value: 'Lv.3 · 日常有锻炼习惯' },
  { label: '已有装备 · MY GEAR',   value: '登山鞋 · 背包 · 登山杖' }
]
const interests = [
  { label: '瀑布', on: true },
  { label: '竹林', on: true },
  { label: '古道', on: false },
  { label: '云海', on: false }
]
const questions = [
  { no: 'Q1', text: '这条路适不适合我？' },
  { no: 'Q2', text: '这条路值不值得去？' },
  { no: 'Q3', text: '怎么去、怎么走、带什么？' }
]
const stats = [
  { num: '12,847', label: '条精选路线' },
  { num: '86,000+', label: '徒步者在用' },
  { num: '342', label: '座城市覆盖' }
]
</script>

<template>
  <section class="screen">
    <HudNav active="plan" @nav="emit('nav', $event)" />

    <!-- Hero 1440×490，pad 40/48/32/48，gap 40 -->
    <div class="hero">
      <div class="hero-left">
        <div class="kicker"><span class="k-sq" /><span class="k-en">HIKING ROUTE DECISION ENGINE</span></div>
        <h1 class="h-title">你想去哪？</h1>
        <div class="h-title-en">WHERE DO YOU WANT TO GO?</div>
        <p class="h-sub">收集推荐所需条件，把复杂信息变成可理解的判断，降低你的出行决策成本。</p>

        <div class="slogan">
          <span class="slogan-bar" />
          <div class="slogan-g">
            <div class="slogan-cn">一径入云深，与世界重联</div>
            <div class="slogan-en">ONE TRAIL INTO THE CLOUDS, RECONNECT WITH THE WORLD</div>
          </div>
        </div>

        <div class="qs">
          <span v-for="q in questions" :key="q.no" class="q-chip">
            <span class="q-no">{{ q.no }}</span><span class="q-tx">{{ q.text }}</span>
          </span>
        </div>

        <div class="bstats">
          <div v-for="s in stats" :key="s.label" class="bs">
            <div class="bs-num">{{ s.num }}</div>
            <div class="bs-label">{{ s.label }}</div>
          </div>
        </div>
      </div>

      <!-- 像素山 420×280 -->
      <div class="pixel-art">
        <span class="px amber" style="left:62px; top:14px; width:32px; height:32px;" />
        <span class="px white" style="left:178px; top:22px;" />
        <span class="px white" style="left:200px; top:44px;" />
        <span class="px white" style="left:238px; top:8px;" />
        <svg class="mtn" viewBox="0 0 420 210" preserveAspectRatio="none">
          <path d="M0 210 V168 H36 V132 H72 V156 H108 V108 H144 V132 H188 V84 H232 V116 H276 V60 H320 V96 H356 V44 H392 V88 H420 V210 Z"
                fill="#141414" stroke="#A3E635" stroke-width="3" />
        </svg>
        <span class="px lime-w" style="left:266px; top:131px;" />
        <span class="px lime-w" style="left:352px; top:95px;" />
      </div>
    </div>

    <!-- Quest Input Panel 1440×351，白底，pad 40，gap 24 -->
    <div class="quest">
      <div class="q-head">
        <div class="q-titles">
          <div class="q-cn">「01」需求输入</div>
          <div class="q-en">QUEST INPUT — TELL US YOUR PLAN</div>
        </div>
        <div class="q-hint">要做什么：收集推荐所需条件，降低决策成本</div>
      </div>

      <div class="q-grid">
        <div v-for="f in fields1" :key="f.label" class="field">
          <div class="f-label">{{ f.label }}</div>
          <div class="f-value">{{ f.value }}</div>
        </div>
      </div>
      <div class="q-grid">
        <div class="field">
          <div class="f-label">{{ fields2[0].label }}</div>
          <div class="f-value">{{ fields2[0].value }}</div>
        </div>
        <div class="field">
          <div class="f-label">兴趣 · INTERESTS</div>
          <div class="f-chips">
            <span v-for="c in interests" :key="c.label" class="i-chip" :class="{ on: c.on }">{{ c.label }}</span>
          </div>
        </div>
        <div class="field">
          <div class="f-label">{{ fields2[1].label }}</div>
          <div class="f-value">{{ fields2[1].value }}</div>
        </div>
        <button class="cta" @click="emit('nav', 's2')">
          <span class="cta-cn">开始生成路线</span>
          <span class="cta-en">PRESS START</span>
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* Hero */
.hero {
  height: 490px;
  padding: 40px 48px 32px;
  display: flex;
  align-items: center;
  gap: 40px;
}
.hero-left { width: 884px; display: flex; flex-direction: column; gap: 20px; }
.kicker { display: flex; align-items: center; gap: 10px; }
.k-sq { width: 10px; height: 10px; background: var(--lime); }
.k-en { font-family: var(--silk); font-size: 12px; color: var(--lime); }
.h-title { font-size: 64px; font-weight: 900; color: #FFFFFF; line-height: 1.15; }
.h-title-en { font-family: var(--p8); font-size: 18px; color: var(--lime); }
.h-sub { font-size: 15px; color: var(--t2); line-height: 24px; }

.slogan { display: flex; align-items: center; gap: 14px; }
.slogan-bar { width: 4px; height: 48px; background: var(--lime); flex: none; }
.slogan-g { display: flex; flex-direction: column; gap: 8px; }
.slogan-cn { font-size: 28px; font-weight: 900; color: #FFFFFF; }
.slogan-en { font-family: var(--silk); font-size: 10px; color: var(--lime); }

.qs { display: flex; gap: 12px; }
.q-chip {
  display: inline-flex; align-items: center; gap: 8px;
  background: var(--panel);
  border: 1px solid var(--lime);
  padding: 9px 14px;
}
.q-no { font-family: var(--silk); font-weight: 700; font-size: 11px; color: var(--lime); }
.q-tx { font-size: 13px; font-weight: 500; color: var(--t1); }

.bstats { display: flex; gap: 36px; }
.bs { display: flex; flex-direction: column; gap: 4px; }
.bs-num { font-family: var(--vt); font-size: 28px; color: var(--lime); line-height: 1; }
.bs-label { font-size: 12px; color: var(--t2); }

/* 像素山 */
.pixel-art { position: relative; width: 420px; height: 280px; flex: none; }
.px { position: absolute; width: 14px; height: 14px; background: #FFFFFF; }
.px.amber { background: var(--amber); }
.px.lime-w { width: 35px; height: 14px; background: var(--lime); }
.mtn { position: absolute; left: 0; bottom: 0; width: 420px; height: 210px; }

/* Quest Panel */
.quest {
  height: 351px;
  background: #FFFFFF;
  padding: 40px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.q-head { display: flex; align-items: center; justify-content: space-between; }
.q-titles { display: flex; flex-direction: column; gap: 6px; }
.q-cn { font-size: 24px; font-weight: 900; color: var(--ink); }
.q-en { font-family: var(--silk); font-size: 11px; color: var(--t3); }
.q-hint { font-size: 13px; color: var(--t3); }

.q-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.field {
  background: var(--paper);
  border: 1px solid var(--ink);
  box-shadow: var(--sh-ink-3);
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 86px;
}
.f-label { font-size: 12px; font-weight: 500; color: var(--t3); }
.f-value { font-size: 16px; font-weight: 700; color: var(--ink); }
.f-chips { display: flex; gap: 8px; }
.i-chip {
  font-size: 12px; font-weight: 500; color: var(--ink);
  background: #FFFFFF; border: 1px solid var(--ink);
  padding: 5px 10px;
}
.i-chip.on { background: var(--ink); color: var(--lime); font-weight: 700; border-color: var(--ink); }

.cta {
  background: var(--lime);
  border: 2px solid var(--ink);
  box-shadow: var(--sh-ink-4);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 83px;
}
.cta-cn { font-size: 20px; font-weight: 900; color: var(--ink); }
.cta-en { font-family: var(--p8); font-size: 10px; color: var(--ink); }
.cta:active { transform: translate(2px, 2px); box-shadow: 2px 2px 0 #0A0A0A; }
</style>
