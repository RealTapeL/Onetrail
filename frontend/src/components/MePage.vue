<script setup>
/**
 * 个人主页 /me（桌面+移动单组件自适应）
 * 四个板块（可用 ?tab=fav|gear|rec|set 直达）：
 *  - fav  收藏路线      GET /routes/favorites/mine
 *  - gear 我的装备      本地清单（localStorage），从真实装备目录 GET /equipment 添加
 *  - rec  我记录的路线  GET /history
 *  - set  设置          GET/PUT /profile/preferences
 */
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import HudNav from './HudNav.vue'
import TabBar from './mobile/TabBar.vue'
import { session, logout } from '../api/http'
import { clearTbti } from '../composables/tbti'
import { useIsMobile } from '../composables/useIsMobile'
import {
  fetchMyFavorites, fetchMyHistory, fetchPreferences, putPreferences,
  fetchEquipmentCatalog, setFavorite
} from '../api/index'

const route = useRoute()
const router = useRouter()
const isMobile = useIsMobile()

const TABS = [
  { key: 'fav', label: '收藏路线' },
  { key: 'gear', label: '我的装备' },
  { key: 'rec', label: '我记录的路线' },
  { key: 'achv', label: '成就' },
  { key: 'set', label: '设置' }
]
const tab = ref(TABS.some(t => t.key === route.query.tab) ? route.query.tab : 'fav')
watch(tab, (v) => router.replace({ query: { ...route.query, tab: v } }))

const initial = computed(() => (session.user?.display_name || '·').slice(0, 1))

/* ---------- 收藏路线 ---------- */
const favs = ref(null)
const favErr = ref('')
async function loadFavs() {
  favErr.value = ''
  try {
    favs.value = await fetchMyFavorites()
  } catch (e) {
    favErr.value = e.message || '收藏加载失败'
    favs.value = []
  }
}
async function unfav(r) {
  try {
    await setFavorite(r.id, false)
    favs.value = favs.value.filter(x => x.id !== r.id)
  } catch { /* 保持原样 */ }
}

/* ---------- 我记录的路线 ---------- */
const recs = ref(null)
const recErr = ref('')
async function loadRecs() {
  recErr.value = ''
  try {
    const list = await fetchMyHistory()
    recs.value = [...list].sort((a, b) => (b.completed_on || '').localeCompare(a.completed_on || ''))
  } catch (e) {
    recErr.value = e.message || '记录加载失败'
    recs.value = []
  }
}
const totalKm = computed(() => (recs.value || []).reduce((s, r) => s + (r.distance_km || 0), 0))
const totalUp = computed(() => (recs.value || []).reduce((s, r) => s + (r.elevation_gain_m || 0), 0))
const fmtDur = (min) => min >= 60 ? `${Math.floor(min / 60)}h${min % 60 ? `${min % 60}m` : ''}` : `${min}m`

/* ---------- 我的装备（本地清单 + 真实目录选品） ---------- */
const GEAR_KEY = 'ot_my_gear'
const myGear = ref([])          // 装备对象数组
const catalog = ref(null)
const showPicker = ref(false)
const pickerFilter = ref('')
const gearErr = ref('')

function readGearIds() {
  try { return JSON.parse(localStorage.getItem(GEAR_KEY) || '[]') } catch { return [] }
}
function saveGearIds(ids) {
  localStorage.setItem(GEAR_KEY, JSON.stringify(ids))
}
async function loadGear() {
  gearErr.value = ''
  try {
    const cat = await fetchEquipmentCatalog()
    catalog.value = cat
    const ids = readGearIds()
    myGear.value = ids.map(id => cat.find(g => g.id === id)).filter(Boolean)
  } catch (e) {
    gearErr.value = e.message || '装备目录加载失败'
    catalog.value = []
  }
}
function addGear(g) {
  const ids = readGearIds()
  if (ids.includes(g.id)) return
  ids.push(g.id)
  saveGearIds(ids)
  myGear.value = [...myGear.value, g]
}
function removeGear(g) {
  saveGearIds(readGearIds().filter(id => id !== g.id))
  myGear.value = myGear.value.filter(x => x.id !== g.id)
}
const myGearIds = computed(() => new Set(myGear.value.map(g => g.id)))
const pickerList = computed(() => {
  const list = catalog.value || []
  const q = pickerFilter.value.trim()
  if (!q) return list
  return list.filter(g => g.name.includes(q) || (g.brand || '').includes(q))
})
const gearWeight = computed(() => myGear.value.reduce((s, g) => s + (g.weight_g || 0), 0) / 1000)
const gearCost = computed(() => myGear.value.reduce((s, g) => s + (g.price_cny || 0), 0))
const fmtKg = (g) => g.weight_g != null ? `${(g.weight_g / 1000).toFixed(2)}kg` : '—'

