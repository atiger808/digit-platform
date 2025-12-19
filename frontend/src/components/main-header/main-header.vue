<script setup lang="ts">
import {ref} from 'vue'
import HeaderInfo from './c-cpns/header-info.vue'
import HeaderCrumb from './c-cpns/header-breadcrumb.vue'

const isFold = ref(false)

// 0.自定义事件
const emit = defineEmits(['foldChange'])


const handleFoldClick = () => {
  // 1.内部改变状态
  isFold.value = !isFold.value

  // 2.将事件和状态传递给父组件
  emit('foldChange', isFold.value)
}

</script>

<template>
  <div class="main-header">
    <div class="menu-icon" @click="handleFoldClick">
      <el-icon size="28px">
        <component :is="isFold ? 'Expand' : 'Fold'"/>
      </el-icon>
    </div>

    <div class="content">
      <header-crumb/>
      <HeaderInfo/>
    </div>
  </div>
</template>

<style scoped lang="scss">

.main-header {
  display: flex;
  align-items: center;
  flex: 1;
  height: 100%;

  .menu-icon {
    display: flex;
    align-items: center;
    cursor: pointer;
  }

  .content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex: 1;
    padding: 0 18px;
  }

}

</style>