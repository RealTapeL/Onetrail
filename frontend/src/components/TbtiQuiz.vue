<script setup>
/** TBTI 徒步者人格测评弹窗：8 题二选一 → 梗人格判型
 *  双端共用；移动端贴底、桌面端居中
 */
import { computed, ref } from 'vue'
import { TBTI_QUESTIONS, computeTbti, tbtiResult } from '../composables/tbti'

const emit = defineEmits(['close', 'done'])

const step = ref(0)
const answers = ref([])
const finished = ref(!!tbtiResult.value)
const result = ref(tbtiResult.value)

const current = computed(() => TBTI_QUESTIONS[step.value])
const progress = computed(() => `${Math.min(step.value + 1, TBTI_QUESTIONS.length)}/${TBTI_QUESTIONS.length}`)

const pick = (optIndex) => {
  answers.value[step.value] = optIndex
  if (step.value + 1 < TBTI_QUESTIONS.length) {
    step.value += 1
  } else {
    result.value = computeTbti(answers.value)
    finished.value = true
  }
}

const restart = () => {
  answers.value = []
  step.value = 0
  finished.value = false
}

/** 结果卡图片：/public/tbti/<CODE>.png（'GAI!' 文件名去掉感叹号） */
const cardSrc = computed(() =>
  result.value ? `/tbti/${result.value.type.replace('!', '')}.png` : ''
)
</script>

<template>
  <div class="tb-overlay" @click.self="emit('close')">
    <div class="tb-panel" role="dialog" aria-label="TBTI 徒步者人格测评">
      <button class="tb-close" aria-label="关闭" @click="emit('close')">✕</button>

      <!-- 结果页 -->
      <template v-if="finished && result">
        <div class="tb-kicker">你的人格类型是：</div>
        <img class="tb-card" :src="cardSrc" :alt="`${result.name}人格卡`">
        <div class="tb-name">{{ result.name }}</div>
        <div class="tb-type">{{ result.type }}</div>
        <div class="tb-desc">{{ result.desc }}</div>
        <div class="tb-foot">
          <button class="tb-ghost" @click="restart">重新测</button>
          <button class="tb-main" @click="emit('done', result)">完成 · 按画像推荐</button>
        </div>
      </template>

      <!-- 答题页 -->
      <template v-else>
        <div class="tb-kicker">TBTI · 徒步者人格测评 <span class="tb-prog">{{ progress }}</span></div>
        <div class="tb-track">
          <div class="tb-fill" :style="{ width: (step / TBTI_QUESTIONS.length) * 100 + '%' }" />
        </div>
        <div class="tb-q">{{ current.q }}</div>
        <button class="tb-opt" @click="pick(0)">{{ current.a.text }}</button>
        <button class="tb-opt" @click="pick(1)">{{ current.b.text }}</button>
        <button v-if="step > 0" class="tb-back" @click="step -= 1">← 上一题</button>
      </template>
    </div>
  </div>
</template>

<style scoped>
.tb-overlay {
  position: fixed; inset: 0; z-index: 92;
  background: rgba(0, 0, 0, 0.72);
  display: flex; align-items: flex-end; justify-content: center;
}
.tb-panel {
  position: relative; width: 100%; max-width: 480px;
  max-height: calc(100vh - 32px);
  overflow-y: auto;
  background: var(--panel); border: 2px solid var(--ink);
  box-shadow: var(--sh-lime-6);
  padding: 22px 20px calc(20px + var(--sab, 0px));
  display: flex; flex-direction: column; gap: 14px;
}
.tb-close {
  position: absolute; top: 10px; right: 10px;
  background: none; border: none; color: var(--t2); font-size: 14px; cursor: pointer;
}
.tb-close:hover { color: var(--lime); }

.tb-kicker { font-family: var(--silk); font-size: 10px; color: var(--lime); display: flex; justify-content: space-between; }
.tb-prog { color: var(--t2); }
.tb-track { height: 6px; background: var(--bg); border: 1px solid var(--line); }
.tb-fill { height: 100%; background: var(--lime); transition: width 0.2s; }

.tb-q { font-size: 17px; font-weight: 900; color: #FFF; line-height: 1.5; }
.tb-opt {
  width: 100%; padding: 14px; cursor: pointer; text-align: left;
  background: var(--bg); border: 1px solid var(--line);
  font-size: 14px; font-weight: 500; color: var(--t1);
}
.tb-opt:hover, .tb-opt:active { border-color: var(--lime); color: var(--lime); }
.tb-back { align-self: flex-start; background: none; border: none; color: var(--t2); font-size: 11px; cursor: pointer; padding: 0; }

/* 结果页 */
.tb-card {
  width: 180px;
  display: block;
  margin: 0 auto;
  border: 2px solid var(--ink);
  box-shadow: var(--sh-lime-4);
}
.tb-name { font-size: 30px; font-weight: 900; color: #FFF; text-align: center; }
.tb-type { font-family: var(--vt); font-size: 38px; color: var(--lime); text-align: center; letter-spacing: 4px; }
.tb-desc { font-size: 13px; color: var(--t1); text-align: center; line-height: 1.7; }
.tb-foot { display: flex; gap: 10px; }
.tb-ghost {
  flex: none; padding: 0 18px; height: 44px; cursor: pointer;
  background: none; border: 1px solid var(--t3); color: var(--t2); font-size: 13px;
}
.tb-main {
  flex: 1; height: 44px; cursor: pointer;
  background: var(--lime); border: 2px solid var(--ink);
  color: var(--ink); font-size: 14px; font-weight: 700;
}

/* 桌面端：居中弹窗 */
@media (min-width: 768px) {
  .tb-overlay { align-items: center; padding: 24px; }
  .tb-panel { padding: 28px 32px; }
}
</style>