/* ---------- 设置（徒步偏好） ---------- */
const prefs = ref(null)
const prefsErr = ref('')
const saving = ref(false)
const savedTip = ref(false)
const interestsText = ref('')
const DIFFS = ['入门', '中等', '进阶', '挑战']

async function loadPrefs() {
  prefsErr.value = ''
  try {
    const p = await fetchPreferences()
    prefs.value = { ...p }
    interestsText.value = (p.interests || []).join('，')
  } catch (e) {
    prefsErr.value = e.message || '偏好加载失败'
    prefs.value = {
      max_distance_km: null, max_elevation_gain_m: null, preferred_duration_min: null,
      difficulty_preference: null, interests: [], tbti_type: null
    }
  }
}
async function savePrefs() {
  if (saving.value) return
  saving.value = true
  savedTip.value = false
  try {
    await putPreferences({
      max_distance_km: prefs.value.max_distance_km || null,
      max_elevation_gain_m: prefs.value.max_elevation_gain_m || null,
      preferred_duration_min: prefs.value.preferred_duration_min || null,
      difficulty_preference: prefs.value.difficulty_preference || null,
      interests: interestsText.value.split(/[,，、\s]+/).map(s => s.trim()).filter(Boolean).slice(0, 20),
      tbti_type: prefs.value.tbti_type || null
    })
    savedTip.value = true
    setTimeout(() => { savedTip.value = false }, 2000)
  } catch (e) {
    prefsErr.value = e.message || '保存失败'
  } finally {
    saving.value = false
  }
}

function onLogout() {
  logout()
  clearTbti()
  router.push('/login')
}

/* ---------- 成就（基于记录/收藏/装备实时计算） ---------- */
const ACHIEVEMENTS = [
  { id: 'first',  icon: '🥾', name: '出发',       desc: '完成第一次徒步记录',     need: 1,    val: () => recs.value?.length || 0 },
  { id: 'r5',     icon: '🧭', name: '常客',       desc: '累计记录 5 条路线',      need: 5,    val: () => recs.value?.length || 0 },
  { id: 'r10',    icon: '🗺️', name: '老驴',       desc: '累计记录 10 条路线',     need: 10,   val: () => recs.value?.length || 0 },
  { id: 'km50',   icon: '⛰️', name: '五十公里',   desc: '累计里程 50 KM',         need: 50,   val: () => totalKm.value },
  { id: 'km100',  icon: '🏅', name: '百公里俱乐部', desc: '累计里程 100 KM',      need: 100,  val: () => totalKm.value },
  { id: 'km300',  icon: '👑', name: '三百公里传说', desc: '累计里程 300 KM',      need: 300,  val: () => totalKm.value },
  { id: 'up1k',   icon: '📈', name: '向上爬',     desc: '累计爬升 1,000 M',       need: 1000, val: () => totalUp.value },
  { id: 'up5k',   icon: '🚀', name: '垂直人生',   desc: '累计爬升 5,000 M',       need: 5000, val: () => totalUp.value },
  { id: 'fav5',   icon: '⭐', name: '种草机',     desc: '收藏 5 条路线',          need: 5,    val: () => favs.value?.length || 0 },
  { id: 'gear5',  icon: '🎒', name: '装备党',     desc: '我的装备达到 5 件',      need: 5,    val: () => myGear.value.length },
  { id: 'tbti',   icon: '🃏', name: '认识自己',   desc: '完成 TBTI 人格测评',     need: 1,    val: () => (prefs.value?.tbti_type ? 1 : 0) }
]
const achvList = computed(() => ACHIEVEMENTS.map(a => {
  const v = a.val()
  return { ...a, value: v, unlocked: v >= a.need, pct: Math.min(100, Math.round((v / a.need) * 100)) }
}))
const achvDone = computed(() => achvList.value.filter(a => a.unlocked).length)

