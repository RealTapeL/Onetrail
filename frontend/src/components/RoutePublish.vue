<script setup>
/** 发布路线（UGC，桌面与移动共用）
 *  提交 POST /api/v1/routes；坐标可由城市名经高德地理编码填充
 */
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import HudNav from './HudNav.vue'
import { geocodeCity, postRoute } from '../api/index'

const router = useRouter()
const form = reactive({
  title: '',
  city: '',
  region: '',
  start_latitude: null,
  start_longitude: null,
  distance_km: null,
  elevation_gain_m: null,
  estimated_duration_min: null,
  difficulty: 'easy',
  suitable_for: '',
  description: ''
})
const tags = ref([])
const submitting = ref(false)
const msg = ref('')
const locating = ref(false)

const difficultyOptions = [
  { value: 'easy', label: '轻松 · easy' },
  { value: 'moderate', label: '适中 · moderate' },
  { value: 'hard', label: '困难 · hard' },
  { value: 'expert', label: '专家 · expert' }
]
const tagCategories = [
  { value: 'scenery', label: '景观' },
  { value: 'terrain', label: '地形' },
  { value: 'safety', label: '安全' },
  { value: 'vibe', label: '气质' }
]

const addTag = () => tags.value.push({ name: '', category: 'terrain', safety_note: '' })
const removeTag = (i) => tags.value.splice(i, 1)

const locate = async () => {
  if (!form.city.trim() || locating.value) return
  locating.value = true
  msg.value = ''
  try {
    const geo = await geocodeCity(form.city.trim())
    form.start_latitude = geo.latitude
    form.start_longitude = geo.longitude
    form.region = geo.formatted_address
    msg.value = `已解析：${geo.formatted_address}`
  } catch (err) {
    msg.value = err.message || '城市解析失败'
  } finally {
    locating.value = false
  }
}

