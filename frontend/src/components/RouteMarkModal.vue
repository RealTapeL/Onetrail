<script setup>
/** 想去 / 去过 记录弹窗（参考豆瓣标记交互）
 *  想去 = 收藏 + 本地备注；去过 = 提交真实评价（星级 + 气质标签 + 感受）
 *  打卡成功后可自动弹出（initialTab="done"）
 */
import { ref } from 'vue'
import { IMPRESSION_OPTIONS, postRouteReview, setFavorite } from '../api/index'

const props = defineProps({
  routeId: { type: [String, Number], required: true },
  initialTab: { type: String, default: 'done' },
  initialRating: { type: Number, default: 5 }
})
const emit = defineEmits(['close', 'marked'])

const tab = ref(props.initialTab)
const wishNote = ref('')
const rating = ref(props.initialRating)
const tags = ref([])
const content = ref('')
const submitting = ref(false)
const errorMsg = ref('')

const noteKey = `onetrail.wishNote.${props.routeId}`
try { wishNote.value = localStorage.getItem(noteKey) || '' } catch { /* 无本地存储环境 */ }

const toggleTag = (t) => {
  tags.value = tags.value.includes(t) ? tags.value.filter((x) => x !== t) : [...tags.value, t]
}

const submit = async () => {
  if (submitting.value) return
  submitting.value = true
  errorMsg.value = ''
  try {
    if (tab.value === 'wish') {
      await setFavorite(props.routeId, true)
      try { localStorage.setItem(noteKey, wishNote.value.trim()) } catch { /* 忽略 */ }
    } else {
      await postRouteReview(props.routeId, {
        rating: rating.value,
        content: content.value.trim(),
        impressionTags: tags.value
      })
    }
    emit('marked', { tab: tab.value })
    emit('close')
  } catch (err) {
    errorMsg.value = err.message || '提交失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="mk-overlay" @click.self="emit('close')">
    <div class="mk-panel" role="dialog" aria-label="记录想去或去过">
      <button class="mk-close" aria-label="关闭" @click="emit('close')">✕</button>

      <div class="mk-tabs">
        <button class="mk-tab" :class="{ on: tab === 'wish' }" @click="tab = 'wish'">想去</button>
        <button class="mk-tab" :class="{ on: tab === 'done' }" @click="tab = 'done'">去过</button>
      </div>

      <template v-if="tab === 'wish'">
        <textarea v-model="wishNote" class="mk-text" rows="4"
                  placeholder="记录一下想去的理由…（可选）" />
      </template>

      <template v-else>
        <div class="mk-label">点击星星评分</div>
        <div class="mk-stars">
          <button v-for="n in 5" :key="n" class="mk-star" :class="{ on: n <= rating }"
                  @click="rating = n">{{ n <= rating ? '★' : '☆' }}</button>
        </div>
        <div class="mk-tags">
          <button v-for="t in IMPRESSION_OPTIONS" :key="t" class="mk-tag"
                  :class="{ on: tags.includes(t) }" @click="toggleTag(t)">{{ t }}</button>
        </div>
        <textarea v-model="content" class="mk-text" rows="4"
                  placeholder="说说你走完之后的感受吧…" />
      </template>

      <div class="mk-foot">
        <span v-if="errorMsg" class="mk-err">{{ errorMsg }}</span>
        <button class="mk-submit" :disabled="submitting" @click="submit">
          {{ submitting ? '提交中…' : '确定' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mk-overlay {
  position: fixed; inset: 0; z-index: 90;
  background: rgba(0, 0, 0, 0.72);
  display: grid; place-items: center; padding: 16px;
}
.mk-panel {
  position: relative; width: min(420px, 100%);
  background: var(--panel); border: 2px solid var(--ink);
  box-shadow: var(--sh-lime-6);
  padding: 20px; display: flex; flex-direction: column; gap: 14px;
}
.mk-close {
  position: absolute; top: 10px; right: 10px;
  background: none; border: none; color: var(--t2); font-size: 14px; cursor: pointer;
}
.mk-close:hover { color: var(--lime); }

.mk-tabs { display: flex; justify-content: center; gap: 32px; border-bottom: 1px solid var(--line); }
.mk-tab {
  background: none; border: none; cursor: pointer;
  font-size: 16px; font-weight: 500; color: var(--t3);
  padding: 4px 2px 10px; border-bottom: 3px solid transparent;
}
.mk-tab.on { color: #FFF; font-weight: 700; border-bottom-color: var(--lime); }

.mk-label { font-size: 11px; color: var(--t2); text-align: center; }
.mk-stars { display: flex; justify-content: center; gap: 8px; }
.mk-star { background: none; border: none; cursor: pointer; font-size: 26px; color: var(--t4); line-height: 1; padding: 0 2px; }
.mk-star.on { color: var(--amber); }

.mk-tags { display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; }
.mk-tag {
  background: var(--bg); border: 1px solid var(--line); color: var(--t1);
  font-size: 11px; padding: 5px 10px; cursor: pointer;
}
.mk-tag.on { background: var(--lime); border-color: var(--lime); color: var(--ink); font-weight: 700; }

.mk-text {
  width: 100%; resize: vertical;
  background: var(--bg); border: 1px solid var(--line);
  color: var(--t1); font-size: 12px; line-height: 1.7; padding: 10px 12px;
}
.mk-text:focus { outline: none; border-color: var(--lime); }

.mk-foot { display: flex; align-items: center; gap: 12px; }
.mk-err { flex: 1; font-size: 11px; color: var(--red); }
.mk-submit {
  margin-left: auto; height: 40px; padding: 0 32px;
  background: var(--lime); border: 2px solid var(--ink);
  color: var(--ink); font-size: 14px; font-weight: 700; cursor: pointer;
}
.mk-submit:disabled { opacity: 0.6; }
</style>
