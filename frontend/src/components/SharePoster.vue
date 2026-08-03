<script setup>
/** 路线分享海报弹层：点「分享」弹出，每条路线按真实数据生成一张
 *  版式对齐参考稿：分享人条 → 路线图 → 名称/标签 → 四数据卡 → 时间轴 → 二维码+风险提示
 */
import { computed } from 'vue'
import { session } from '../api/http'
import { state } from '../api/index'

const props = defineProps({ route: { type: Object, required: true } })
const emit = defineEmits(['close'])

const userName = computed(() => session.user?.display_name || '山友')
const departDate = computed(() => {
  const d = state.travelDate ? new Date(state.travelDate) : new Date()
  return `${d.getMonth() + 1}月${d.getDate()}日`
})
const groupSize = computed(() => state.groupSize || 1)

const tags = computed(() => (props.route.terrain?.tags || []).slice(0, 4))
const risk = computed(() => {
  const s = props.route.terrain?.safetyNotes?.[0]
  return s ? `风险提示：${s.note}` : '风险提示：雨后部分路段湿滑，建议穿防滑徒步鞋'
})
const matchPct = computed(() => {
  const avg = props.route.averageRating
  return avg ? Math.round(avg * 20) : 96
})
const durH = computed(() => Math.round((props.route.durationMin || 0) / 60))
const fmtTime = (h, m) => `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
const timeline = computed(() => {
  const startH = 8, startM = 30
  const mid = startH * 60 + startM + Math.round((props.route.durationMin || 240) * 0.55)
  const end = startH * 60 + startM + (props.route.durationMin || 240)
  const region = (props.route.region || '').split(' ').pop() || '起点'
  return [
    { t: fmtTime(startH, startM), p: `${region}入口` },
    { t: fmtTime(Math.floor(mid / 60), mid % 60), p: '途中休整' },
    { t: fmtTime(Math.floor(end / 60), end % 60), p: '终点下撤', amber: true }
  ]
})

/** 伪二维码：由路线 id 生成确定性点阵（仅海报视觉用） */
const qrCells = computed(() => {
  let h = 0
  for (const c of String(props.route.id)) h = (h * 31 + c.charCodeAt(0)) >>> 0
  const cells = []
  let x = h || 7
  for (let i = 0; i < 144; i++) {
    x = (x * 1103515245 + 12345) >>> 0
    cells.push((x >> 16) % 3 === 0)
  }
  return cells
})

const copyMsg = defineModel('msg', { type: String, default: '' })
const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(window.location.href)
    copyMsg.value = '链接已复制'
  } catch {
    copyMsg.value = '复制失败，请手动复制'
  }
  setTimeout(() => { copyMsg.value = '' }, 2000)
}
</script>

<template>
  <div class="sp-overlay" @click.self="emit('close')">
    <div class="sp-poster">
      <button class="sp-close" aria-label="关闭" @click="emit('close')">✕</button>

      <!-- 顶条 -->
      <div class="sp-top">
        <span class="sp-brand">
          <svg viewBox="0 0 20 20" width="16" height="16"><polygon points="10,3 19,17 1,17" fill="#A3E635"/></svg>
          ONE TRAIL
        </span>
        <span class="sp-share-tag">分享路线 · SHARE</span>
      </div>

      <!-- 分享人 -->
      <div class="sp-sharer">
        <span class="sp-ava">{{ userName.slice(0, 1) }}</span>
        <span class="sp-line"><b>{{ userName }}</b> 向你分享了一条路线</span>
        <span class="sp-date">{{ departDate }}出发 · {{ groupSize }}人</span>
      </div>

      <!-- 路线图 -->
      <div class="sp-map">
        <svg viewBox="0 0 640 280" preserveAspectRatio="none">
          <rect width="640" height="280" fill="#101410"/>
          <g fill="#1d241d">
            <circle v-for="i in 60" :key="i" :cx="(i * 97) % 640" :cy="(i * 53) % 280" r="2"/>
          </g>
          <polygon points="40,120 110,40 180,120" fill="#222a22"/>
          <polygon points="120,120 190,55 260,120" fill="#1a211a"/>
          <polygon points="430,130 510,45 590,130" fill="#1a211a"/>
          <path d="M0 200 C 120 180, 200 230, 320 205 S 520 175, 640 200" stroke="#4a6b5a" stroke-width="10" fill="none" opacity=".8"/>
          <path d="M60 235 C 150 200, 180 150, 260 160 S 380 120, 450 105 S 560 70, 600 55"
                stroke="#A3E635" stroke-width="5" stroke-dasharray="12 8" fill="none"/>
          <rect x="52" y="228" width="12" height="12" fill="#A3E635"/>
          <text x="52" y="262" fill="#A3E635" font-size="13" font-family="monospace">START</text>
          <rect x="592" y="40" width="14" height="18" fill="#FFD028"/>
          <text x="575" y="34" fill="#FFD028" font-size="13" font-family="monospace">END</text>
          <rect x="248" y="152" width="10" height="10" fill="#A3E635"/>
          <text x="238" y="140" fill="#8E8E8E" font-size="12" font-family="monospace">S1 · LUNCH</text>
          <rect x="438" y="97" width="10" height="10" fill="#A3E635"/>
          <text x="428" y="85" fill="#8E8E8E" font-size="12" font-family="monospace">S2 · WATER</text>
          <g font-size="14" fill="#F5F5F5">
            <rect x="300" y="240" width="220" height="26" fill="none"/>
            <text x="640" y="262" text-anchor="end" fill="#8E8E8E" font-family="monospace" font-size="15">
              {{ route.distanceKm }}KM LOOP · ELEV {{ route.elevationGainM }}M
            </text>
          </g>
        </svg>
        <span class="sp-match">MATCH {{ matchPct }}%</span>
      </div>

      <!-- 名称与判定 -->
      <div class="sp-name-row">
        <div>
          <div class="sp-name">{{ route.name }}</div>
          <div class="sp-name-en">{{ (route.region || 'ONE TRAIL').toUpperCase() }} · LOOP</div>
        </div>
        <span v-if="route.verdict?.worth" class="sp-verdict">{{ route.verdict.text }} · {{ route.verdict.voteCount }} 票</span>
      </div>

      <!-- 标签 -->
      <div class="sp-tags">
        <span v-for="t in tags" :key="t.label" class="sp-tag" :class="{ warn: t.warning }">{{ t.label }}</span>
      </div>

      <!-- 四数据卡 -->
      <div class="sp-stats">
        <div v-for="s in route.stats" :key="s.label" class="sp-stat">
          <span class="sp-stat-lb">{{ s.label }}</span>
          <span class="sp-stat-v">{{ s.value }}</span>
        </div>
      </div>

      <!-- 时间轴 -->
      <div class="sp-tl">
        <template v-for="(p, i) in timeline" :key="i">
          <span class="sp-tl-item"><i :class="{ amber: p.amber }" />{{ p.t }} {{ p.p }}</span>
          <span v-if="i < timeline.length - 1" class="sp-tl-dash" />
        </template>
      </div>

      <!-- 二维码 + 风险 -->
      <div class="sp-bottom">
        <div class="sp-qr">
          <span v-for="(c, i) in qrCells" :key="i" :class="{ on: c }" />
        </div>
        <div class="sp-btext">
          <b>扫码查看路线详情</b>
          <span>打开一径 · 把这条路线同步到你的计划</span>
          <span class="sp-risk">{{ risk }}</span>
        </div>
      </div>

      <!-- 底条 -->
      <div class="sp-foot">
        <span>ONE TRAIL · 一径</span>
        <button class="sp-copy" @click="copyLink">{{ copyMsg || '复制链接' }}</button>
        <span>走一条属于你的路</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sp-overlay {
  position: fixed; inset: 0; z-index: 95;
  background: rgba(0, 0, 0, .78);
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}
.sp-poster {
  position: relative;
  width: 460px; max-width: 100%;
  max-height: calc(100vh - 40px);
  overflow-y: auto;
  background: #0B0B0B;
  border: 2px solid var(--lime);
  padding: 22px 24px 16px;
  display: flex; flex-direction: column; gap: 14px;
  color: var(--t1);
}
.sp-close {
  position: absolute; top: 8px; right: 10px; z-index: 2;
  background: none; border: none; color: var(--t2); font-size: 14px; cursor: pointer;
}
.sp-close:hover { color: var(--lime); }

.sp-top {
  display: flex; justify-content: space-between; align-items: center;
  padding-bottom: 10px; border-bottom: 1px dashed var(--line);
}
.sp-brand {
  display: flex; align-items: center; gap: 8px;
  font-family: var(--p8); font-size: 10px; color: var(--lime);
}
.sp-share-tag {
  font-family: var(--silk); font-size: 9px; color: var(--lime);
  border: 1px solid var(--lime); padding: 3px 8px;
}

.sp-sharer { display: flex; align-items: center; gap: 10px; }
.sp-ava {
  width: 30px; height: 30px; flex: none;
  display: flex; align-items: center; justify-content: center;
  background: #2F5B2A; color: var(--lime); font-weight: 900; font-size: 13px;
  border: 1px solid var(--lime);
}
.sp-line { flex: 1; font-size: 13px; min-width: 0; }
.sp-line b { color: #FFF; }
.sp-date { font-size: 11px; color: var(--t2); border: 1px solid var(--line); padding: 3px 8px; flex: none; }

.sp-map { position: relative; border: 1px solid var(--line); }
.sp-map svg { width: 100%; display: block; }
.sp-match {
  position: absolute; top: 10px; left: 10px;
  background: var(--amber); color: #0B0B0B;
  font-family: var(--silk); font-size: 10px; font-weight: 700;
  padding: 4px 8px;
}

.sp-name-row { display: flex; justify-content: space-between; align-items: flex-end; gap: 12px; }
.sp-name { font-size: 26px; font-weight: 900; color: #FFF; }
.sp-name-en { font-family: var(--p8); font-size: 9px; color: var(--t2); margin-top: 4px; }
.sp-verdict {
  flex: none;
  background: var(--lime); color: #0B0B0B;
  font-size: 12px; font-weight: 900; padding: 6px 10px;
}

.sp-tags { display: flex; gap: 8px; flex-wrap: wrap; }
.sp-tag {
  font-size: 11px; color: var(--lime);
  border: 1px solid var(--lime); padding: 3px 10px;
}
.sp-tag.warn { color: var(--red); border-color: var(--red); }

.sp-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.sp-stat {
  background: #FFF; color: var(--ink);
  padding: 10px 8px;
  display: flex; flex-direction: column; gap: 4px;
  box-shadow: 3px 3px 0 var(--lime);
}
.sp-stat-lb { font-size: 9px; color: var(--t3); }
.sp-stat-v { font-family: var(--vt); font-size: 20px; color: #0B0B0B; }

.sp-tl { display: flex; align-items: center; gap: 8px; font-size: 11px; color: var(--t1); flex-wrap: wrap; }
.sp-tl-item { display: flex; align-items: center; gap: 6px; }
.sp-tl-item i { width: 8px; height: 8px; background: var(--lime); flex: none; }
.sp-tl-item i.amber { background: var(--amber); }
.sp-tl-dash { flex: 1; min-width: 20px; border-top: 1px dashed var(--line); }

.sp-bottom {
  display: flex; gap: 16px; align-items: center;
  border-top: 1px dashed var(--line); padding-top: 14px;
}
.sp-qr {
  width: 96px; height: 96px; flex: none;
  display: grid; grid-template-columns: repeat(12, 1fr); grid-template-rows: repeat(12, 1fr);
  background: #FFF; padding: 6px; gap: 0;
  border: 2px solid var(--lime);
}
.sp-qr span { background: transparent; }
.sp-qr span.on { background: #0B0B0B; }
.sp-btext { display: flex; flex-direction: column; gap: 5px; font-size: 12px; color: var(--t2); }
.sp-btext b { font-size: 15px; color: #FFF; }
.sp-risk { color: var(--red); font-size: 11px; }

.sp-foot {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 10px; color: var(--t3);
}
.sp-copy {
  background: none; border: 1px solid var(--lime); color: var(--lime);
  font-family: var(--silk); font-size: 10px; padding: 5px 12px; cursor: pointer;
}
.sp-copy:hover { background: var(--lime); color: #0B0B0B; }
</style>