const submit = async () => {
  if (submitting.value) return
  msg.value = ''
  if (!form.title.trim()) { msg.value = '请填写路线名称'; return }
  if (form.start_latitude == null || form.start_longitude == null) { msg.value = '请先输入城市并点「解析坐标」'; return }
  if (!form.distance_km || !form.estimated_duration_min || form.elevation_gain_m == null) {
    msg.value = '请填写距离、爬升和预计耗时'; return
  }
  const cleanTags = tags.value
    .filter((t) => t.name.trim())
    .map((t) => ({ name: t.name.trim(), category: t.category, safety_note: t.safety_note.trim() || null }))
  submitting.value = true
  try {
    const created = await postRoute({
      title: form.title.trim(),
      region: form.region || form.city.trim(),
      start_latitude: form.start_latitude,
      start_longitude: form.start_longitude,
      distance_km: form.distance_km,
      elevation_gain_m: form.elevation_gain_m,
      estimated_duration_min: form.estimated_duration_min,
      difficulty: form.difficulty,
      suitable_for: form.suitable_for.trim() || null,
      description: form.description.trim() || null,
      tags: cleanTags
    })
    router.push(`/routes/${created.id}`)
  } catch (err) {
    msg.value = err.message || '发布失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="screen">
    <HudNav />

    <header class="screen-head">
      <div>
        <div class="sh-title-cn">发布路线</div>
        <div class="sh-title-en">PUBLISH YOUR ROUTE — UGC</div>
      </div>
      <button class="back-btn" @click="router.push('/routes')">返回路线库</button>
    </header>

    <div class="form-wrap panel-d">
      <div class="f-row">
        <label class="f-label">路线名称 *</label>
        <input v-model="form.title" class="f-input" placeholder="例：九溪十八涧环线" />
      </div>

      <div class="f-row">
        <label class="f-label">所在城市 *</label>
        <div class="geo-row">
          <input v-model="form.city" class="f-input" placeholder="例：杭州" @keyup.enter="locate" />
          <button class="geo-btn" :disabled="locating" @click="locate">{{ locating ? '解析中…' : '解析坐标' }}</button>
        </div>
        <div v-if="form.start_latitude != null" class="geo-result">
          {{ form.region }} · {{ form.start_latitude.toFixed(4) }}, {{ form.start_longitude.toFixed(4) }}
        </div>
      </div>

      <div class="f-grid">
        <div class="f-row">
          <label class="f-label">距离 KM *</label>
          <input v-model.number="form.distance_km" type="number" min="0.1" step="0.1" class="f-input" placeholder="8.0" />
        </div>
        <div class="f-row">
          <label class="f-label">累计爬升 M *</label>
          <input v-model.number="form.elevation_gain_m" type="number" min="0" class="f-input" placeholder="300" />
        </div>
        <div class="f-row">
          <label class="f-label">预计耗时（分钟）*</label>
          <input v-model.number="form.estimated_duration_min" type="number" min="10" class="f-input" placeholder="180" />
        </div>
        <div class="f-row">
          <label class="f-label">难度 *</label>
          <select v-model="form.difficulty" class="f-input">
            <option v-for="d in difficultyOptions" :key="d.value" :value="d.value">{{ d.label }}</option>
          </select>
        </div>
      </div>

      <div class="f-row">
        <label class="f-label">适合人群</label>
        <input v-model="form.suitable_for" class="f-input" placeholder="例：新手 · 亲子 · 半日徒步" />
      </div>

      <div class="f-row">
        <label class="f-label">路线描述</label>
        <textarea v-model="form.description" class="f-text" rows="3"
                  placeholder="起点终点、路况、景色、注意事项……"></textarea>
      </div>

      <div class="f-row">
        <label class="f-label">地形与安全标签</label>
        <div v-for="(t, i) in tags" :key="i" class="tag-row">
          <input v-model="t.name" class="f-input tag-name" placeholder="标签名，如 溪谷" />
          <select v-model="t.category" class="f-input tag-cat">
            <option v-for="c in tagCategories" :key="c.value" :value="c.value">{{ c.label }}</option>
          </select>
          <input v-model="t.safety_note" class="f-input tag-note" placeholder="安全提示（可选）" />
          <button class="tag-del" @click="removeTag(i)">×</button>
        </div>
        <button class="tag-add" @click="addTag">+ 添加标签</button>
      </div>

      <div v-if="msg" class="f-msg">{{ msg }}</div>
      <button class="f-submit" :disabled="submitting" @click="submit">
        {{ submitting ? '发布中…' : '发布路线' }}
      </button>
    </div>
  </section>
</template>

<style scoped>
.screen { min-height: 100vh; background: var(--bg); }
.screen-head {
  padding: 24px 48px 0;
  display: flex; align-items: center; justify-content: space-between;
}
.sh-title-cn { font-size: 22px; font-weight: 900; color: #FFF; }
.sh-title-en { font-family: var(--p8); font-size: 10px; color: var(--lime); margin-top: 4px; }
.back-btn {
  background: none; border: 1px solid var(--line); color: var(--t2);
  padding: 8px 14px; font-size: 12px; cursor: pointer;
}
.back-btn:hover { color: var(--lime); border-color: var(--lime); }

.form-wrap {
  margin: 24px auto 48px;
  max-width: 720px;
  width: calc(100% - 32px);
  padding: 24px;
  display: flex; flex-direction: column; gap: 18px;
}
.f-row { display: flex; flex-direction: column; gap: 8px; }
.f-label { font-family: var(--silk); font-size: 11px; color: var(--t2); }
.f-input {
  background: #FFF; border: 2px solid var(--ink);
  padding: 10px 12px; font-size: 13px; color: var(--ink);
}
.f-text {
  background: #FFF; border: 2px solid var(--ink);
  padding: 10px 12px; font-size: 13px; color: var(--ink); resize: vertical;
}
.f-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; }
.geo-row { display: flex; gap: 10px; }
.geo-btn {
  flex: none; background: var(--lime); border: 2px solid var(--ink);
  padding: 0 14px; font-size: 12px; font-weight: 700; cursor: pointer;
}
.geo-result { font-size: 11px; color: var(--lime); }
.tag-row { display: flex; gap: 8px; margin-bottom: 8px; }
.tag-name { width: 110px; flex: none; }
.tag-cat { width: 84px; flex: none; }
.tag-note { flex: 1; }
.tag-del {
  flex: none; width: 34px; background: none; border: 1px solid var(--line);
  color: var(--t3); font-size: 16px; cursor: pointer;
}
.tag-del:hover { color: var(--red); border-color: var(--red); }
.tag-add {
  align-self: flex-start; background: none; border: 1px dashed var(--line);
  color: var(--t2); padding: 6px 12px; font-size: 12px; cursor: pointer;
}
.tag-add:hover { color: var(--lime); border-color: var(--lime); }
.f-msg { font-size: 12px; color: var(--red); }
.f-submit {
  background: var(--lime); border: 2px solid var(--ink); box-shadow: var(--sh-lime-6);
  padding: 14px; font-size: 15px; font-weight: 900; color: var(--ink); cursor: pointer;
}
.f-submit:disabled { opacity: 0.6; cursor: default; }
</style>
