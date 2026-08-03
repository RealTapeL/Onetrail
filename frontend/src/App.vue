<script setup>
/** ONE TRAIL 原型 · vue-router 驱动
 *  路由与页面归属见 docs/SITEMAP.md；数据层 src/api/index.js 已接真实后端
 */
import { onMounted } from 'vue'
import { ensureSession } from './api/http'
import { syncTbtiFromAccount } from './composables/tbti'

onMounted(async () => {
  await ensureSession()
  syncTbtiFromAccount()
})
</script>

<template>
  <div class="stage">
    <router-view v-slot="{ Component, route }">
      <!-- KeepAlive 按路径缓存页面：侧滑/点返回后恢复原页面内容与状态，不重置 -->
      <keep-alive :max="20">
        <component :is="Component" :key="route.fullPath" />
      </keep-alive>
    </router-view>
  </div>
</template>

<style scoped>
.stage {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  background: #000;
}
</style>
