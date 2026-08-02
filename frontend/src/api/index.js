/**
 * ONE TRAIL · 真实数据层
 *
 * 所有 loader 直连后端真实接口（见 docs/API.md v0.2 对齐说明），
 * 返回组件直接可用的视图结构；无真实来源的内容保留静态展示并标注"示意/演示"。
 */
import { reactive } from 'vue'
import { api } from './http'

const COVERS_TOP = ['/images/2_469.webp', '/images/2_470.webp', '/images/2_471.webp']
const THUMBS_ALT = ['/images/2_472.webp', '/images/2_473.webp']
const COVERS_LIB = ['/images/2_388.webp', '/images/2_392.webp', '/images/2_396.webp', '/images/2_400.webp', '/images/2_404.webp', '/images/2_408.webp']
const COVERS_GEAR = ['/images/2_448.webp', '/images/2_452.webp', '/images/2_458.webp']

const GEAR_CATEGORIES = [
  { label: '背包', value: 'backpack' },
  { label: '徒步鞋', value: 'footwear' },
  { label: '帐篷', value: 'tent' },
  { label: '睡袋', value: 'sleeping_bag' }
]

/** S1/M1 表单默认值（v-model 绑定此形状的副本；日期默认今天，高德预报仅覆盖未来约 3 天） */
const todayStr = () => new Date().toLocaleDateString('sv-SE')

export const questFormDefaults = {
  dateRange: { start: todayStr() },
  location: { city: '杭州', district: '西湖区', lat: 30.25, lng: 120.13, useCurrentPosition: false },
  party: { adults: 2 },
  budgetPerPerson: { max: 500 },
  fitnessLevel: 3,
  interests: ['瀑布', '竹林'],
  ownedGear: ['登山鞋', '背包', '登山杖']
}

/** 跨页共享状态：S1 提交后写入，S2/S4 消费 */
export const state = reactive({
  recommendation: null, // 视图结构（同 mock.recommendation）
  planByRouteId: {}, // routeId -> 后端 RecommendedRoute 原始对象（S4 数据源）
  selectedRouteId: null,
  budgetCny: null, // S1 提交的预算，S6 GAP PICKS 使用
  travelDate: null, // S1 提交的出行日期（buildPlan 标题用）
  groupSize: null // S1 提交的同行人数（buildPlan 标题用）
})

/** 推荐快照持久化：刷新页面后「推荐结果/我的行程」仍可恢复 */
const PLAN_SNAPSHOT_KEY = 'ot_plan_snapshot'

function persistPlan() {
  try {
    localStorage.setItem(PLAN_SNAPSHOT_KEY, JSON.stringify({
      recommendation: state.recommendation,
      planByRouteId: state.planByRouteId,
      selectedRouteId: state.selectedRouteId,
      budgetCny: state.budgetCny,
      travelDate: state.travelDate,
      groupSize: state.groupSize
    }))
  } catch { /* 存储失败不影响使用 */ }
}

;(function restorePlan() {
  try {
    const raw = localStorage.getItem(PLAN_SNAPSHOT_KEY)
    if (!raw) return
    const snap = JSON.parse(raw)
    state.recommendation = snap.recommendation || null
    state.planByRouteId = snap.planByRouteId || {}
    state.selectedRouteId = snap.selectedRouteId || null
    state.budgetCny = snap.budgetCny ?? null
    state.travelDate = snap.travelDate ?? null
    state.groupSize = snap.groupSize ?? null
  } catch { /* 快照损坏则忽略 */ }
})()

/** GET /meta/brand-stats → [{num, label}] */
export async function fetchBrandStats() {
  const data = await api('/meta/brand-stats', { auth: false })
  return [
    { num: String(data.routeCount), label: '条精选路线' },
    { num: String(data.hikerCount), label: '徒步者在用' },
    { num: String(data.cityCount), label: '座城市覆盖' }
  ]
}

// 体能等级 → 距离/爬升上限（传给推荐引擎做硬筛选）
const FITNESS_LIMITS = {
  1: { max_distance_km: 5, max_elevation_gain_m: 200 },
  2: { max_distance_km: 8, max_elevation_gain_m: 400 },
  3: { max_distance_km: 12, max_elevation_gain_m: 600 },
  4: { max_distance_km: 16, max_elevation_gain_m: 900 },
  5: { max_distance_km: 30, max_elevation_gain_m: 2000 }
}

