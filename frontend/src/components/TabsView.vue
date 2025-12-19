<template>
  <div class="tabs-container">
    <div
      v-for="tab in tabs"
      :key="tab.path"
      :class="['tab-item', { active: currentTab === tab.path }]"
      @click="handleTabClick(tab.path)"
    >
      <span>{{ tab.title }}</span>
      <el-icon @click.stop="handleTabClose(tab.path)">
        <Close />
      </el-icon>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Close } from '@element-plus/icons-vue'
import { useTabsStore } from '@/store/main/tabs/tabs.ts'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'

const router = useRouter()
const tabsStore = useTabsStore()
const { tabs, currentTab } = storeToRefs(tabsStore)

const handleTabClick = (path: string) => {
  router.push(path)
}

const handleTabClose = (path: string) => {
  tabsStore.removeTab(path)
  if (currentTab.value === path) {
    const lastTab = tabs.value[tabs.value.length - 1]
    if (lastTab) {
      router.push(lastTab.path)
    } else {
      router.push('/')
    }
  }
}
</script>

<style scoped>
.tabs-container {
  display: flex;
  background: #fff;
  padding: 8px;
  border-bottom: 1px solid #e6e6e6;
}
.tab-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  margin-right: 4px;
  border: 1px solid #e6e6e6;
  cursor: pointer;
}
.tab-item.active {
  border-bottom: 2px solid #409eff;
}
</style>