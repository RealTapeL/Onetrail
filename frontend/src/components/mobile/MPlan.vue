<script setup>
/** M1 规划 · 需求输入（移动端 Tab 1，对齐设计稿 6:21）
 *  提交后调用真实后端 POST /api/v1/recommendations/plan
 */
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import MHeader from './MHeader.vue'
import TabBar from './TabBar.vue'
import { postRecommendations, questFormDefaults } from '../../api/index'

const router = useRouter()
const form = reactive(JSON.parse(JSON.stringify(questFormDefaults)))
const interestOptions = ['瀑布', '竹林', '古道', '云海']
const submitting = ref(false)
const errorMsg = ref('')
const toggle = (tag) => {
  const i = form.interests.indexOf(tag)
  i >= 0 ? form.interests.splice(i, 1) : form.interests.push(tag)
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

      <section class="form">
        <div class="f-head">
          <div class="f-cn">「01」需求输入</div>
          <div class="f-en">QUEST INPUT — TELL US YOUR PLAN</div>
        </div>

        <div class="sec-label"><span class="sec-cn">必填</span><span class="sec-line" /></div>
        <div class="row"><span class="lb">出行日期 · DATE</span>
          <span class="ctl"><input type="date" v-model="form.dateRange.start" class="in" /></span></div>
        <div class="row"><span class="lb">目的地 · LOCATION</span>
          <span class="ctl"><input v-model="form.location.city" class="in" /></span></div>
        <div class="row"><span class="lb">同行人数 · PARTY</span>
          <span class="ctl"><input type="number" min="1" v-model.number="form.party.adults" class="in" /> 人</span></div>
        <div class="row"><span class="lb">预算 · BUDGET（元/人）</span>
          <span class="ctl">¥<input type="number" v-model.number="form.budgetPerPerson.max" class="in" /></span></div>

        <div class="sec-label"><span class="sec-cn">选填</span><span class="sec-line" /></div>
        <div class="row"><span class="lb">体能 · FITNESS</span>
          <span class="ctl"><select v-model.number="form.fitnessLevel" class="in">
            <option v-for="n in 5" :key="n" :value="n">Lv.{{ n }}</option>
          </select></span></div>
        <div class="row"><span class="lb">已有装备 · MY GEAR</span>
          <span class="ctl"><input :value="form.ownedGear.join(' · ')" class="in"
            @input="form.ownedGear = $event.target.value.split(/[·,，、\s]+/).filter(Boolean)" /></span></div>
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

.form {
  background: #FFF; border: 2px solid var(--ink); box-shadow: var(--sh-ink-3);
  padding: 16px; display: flex; flex-direction: column; gap: 12px;
}
.f-head { display: flex; flex-direction: column; gap: 4px; }
.f-cn { font-size: 18px; font-weight: 900; color: var(--ink); }
.f-en { font-family: var(--silk); font-size: 8px; color: var(--t3); }
.sec-label { display: flex; align-items: center; gap: 8px; margin-top: 2px; }
.sec-cn { font-size: 11px; font-weight: 900; color: var(--ink); }
.sec-line { flex: 1; height: 1px; background: #D8D8D0; }
.row { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.lb { font-size: 10px; font-weight: 500; color: var(--t3); flex: none; }
.ctl { flex: 1 1 auto; min-width: 0; display: flex; align-items: center; justify-content: flex-end; gap: 4px; font-size: 13px; font-weight: 700; color: var(--ink); }
.in {
  width: 100%;
  max-width: 170px;
  min-width: 0;
  font-size: 13px; font-weight: 700; color: var(--ink);
  border: none; border-bottom: 1px solid #D8D8D0; background: none;
  text-align: right; padding: 2px 0;
}
.in:focus { outline: none; border-bottom-color: var(--ink); }
select.in { appearance: auto; }
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