/** GET /meta/geocode：城市/地名 → 坐标（目的地输入用；失败时抛出真实原因，由表单展示） */
export async function geocodeCity(city) {
  if (!city || !city.trim()) return null
  try {
    return await api(`/meta/geocode?city=${encodeURIComponent(city.trim())}`, { auth: false })
  } catch (err) {
    throw new Error(`目的地「${city.trim()}」解析失败：${err.message || '服务暂不可用'}`)
  }
}

/** 高德天气可预报窗口：今天 ~ 今天+3 天（后端按出行日精确匹配预报，超出会 502） */
export const FORECAST_MIN_DATE = todayStr()
export const FORECAST_MAX_DATE = new Date(Date.now() + 3 * 86400000).toLocaleDateString('sv-SE')

/**
 * POST /recommendations/plan（S1 表单提交）
 * 返回视图结构（同 mock.recommendation），并写入共享状态供 S2/S4 使用。
 */
export async function postRecommendations(form) {
  if (!form.dateRange.start) throw new Error('请选择出行日期')
  // 预报窗口按提交时现算（模块级常量仅是 input 的 min/max 展示用，刷新前不更新）
  const forecastMin = todayStr()
  const forecastMax = new Date(Date.now() + 3 * 86400000).toLocaleDateString('sv-SE')
  if (form.dateRange.start < forecastMin || form.dateRange.start > forecastMax) {
    throw new Error(`天气只可预报 ${forecastMin} ~ ${forecastMax}，请把出行日期调整到这个范围内`)
  }
  // 兴趣写入偏好画像，供推荐引擎做兴趣匹配
  await api('/profile/preferences', { method: 'PUT', body: { interests: form.interests } }).catch(() => {})
  // 未点「定位」时按城市文本解析坐标（用户手输城市不会自动改坐标）
  if (!form.location.useCurrentPosition && form.location.city.trim()) {
    const geo = await geocodeCity(form.location.city)
    form.location.lat = geo.latitude
    form.location.lng = geo.longitude
  }
  // 已有装备按名称匹配装备目录，得到真实目录 id
  let ownedIds = []
  if (form.ownedGear.length) {
    const catalog = await api('/equipment', { auth: false }).catch(() => [])
    ownedIds = catalog
      .filter((item) => form.ownedGear.some((k) => item.name.includes(k)))
      .map((item) => item.id)
  }
  const limits = FITNESS_LIMITS[form.fitnessLevel] || FITNESS_LIMITS[3]
  const request = {
    travel_date: form.dateRange.start,
    latitude: form.location.lat,
    longitude: form.location.lng,
    group_size: form.party.adults,
    budget_cny: form.budgetPerPerson.max,
    max_distance_km: limits.max_distance_km,
    max_elevation_gain_m: limits.max_elevation_gain_m,
    owned_equipment_ids: ownedIds
  }
  const res = await api('/recommendations/plan', { method: 'POST', body: request })

  const weatherMeta = res.weather
    ? `${res.weather.weather}${res.weather.temperature_max_c != null ? ` ${res.weather.temperature_max_c}°C` : ''}`
    : ''
  const view = {
    id: `rec_${request.travel_date}`,
    conditionSummary: `${request.travel_date} · ${form.location.city} · ${form.party.adults} 人 · ¥${form.budgetPerPerson.max} · 体能 Lv.${form.fitnessLevel}`,
    notice: res.notice || '',
    top: res.routes.slice(0, 3).map((r, i) => ({
      rank: i + 1,
      routeId: r.route_id,
      name: r.title,
      img: COVERS_TOP[i % COVERS_TOP.length],
      matchScore: Math.round(r.score),
      meta: `${r.distance_km}KM · 爬升 ${r.elevation_gain_m}M · 耗时 ${Math.round(r.estimated_duration_min / 60)}H · ${weatherMeta}`,
      reasons: r.reasons.slice(0, 3),
      risk: r.risk_notes.length ? `风险提示：${r.risk_notes[0]}` : '风险提示：暂无特别提示，出发前请确认现场状况',
      tags: r.scene_tags.join(' · ')
    })),
    alternatives: res.alternates.slice(0, 2).map((r, i) => ({
      routeId: r.route_id,
      name: r.title,
      summary: `${r.region} · ${r.distance_km}KM · 匹配度 ${Math.round(r.score)}%`,
      thumb: THUMBS_ALT[i % THUMBS_ALT.length]
    })),
    // 目的地附近无路线库路线时，高德 POI 补充的真实周边徒步地
    hikingSpots: (res.hiking_spots || []).map((s) => ({
      name: s.name,
      meta: [s.address, s.distance_m != null ? `距目的地约 ${(s.distance_m / 1000).toFixed(1)}KM` : null]
        .filter(Boolean)
        .join(' · ')
    }))
  }
  state.recommendation = view
  state.planByRouteId = Object.fromEntries(res.routes.map((r) => [r.route_id, r]))
  state.budgetCny = request.budget_cny
  state.travelDate = request.travel_date
  state.groupSize = request.group_size
  persistPlan()
  return view
}

