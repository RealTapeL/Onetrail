/**
 * ONE TRAIL · 数据层（Mock 实现）
 *
 * 本文件集中所有页面渲染所需的数据，结构对齐 docs/API.md。
 * 后端接管方式：
 *   1. 保留每个 export 的数据结构不变；
 *   2. 把对象字面量替换为 `fetch('/api/v1/...').then(r => r.json())`；
 *   3. 页面组件无需改动（目前为同步 import，换 HTTP 时在页面 setup 中改为 await 或 onMounted 拉取）。
 *
 * 每个对象上方注释标明未来对应的接口。
 */

// GET /meta/brand-stats
export const brandStats = [
  { num: '12,847', label: '条精选路线' },
  { num: '86,000+', label: '徒步者在用' },
  { num: '342', label: '座城市覆盖' }
]

// POST /recommendations 的请求体（S1/M1 表单 v-model 绑定此形状的副本）
export const questFormDefaults = {
  dateRange: { start: '2026-05-02', end: '2026-05-04', nights: 2 },
  location: { city: '杭州', district: '西湖区', lat: 30.25, lng: 120.13, useCurrentPosition: true },
  party: { adults: 2, type: 'FRIENDS' },
  budgetPerPerson: { min: 300, max: 500 },
  fitnessLevel: 3,
  interests: ['瀑布', '竹林'],
  ownedGear: ['登山鞋', '背包', '登山杖']
}

// GET /recommendations/{id}
export const recommendation = {
  id: 'rec_20260502_001',
  conditionSummary: '本周末 · 杭州 · 2 人 · ¥500 · 体能 Lv.3',
  top: [
    {
      rank: 1, routeId: 'r_jiuxi', name: '九溪十八涧 · 环线', img: '/images/2_469.webp', matchScore: 96,
      meta: '9.5KM · 爬升 320M · 耗时 4H · 晴 18°C',
      reasons: ['体能 Lv.3 匹配，爬升平缓友好', '竹林溪谷景观，命中你的兴趣', '沿途 3 处补给点，风险可控'],
      risk: '风险提示：雨后溪石湿滑，建议防滑徒步鞋',
      tags: '溪谷 · 竹林 · 新手友好'
    },
    {
      rank: 2, routeId: 'r_huihang', name: '徽杭古道 · 精华段', img: '/images/2_470.webp', matchScore: 89,
      meta: '12.5KM · 爬升 480M · 耗时 5.5H · 多云 16°C',
      reasons: ['古道人文加山景，故事性强', '难度 Lv.3 与体能刚好匹配', '民宿补给完善，适合 2 人同行'],
      risk: '风险提示：部分路段手机信号弱，提前下载离线地图',
      tags: '古道 · 人文 · 进阶'
    },
    {
      rank: 3, routeId: 'r_damingshan', name: '大明山 · 云海线', img: '/images/2_471.webp', matchScore: 82,
      meta: '8.2KM · 爬升 650M · 耗时 4.5H · 晴 15°C',
      reasons: ['云海概率 78%，出片率高', '爬升偏大，接近体能上限', '山顶补给少，需自带路餐'],
      risk: '风险提示：山顶风大，昼夜温差达 10°C',
      tags: '云海 · 出片 · 体能挑战'
    }
  ],
  alternatives: [
    { routeId: 'r_luniao', name: '鸬鸟山温泉线', summary: '轻松休闲 · 6.0KM · 温泉补给', thumb: '/images/2_472.webp' },
    { routeId: 'r_jingshan', name: '径山古道', summary: '文化禅意 · 7.8KM · 新手友好', thumb: '/images/2_473.webp' }
  ]
}

// GET /routes/{id}
export const routeDetail = {
  id: 'r_jiuxi',
  name: '九溪十八涧 · 环线',
  coverImage: '/images/2_206.webp',
  stats: [
    { label: '距离 · DIST', value: '9.5KM' },
    { label: '爬升 · ELEV', value: '320M' },
    { label: '耗时 · TIME', value: '4H' },
    { label: '难度 · LEVEL', value: 'Lv.2' }
  ],
  terrain: {
    tags: [
      { label: '垭口', warning: false },
      { label: '溪谷', warning: false },
      { label: '碎石坡', warning: false },
      { label: '涉水 ×2 处', warning: true },
      { label: '陡坡 ×1 段', warning: true }
    ],
    safetyTip: '安全提示：涉水路段雨后水位上涨，建议上午通过；碎石坡路段注意防滑。'
  },
  reviews: [
    { author: '阿绿', rating: 5, visitedAt: '上周走过', content: '溪水清澈，竹林段特别出片，带爸妈走也完全没问题。' },
    { author: '山雾散人', rating: 4, visitedAt: '3 月走过', content: '雨后涉水段水有点深，早点出发人少体验更好。' }
  ],
  vibeVote: [
    { label: '出片', percent: 86, lime: true },
    { label: '自然体验', percent: 92, lime: true },
    { label: '故事性', percent: 64, lime: false },
    { label: '体能挑战', percent: 41, lime: false }
  ],
  suitableFor: '新手友好 · 亲子出行 · 摄影爱好者',
  verdict: { worth: true, text: '值得去', voteCount: 1284 }
}

