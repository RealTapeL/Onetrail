<script setup>
/** S1 首页 · 需求输入（桌面端，排列与移动端设计稿一致）
 *  顺序：NEON hero（天气）→ TBTI 测评卡 → 你想去哪 → 需求表单卡 → 我的行程预览
 *  表单控件全部映射真实推荐字段，提交走 POST /api/v1/recommendations/plan
 */
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import HudNav from './HudNav.vue'
import TbtiQuiz from './TbtiQuiz.vue'
import PrefsSheet from './PrefsSheet.vue'
import { buildPlan, postRecommendations, questFormDefaults, state, fetchWeatherTip, FORECAST_MIN_DATE, FORECAST_MAX_DATE } from '../api/index'
import { applyTbtiToForm, tbtiResult } from '../composables/tbti'

const forecastMin = FORECAST_MIN_DATE
const forecastMax = FORECAST_MAX_DATE

const router = useRouter()
const form = reactive(JSON.parse(JSON.stringify(questFormDefaults)))
const interestOptions = ['瀑布', '竹林', '古道', '云海']
const submitting = ref(false)
const errorMsg = ref('')
const quizOpen = ref(false)
const prefsOpen = ref(false)
const weatherText = ref('')

// 我的行程预览：有选中方案时取时间线前两条
const plan = computed(() => buildPlan(state.selectedRouteId))
const tripPreview = computed(() => (plan.value?.timeline || []).slice(0, 2))

onMounted(() => {
  applyTbtiToForm(form)
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(async (pos) => {
      const tip = await fetchWeatherTip(pos.coords.latitude, pos.coords.longitude)
      if (tip) weatherText.value = tip.text
    })
  }
})

// 轻装 / 重装：真实改表单默认值（体能 + 露营装备），用户可再改
const packMode = ref('light')
const setPack = (m) => {
  packMode.value = m
  if (m === 'heavy') {
    form.fitnessLevel = Math.max(form.fitnessLevel, 4)
    for (const g of ['帐篷', '睡袋']) {
      if (!form.ownedGear.includes(g)) form.ownedGear.push(g)
    }
  } else {
    form.fitnessLevel = Math.min(form.fitnessLevel, 2)
    form.ownedGear = form.ownedGear.filter((g) => !['帐篷', '睡袋'].includes(g))
  }
}