onMounted(() => {
  loadFavs()
  loadRecs()
  loadGear()
  loadPrefs()
})
</script>

<template>
  <section class="screen">
    <HudNav v-if="!isMobile" />

    <header class="screen-head">
      <div>
        <div class="sh-title-cn">「07」个人主页</div>
        <div class="sh-title-en">MY PROFILE — PLAYER CARD</div>
      </div>
    </header>

    <!-- 资料头卡 -->
    <div class="me-card panel-d">
      <span class="me-ava">{{ initial }}</span>
      <div class="me-who">
        <b class="me-name">{{ session.user?.display_name || '未登录' }}</b>
        <span class="me-mail">{{ session.user?.email }}</span>
        <div class="me-chips">
          <span v-if="prefs?.tbti_type" class="chip lime">TBTI · {{ prefs.tbti_type }}</span>
          <span v-if="prefs?.difficulty_preference" class="chip">偏好难度 · {{ prefs.difficulty_preference }}</span>
        </div>
      </div>
      <div class="me-stats">
        <div><b>{{ favs?.length ?? '—' }}</b><span>收藏路线</span></div>
        <div><b>{{ recs?.length ?? '—' }}</b><span>记录路线</span></div>
        <div><b>{{ totalKm.toFixed(0) }}</b><span>总里程 KM</span></div>
        <div><b>{{ myGear.length }}</b><span>我的装备</span></div>
      </div>
    </div>

    <!-- 板块切换：桌面侧栏 / 移动横向页签 -->
    <div class="me-body">
      <nav class="me-tabs" :class="{ h: isMobile }">
        <button v-for="t in TABS" :key="t.key"
                class="me-tab" :class="{ on: tab === t.key }"
                @click="tab = t.key">{{ t.label }}</button>
      </nav>

      <div class="me-panel">

        <!-- ===== 收藏路线 ===== -->
        <div v-if="tab === 'fav'" class="blk">
          <p v-if="favErr" class="err">{{ favErr }}</p>
          <p v-else-if="favs === null" class="dim">加载中…</p>
          <p v-else-if="!favs.length" class="dim">还没有收藏路线，去<router-link to="/routes" class="lk">路线库</router-link>逛逛</p>
          <div v-else class="fav-grid">
            <div v-for="r in favs" :key="r.id" class="fav-card panel-d">
              <router-link class="fav-main" :to="`/routes/${r.id}`">
                <b>{{ r.title }}</b>
                <span class="dim">{{ r.region }}</span>
                <div class="fav-kpi">
                  <span>{{ r.distance_km }}KM</span>
                  <span>爬升 {{ r.elevation_gain_m }}M</span>
                  <span>{{ r.difficulty }}</span>
                  <span v-if="r.average_rating != null">★ {{ r.average_rating }}</span>
                </div>
              </router-link>
              <button class="mini danger" @click="unfav(r)">取消收藏</button>
            </div>
          </div>
        </div>

        <!-- ===== 我的装备 ===== -->
        <div v-else-if="tab === 'gear'" class="blk">
          <div class="gear-sum panel-d">
            <span><b>{{ myGear.length }}</b> 件</span>
            <span>总重 <b>{{ gearWeight.toFixed(1) }}</b> KG</span>
            <span>投入 <b>¥{{ gearCost.toFixed(0) }}</b></span>
            <button class="mini" @click="showPicker = !showPicker">{{ showPicker ? '收起目录' : '+ 从装备库添加' }}</button>
          </div>
          <p v-if="gearErr" class="err">{{ gearErr }}</p>

          <div v-if="showPicker" class="picker panel-d">
            <input v-model="pickerFilter" class="p-input" placeholder="搜索装备名称 / 品牌">
            <p v-if="catalog === null" class="dim">目录加载中…</p>
            <div v-else class="pick-list">
              <div v-for="g in pickerList" :key="g.id" class="pick-row">
                <div class="pick-who">
                  <b>{{ g.name }}</b>
                  <span class="dim">{{ g.brand || '—' }} · {{ g.category }}</span>
                </div>
                <span class="dim pick-meta">{{ fmtKg(g) }} / ¥{{ g.price_cny ?? '—' }}</span>
                <button class="mini" :disabled="myGearIds.has(g.id)" @click="addGear(g)">
                  {{ myGearIds.has(g.id) ? '已加入' : '加入' }}
                </button>
              </div>
              <p v-if="!pickerList.length" class="dim">没有匹配的装备</p>
            </div>
          </div>

          <p v-if="!myGear.length && !gearErr" class="dim">清单还是空的，点「+ 从装备库添加」把家当放进来</p>
          <div v-else class="gear-grid">
            <div v-for="g in myGear" :key="g.id" class="gear-card panel-d">
              <b>{{ g.name }}</b>
              <span class="dim">{{ g.brand || '—' }}</span>
              <div class="fav-kpi">
                <span>{{ g.category }}</span>
                <span>{{ fmtKg(g) }}</span>
                <span>¥{{ g.price_cny ?? '—' }}</span>
              </div>
              <button class="mini danger" @click="removeGear(g)">移出清单</button>
            </div>
          </div>
        </div>

        <!-- ===== 我记录的路线 ===== -->
        <div v-else-if="tab === 'rec'" class="blk">
          <p v-if="recErr" class="err">{{ recErr }}</p>
          <p v-else-if="recs === null" class="dim">加载中…</p>
          <p v-else-if="!recs.length" class="dim">还没有徒步记录，完成一次打卡后会出现在这里</p>
          <template v-else>
            <div class="gear-sum panel-d">
              <span><b>{{ recs.length }}</b> 次</span>
              <span>总里程 <b>{{ totalKm.toFixed(1) }}</b> KM</span>
              <span>总爬升 <b>{{ totalUp }}</b> M</span>
            </div>
            <div class="rec-list">
              <div v-for="r in recs" :key="r.id" class="rec-row panel-d">
                <div class="rec-date">
                  <b>{{ (r.completed_on || '').slice(5) }}</b>
                  <span>{{ (r.completed_on || '').slice(0, 4) }}</span>
                </div>
                <div class="rec-body">
                  <div class="fav-kpi">
                    <span>{{ r.distance_km }}KM</span>
                    <span>爬升 {{ r.elevation_gain_m }}M</span>
                    <span>用时 {{ fmtDur(r.duration_min) }}</span>
                    <span v-if="r.rating">自评 ★{{ r.rating }}</span>
                  </div>
                </div>
                <router-link v-if="r.route_id" class="mini lk-btn" :to="`/routes/${r.route_id}`">路线</router-link>
              </div>
            </div>
          </template>
        </div>

        <!-- ===== 成就 ===== -->
        <div v-else-if="tab === 'achv'" class="blk">
          <div class="gear-sum panel-d">
            <span>已解锁 <b>{{ achvDone }}</b> / {{ achvList.length }} 枚成就</span>
          </div>
          <div class="achv-grid">
            <div v-for="a in achvList" :key="a.id" class="achv-card panel-d" :class="{ lock: !a.unlocked }">
              <span class="a-icon">{{ a.icon }}</span>
              <b>{{ a.name }}</b>
              <span class="a-desc">{{ a.desc }}</span>
              <div class="a-bar"><i :style="{ width: a.pct + '%' }" /></div>
              <span class="a-prog">{{ a.unlocked ? '已解锁' : `${a.value.toFixed ? a.value.toFixed(0) : a.value} / ${a.need}` }}</span>
            </div>
          </div>
        </div>

        <!-- ===== 设置 ===== -->
        <div v-else class="blk"><template v-if="prefs">
            <div class="set-group panel-d">
              <h3>徒步偏好（影响智能推荐）</h3>
              <div class="set-row">
                <label>单日最远距离 KM</label>
                <input v-model.number="prefs.max_distance_km" type="number" min="1" max="300" placeholder="如 25">
              </div>
              <div class="set-row">
                <label>单日最大爬升 M</label>
                <input v-model.number="prefs.max_elevation_gain_m" type="number" min="0" max="15000" placeholder="如 1500">
              </div>
              <div class="set-row">
                <label>偏好时长 分钟</label>
                <input v-model.number="prefs.preferred_duration_min" type="number" min="1" max="4320" placeholder="如 480">
              </div>
              <div class="set-row">
                <label>难度偏好</label>
                <div class="diffs">
                  <button v-for="d in DIFFS" :key="d"
                          class="mini" :class="{ on: prefs.difficulty_preference === d }"
                          @click="prefs.difficulty_preference = prefs.difficulty_preference === d ? null : d">{{ d }}</button>
                </div>
              </div>
              <div class="set-row">
                <label>兴趣标签（逗号分隔）</label>
                <input v-model="interestsText" type="text" placeholder="如 云海，古道，露营">
              </div>
              <div class="set-row">
                <label>TBTI 人格类型</label>
                <input v-model="prefs.tbti_type" type="text" maxlength="8" placeholder="如 FTRL">
              </div>
              <div class="set-actions">
                <button class="save" :disabled="saving" @click="savePrefs">{{ saving ? '保存中…' : '保存修改' }}</button>
                <span v-if="savedTip" class="ok">已保存 ✓</span>
                <span v-if="prefsErr" class="err">{{ prefsErr }}</span>
              </div>
            </div>

            <div class="set-group panel-d">
              <h3>账号</h3>
              <div class="set-row">
                <label>登录邮箱</label>
                <span class="dim">{{ session.user?.email }}</span>
              </div>
              <div class="set-row">
                <label>退出当前账号</label>
                <button class="mini danger" @click="onLogout">退出登录</button>
              </div>
            </div>
          </template>
          <p v-else class="dim">加载中…</p>
        </div>

      </div>
    </div>

    <TabBar v-if="isMobile" />
  </section>
