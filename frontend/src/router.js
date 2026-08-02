import { h } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { useIsMobile } from './composables/useIsMobile'
import { hasToken } from './api/http'

import LoginScreen from './components/LoginScreen.vue'
import RoutePublish from './components/RoutePublish.vue'
import S1Home from './components/S1Home.vue'
import S2Routes from './components/S2Routes.vue'
import S3Detail from './components/S3Detail.vue'
import S4Exec from './components/S4Exec.vue'
import S5Library from './components/S5Library.vue'
import S6Gear from './components/S6Gear.vue'

import MPlan from './components/mobile/MPlan.vue'
import MPlanResults from './components/mobile/MPlanResults.vue'
import MRoutes from './components/mobile/MRoutes.vue'
import MRouteDetail from './components/mobile/MRouteDetail.vue'
import MTrip from './components/mobile/MTrip.vue'
import MGear from './components/mobile/MGear.vue'

/** 按设备渲染桌面版或移动版（结构对齐 docs/SITEMAP.md） */
const byDevice = (desktop, mobile) => ({
  setup() {
    const isMobile = useIsMobile()
    return () => h(isMobile.value ? mobile : desktop)
  }
})

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/plan' },
    { path: '/login', component: LoginScreen, meta: { title: '登录' } },
    { path: '/plan', component: byDevice(S1Home, MPlan), meta: { bundle: 'plan', title: '开始规划' } },
    { path: '/plan/results', component: byDevice(S2Routes, MPlanResults), meta: { bundle: 'plan', title: '推荐结果' } },
    { path: '/routes', component: byDevice(S5Library, MRoutes), meta: { bundle: 'library', title: '路线库' } },
    { path: '/routes/new', component: RoutePublish, meta: { bundle: 'library', title: '发布路线' } },
    { path: '/routes/:id', component: byDevice(S3Detail, MRouteDetail), meta: { bundle: 'library', title: '路线详情' } },
    { path: '/trip/current', component: byDevice(S4Exec, MTrip), meta: { bundle: 'trip', title: '我的行程' } },
    { path: '/gear', component: byDevice(S6Gear, MGear), meta: { bundle: 'gear', title: '装备' } },
    { path: '/:pathMatch(.*)*', redirect: '/plan' }
  ],
  scrollBehavior: () => ({ top: 0 })
})

// 未登录一律先走登录/注册页
router.beforeEach((to) => {
  if (to.path !== '/login' && !hasToken()) return '/login'
  return true
})

export default router
