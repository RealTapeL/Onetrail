import { reactive } from 'vue'
import { api } from './api'

// 预设的演示账号：首次启动自动注册，之后直接登录。
const ADMIN = { email: 'admin@onetrail.dev', password: 'admin123456', display_name: 'admin' }

export const store = reactive({
  session: { user: null, ready: false, error: null },
  // { request, response } — S1 提交后保存，S2/S4 消费
  recommendation: null,
  selectedRouteId: null,
  // S2 选中的推荐路线对象（含交通/补给/装备建议）
  selectedPlan: null,
  gearContext: { routeTitle: null, tags: [], budget: null }
})

export async function ensureSession() {
  if (store.session.ready) return
  try {
    let token
    try {
      const data = await api('/auth/login', {
        method: 'POST',
        auth: false,
        body: { email: ADMIN.email, password: ADMIN.password }
      })
      token = data.access_token
    } catch {
      await api('/auth/register', {
        method: 'POST',
        auth: false,
        body: { email: ADMIN.email, password: ADMIN.password, display_name: ADMIN.display_name }
      })
      const data = await api('/auth/login', {
        method: 'POST',
        auth: false,
        body: { email: ADMIN.email, password: ADMIN.password }
      })
      token = data.access_token
    }
    localStorage.setItem('ot_token', token)
    store.session.user = await api('/profile/me')
    store.session.error = null
  } catch (err) {
    store.session.error = err.message || '后端连接失败'
  } finally {
    store.session.ready = true
  }
}

export function selectRoute(routeId, plan = null) {
  store.selectedRouteId = routeId
  if (plan) {
    store.selectedPlan = plan
    store.gearContext = {
      routeTitle: plan.title,
      tags: plan.scene_tags || [],
      budget: store.recommendation?.request?.budget_cny ?? null
    }
  }
}
