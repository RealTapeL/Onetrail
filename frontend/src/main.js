import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { installLogger } from './api/logger'
import './styles/main.css'

installLogger()
createApp(App).use(router).mount('#app')