/** GET /routes/{id} + /routes/{id}/reviews → 视图结构（同 mock.routeDetail） */
export async function fetchRouteDetail(routeId) {
  state.selectedRouteId = routeId
  persistPlan()
  const [detail, reviewList] = await Promise.all([
    api(`/routes/${routeId}`, { auth: false }),
    api(`/routes/${routeId}/reviews`, { auth: false })
  ])
  // 非推荐来源（路线库/收藏）进入详情时补一份最小计划数据，「加入出行计划」不再落空页
  if (!state.planByRouteId[detail.id]) {
    state.planByRouteId[detail.id] = {
      route_id: detail.id,
      title: detail.title,
      distance_km: detail.distance_km,
      estimated_duration_min: detail.estimated_duration_min,
      elevation_gain_m: detail.elevation_gain_m,
      transport_options: [],
      supply_points: [],
      equipment_suggestions: []
    }
    persistPlan()
  }
  const total = detail.review_count || 0
  const avg = detail.average_rating
  return {
    id: detail.id,
    name: detail.title,
    coverImage: '/images/2_206.webp',
    stats: [
      { label: '距离 · DIST', value: `${detail.distance_km}KM` },
      { label: '爬升 · ELEV', value: `${detail.elevation_gain_m}M` },
      { label: '耗时 · TIME', value: `${Math.round(detail.estimated_duration_min / 60)}H` },
      { label: '难度 · LEVEL', value: `Lv.${detail.level}` }
    ],
    terrain: {
      tags: detail.tags.map((t) => ({
        label: t.name,
        warning: t.category === 'safety' || Boolean(t.safety_note),
        note: t.safety_note || null
      })),
      safetyNotes: detail.tags
        .filter((t) => t.safety_note)
        .map((t) => ({ label: t.name, note: t.safety_note })),
      safetyTip: '安全提示：暂无标签化安全提示，请出发前确认现场状况。'
    },
    videoUrl: detail.video_url || null,
    reviews: reviewList.map((r) => ({
      id: r.id,
      author: '徒步者',
      rating: r.rating,
      visitedAt: r.created_at ? r.created_at.slice(0, 10) : '',
      content: r.content || '（未填写评价内容）'
    })),
    vibeVote: detail.impression_stats.map((s) => {
      const percent = total ? Math.min(100, Math.round((s.count / total) * 100)) : 0
      return { label: s.tag, percent, lime: percent >= 60 }
    }),
    suitableFor: detail.suitable_for || '暂无标注',
    verdict: total
      ? { worth: avg >= 4, text: avg >= 4 ? '值得去' : '再想想', voteCount: total }
      : { worth: false, text: '暂无评价', voteCount: 0 }
  }
}

/** 收藏 / 取消收藏 */
export async function setFavorite(routeId, favored) {
  await api(`/routes/${routeId}/favorite`, { method: favored ? 'POST' : 'DELETE' })
}

