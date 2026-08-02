<script setup>
/** S1 首页 · 需求输入（桌面端）
 *  布局：左品牌区 / 右需求输入卡（左右分栏，表单首屏可见）
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

    <div class="home-body">
      <!-- 左：品牌区 -->
      <div class="brand">
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

        <!-- 品牌统计：小字随行展示（后端未启动时不占位） -->
        <div v-if="brandStats.length" class="bstats">
          <span v-for="s in brandStats" :key="s.label" class="bs"><b class="bs-num">{{ s.num }}</b>{{ s.label }}</span>
        </div>

        <div class="qs">
          <span v-for="q in questions" :key="q.no" class="q-chip">
            <span class="q-no">{{ q.no }}</span><span class="q-tx">{{ q.text }}</span>
          </span>
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

      <!-- 右：需求输入卡 -->
      <div class="quest">
        <div class="q-head">
          <div class="q-titles">
            <div class="q-cn">「01」需求输入</div>
            <div class="q-en">QUEST INPUT — TELL US YOUR PLAN</div>
          </div>
          <div class="q-hint">要做什么：收集推荐所需条件，降低决策成本</div>
        </div>

        <div class="sec-label"><span class="sec-cn">必填</span><span class="sec-en">REQUIRED</span><span class="sec-line" /></div>

        <div class="q-grid">
          <div class="field">
            <div class="f-label">出行日期 · DATE</div>
            <input type="date" v-model="form.dateRange.start" class="f-input" />
          </div>
          <div class="field">
            <div class="f-label">同行人数 · PARTY</div>
            <input type="number" min="1" v-model.number="form.party.adults" class="f-input" />
          </div>
          <div class="field span2">
            <div class="f-label">目的地 · LOCATION</div>
            <div class="f-row">
              <input v-model="form.location.city" class="f-input" placeholder="城市"
                     @input="form.location.useCurrentPosition = false" />
              <button class="locate" @click="locate">定位</button>
            </div>
            <div class="f-coord">坐标 {{ form.location.lat.toFixed(2) }}, {{ form.location.lng.toFixed(2) }} · 定位后自动填入</div>
          </div>
          <div class="field">
            <div class="f-label">预算 · BUDGET（元/人）</div>
            <input type="number" v-model.number="form.budgetPerPerson.max" class="f-input" />
          </div>
        </div>

        <div class="sec-label"><span class="sec-cn">选填</span><span class="sec-en">OPTIONAL</span><span class="sec-line" /></div>

        <div class="q-grid">
          <div class="field">
            <div class="f-label">体能 · FITNESS</div>
            <select v-model.number="form.fitnessLevel" class="f-input">
              <option v-for="n in 5" :key="n" :value="n">Lv.{{ n }}</option>
            </select>
          </div>
          <div class="field">
            <div class="f-label">已有装备 · MY GEAR</div>
            <input :value="form.ownedGear.join(' · ')" class="f-input"
                   @input="form.ownedGear = $event.target.value.split(/[·,，、\s]+/).filter(Boolean)" />
          </div>
          <div class="field span2">
            <div class="f-label">兴趣 · INTERESTS</div>
            <div class="f-chips">
              <button v-for="t in interestOptions" :key="t" class="i-chip"
                      :class="{ on: form.interests.includes(t) }" @click="toggle(t)">{{ t }}</button>
            </div>
          </div>
        </div>

        <button class="cta" :disabled="submitting" @click="submit">
          <span class="cta-cn">{{ submitting ? '生成中…' : '开始生成路线' }}</span>
          <span class="cta-en">PRESS START</span>
        </button>
        <div v-if="errorMsg" class="q-error">{{ errorMsg }}</div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.home-body {
  height: calc(960px - var(--nav-h));
  padding: 32px var(--content-px) 36px;
  display: flex;
  gap: 40px;
}

/* ---- 左：品牌区 ---- */
.brand { width: 508px; flex: none; display: flex; flex-direction: column; gap: 18px; }
.kicker { display: flex; align-items: center; gap: 10px; }
.k-sq { width: 10px; height: 10px; background: var(--lime); }
.k-en { font-family: var(--silk); font-size: 12px; color: var(--lime); }
.h-title { font-size: 52px; font-weight: 900; color: #FFFFFF; line-height: 1.15; }
.h-title-en { font-family: var(--p8); font-size: 15px; color: var(--lime); }
.h-sub { font-size: 14px; color: var(--t2); line-height: 24px; }

.slogan { display: flex; align-items: center; gap: 14px; }
.slogan-bar { width: 4px; height: 44px; background: var(--lime); flex: none; }
.slogan-g { display: flex; flex-direction: column; gap: 6px; }
.slogan-cn { font-size: 24px; font-weight: 900; color: #FFFFFF; }
.slogan-en { font-family: var(--silk); font-size: 10px; color: var(--lime); }

/* 品牌统计：小字随行展示 */
.bstats { display: flex; align-items: baseline; gap: 18px; font-size: 12px; color: var(--t2); }
.bs { display: inline-flex; align-items: baseline; gap: 5px; white-space: nowrap; }
.bs-num { font-family: var(--vt); font-size: 20px; color: var(--lime); line-height: 1; }

.qs { display: flex; flex-direction: column; gap: 10px; }
.q-chip { display: inline-flex; align-items: center; gap: 8px; background: var(--panel); border: 1px solid var(--lime); padding: 8px 12px; }
.q-no { font-family: var(--silk); font-weight: 700; font-size: 11px; color: var(--lime); }
.q-tx { font-size: 13px; font-weight: 500; color: var(--t1); }

.pixel-art { position: relative; width: 420px; height: 240px; flex: none; margin-top: auto; }
.px { position: absolute; width: 14px; height: 14px; background: #FFFFFF; }
.px.amber { background: var(--amber); }
.px.lime-w { width: 35px; height: 14px; background: var(--lime); }
.mtn { position: absolute; left: 0; bottom: 0; width: 420px; height: 210px; }

/* ---- 右：需求输入卡 ---- */
.quest {
  flex: 1;
  background: #FFFFFF;
  padding: 28px 32px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.q-head { display: flex; align-items: center; justify-content: space-between; }
.q-titles { display: flex; flex-direction: column; gap: 6px; }
.q-cn { font-size: 24px; font-weight: 900; color: var(--ink); }
.q-en { font-family: var(--silk); font-size: 11px; color: var(--t3); }
.q-hint { font-size: 13px; color: var(--t3); }

/* 分组分隔标题 */
.sec-label { display: flex; align-items: center; gap: 8px; }
.sec-cn { font-size: 13px; font-weight: 900; color: var(--ink); }
.sec-en { font-family: var(--silk); font-size: 9px; color: var(--t3); }
.sec-line { flex: 1; height: 1px; background: #D8D8D0; }

.q-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
.field {
  background: var(--paper);
  border: 1px solid var(--ink);
  box-shadow: var(--sh-ink-3);
  padding: 12px 14px 11px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.field.span2 { grid-column: span 2; }
.f-label { font-size: 12px; font-weight: 500; color: var(--t3); }
.f-input {
  font-size: 15px; font-weight: 700; color: var(--ink);
  border: 1px solid #D8D8D0; background: #FFFFFF;
  padding: 6px 8px; width: 100%;
}
.f-input:focus { outline: none; border-color: var(--ink); }
.f-row { display: flex; align-items: center; gap: 8px; }
.f-row .f-input { flex: 1; }
.f-coord { font-size: 11px; color: var(--t3); }
.locate {
  flex: none; background: var(--ink); color: var(--lime);
  font-size: 12px; font-weight: 700; padding: 7px 12px;
}
.f-chips { display: flex; gap: 8px; }
.i-chip { font-size: 12px; font-weight: 500; color: var(--ink); background: #FFFFFF; border: 1px solid var(--ink); padding: 5px 10px; }
.i-chip.on { background: var(--ink); color: var(--lime); font-weight: 700; border-color: var(--ink); }

/* CTA：独占整行横贯表单底部 */
.cta {
  margin-top: auto;
  width: 100%;
  height: 72px;
  flex: none;
  background: var(--lime);
  border: 2px solid var(--ink);
  box-shadow: var(--sh-ink-4);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.cta-cn { font-size: 22px; font-weight: 900; color: var(--ink); }
.cta-en { font-family: var(--p8); font-size: 11px; color: var(--ink); }
.cta:active { transform: translate(2px, 2px); box-shadow: 2px 2px 0 #0A0A0A; }
.cta:disabled { opacity: 0.6; cursor: wait; }
.q-error {
  background: var(--red-bg);
  border: 1px solid var(--red-line);
  color: var(--red);
  font-size: 13px;
  padding: 10px 14px;
}
</style>
