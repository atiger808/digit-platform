<script setup lang="ts">

defineProps({
  title: {
    type: String,
    default: '卡片头部标题'
  },
})

</script>

<template>
  <div class="chart-card">
    <el-card shadow="hover" class="base-card">
      <template #header>
        <div class="card-header">
          <span>{{ title }}</span>
          <slot name="header-extra"></slot>
        </div>
      </template>

      <!-- 默认插槽用于放置主要内容 -->
      <div class="item">
        <slot></slot>
      </div>

      <!-- 可选的底部插槽 -->
      <template v-if="$slots.footer" #footer>
        <slot name="footer"></slot>
      </template>


    </el-card>
  </div>
</template>

<style scoped lang="scss">

.chart-card {

  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.base-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>