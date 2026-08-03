<script setup>
/** 预算 / 体能 / 装备 选择弹层（参考携程价格/星级底部弹窗）
 *  双端共用；移动端贴底抽屉、桌面端居中弹窗
 *  props.form: 需求表单 reactive 对象，直接读写其字段
 */
import { questFormDefaults } from '../api/index'

const props = defineProps({
  form: { type: Object, required: true }
})
const emit = defineEmits(['close'])

const BUDGET_PRESETS = [
  { label: '¥200以下', value: 200 },
  { label: '¥400', value: 400 },
  { label: '¥600', value: 600 },
  { label: '¥1000', value: 1000 },
  { label: '不限', value: 2000 }
]
const GEAR_OPTIONS = ['登山鞋', '背包', '登山杖', '冲锋衣', '头灯', '帐篷', '睡袋', '水袋']

const toggleGear = (g) => {
  const i = props.form.ownedGear.indexOf(g)
  i >= 0 ? props.form.ownedGear.splice(i, 1) : props.form.ownedGear.push(g)
}

const reset = () => {
  const d = JSON.parse(JSON.stringify(questFormDefaults))
  props.form.budgetPerPerson.max = d.budgetPerPerson.max
  props.form.fitnessLevel = d.fitnessLevel
  props.form.ownedGear = d.ownedGear
}
</script>

<template>
  <div class="pf-overlay" @click.self="emit('close')">
    <div class="pf-panel" role="dialog" aria-label="预算体能装备选择">
      <div class="pf-head">
        <button class="pf-x" aria-label="关闭" @click="emit('close')">✕</button>
        <div class="pf-title">预算 / 体能 / 装备</div>
      </div>

      <div class="pf-sec">
        <div class="pf-label">预算 · 每人 <b class="pf-val">¥{{ form.budgetPerPerson.max }}</b></div>
        <input type="range" min="100" max="2000" step="50"
               v-model.number="form.budgetPerPerson.max" class="pf-range" />
        <div class="pf-grid">
          <button v-for="p in BUDGET_PRESETS" :key="p.value" class="pf-chip"
                  :class="{ on: form.budgetPerPerson.max === p.value }"
                  @click="form.budgetPerPerson.max = p.value">{{ p.label }}</button>
        </div>
      </div>

      <div class="pf-sec">
        <div class="pf-label">体能等级 · <b class="pf-val">Lv.{{ form.fitnessLevel }}</b></div>
        <div class="pf-grid">
          <button v-for="n in 5" :key="n" class="pf-chip"
                  :class="{ on: form.fitnessLevel === n }"
                  @click="form.fitnessLevel = n">Lv.{{ n }}</button>
        </div>
        <div class="pf-hint">Lv.1 台阶完好新手友好 — Lv.5 重装拉练高强度</div>
      </div>

      <div class="pf-sec">
        <div class="pf-label">已有装备 · <b class="pf-val">{{ form.ownedGear.length }} 件</b></div>
        <div class="pf-grid">
          <button v-for="g in GEAR_OPTIONS" :key="g" class="pf-chip"
                  :class="{ on: form.ownedGear.includes(g) }"
                  @click="toggleGear(g)">{{ g }}</button>
        </div>
      </div>

      <div class="pf-foot">
        <button class="pf-clear" @click="reset">清空</button>
        <button class="pf-done" @click="emit('close')">完成</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pf-overlay {
  position: fixed; inset: 0; z-index: 91;
  background: rgba(0, 0, 0, 0.72);
  display: flex; align-items: flex-end; justify-content: center;
}
.pf-panel {
  width: 100%; max-width: 520px;
  background: var(--panel); border: 2px solid var(--ink);
  box-shadow: var(--sh-lime-6);
  padding: 16px 20px calc(18px + var(--sab, 0px));
  display: flex; flex-direction: column; gap: 18px;
}
.pf-head { display: flex; align-items: center; }
.pf-x { background: none; border: none; color: var(--t2); font-size: 15px; cursor: pointer; padding: 0; }
.pf-x:hover { color: var(--lime); }
.pf-title { flex: 1; text-align: center; font-size: 15px; font-weight: 900; color: #FFF; margin-right: 15px; }

.pf-sec { display: flex; flex-direction: column; gap: 10px; }
.pf-label { font-size: 12px; color: var(--t2); }
.pf-val { color: var(--lime); font-family: var(--vt); font-size: 14px; }
.pf-hint { font-size: 10px; color: var(--t3); }

.pf-range { width: 100%; accent-color: var(--lime); }

.pf-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.pf-grid:has(.pf-chip:nth-child(5):last-child) { grid-template-columns: repeat(5, 1fr); }
.pf-chip {
  padding: 9px 4px; cursor: pointer;
  background: var(--bg); border: 1px solid var(--line);
  font-size: 12px; font-weight: 500; color: var(--t1);
}
.pf-chip.on { background: var(--lime); border-color: var(--lime); color: var(--ink); font-weight: 700; }

.pf-foot { display: flex; gap: 10px; }
.pf-clear {
  flex: 1; height: 44px; cursor: pointer;
  background: none; border: 2px solid var(--t3); color: var(--t1); font-size: 14px; font-weight: 700;
}
.pf-done {
  flex: 2; height: 44px; cursor: pointer;
  background: var(--lime); border: 2px solid var(--ink);
  color: var(--ink); font-size: 14px; font-weight: 700;
}

/* 桌面端：居中弹窗 */
@media (min-width: 768px) {
  .pf-overlay { align-items: center; padding: 24px; }
  .pf-panel { padding: 22px 28px; }
}
</style>
