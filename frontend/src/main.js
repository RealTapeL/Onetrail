import { createApp } from 'vue'
import { Capacitor } from '@capacitor/core'
import { StatusBar, Style } from '@capacitor/status-bar'
import { App as CapApp } from '@capacitor/app'
import App from './App.vue'
import router from './router'
import { installLogger } from './api/logger'
import './styles/main.css'

installLogger()

// 原生壳内：状态栏不与 WebView 重叠，底色与页面一致、图标用浅色（深色主题）
if (Capacitor.isNativePlatform()) {
  StatusBar.setOverlaysWebView({ overlay: false }).catch(() => {})
  StatusBar.setBackgroundColor({ color: '#0B0B0B' }).catch(() => {})
  StatusBar.setStyle({ style: Style.Light }).catch(() => {})

  // 安卓侧滑/按键返回：有历史则返回上一级，否则退出
  CapApp.addListener('backButton', ({ canGoBack }) => {
    if (canGoBack) window.history.back()
    else CapApp.exitApp()
  }).catch(() => {})
}

createApp(App).use(router).mount('#app')
