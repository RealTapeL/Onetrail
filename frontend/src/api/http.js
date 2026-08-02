/**
 * ONE TRAIL · HTTP 基础设施
 * fetch 封装（/api/v1、Bearer token）+ 预设演示账号自动登录。
 */
import { reactive } from 'vue'
import { reportError } from './logger'

const BASE = '/api/v1'

// 上报豁免：日志端点自身失败不再上报，避免循环
const isLogEndpoint = (path) => path.startsWith('/logs/')

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