/** POST /routes/{id}/reviews：写评价 + 气质投票（impression_tags 聚合为投票统计） */
export async function postRouteReview(routeId, { rating, content, impressionTags }) {
  await api(`/routes/${routeId}/reviews`, {
    method: 'POST',
    body: { rating, content: content || null, impression_tags: impressionTags }
  })
}

/** POST /history：徒步打卡（反哺推荐引擎的能力画像） */
export async function postActivity({ routeId, distanceKm, elevationGainM, durationMin, rating }) {
  await api('/history', {
    method: 'POST',
    body: {
      route_id: routeId ?? null,
      completed_on: todayStr(),
      distance_km: distanceKm,
      elevation_gain_m: elevationGainM,
      duration_min: durationMin,
      rating: rating ?? null
    }
  })
}

/** 气质投票候选维度（对齐产品逻辑图：出片/故事/自然体验/体能挑战） */
export const IMPRESSION_OPTIONS = ['出片', '故事', '自然体验', '体能挑战']

/** GET /meta/community-pulse → 社区动态（热门路线 + 最新评价，真实库数据） */
export async function fetchCommunityPulse() {
  return api('/meta/community-pulse', { auth: false })
}

/** POST /routes：用户发布路线（UGC，需登录；tags 含 category/safety_note） */
export async function postRoute(payload) {
  return api('/routes', { method: 'POST', body: payload })
}

/** GET /routes → 视图结构（同 mock.routeLibrary 的 items） */
export async function fetchRouteLibrary({ query = '', tag = '', maxDistanceKm = null } = {}) {
  const params = new URLSearchParams({ page: '1', page_size: '12' })
  if (query) params.set('query', query)
  if (tag) params.set('tag', tag)
  if (maxDistanceKm) params.set('max_distance_km', String(maxDistanceKm))
  const data = await api(`/routes?${params}`, { auth: false })
  return {
    total: data.total,
    items: data.items.map((r, i) => ({
      id: r.id,
      img: COVERS_LIB[i % COVERS_LIB.length],
      name: r.title,
      meta: `${r.distance_km}KM · 爬升 ${r.elevation_gain_m}M · Lv.${r.level} · ${r.average_rating != null ? `评分 ${r.average_rating}` : '暂无评分'}`
    }))
  }
}

/** GET /meta/weather-tip（未配置天气服务时返回 null） */
export async function fetchWeatherTip(latitude, longitude) {
  try {
    return await api(`/meta/weather-tip?latitude=${latitude}&longitude=${longitude}`, { auth: false })
  } catch {
    return null
  }
}

/**
 * S4 出行计划：由 S2 选中的推荐路线生成（不落库）
 * routeId 无推荐上下文时返回 null，页面显示引导。
 */
export function buildPlan(routeId) {
  const r = state.planByRouteId[routeId]
  if (!r) return null
  const date = state.travelDate
  const group = state.groupSize
  const title = date ? `${r.title} · ${date} 出发 · ${group || 1} 人` : `${r.title} · 出行计划`
  // 交通耗时取公交方案，无则驾车；用于把演示时间线换成按真实耗时估算的排期
  const transitMin =
    r.transport_options.find((t) => t.mode.includes('公交'))?.duration_min ??
    r.transport_options[0]?.duration_min ??
    null
  const fmt = (min) => `${String(Math.floor(min / 60)).padStart(2, '0')}:${String(min % 60).padStart(2, '0')}`
  const departMin = 8 * 60 + 30 // 默认 08:30 出发（界面注明为假定出发时间）
  const timeline = []
  if (transitMin != null) {
    const arriveMin = departMin + transitMin
    const finishMin = arriveMin + r.estimated_duration_min
    timeline.push(
      { time: fmt(departMin), event: '出发（假定时间，可自定）' },
      { time: fmt(arriveMin), event: `到达起点 · ${r.transport_options[0]?.mode || '交通'}约 ${transitMin} 分钟` },
      { time: fmt(finishMin), event: `走完主线 · 路线预计 ${Math.round(r.estimated_duration_min / 60)}H` },
      { time: fmt(finishMin + transitMin), event: '返程回到市区' }
    )
  }
  return {
    id: `plan_${routeId}`,
    title,
    transit: r.transport_options.map((t) => ({
      type: t.mode.includes('公交') || t.mode.includes('地铁') ? 'metro' : 'bus',
      line: `${t.mode} · ${t.summary}`,
      detail:
        [t.distance_km != null ? `${t.distance_km}KM` : null, t.duration_min != null ? `约 ${t.duration_min} 分钟` : null]
          .filter(Boolean)
          .join(' · ') || '以高德实时方案为准',
      steps: t.steps || []
    })),
    transitTip: '交通方案与换乘步骤来自高德实时规划，请以出行当日查询为准',
    // 时间线由高德交通耗时 + 路线预计耗时推算（无固定班次数据，已注明假定出发点）
    timeline,
    timelineNote: transitMin != null
      ? `按高德交通耗时与路线预计 ${Math.round(r.estimated_duration_min / 60)}H 耗时估算，出发时间为假定 08:30`
      : '暂无交通耗时数据，无法估算排期，请按实际情况安排',
    supplyText: r.supply_points.length
      ? r.supply_points
          .slice(0, 6)
          .map((p, i) => `S${i + 1} ${p.name} · ${p.category}${p.distance_m != null ? ` · 距起点 ${Math.round(p.distance_m)}M` : ''}`)
          .join('\n')
      : '起点 3KM 内未查询到补给点，请提前备足饮水。',
    checklist: r.equipment_suggestions.map((s) => ({ item: `${s.name} · ${s.reason}`, owned: false })),
    elevation: { caption: `累计爬升 ${r.elevation_gain_m}M · 海拔剖面为示意图，非实测轨迹` }
  }
}

