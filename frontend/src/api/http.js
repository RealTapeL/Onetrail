/**
 * ONE TRAIL · HTTP 基础设施
 * fetch 封装（/api/v1、Bearer token）+ 预设演示账号自动登录。
 */
import { reactive } from 'vue'

const BASE = '/api/v1'

// 预设的演示账号：首次启动自动注册，之后直接登录。
const ADMIN = { email: 'admin@onetrail.dev', password: 'admin123456', display_name: 'admin' }

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
  const token = localStorage.getItem('ot_token')
  if (auth && token) headers.Authorization = `Bearer ${token}`
  const response = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body)
  })
  if (!response.ok) {
    let message = `请求失败（${response.status}）`
    try {
      const data = await response.json()
      if (typeof data.detail === 'string') message = data.detail
    } catch { /* keep default message */ }
    throw new ApiError(response.status, message)
  }
  if (response.status === 204) return null
  return response.json()
}

async function login() {
  const data = await api('/auth/login', {
    method: 'POST',
    auth: false,
    body: { email: ADMIN.email, password: ADMIN.password }
  })
  return data.access_token
}

export async function ensureSession() {
  if (session.ready) return
  try {
    let token
    try {
      token = await login()
    } catch {
      await api('/auth/register', {
        method: 'POST',
        auth: false,
        body: { email: ADMIN.email, password: ADMIN.password, display_name: ADMIN.display_name }
      })
      token = await login()
    }
    localStorage.setItem('ot_token', token)
    session.user = await api('/profile/me')
    session.error = null
  } catch (err) {
    session.error = err.message || '后端连接失败'
  } finally {
    session.ready = true
  }
}
