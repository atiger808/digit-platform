<template>
  <div class="app">
    <el-config-provider :locale="zhCn">

      <router-view/>


    </el-config-provider>
  </div>
</template>

<script setup lang="ts">
// 国际化配置
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
</script>

<style scoped>
.app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  height: 100vh;
  overflow: hidden;
}

</style>