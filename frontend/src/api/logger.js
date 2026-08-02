/**
 * ONE TRAIL · 前端错误上报
 * 捕获未处理异常 / Promise 拒绝 / 关键 API 失败，上报到后端写入 logs/frontend.log。
 * 上报本身失败时静默忽略，避免递归报错。
 */

const ENDPOINT = '/api/v1/logs/client'

export function reportError(message, { level = 'error', stack = null } = {}) {
  const payload = JSON.stringify({
    level,
    message: String(message),
    stack,
    url: window.location.pathname + window.location.search,
    ts: new Date().toISOString()
  })
  try {
    if (navigator.sendBeacon) {
      navigator.sendBeacon(ENDPOINT, new Blob([payload], { type: 'application/json' }))
    } else {
      fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: payload, keepalive: true })
    }
  } catch { /* 上报失败静默 */ }
}

export function installLogger() {
  window.addEventListener('error', (event) => {
    reportError(event.message, { stack: event.error?.stack ?? null })
  })
  window.addEventListener('unhandledrejection', (event) => {
    const reason = event.reason
    reportError(reason?.message ?? String(reason), { stack: reason?.stack ?? null })
  })
}
