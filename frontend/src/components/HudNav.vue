<script setup>
/**
 * HUD Nav · Web 顶部导航（对齐 Ardot 组件 6:4）
 * 菜单对齐束状 IA：开始规划 / 路线库 / 我的行程 / 装备
 * 激活态由路由 meta.bundle 决定
 * 右侧用户 chip 点击弹出个人浮窗（收藏/装备/记录/设置 + 个人主页入口 + 退出）
 */
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { session, logout } from '../api/http'
import { clearTbti } from '../composables/tbti'

const route = useRoute()
const router = useRouter()
const active = computed(() => route.meta.bundle || 'plan')

const popOpen = ref(false)
const initial = computed(() => (session.user?.display_name || '·').slice(0, 1))

function togglePop() {
  if (!session.user) return
  popOpen.value = !popOpen.value
}
function closePop() {
  popOpen.value = false
}
function onDocClick(e) {
  if (!e.target.closest('.userzone')) closePop()
}
onMounted(() => document.addEventListener('click', onDocClick))
onBeforeUnmount(() => document.removeEventListener('click', onDocClick))

/** 浮窗菜单 → 个人主页对应板块 */
function goto(tab) {
  closePop()
  router.push(tab === 'home' ? '/me' : `/me?tab=${tab}`)
}

function onLogout() {
  closePop()
  logout()
  clearTbti()
  router.push('/login')
}

const menus = [
  { key: 'plan', label: '开始规划', to: '/plan' },
  { key: 'library', label: '路线库', to: '/routes' },
  { key: 'trip', label: '我的行程', to: '/trip/current' },
  { key: 'gear', label: '装备', to: '/gear' }
]

const popMenus = [
  { tab: 'fav', label: '收藏路线' },
  { tab: 'gear', label: '我的装备' },
  { tab: 'rec', label: '我记录的路线' },
  { tab: 'set', label: '设置' }
]
</script>

<template>
  <nav class="hud-nav">
    <router-link class="logo" to="/plan">
      <span class="logo-mark">
        <i v-for="p in [[12,6],[8,10],[16,10],[4,14],[12,14],[20,14]]"
           :key="p.join(',')" :style="{ left: p[0]+'px', top: p[1]+'px' }" />
      </span>
      <span class="logo-cn">一径</span>
      <span class="logo-en">ONE TRAIL</span>
    </router-link>

    <div class="menu">
      <router-link v-for="m in menus" :key="m.key"
                   class="mi" :class="{ on: active === m.key }"
                   :to="m.to">{{ m.label }}</router-link>
    </div>

    <div class="right">
      <div class="userzone">
        <button class="user" :class="{ open: popOpen }" @click.stop="togglePop">
          <i class="dot" :class="{ off: !session.user }" />{{ session.user ? session.user.display_name : '连接中…' }}
          <span class="caret" :class="{ up: popOpen }" />
        </button>

        <!-- 个人浮窗 -->
        <transition name="pop">
          <div v-if="popOpen" class="popover" @click.stop>
            <div class="p-head">
              <span class="p-ava">{{ initial }}</span>
              <div class="p-who">
                <b>{{ session.user.display_name }}</b>
                <span>{{ session.user.email }}</span>
              </div>
            </div>
            <div class="p-menu">
              <button v-for="m in popMenus" :key="m.tab" class="p-item" @click="goto(m.tab)">
                {{ m.label }}<i class="arr">→</i>
              </button>
            </div>
            <button class="p-home" @click="goto('home')">查看个人主页 →</button>
            <button class="p-quit" @click="onLogout">退出登录</button>
          </div>
        </transition>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.hud-nav {
  width: 100%;
  height: 72px;
  padding: 0 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  background: var(--bg);
  flex: none;
}
.logo { display: flex; align-items: center; gap: 12px; cursor: pointer; text-decoration: none; }
.logo-mark { position: relative; width: 28px; height: 28px; background: #2F5B2A; flex: none; }
.logo-mark i { position: absolute; width: 4px; height: 4px; background: #FFFFFF; }
.logo-cn { font-size: 20px; font-weight: 900; color: #FFFFFF; }
.logo-en { font-family: var(--p8); font-size: 11px; color: var(--lime); }

.menu { display: flex; align-items: center; gap: 32px; flex: none; }
.mi { font-size: 14px; font-weight: 500; color: var(--t2); text-decoration: none; }
.mi.on { color: var(--lime); font-weight: 700; }
.mi:hover { color: var(--t1); }
.mi.on:hover { color: var(--lime); }

.right { display: flex; align-items: center; gap: 10px; }

/* 用户区 + 浮窗 */
.userzone { position: relative; }
.user {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--panel);
  border: 1px solid var(--line);
  padding: 8px 14px;
  font-family: var(--silk);
  font-size: 11px;
  color: var(--lime);
  cursor: pointer;
}
.user:hover, .user.open { border-color: var(--lime); }
.caret {
  width: 0; height: 0; flex: none;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 5px solid var(--t3);
  transition: transform .15s;
}
.caret.up { transform: rotate(180deg); }
.dot { width: 8px; height: 8px; background: var(--lime); flex: none; }
.dot.off { background: var(--t4); }

.popover {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: 240px;
  background: var(--panel);
  border: 1px solid var(--line);
  box-shadow: var(--sh-ink-4);
  z-index: 200;
}
.pop-enter-active, .pop-leave-active { transition: all .15s; }
.pop-enter-from, .pop-leave-to { opacity: 0; transform: translateY(-6px); }

.p-head {
  display: flex; align-items: center; gap: 12px;
  padding: 14px;
  border-bottom: 1px solid var(--line);
}
.p-ava {
  width: 40px; height: 40px; flex: none;
  display: flex; align-items: center; justify-content: center;
  background: #2F5B2A; color: var(--lime);
  font-size: 16px; font-weight: 900;
  border: 1px solid var(--lime);
}
.p-who { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.p-who b { font-size: 14px; color: var(--t1); }
.p-who span {
  font-size: 11px; color: var(--t3);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

.p-menu { padding: 6px 0; }
.p-item {
  width: 100%;
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px;
  background: none; border: none;
  font-size: 13px; color: var(--t1);
  cursor: pointer; text-align: left;
}
.p-item .arr { color: var(--t4); font-style: normal; }
.p-item:hover { background: #1E1E1E; color: var(--lime); }
.p-item:hover .arr { color: var(--lime); }

.p-home {
  width: calc(100% - 24px);
  margin: 6px 12px;
  padding: 10px;
  background: var(--lime);
  border: none;
  font-family: var(--silk);
  font-size: 11px;
  font-weight: 700;
  color: #0B0B0B;
  cursor: pointer;
}
.p-home:hover { box-shadow: 3px 3px 0 #2F5B2A; }
.p-quit {
  width: 100%;
  padding: 10px 14px;
  background: none; border: none;
  border-top: 1px solid var(--line);
  font-size: 12px; color: var(--t3);
  cursor: pointer; text-align: left;
}
.p-quit:hover { color: var(--red); }

/* 小屏（如移动端进发布路线页）：收缩菜单间距，隐藏英文标与用户 chip 防溢出 */
@media (max-width: 860px) {
  .hud-nav { padding: 0 16px; }
  .menu { gap: 16px; }
  .logo-en, .userzone { display: none; }
}
@media (max-width: 520px) {
  .menu { gap: 10px; }
  .mi { font-size: 12px; }
}
</style>