const toggle = (tag) => {
  const i = form.interests.indexOf(tag)
  i >= 0 ? form.interests.splice(i, 1) : form.interests.push(tag)
}
const locate = () => {
  if (!navigator.geolocation) return
  navigator.geolocation.getCurrentPosition((pos) => {
    form.location.lat = +pos.coords.latitude.toFixed(5)
    form.location.lng = +pos.coords.longitude.toFixed(5)
    form.location.useCurrentPosition = true
  })
}
const onQuizDone = () => {
  quizOpen.value = false
  applyTbtiToForm(form)
}
const submit = async () => {
  if (submitting.value) return
  submitting.value = true
  errorMsg.value = ''
  try {
    await postRecommendations(form)
    router.push('/plan/results')
  } catch (err) {
    errorMsg.value = err.message || '推荐生成失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="screen">
    <HudNav />

    <div class="home-body">
      <!-- NEON hero：问候 + 天气 + 像素山 -->
      <section class="hero">
        <div class="h-titles">
          <div class="h-neon">NEON</div>
          <h1 class="h-title">来都来了，徒步吗？;)</h1>
          <div class="h-sub">一径入云深，与世界重联 · ONE TRAIL INTO THE CLOUDS</div>
          <div v-if="weatherText" class="h-weather">{{ weatherText }}</div>
        </div>
        <svg class="mtn" viewBox="0 0 420 210" preserveAspectRatio="none">
          <path d="M0 210 V168 H36 V132 H72 V156 H108 V108 H144 V132 H188 V84 H232 V116 H276 V60 H320 V96 H356 V44 H392 V88 H420 V210 Z"
                fill="#141414" stroke="#A3E635" stroke-width="3"/>
          <rect x="62" y="14" width="32" height="32" fill="#FFD028"/>
          <rect x="178" y="22" width="14" height="14" fill="#FFF"/><rect x="200" y="44" width="14" height="14" fill="#FFF"/>
          <rect x="238" y="8" width="14" height="14" fill="#FFF"/>
          <rect x="266" y="131" width="35" height="14" fill="#A3E635"/><rect x="352" y="95" width="35" height="14" fill="#A3E635"/>
        </svg>
      </section>

      <div class="flow">
        <!-- TBTI 测评卡：未测 = 引导，已测 = 人格展示 -->
        <section class="tbti-card">
          <div class="tc-text">
            <div class="tc-title">{{ tbtiResult ? `我的TBTI · ${tbtiResult.name}` : '测测我的TBTI' }}</div>
            <div class="tc-sub">{{ tbtiResult ? `${tbtiResult.type} · ${tbtiResult.desc}` : '以便我们更好的推荐' }}</div>
          </div>
          <button class="tc-btn" @click="quizOpen = true">{{ tbtiResult ? '重测' : '开始测试' }}</button>
        </section>

        <!-- 大标题 -->
        <section class="w-title">
          <div class="w-cn">你想去哪？</div>
          <div class="w-en">WHERE DO YOU WANT TO GO?</div>
        </section>

        <!-- 需求表单卡 -->
        <section class="form">
          <div class="pack-tabs">
            <button class="pt" :class="{ on: packMode === 'light' }" @click="setPack('light')">轻装徒步</button>
            <button class="pt" :class="{ on: packMode === 'heavy' }" @click="setPack('heavy')">重装徒步</button>
          </div>

          <div class="loc-bar">
            <span class="lb-text">⌖ 已定位到 {{ form.location.city }} · {{ form.location.lat.toFixed(2) }}, {{ form.location.lng.toFixed(2) }}</span>
            <button class="lb-btn" @click="locate">重新定位</button>
          </div>

          <div class="grid2">
            <div class="cell">
              <div class="c-lb">我的位置</div>
              <input v-model="form.location.city" class="c-in" @input="form.location.useCurrentPosition = false" />
            </div>
            <div class="cell">
              <div class="c-lb">难度 · LEVEL</div>
              <select v-model.number="form.fitnessLevel" class="c-in">
                <option v-for="n in 5" :key="n" :value="n">Lv.{{ n }}</option>
              </select>
            </div>
            <div class="cell">
              <div class="c-lb">出行日期</div>
              <input type="date" v-model="form.dateRange.start" class="c-in" :min="forecastMin" :max="forecastMax" />
            </div>
            <div class="cell">
              <div class="c-lb">同行人数</div>
              <input type="number" min="1" v-model.number="form.party.adults" class="c-in" />
            </div>
          </div>

          <button class="prefs-row" @click="prefsOpen = true">
            <span>预算 / 体能 / 装备</span>
            <span class="pr-val">¥{{ form.budgetPerPerson.max }} / 人 · Lv.{{ form.fitnessLevel }} · 装备 {{ form.ownedGear.length }} 件 ›</span>
          </button>

          <div class="chips">
            <button v-for="t in interestOptions" :key="t" class="i-chip"
                    :class="{ on: form.interests.includes(t) }" @click="toggle(t)">{{ t }}</button>
          </div>

          <div v-if="errorMsg" class="q-error">{{ errorMsg }}</div>
          <button class="cta" :disabled="submitting" @click="submit">
            <span class="cta-cn">{{ submitting ? '生成中…' : '开始生成路线' }}</span>
            <span class="cta-en">PRESS START</span>
          </button>
        </section>

        <!-- 我的行程预览 -->
        <section class="trip-sec">
          <div class="ts-head">
            <span class="ts-title">我的行程</span>
            <button class="ts-all" @click="$router.push('/trip/current')">全部 ›</button>
          </div>
          <div v-if="tripPreview.length" class="ts-card" @click="$router.push('/trip/current')">
            <div class="ts-label">时间安排 · TIMELINE</div>
            <div v-for="t in tripPreview" :key="t.time" class="ts-row">
              <span class="ts-time">{{ t.time }}</span>
              <span class="ts-event">{{ t.event }}</span>
            </div>
          </div>
          <div v-else class="ts-empty">还没有行程，生成推荐后这里会出现你的时间安排</div>
        </section>
      </div>
    </div>
    <TbtiQuiz v-if="quizOpen" @close="quizOpen = false" @done="onQuizDone" />
    <PrefsSheet v-if="prefsOpen" :form="form" @close="prefsOpen = false" />
  </section>
</template>

<style scoped>
.home-body {
  min-height: calc(100vh - var(--nav-h));
  padding: 32px var(--content-px) 48px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* NEON hero */
.hero { display: flex; align-items: flex-end; justify-content: space-between; gap: 24px; }
.h-titles { display: flex; flex-direction: column; gap: 8px; min-width: 0; }
.h-neon { font-family: var(--vt); font-size: 34px; color: var(--lime); line-height: 1; }
.h-title { font-size: 32px; font-weight: 900; color: #FFF; }
.h-sub { font-size: 12px; color: var(--t2); }
.h-weather { font-size: 12px; color: var(--t2); margin-top: 4px; }
.mtn { width: 320px; height: 160px; flex: none; }

/* 主流程单栏居中 */
.flow { width: min(680px, 100%); display: flex; flex-direction: column; gap: 24px; }

/* TBTI 测评卡（白卡） */
.tbti-card {
  background: #FFF; border: 2px solid var(--ink); box-shadow: var(--sh-lime-6);
  padding: 18px 22px; display: flex; align-items: center; gap: 16px;
}
.tc-text { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px; }
.tc-title { font-size: 17px; font-weight: 900; color: var(--ink); }
.tc-sub { font-size: 12px; color: var(--t3); }
.tc-btn {
  flex: none; height: 42px; padding: 0 20px; cursor: pointer;
  background: var(--lime); border: 2px solid var(--ink);
  font-size: 14px; font-weight: 700; color: var(--ink);
}

/* 大标题 */
.w-title { display: flex; flex-direction: column; gap: 6px; }
.w-cn { font-size: 36px; font-weight: 900; color: #FFF; }
.w-en { font-family: var(--p8); font-size: 12px; color: var(--lime); }

/* 表单卡 */
.form {
  background: #FFF; border: 2px solid var(--ink); box-shadow: var(--sh-lime-6);
  display: flex; flex-direction: column;
}
.pack-tabs { display: flex; }
.pt {
  flex: 1; padding: 16px; cursor: pointer;
  background: #161616; color: #FFF; font-size: 15px; font-weight: 700;
  border: none; border-bottom: 2px solid var(--ink);
}
.pt.on { background: #FFF; color: var(--lime); }
.loc-bar {
  background: #161616; color: var(--t1);
  display: flex; align-items: center; justify-content: space-between; gap: 8px;
  padding: 10px 18px; font-size: 11px;
}
.lb-text { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.lb-btn { flex: none; background: none; border: none; color: var(--lime); font-size: 11px; font-weight: 700; cursor: pointer; padding: 0; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; }
.cell {
  padding: 14px 18px; border-bottom: 1px solid #D8D8D0;
  display: flex; flex-direction: column; gap: 6px;
}
.cell:nth-child(odd) { border-right: 1px solid #D8D8D0; }
.c-lb { font-size: 11px; color: var(--t3); }
.c-in {
  border: none; background: none; padding: 0;
  font-size: 15px; font-weight: 700; color: var(--ink); width: 100%;
}
.c-in:focus { outline: none; }
.prefs-row {
  display: flex; align-items: center; justify-content: space-between; gap: 8px;
  padding: 14px 18px; background: none; border: none; border-bottom: 1px solid #D8D8D0;
  cursor: pointer; font-size: 13px; font-weight: 700; color: var(--ink); width: 100%;
}
.pr-val { color: var(--t3); font-size: 12px; }
.chips { display: flex; gap: 10px; padding: 14px 18px; }
.i-chip { font-size: 12px; font-weight: 500; padding: 6px 12px; background: #FFF; border: 1px solid var(--ink); color: var(--ink); cursor: pointer; }
.i-chip.on { background: var(--ink); color: var(--lime); font-weight: 700; }
.q-error { margin: 0 18px; font-size: 12px; font-weight: 500; color: var(--red); }
.cta {
  margin: 6px 18px 18px; height: 64px; cursor: pointer;
  background: var(--lime); border: 2px solid var(--ink); box-shadow: var(--sh-ink-4);
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px;
}
.cta-cn { font-size: 20px; font-weight: 900; color: var(--ink); }
.cta-en { font-family: var(--p8); font-size: 10px; color: var(--ink); }
.cta:active { transform: translate(2px, 2px); box-shadow: 2px 2px 0 #0A0A0A; }
.cta:disabled { opacity: 0.6; cursor: wait; }

/* 我的行程预览 */
.trip-sec { display: flex; flex-direction: column; gap: 12px; }
.ts-head { display: flex; align-items: baseline; justify-content: space-between; }
.ts-title { font-size: 20px; font-weight: 900; color: #FFF; }
.ts-all { background: none; border: none; color: var(--t2); font-size: 12px; cursor: pointer; padding: 0; }
.ts-card {
  background: var(--panel); border: 1px solid var(--line); cursor: pointer;
  padding: 16px 20px; display: flex; flex-direction: column; gap: 10px;
}
.ts-card:hover { border-color: var(--lime); }
.ts-label { font-size: 13px; font-weight: 700; color: #FFF; }
.ts-row { display: flex; gap: 12px; align-items: baseline; }
.ts-time { font-family: var(--vt); font-size: 16px; color: var(--lime); width: 56px; flex: none; }
.ts-event { font-size: 13px; color: var(--t1); }
.ts-empty { font-size: 12px; color: var(--t3); }

/* 窄屏：像素山让位 */
@media (max-width: 900px) {
  .mtn { display: none; }
}

/* 桌面端：整体纵向拉长、加大呼吸感，消除大片空白 */
@media (min-width: 901px) {
  .home-body { gap: 44px; padding: 56px var(--content-px) 72px; }
  .flow { width: min(760px, 100%); gap: 36px; }
  .h-neon { font-size: 44px; }
  .h-title { font-size: 40px; }
  .h-sub { font-size: 14px; }
  .h-weather { font-size: 13px; }
  .mtn { width: 400px; height: 200px; }
  .tbti-card { padding: 26px 30px; }
  .tc-title { font-size: 19px; }
  .tc-sub { font-size: 13px; }
  .tc-btn { height: 48px; padding: 0 26px; font-size: 15px; }
  .w-cn { font-size: 46px; }
  .w-en { font-size: 13px; }
  .pt { padding: 20px; font-size: 16px; }
  .loc-bar { padding: 13px 22px; font-size: 12px; }
  .cell { padding: 20px 24px; gap: 8px; }
  .c-in { font-size: 16px; }
  .prefs-row { padding: 18px 24px; font-size: 14px; }
  .chips { padding: 18px 24px; }
  .i-chip { font-size: 13px; padding: 8px 14px; }
  .cta { height: 76px; margin: 8px 22px 22px; }
  .cta-cn { font-size: 22px; }
  .trip-sec { gap: 16px; }
  .ts-title { font-size: 22px; }
  .ts-card { padding: 22px 26px; gap: 12px; }
  .ts-label { font-size: 15px; }
  .ts-time { font-size: 18px; }
  .ts-event { font-size: 14px; }
}
</style>
