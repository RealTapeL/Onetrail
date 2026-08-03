/**
 * TBTI（Trail-Based Type Indicator）徒步者人格测评 · 原创玩梗版
 * 16 种原创徒步梗人格：8 道题二选一，每个选项给 2 个人格加分，
 * 得分最高者判型；平分取最近一题命中的类型
 * 结果持久化 localStorage，并映射为推荐表单默认值（体能/兴趣/预算/人数/装备）
 */
import { ref } from 'vue'

const GEAR_ALL = ['登山鞋', '背包', '登山杖', '冲锋衣', '头灯', '帐篷', '睡袋', '水袋']

function addInterests(form, tags) {
  form.interests = [...new Set([...form.interests, ...tags])]
}

/** 16 种原创梗人格：code 仿 MBTI 四字母、name 中文称号、desc 一句话梗、apply 回填表单 */
export const TBTI_TYPES = {
  'JUAN': { name: '卷王',   desc: '里程卷死全场，15km 算热身', apply: (f) => { f.fitnessLevel = 5; addInterests(f, ['云海', '古道']) } },
  'TANG': { name: '躺者',   desc: '能躺不坐，营地人形地垫', apply: (f) => { f.fitnessLevel = 1; addInterests(f, ['瀑布', '竹林']) } },
  'NAIM': { name: '奶妈',   desc: '全队移动补给站，操碎了心', apply: (f) => { f.party.adults = 3; f.ownedGear = [...GEAR_ALL] } },
  'WOLF': { name: '独狼',   desc: '一个人才走得快，别等我', apply: (f) => { f.party.adults = 1 } },
  'JIUC': { name: '韭菜',   desc: '装备链接发来，我先买为敬', apply: (f) => { f.budgetPerPerson.max = 1500; f.ownedGear = [...GEAR_ALL] } },
  'GAI!': { name: '丐帮',   desc: '预算五十，全靠一双腿', apply: (f) => { f.budgetPerPerson.max = 200; f.ownedGear = ['登山鞋'] } },
  'HAIW': { name: '海王',   desc: '见一条爱一条，收藏夹全是路线', apply: (f) => { addInterests(f, ['瀑布', '竹林', '古道', '云海']) } },
  'LEAD': { name: '头羊',   desc: '攻略我做，队我带，跟我走', apply: (f) => { f.fitnessLevel = 4; addInterests(f, ['云海', '古道']) } },
  'SHEN': { name: '山神',   desc: '装备随缘，山顶打坐，四大皆空', apply: (f) => { f.ownedGear = []; addInterests(f, ['云海']) } },
  'JIUM': { name: '酒蒙子', desc: '上山是为了下山整两口', apply: (f) => { addInterests(f, ['云海']) } },
  'WOCC': { name: '握草机', desc: '词汇量只剩握草，但快乐是真的', apply: (f) => { addInterests(f, ['瀑布', '云海']) } },
  'MILI': { name: '米粒',   desc: '行程精确到分钟，水按毫升带', apply: (f) => { f.fitnessLevel = 3; f.budgetPerPerson.max = 600 } },
  'FOXI': { name: '佛系',   desc: '走哪算哪，都行都可以', apply: () => { /* 佛系，什么都不改 */ } },
  'ZOMB': { name: '僵尸',   desc: '走完这条就死了，下次还敢', apply: (f) => { f.fitnessLevel = 1 } },
  'HAHA': { name: '哈哈怪', desc: '全程哈哈哈，快乐传染源', apply: (f) => { f.party.adults = Math.max(f.party.adults, 2) } },
  'HAMS': { name: '仓鼠',   desc: '啥都往包里塞，万一用得上呢', apply: (f) => { f.ownedGear = [...GEAR_ALL]; f.budgetPerPerson.max = 800 } }
}

/** 8 题；每个选项给 2 个人格加分 */
export const TBTI_QUESTIONS = [
  { q: '出发前一晚，你在干嘛？',
    a: { text: '检查三遍清单，水按毫升算好', types: ['MILI', 'LEAD'] },
    b: { text: '啥也没整，明天再说', types: ['FOXI', 'ZOMB'] } },
  { q: '面对 800m 大爬升，你的内心 OS？',
    a: { text: '就这？加练！', types: ['JUAN', 'LEAD'] },
    b: { text: '现在躺下还来得及吗', types: ['TANG', 'ZOMB'] } },
  { q: '队友走崩了，你会？',
    a: { text: '包给我，水给你，饭我来做', types: ['NAIM', 'HAMS'] },
    b: { text: '你歇着，我先登顶了', types: ['WOLF', 'JUAN'] } },
  { q: '徒步群里有人晒新装备？',
    a: { text: '链接发来，已下单', types: ['JIUC', 'HAMS'] },
    b: { text: '我的解放鞋还能再战五年', types: ['GAI!', 'SHEN'] } },
  { q: '同一条路线，你会走几次？',
    a: { text: '一次就够，下一条更乖', types: ['HAIW', 'FOXI'] },
    b: { text: '反复刷，闭着眼都能走', types: ['LEAD', 'MILI'] } },
  { q: '登顶第一件事？',
    a: { text: '掏出小酒壶，整一口', types: ['JIUM', 'HAHA'] },
    b: { text: '打坐十分钟，吸收天地灵气', types: ['SHEN', 'TANG'] } },
  { q: '看到云海翻涌，你说？',
    a: { text: '握草！！握草草草！！', types: ['WOCC', 'HAHA'] },
    b: { text: '（内心毫无波澜，继续走）', types: ['ZOMB', 'WOLF'] } },
  { q: '你的徒步预算是？',
    a: { text: '装备拉满，钱不是问题', types: ['JIUC', 'HAMS'] },
    b: { text: '公交直达，干粮自带', types: ['GAI!', 'HAIW'] } }
]

const KEY = 'ot_tbti'

function load() {
  try { return JSON.parse(localStorage.getItem(KEY)) } catch { return null }
}

/** 全局共享：已测结果（null = 未测） */
export const tbtiResult = ref(load())

/** answers: 8 个选项索引（0=a / 1=b，按 TBTI_QUESTIONS 顺序）→ 判型结果 */
export function computeTbti(answers) {
  const scores = {}
  const lastHit = {}
  answers.forEach((pick, qi) => {
    const opt = pick === 0 ? TBTI_QUESTIONS[qi].a : TBTI_QUESTIONS[qi].b
    opt.types.forEach((t) => {
      scores[t] = (scores[t] || 0) + 1
      lastHit[t] = qi
    })
  })
  // 最高分获胜；平分取命中题目更靠后的类型
  const winner = Object.keys(scores).sort((x, y) =>
    scores[y] - scores[x] || lastHit[y] - lastHit[x]
  )[0] || 'FOXI'
  const def = TBTI_TYPES[winner]
  const result = {
    type: winner,
    name: def.name,
    desc: def.desc,
    testedAt: new Date().toISOString()
  }
  tbtiResult.value = result
  try { localStorage.setItem(KEY, JSON.stringify(result)) } catch { /* 存储失败不影响使用 */ }
  return result
}

export function clearTbti() {
  tbtiResult.value = null
  try { localStorage.removeItem(KEY) } catch { /* 忽略 */ }
}

/** 把测评结果映射为表单默认值（首页挂载/测完时调用） */
export function applyTbtiToForm(form) {
  const r = tbtiResult.value
  if (!r || !form) return
  TBTI_TYPES[r.type]?.apply(form)
}
