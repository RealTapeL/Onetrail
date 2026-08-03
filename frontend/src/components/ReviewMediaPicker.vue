<script setup>
/** 评价图片/视频选择器：选择 + 本地预览 + 「可能被官方采用」提示
 *  v-model:files 为 File 数组（当前仅前端暂存，随评价提交后清空）
 */
import { ref, watch, onBeforeUnmount } from 'vue'

const props = defineProps({ files: { type: Array, default: () => [] } })
const emit = defineEmits(['update:files'])

const inputEl = ref(null)
const items = ref([]) // { file, url, isVideo }

watch(() => props.files.length, (n) => { if (n === 0) clearAll() })

function clearAll() {
  items.value.forEach(i => URL.revokeObjectURL(i.url))
  items.value = []
}
onBeforeUnmount(clearAll)

function open() { inputEl.value?.click() }

function onPick(e) {
  const picked = Array.from(e.target.files || [])
  picked.forEach(f => {
    const isVideo = f.type.startsWith('video/')
    if (!isVideo && !f.type.startsWith('image/')) return
    items.value.push({ file: f, url: URL.createObjectURL(f), isVideo })
  })
  e.target.value = ''
  emit('update:files', items.value.map(i => i.file))
}

function remove(idx) {
  URL.revokeObjectURL(items.value[idx].url)
  items.value.splice(idx, 1)
  emit('update:files', items.value.map(i => i.file))
}
</script>

<template>
  <div class="mp">
    <input ref="inputEl" type="file" accept="image/*,video/*" multiple hidden @change="onPick">
    <div class="mp-row">
      <button type="button" class="mp-btn" @click="open">📷 添加图片 / 视频</button>
      <div v-for="(m, i) in items" :key="m.url" class="mp-thumb">
        <video v-if="m.isVideo" :src="m.url" muted />
        <img v-else :src="m.url" alt="评价图片预览">
        <span v-if="m.isVideo" class="mp-tag">视频</span>
        <button type="button" class="mp-x" @click="remove(i)">✕</button>
      </div>
    </div>
    <div class="mp-note">上传的图片/视频可能被官方采用，用于路线页展示</div>
  </div>
</template>

<style scoped>
.mp { display: flex; flex-direction: column; gap: 6px; }
.mp-row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.mp-btn {
  height: 56px; padding: 0 14px; cursor: pointer;
  background: none; border: 1px dashed var(--t3); color: var(--t2); font-size: 12px;
}
.mp-btn:hover { border-color: var(--lime); color: var(--lime); }
.mp-thumb {
  position: relative; width: 56px; height: 56px;
  border: 1px solid var(--line); overflow: hidden;
}
.mp-thumb img, .mp-thumb video { width: 100%; height: 100%; object-fit: cover; display: block; }
.mp-tag {
  position: absolute; left: 0; bottom: 0;
  background: rgba(0,0,0,.7); color: var(--lime);
  font-size: 9px; padding: 1px 4px;
}
.mp-x {
  position: absolute; top: 0; right: 0;
  width: 16px; height: 16px; padding: 0;
  background: rgba(0,0,0,.7); border: none; color: #FFF;
  font-size: 9px; cursor: pointer; line-height: 1;
}
.mp-x:hover { color: var(--red); }
.mp-note { font-size: 11px; color: var(--t3); }
</style>