</template>

<style scoped>
.me-card {
  display: flex; align-items: center; gap: 20px;
  margin: 0 var(--content-px);
  padding: 24px 28px;
}
.me-ava {
  width: 72px; height: 72px; flex: none;
  display: flex; align-items: center; justify-content: center;
  background: var(--brand-deep); color: var(--lime);
  font-size: 28px; font-weight: 900;
  border: 2px solid var(--lime);
  box-shadow: var(--sh-lime-4);
}
.me-who { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.me-name { font-size: 20px; color: var(--t1); }
.me-mail { font-size: 12px; color: var(--t3); }
.me-chips { display: flex; gap: 8px; margin-top: 6px; flex-wrap: wrap; }
.chip {
  font-size: 11px; color: var(--t2);
  border: 1px solid var(--line); padding: 2px 10px;
}
.chip.lime { color: var(--lime); border-color: var(--lime); }
.me-stats { margin-left: auto; display: flex; gap: 28px; text-align: center; }
.me-stats b { display: block; font-family: var(--silk); font-size: 20px; color: var(--lime); }
.me-stats span { font-size: 11px; color: var(--t3); }

.me-body { display: grid; grid-template-columns: 180px 1fr; gap: 20px; margin: 20px var(--content-px) 0; align-items: start; }
.me-tabs { display: flex; flex-direction: column; gap: 6px; position: sticky; top: 16px; }
.me-tab {
  padding: 12px 16px;
  background: var(--panel);
  border: 1px solid var(--line);
  color: var(--t2); font-size: 13px;
  cursor: pointer; text-align: left;
}
.me-tab:hover { color: var(--t1); }
.me-tab.on { color: var(--lime); border-color: var(--lime); font-weight: 700; box-shadow: var(--sh-lime-4); }
.me-tabs.h { flex-direction: row; overflow-x: auto; position: static; }
.me-tabs.h .me-tab { white-space: nowrap; text-align: center; }

.blk { display: flex; flex-direction: column; gap: 14px; }
.dim { color: var(--t3); font-size: 13px; }
.err { color: var(--red); font-size: 13px; }
.ok { color: var(--lime); font-size: 13px; }
.lk { color: var(--lime); }

.fav-grid, .gear-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.fav-card, .gear-card { padding: 16px 18px; display: flex; flex-direction: column; gap: 6px; }
.fav-main { display: flex; flex-direction: column; gap: 4px; text-decoration: none; }
.fav-main b, .gear-card b { color: var(--t1); font-size: 15px; }
.fav-main:hover b { color: var(--lime); }
.fav-kpi { display: flex; gap: 14px; flex-wrap: wrap; font-family: var(--silk); font-size: 11px; color: var(--lime); }

.mini {
  align-self: flex-start;
  background: none; border: 1px solid var(--line);
  padding: 6px 12px;
  font-size: 12px; color: var(--t2);
  cursor: pointer;
}
.mini:hover:not(:disabled) { color: var(--lime); border-color: var(--lime); }
.mini:disabled { opacity: .45; cursor: default; }
.mini.danger:hover { color: var(--red); border-color: var(--red); }
.mini.on { color: var(--lime); border-color: var(--lime); }
.lk-btn { text-decoration: none; }

.gear-sum {
  display: flex; align-items: center; gap: 26px; flex-wrap: wrap;
  padding: 14px 18px;
  font-size: 13px; color: var(--t2);
}
.gear-sum b { font-family: var(--silk); color: var(--lime); font-size: 16px; }
.gear-sum .mini { margin-left: auto; align-self: center; }

.picker { padding: 14px 18px; }
.p-input {
  width: 100%; margin-bottom: 10px;
  background: var(--bg); border: 1px solid var(--line);
  padding: 9px 12px; color: var(--t1); font-size: 13px; outline: none;
}
.p-input:focus { border-color: var(--lime); }
.pick-list { max-height: 300px; overflow-y: auto; display: flex; flex-direction: column; }
.pick-row {
  display: flex; align-items: center; gap: 14px;
  padding: 9px 0; border-bottom: 1px solid var(--line);
}
.pick-row:last-child { border-bottom: none; }
.pick-who { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.pick-who b { font-size: 13px; color: var(--t1); }
.pick-meta { font-size: 11px; flex: none; }

.rec-list { display: flex; flex-direction: column; gap: 10px; }
.rec-row { display: flex; align-items: center; gap: 16px; padding: 14px 18px; }
.rec-date { flex: none; width: 56px; text-align: center; }
.rec-date b { display: block; font-family: var(--silk); font-size: 15px; color: var(--lime); }
.rec-date span { font-size: 11px; color: var(--t3); }
.rec-body { flex: 1; }

.achv-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.achv-card { padding: 18px; display: flex; flex-direction: column; gap: 6px; align-items: flex-start; }
.achv-card b { font-size: 14px; color: var(--t1); }
.a-icon { font-size: 26px; }
.a-desc { font-size: 12px; color: var(--t3); }
.a-bar { width: 100%; height: 6px; background: var(--bg); border: 1px solid var(--line); margin-top: 4px; }
.a-bar i { display: block; height: 100%; background: var(--lime); }
.a-prog { font-family: var(--silk); font-size: 10px; color: var(--lime); }
.achv-card.lock { opacity: .55; }
.achv-card.lock .a-prog { color: var(--t3); }
.achv-card.lock .a-bar i { background: var(--t4); }

.set-group { padding: 18px 22px; }
.set-group h3 { font-size: 13px; color: var(--t3); margin-bottom: 12px; letter-spacing: 1px; }
.set-row {
  display: flex; align-items: center; gap: 16px;
  padding: 10px 0; border-bottom: 1px solid var(--line);
}
.set-row:last-of-type { border-bottom: none; }
.set-row label { width: 150px; flex: none; font-size: 13px; color: var(--t1); }
.set-row input {
  flex: 1; max-width: 260px;
  background: var(--bg); border: 1px solid var(--line);
  padding: 8px 12px; color: var(--t1); font-size: 13px; outline: none;
}
.set-row input:focus { border-color: var(--lime); }
.diffs { display: flex; gap: 8px; }
.set-actions { display: flex; align-items: center; gap: 14px; margin-top: 14px; }
.save {
  background: var(--lime); border: none;
  padding: 10px 26px;
  font-family: var(--silk); font-size: 12px; font-weight: 700;
  color: #0B0B0B; cursor: pointer;
}
.save:hover:not(:disabled) { box-shadow: var(--sh-ink-4); }
.save:disabled { opacity: .5; cursor: default; }

@media (max-width: 820px) {
  /* 移动端骨架对齐 .m-screen：安全区 + 480 版心 + 16px 页边距 */
  .screen { padding-top: var(--sat); max-width: 480px; margin: 0 auto; overflow-x: hidden; }
  .me-card { flex-wrap: wrap; margin: 0 16px; }
  .me-stats { margin-left: 0; width: 100%; justify-content: space-between; gap: 12px; }
  .me-body { grid-template-columns: 1fr; margin: 20px 16px 0; }
  .fav-grid, .gear-grid { grid-template-columns: 1fr; }
  .achv-grid { grid-template-columns: 1fr 1fr; }
  .set-row label { width: 110px; }
}
</style>
