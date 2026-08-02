/**
 * ONE TRAIL · HTTP 基础设施
 * fetch 封装（/api/v1、Bearer token）+ 真实账号登录/注册会话。
 */
import { reactive } from 'vue'
import { reportError } from './logger'

// 本地开发走 vite 代理（/api/v1）；部署到 Vercel 时用 VITE_API_BASE 指向后端公网地址
const BASE = import.meta.env.VITE_API_BASE || '/api/v1'
const TOKEN_KEY = 'ot_token'

// 上报豁免：日志端点自身失败不再上报，避免循环
const isLogEndpoint = (path) => path.startsWith('/logs/')

export class ApiError extends Error {
  constructor(status, message) {
    super(message)
    this.status = status
  }
}

export const session = reactive({
  user: null,
  ready: false,
  error: null
})

export async function api(path, { method = 'GET', body, auth = true } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  const token = localStorage.getItem(TOKEN_KEY)
  if (auth && token) headers.Authorization = `Bearer ${token}`
  let response
  try {
    response = await fetch(`${BASE}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body)
    })
  } catch (err) {
    // 网络层失败（后端不可达等）：除日志端点外上报
    if (!isLogEndpoint(path)) reportError(`网络错误 ${method} ${path}: ${err.message}`)
    throw err
  }
  if (!response.ok) {
    let message = `请求失败（${response.status}）`
    try {
      const data = await response.json()
      if (typeof data.detail === 'string') message = data.detail
    } catch { /* keep default message */ }
    // 5xx 服务端错误上报（4xx 属业务提示，不算系统故障）
    if (response.status >= 500 && !isLogEndpoint(path)) {
      reportError(`服务端错误 ${response.status} ${method} ${path}: ${message}`)
    }
    throw new ApiError(response.status, message)
  }
  if (response.status === 204) return null
  return response.json()
}

export function hasToken() {
  return Boolean(localStorage.getItem(TOKEN_KEY))
}

/** 真实账号登录：成功则保存 token 并拉取用户信息 */
export async function loginWith(email, password) {
  const data = await api('/auth/login', { method: 'POST', auth: false, body: { email, password } })
  localStorage.setItem(TOKEN_KEY, data.access_token)
  session.user = await api('/profile/me')
  session.error = null
  session.ready = true
}

/** 真实账号注册：注册成功后自动登录 */
export async function registerWith(email, password, displayName) {
  await api('/auth/register', {
    method: 'POST',
    auth: false,
    body: { email, password, display_name: displayName }
  })
  await loginWith(email, password)
}

/** 退出登录：清除 token、会话与推荐快照（防下一用户看到上一用户数据） */
export function logout() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem('ot_plan_snapshot')
  session.user = null
  session.error = null
}

/** 已有 token 时恢复会话（刷新页面后用）；无 token 直接标记 ready */
export async function ensureSession() {
  if (session.ready) return
  if (!hasToken()) {
    session.ready = true
    return
  }
  try {
    session.user = await api('/profile/me')
    session.error = null
  } catch (err) {
    // 仅 token 失效（401/403）才清除；后端暂时不可达时保留 token
    if (err instanceof ApiError && (err.status === 401 || err.status === 403)) {
      localStorage.removeItem(TOKEN_KEY)
    }
    session.error = err.message || '后端连接失败'
  } finally {
    session.ready = true
  }
}