// GET /plans/{id}
export const plan = {
  id: 'p_001',
  title: '九溪十八涧环线 · 5月2日出发 · 2 人',
  transit: [
    { type: 'train', line: '高铁 · 上海虹桥 → 杭州东', detail: '07:15 – 08:06 · 二等座 ¥73' },
    { type: 'metro', line: '地铁 1 号线 · 杭州东 → 龙翔桥', detail: '25 分钟 · ¥4' },
    { type: 'bus', line: '公交 4 路 · 龙翔桥 → 九溪站', detail: '30 分钟 · ¥2 · 步行 800M 至入口' }
  ],
  transitTip: '接驳提示：返程末班公交 18:30，注意下山时间',
  timeline: [
    { time: '08:30', event: '九溪入口集合' },
    { time: '09:00', event: '出发 · 溪谷竹林段' },
    { time: '12:00', event: '龙井村 · 午餐补给' },
    { time: '15:30', event: '杨梅岭 · 到达终点' },
    { time: '17:00', event: '返程' }
  ],
  timelineNote: '全程约 4H · 点击铃铛设置出发提醒',
  supplyText: 'S1 龙井村 · 午餐/补水 · 4.2KM 处\nS2 理安寺 · 补水/休息 · 6.8KM 处\nS3 杨梅岭 · 终点补给 · 9.5KM 处',
  checklist: [
    { item: '登山鞋 · 已有', owned: true },
    { item: '背包 20L · 已有', owned: true },
    { item: '2L 饮水', owned: false },
    { item: '雨具', owned: false },
    { item: '头灯', owned: false },
    { item: '能量食品', owned: false }
  ],
  elevation: { caption: '最高海拔 420M · 累计爬升 320M · 涉水点 2 处 · 补给点 3 处' }
}

// GET /routes?keyword=&scene=
export const routeLibrary = {
  scenes: ['瀑布', '古道', '竹林', '云海', '星空'],
  activeScene: '竹林',
  filterSummary: '难度 Lv.1 – Lv.5 · 距离 ≤ 15KM · 新手 / 亲子 / 硬核 · 更多筛选 →',
  items: [
    { id: 'r_jiuxi', img: '/images/2_388.webp', name: '九溪十八涧 · 环线', meta: '9.5KM · 爬升 320M · Lv.2 · 评分 4.8' },
    { id: 'r_huihang', img: '/images/2_392.webp', name: '徽杭古道 · 精华段', meta: '12.5KM · 爬升 480M · Lv.3 · 评分 4.7' },
    { id: 'r_damingshan', img: '/images/2_396.webp', name: '大明山 · 云海线', meta: '8.2KM · 爬升 650M · Lv.4 · 评分 4.6' },
    { id: 'r_luniao', img: '/images/2_400.webp', name: '鸬鸟山温泉线', meta: '6.0KM · 爬升 180M · Lv.1 · 评分 4.5' },
    { id: 'r_jingshan', img: '/images/2_404.webp', name: '径山古道', meta: '7.8KM · 爬升 260M · Lv.2 · 评分 4.7' },
    { id: 'r_qingliang', img: '/images/2_408.webp', name: '清凉峰 · 星空线', meta: '14.0KM · 爬升 920M · Lv.5 · 评分 4.9' }
  ]
}

// GET /meta/weather-tip
export const weatherTip = { text: '本周晴好 · 适合溪谷竹林线' }

// GET /gear/compare?category=徒步鞋&routeId=r_jiuxi
export const gearCompare = {
  categories: ['背包', '徒步鞋', '帐篷', '睡袋'],
  activeCategory: '徒步鞋',
  contextSummary: '已按「九溪环线 · 溪谷涉水」生成建议',
  items: [
    { id: 'g_crispi', img: '/images/2_448.webp', name: 'CRISPI Monaco GTX', best: false,
      specs: ['价格 ¥1,899', '重量 1.4KG（单只）', '防水 GTX 全袜套', '适合 轻装 · 古道', '用户评分 4.8'] },
    { id: 'g_scarpa', img: '/images/2_452.webp', name: 'SCARPA 冈仁波齐', best: true,
      specs: ['价格 ¥1,299', '重量 1.2KG（单只）', '防水 GTX 全袜套', '适合 溪谷 · 涉水路线', '用户评分 4.7'] },
    { id: 'g_kailas', img: '/images/2_458.webp', name: '凯乐石 征途', best: false,
      specs: ['价格 ¥699', '重量 1.1KG（单只）', '防水 防泼水涂层', '适合 新手 · 轻徒步', '用户评分 4.5'] }
  ]
}

// GET /gear/gap-picks?routeId=r_jiuxi
export const gapPicks = [
  { name: '雨具 · 三峰出 15D 雨衣', meta: '防暴雨 · 仅 180G · 收纳巴掌大', price: '¥129' },
  { name: '头灯 · 奈特科尔 NU25', meta: '400 流明 · 仅 56G · USB-C 充电', price: '¥168' },
  { name: '饮水 · 驼峰 2L 水袋', meta: '快拆吸嘴 · 适配 20L 背包', price: '¥149' }
]

// GET /gear/reviews-summary
export const gearReviews = {
  totalCount: 1203,
  quote: '「冈仁波齐走溪谷两天，鞋里没进水。」—— 来自真实用户评价'
}

// GET /users/me
export const me = { nickname: '阿绿', level: 3, levelTitle: 'HIKER' }

/**
 * 模拟提交：POST /recommendations
 * 当前仅打印并返回固定 id；后端实现后换成真实请求。
 */
export async function postRecommendations(questForm) {
  console.log('[mock] POST /recommendations', questForm)
  return { recommendationId: recommendation.id }
}