/** GET /equipment?category= → 视图结构（同 mock.gearCompare.items） */
export async function fetchGearCompare(categoryValue) {
  const items = await api(`/equipment?category=${categoryValue}`, { auth: false })
  const bestId = items.reduce(
    (best, g) => (g.average_rating != null && (best == null || g.average_rating > best.average_rating) ? g : best),
    null
  )?.id
  return items.slice(0, 3).map((g, i) => ({
    id: g.id,
    img: g.image_url || COVERS_GEAR[i % COVERS_GEAR.length],
    name: g.name,
    best: g.id === bestId && g.average_rating != null,
    sourceUrl: g.source_url || null,
    specs: [
      g.price_cny != null ? `价格 ¥${g.price_cny}` : '价格 暂无',
      g.weight_g != null ? `重量 ${(g.weight_g / 1000).toFixed(1)}KG` : '重量 暂无',
      `防水 ${g.specifications?.防水 ?? '暂无参数'}`,
      `适合 ${g.suitable_scenarios.join(' · ') || '通用'}`,
      g.average_rating != null ? `用户评分 ${g.average_rating}` : '暂无评分',
      g.specifications?.官网港币价 ? `官网价 ${g.specifications.官网港币价}` : null
    ].filter(Boolean)
  }))
}

/** GAP PICKS：其他品类中预算内最低价 3 件（真实目录） */
export async function fetchGapPicks(excludeCategoryValue, budgetMax = 500) {
  const catalog = await api('/equipment', { auth: false })
  const labelOf = (v) => GEAR_CATEGORIES.find((c) => c.value === v)?.label || v
  return catalog
    .filter((g) => g.category !== excludeCategoryValue && g.price_cny != null && g.price_cny <= budgetMax)
    .sort((a, b) => a.price_cny - b.price_cny)
    .slice(0, 3)
    .map((g) => ({
      name: `${labelOf(g.category)} · ${g.name}`,
      meta: g.suitable_scenarios.join(' · ') || (g.weight_g != null ? `约 ${(g.weight_g / 1000).toFixed(1)}KG` : '通用场景'),
      price: `¥${g.price_cny}`
    }))
}

/** GET /equipment/reviews/summary → 视图结构（同 mock.gearReviews） */
export async function fetchGearReviews() {
  const data = await api('/equipment/reviews/summary', { auth: false })
  return {
    totalCount: data.total_count,
    quote: data.sample
      ? `「${data.sample.quote}」—— ${data.sample.equipment_name} 的真实评价`
      : '暂无真实评价，欢迎提交第一条装备反馈'
  }
}

export { GEAR_CATEGORIES }
