<script setup>
/** 登录 / 注册（桌面与移动共用，响应式） */
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { loginWith, registerWith } from '../api/http'
import { syncTbtiFromAccount } from '../composables/tbti'

const route = useRoute()
const router = useRouter()
const mode = ref('login') // login | register
const form = reactive({ email: '', password: '', displayName: '' })
const submitting = ref(false)
const errorMsg = ref('')

const submit = async () => {
  if (submitting.value) return
  errorMsg.value = ''
  if (!form.email.trim() || !form.password) {
    errorMsg.value = '请填写邮箱和密码'
    return
  }
  if (mode.value === 'register' && !form.displayName.trim()) {
    errorMsg.value = '注册需要填写昵称'
    return
  }
  submitting.value = true
  try {
    if (mode.value === 'login') {
      await loginWith(form.email.trim(), form.password)
    } else {
      await registerWith(form.email.trim(), form.password, form.displayName.trim())
    }
    await syncTbtiFromAccount()
    // 有回跳目标（未登录被拦到登录页的场景）则返回原页面
    router.push(typeof route.query.redirect === 'string' ? route.query.redirect : '/plan')
  } catch (err) {
    errorMsg.value = err.message || '操作失败，请稍后重试'
  } finally {
    submitting.value = false
    form.password = '' // 页面被 KeepAlive 缓存，避免密码残留
  }
}

const switchMode = () => {
  mode.value = mode.value === 'login' ? 'register' : 'login'
  errorMsg.value = ''
}

</script>

<template>
  <div class="login-screen">
    <div class="card">
      <div class="brand">
        <svg class="mark" viewBox="0 0 20 20">
          <rect width="20" height="20" style="fill: var(--brand-deep)" />
          <rect x="9" y="4" width="3" height="3" fill="#FFF" /><rect x="6" y="7" width="3" height="3" fill="#FFF" />
          <rect x="12" y="7" width="3" height="3" fill="#FFF" /><rect x="3" y="10" width="3" height="3" fill="#FFF" />
          <rect x="9" y="10" width="3" height="3" fill="#FFF" /><rect x="15" y="10" width="3" height="3" fill="#FFF" />
        </svg>
        <span class="en">ONE TRAIL</span>
      </div>
      <h1 class="title">{{ mode === 'login' ? '欢迎回来' : '创建账号' }}</h1>
      <div class="sub">{{ mode === 'login' ? '登录后继续你的徒步计划' : '注册后即可收藏路线、打卡积累能力画像' }}</div>

      <label class="lb">邮箱 · EMAIL</label>
      <input v-model="form.email" type="email" class="in" placeholder="you@example.com" @keyup.enter="submit" />
      <label v-if="mode === 'register'" class="lb">昵称 · NAME</label>
      <input v-if="mode === 'register'" v-model="form.displayName" class="in" placeholder="阿绿" @keyup.enter="submit" />
      <label class="lb">密码 · PASSWORD</label>
      <input v-model="form.password" type="password" class="in" placeholder="至少 12 位" @keyup.enter="submit" />

      <div v-if="errorMsg" class="err">{{ errorMsg }}</div>

      <button class="cta" :disabled="submitting" @click="submit">
        {{ submitting ? '请稍候…' : mode === 'login' ? '登 录' : '注册并登录' }}
      </button>
      <button class="switch" @click="switchMode">
        {{ mode === 'login' ? '没有账号？去注册 →' : '已有账号？去登录 →' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.login-screen {
  position: fixed;
  inset: 0;
  overflow-y: auto;
  overscroll-behavior: none; /* 安卓 WebView 内禁止整页拖动/回弹 */
  display: flex;
  background: var(--bg);
  padding: 24px;
}
.card {
  margin: auto; /* flex + margin:auto 居中，内容超高时顶部仍可正常滚动到 */
  width: 400px;
  max-width: 100%;
  background: #FFFFFF;
  border: 2px solid var(--ink);
  box-shadow: var(--sh-lime-6);
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.brand { display: flex; align-items: center; gap: 10px; }
.mark { width: 24px; height: 24px; }
.en { font-family: var(--p8); font-size: 10px; color: var(--ink); }
.title { font-size: 26px; font-weight: 900; color: var(--ink); }
.sub { font-size: 13px; color: var(--t3); margin-bottom: 6px; }
.lb { font-size: 11px; font-weight: 500; color: var(--t3); }
.in {
  border: 1px solid var(--line-soft);
  background: #FFF;
  font-size: 14px;
  font-weight: 700;
  color: var(--ink);
  padding: 10px 12px;
  width: 100%;
}
.in:focus { outline: none; border-color: var(--ink); }
.err { font-size: 12px; color: var(--red); }
.cta {
  margin-top: 6px;
  height: 48px;
  background: var(--lime);
  border: 2px solid var(--ink);
  box-shadow: var(--sh-ink-3);
  font-size: 15px;
  font-weight: 900;
  color: var(--ink);
}
.cta:disabled { opacity: 0.6; }
.switch { font-size: 12px; font-weight: 500; color: var(--t3); padding: 4px; }
.switch:hover { color: var(--ink); }

/* 移动端：整体缩小，避免一屏放不下 */
@media (max-width: 520px) {
  .card { padding: 20px; gap: 8px; }
  .title { font-size: 21px; }
  .sub { font-size: 12px; margin-bottom: 2px; }
  .in { padding: 8px 10px; font-size: 13px; }
  .cta { height: 42px; font-size: 14px; }
  .demo { height: 36px; font-size: 12px; }
}
.demo {
  margin-top: 4px;
  height: 40px;
  background: #FFFFFF;
  border: 2px dashed var(--ink);
  font-size: 13px;
  font-weight: 700;
  color: var(--ink);
}
.demo:hover { background: var(--lime); }
</style>
