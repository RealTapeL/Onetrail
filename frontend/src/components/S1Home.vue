<script setup>
/** S1 首页 · 需求输入（桌面端，对齐设计稿 2:2）
 *  表单为真实控件，提交走真实后端 POST /api/v1/recommendations/plan
 */
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import HudNav from './HudNav.vue'
import { fetchBrandStats, postRecommendations } from '../api/index'
import { questFormDefaults } from '../api/index'

const router = useRouter()
const form = reactive(JSON.parse(JSON.stringify(questFormDefaults)))
const brandStats = ref([])
const submitting = ref(false)
const errorMsg = ref('')

onMounted(async () => {
  try {
    brandStats.value = await fetchBrandStats()
  } catch { /* 后端未启动时保留空 */ }
})

const questions = [
  { no: 'Q1', text: '这条路适不适合我？' },
  { no: 'Q2', text: '这条路值不值得去？' },
  { no: 'Q3', text: '怎么去、怎么走、带什么？' }
]
const interestOptions = ['瀑布', '竹林', '古道', '云海']
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
          <div v-for="s in brandStats" :key="s.label" class="bs">
            <div class="bs-num">{{ s.num }}</div>
            <div class="bs-label">{{ s.label }}</div>
          </div>
        </div>
      </div>

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

    <div class="quest">
      <div class="q-head">
        <div class="q-titles">
          <div class="q-cn">「01」需求输入</div>
          <div class="q-en">QUEST INPUT — TELL US YOUR PLAN</div>
        </div>
        <div class="q-hint">要做什么：收集推荐所需条件，降低决策成本</div>
      </div>

      <div class="q-grid">
        <div class="field">
          <div class="f-label">出行日期 · DATE</div>
          <input type="date" v-model="form.dateRange.start" class="f-input" />
        </div>
        <div class="field">
          <div class="f-label">目的地 · LOCATION</div>
          <div class="f-row">
            <input v-model="form.location.city" class="f-input" placeholder="城市" />
            <button class="locate" @click="locate">定位</button>
          </div>
          <div class="f-row">
            <input v-model.number="form.location.lat" class="f-input half" />
            <input v-model.number="form.location.lng" class="f-input half" />
          </div>
        </div>
        <div class="field">
          <div class="f-label">同行人数 · PARTY</div>
          <input type="number" min="1" v-model.number="form.party.adults" class="f-input" />
        </div>
        <div class="field">
          <div class="f-label">预算 · BUDGET（元/人）</div>
          <input type="number" v-model.number="form.budgetPerPerson.max" class="f-input" />
        </div>
      </div>
      <div class="q-grid">
        <div class="field">
          <div class="f-label">体能 · FITNESS</div>
          <select v-model.number="form.fitnessLevel" class="f-input">
            <option v-for="n in 5" :key="n" :value="n">Lv.{{ n }}</option>
          </select>
        </div>
        <div class="field">
          <div class="f-label">兴趣 · INTERESTS</div>
          <div class="f-chips">
            <button v-for="t in interestOptions" :key="t" class="i-chip"
                    :class="{ on: form.interests.includes(t) }" @click="toggle(t)">{{ t }}</button>
          </div>
        </div>
        <div class="field">
          <div class="f-label">已有装备 · MY GEAR</div>
          <input :value="form.ownedGear.join(' · ')" class="f-input"
                 @input="form.ownedGear = $event.target.value.split(/[·,，、\s]+/).filter(Boolean)" />
        </div>
        <button class="cta" :disabled="submitting" @click="submit">
          <span class="cta-cn">{{ submitting ? '生成中…' : '开始生成路线' }}</span>
          <span class="cta-en">PRESS START</span>
        </button>
      </div>
      <div v-if="errorMsg" class="q-error">{{ errorMsg }}</div>
    </div>
  </section>
</template>

<style scoped>
.hero { height: 490px; padding: 40px 48px 32px; display: flex; align-items: center; gap: 40px; }
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
.q-chip { display: inline-flex; align-items: center; gap: 8px; background: var(--panel); border: 1px solid var(--lime); padding: 9px 14px; }
.q-no { font-family: var(--silk); font-weight: 700; font-size: 11px; color: var(--lime); }
.q-tx { font-size: 13px; font-weight: 500; color: var(--t1); }

.bstats { display: flex; gap: 36px; }
.bs { display: flex; flex-direction: column; gap: 4px; }
.bs-num { font-family: var(--vt); font-size: 28px; color: var(--lime); line-height: 1; }
.bs-label { font-size: 12px; color: var(--t2); }

.pixel-art { position: relative; width: 420px; height: 280px; flex: none; }
.px { position: absolute; width: 14px; height: 14px; background: #FFFFFF; }
.px.amber { background: var(--amber); }
.px.lime-w { width: 35px; height: 14px; background: var(--lime); }
.mtn { position: absolute; left: 0; bottom: 0; width: 420px; height: 210px; }

.quest { height: 351px; background: #FFFFFF; padding: 40px; display: flex; flex-direction: column; gap: 24px; }
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
  padding: 14px 14px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 86px;
}
.f-label { font-size: 12px; font-weight: 500; color: var(--t3); }
.f-input {
  font-size: 15px; font-weight: 700; color: var(--ink);
  border: 1px solid #D8D8D0; background: #FFFFFF;
  padding: 6px 8px; width: 100%;
}
.f-input:focus { outline: none; border-color: var(--ink); }
.f-input.half { width: 48%; }
.f-row { display: flex; align-items: center; gap: 8px; }
.f-row .f-input { flex: 1; }
.locate {
  flex: none; background: var(--ink); color: var(--lime);
  font-size: 12px; font-weight: 700; padding: 7px 12px;
}
.f-chips { display: flex; gap: 8px; }
.i-chip { font-size: 12px; font-weight: 500; color: var(--ink); background: #FFFFFF; border: 1px solid var(--ink); padding: 5px 10px; }
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
.cta:disabled { opacity: 0.6; cursor: wait; }
.q-error {
  background: var(--red-bg);
  border: 1px solid var(--red-line);
  color: var(--red);
  font-size: 13px;
  padding: 10px 14px;
}
.quest { height: auto; min-height: 351px; }
</style>
