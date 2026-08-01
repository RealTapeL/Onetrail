<script setup>
/** ONE TRAIL 原型 · vue-router 驱动
 *  路由与页面归属见 docs/SITEMAP.md；数据层见 src/api/mock.js（后端按 docs/API.md 替换）
 */
</script>

<template>
  <div class="stage">
    <router-view />
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
