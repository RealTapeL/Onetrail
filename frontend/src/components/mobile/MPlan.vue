<script setup>
/** M1 规划 · 需求输入（移动端 Tab 1）
 *  分块入口（TBTI 测评/路线库/行程/装备）+ 需求表单 + 携程式预算/体能/装备弹层
 *  提交后调用真实后端 POST /api/v1/recommendations/plan
 */
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import MHeader from './MHeader.vue'
import TabBar from './TabBar.vue'
import TbtiQuiz from '../TbtiQuiz.vue'
import PrefsSheet from '../PrefsSheet.vue'
import { postRecommendations, questFormDefaults, FORECAST_MIN_DATE, FORECAST_MAX_DATE } from '../../api/index'
import { applyTbtiToForm, tbtiResult } from '../../composables/tbti'

const forecastMin = FORECAST_MIN_DATE
const forecastMax = FORECAST_MAX_DATE

const router = useRouter()
const form = reactive(JSON.parse(JSON.stringify(questFormDefaults)))
const interestOptions = ['瀑布', '竹林', '古道', '云海']
const submitting = ref(false)
const errorMsg = ref('')
const quizOpen = ref(false)
const prefsOpen = ref(false)

onMounted(() => applyTbtiToForm(form))

const toggle = (tag) => {
  const i = form.interests.indexOf(tag)
  i >= 0 ? form.interests.splice(i, 1) : form.interests.push(tag)
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
  } catch (e) {
    errorMsg.value = e?.message || '生成失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="m-screen">
    <MHeader />
    <div class="m-body">
      <section class="hero">
        <div class="kicker"><span class="k-sq" /><span class="k-en">HIKING ROUTE DECISION ENGINE</span></div>
        <div class="h-row">
          <div class="h-titles">
            <h1 class="h-title">你想去哪？</h1>
            <div class="h-en">WHERE DO YOU WANT TO GO?</div>
          </div>
          <svg class="mtn" viewBox="0 0 343 120" preserveAspectRatio="xMidYMax meet">
            <path d="M0 120 V96 H29 V75 H59 V89 H88 V62 H117 V75 H153 V48 H190 V66 H225 V34 H261 V55 H291 V25 H320 V50 H343 V120 Z"
                  fill="#141414" stroke="#A3E635" stroke-width="2"/>
            <rect x="50" y="6" width="20" height="20" fill="#FFD028"/>
            <rect x="145" y="12" width="10" height="10" fill="#FFF"/><rect x="163" y="26" width="10" height="10" fill="#FFF"/>
            <rect x="194" y="4" width="10" height="10" fill="#FFF"/>
            <rect x="232" y="25" width="22" height="9" fill="#A3E635"/><rect x="299" y="16" width="22" height="9" fill="#A3E635"/>
          </svg>
        </div>
        <div class="slogan">
          <span class="s-bar" />
          <div>
            <div class="s-cn">一径入云深，与世界重联</div>
            <div class="s-en">ONE TRAIL INTO THE CLOUDS, RECONNECT WITH THE WORLD</div>
          </div>
        </div>
      </section>

      <!-- 分块入口（豆瓣式）：TBTI 测评为核心入口，已测显示人格 -->
      <section class="entries">
        <button class="entry" @click="quizOpen = true">
          <div class="e-main tbti">
            <template v-if="tbtiResult">{{ tbtiResult.type }}</template>
            <template v-else>TBTI</template>
          </div>
          <div class="e-label">{{ tbtiResult ? `${tbtiResult.name} · 重测` : '测测我的TBTI' }}</div>
        </button>
        <button class="entry" @click="$router.push('/routes')">
          <div class="e-main">路线</div>
          <div class="e-label">路线库</div>
        </button>
        <button class="entry" @click="$router.push('/trip/current')">
          <div class="e-main">行程</div>
          <div class="e-label">我的行程</div>
        </button>
        <button class="entry" @click="$router.push('/gear')">
          <div class="e-main">装备</div>
          <div class="e-label">装备比选</div>
        </button>
      </section>

      <section class="form">
        <div class="f-head">
          <div class="f-cn">「01」需求输入</div>
          <div class="f-en">QUEST INPUT — TELL US YOUR PLAN</div>
        </div>

        <div class="row"><span class="lb">出行日期 · DATE</span>
          <span class="ctl"><input type="date" v-model="form.dateRange.start" class="in"
                 :min="forecastMin" :max="forecastMax" /></span></div>
        <div class="row"><span class="lb">目的地 · LOCATION</span>
          <span class="ctl"><input v-model="form.location.city" class="in" @input="form.location.useCurrentPosition = false" /></span></div>
        <div class="row"><span class="lb">同行人数 · PARTY</span>
          <span class="ctl"><input type="number" min="1" v-model.number="form.party.adults" class="in" /> 人</span></div>

        <!-- 预算/体能/装备：摘要行，点开底部弹层 -->
        <button class="row prefs-row" @click="prefsOpen = true">
          <span class="lb">预算 / 体能 / 装备</span>
          <span class="ctl prefs-val">
            ¥{{ form.budgetPerPerson.max }} · Lv.{{ form.fitnessLevel }} · {{ form.ownedGear.length }}件
            <span class="prefs-arrow">›</span>
          </span>
        </button>

        <div class="row"><span class="lb">兴趣 · INTERESTS</span>
          <span class="ctl chips">
            <button v-for="t in interestOptions" :key="t" class="i-chip"
                    :class="{ on: form.interests.includes(t) }" @click="toggle(t)">{{ t }}</button>
          </span></div>

        <div v-if="errorMsg" class="q-error">{{ errorMsg }}</div>
        <button class="cta" :disabled="submitting" @click="submit">
          <span class="cta-cn">{{ submitting ? '生成中…' : '开始生成路线' }}</span>
          <span class="cta-en">PRESS START</span>
        </button>
      </section>
    </div>
    <TabBar />
    <TbtiQuiz v-if="quizOpen" @close="quizOpen = false" @done="onQuizDone" />
    <PrefsSheet v-if="prefsOpen" :form="form" @close="prefsOpen = false" />
  </div>
</template>

<style scoped>
.hero { display: flex; flex-direction: column; gap: 8px; }
.kicker { display: flex; align-items: center; gap: 6px; }
.k-sq { width: 8px; height: 8px; background: var(--lime); }
.k-en { font-family: var(--silk); font-size: 9px; color: var(--lime); }
.h-row { display: flex; align-items: flex-end; justify-content: space-between; gap: 10px; }
.h-titles { display: flex; flex-direction: column; gap: 4px; }
.h-title { font-size: 26px; font-weight: 900; color: #FFF; }
.h-en { font-family: var(--p8); font-size: 8px; color: var(--lime); }
.mtn { width: 150px; height: 52px; flex: none; }
.slogan { display: flex; align-items: center; gap: 10px; }
.s-bar { width: 3px; height: 30px; background: var(--lime); flex: none; }
.s-cn { font-size: 14px; font-weight: 900; color: #FFF; }
.s-en { font-family: var(--silk); font-size: 7px; color: var(--lime); margin-top: 3px; }

/* 分块入口 */
.entries { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.entry {
  background: var(--panel); border: 1px solid var(--line);
  padding: 12px 4px 10px; cursor: pointer;
  display: flex; flex-direction: column; align-items: center; gap: 6px;
}
.entry:active { border-color: var(--lime); }
.e-main { font-family: var(--vt); font-size: 15px; color: #FFF; }
.e-main.tbti { color: var(--lime); }
.e-label { font-size: 10px; color: var(--t2); white-space: nowrap; }

.form {
  background: #FFF; border: 2px solid var(--ink); box-shadow: var(--sh-ink-3);
  padding: 16px; display: flex; flex-direction: column; gap: 12px;
}
.f-head { display: flex; flex-direction: column; gap: 4px; }
.f-cn { font-size: 18px; font-weight: 900; color: var(--ink); }
.f-en { font-family: var(--silk); font-size: 8px; color: var(--t3); }
.row { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.lb { font-size: 10px; font-weight: 500; color: var(--t3); flex: none; }
.ctl { flex: 1 1 auto; min-width: 0; display: flex; align-items: center; justify-content: flex-end; gap: 4px; font-size: 13px; font-weight: 700; color: var(--ink); }
.in {
  width: 100%;
  max-width: 220px;
  min-width: 0;
  font-size: 13px; font-weight: 700; color: var(--ink);
  border: none; border-bottom: 1px solid #D8D8D0; background: none;
  text-align: right; padding: 2px 0;
}
.in:focus { outline: none; border-bottom-color: var(--ink); }
.prefs-row { background: none; border: none; padding: 0; cursor: pointer; width: 100%; }
.prefs-val { color: var(--ink); }
.prefs-arrow { color: var(--t3); font-size: 15px; }
.chips { gap: 6px; }
.i-chip {
  font-size: 10px; font-weight: 500; padding: 3px 8px;
  background: #FFF; border: 1px solid var(--ink); color: var(--ink);
}
.i-chip.on { background: var(--ink); color: var(--lime); font-weight: 700; }
.cta {
  margin-top: 4px; height: 48px;
  background: var(--lime); border: 2px solid var(--ink); box-shadow: var(--sh-ink-3);
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px;
}
.cta-cn { font-size: 15px; font-weight: 900; color: var(--ink); }
.cta-en { font-family: var(--p8); font-size: 7px; color: var(--ink); }
.cta:disabled { opacity: 0.6; }
.q-error { font-size: 10px; font-weight: 500; color: var(--red); }
</style>
