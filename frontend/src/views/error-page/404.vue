<template>
  <div class="error-page">
    <div class="error-content">
      <el-result icon="error" title="404" sub-title="抱歉，您访问的页面不存在">
        <template #extra>
          <el-button type="primary" @click="goHome">返回首页</el-button>
        </template>
      </el-result>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { useRouter } from 'vue-router'

const router = useRouter()
console.log(window.history.state)
const goHome = () => {
  router.push('/')
}
</script>

<style lang="scss" scoped>
.error-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;

  .error-content {
    text-align: center;
  }
}
</style>