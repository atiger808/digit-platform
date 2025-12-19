<template>
  <div class="tabs-container">

    <div
        v-for="tab in tabs"
        :key="tab.path"
        :class="['tab-item', { active: currentTab === tab.path }]"
        @click="handleTabClick(tab.path)"
    >
      <span>{{ tab.title }}</span>
      <el-icon v-if="tabs.length > 1" @click.stop="handleTabClose(tab.path)">
        <Close/>
      </el-icon>
    </div>


    <!-- 下拉菜单 -->
    <el-dropdown class="tabs-dropdown-container" @command="handleTabCommand" trigger="click">

      <!--      <el-button class="tabs-dropdown" size="small" type="text">-->
      <!--        <el-icon>-->
      <!--          <ArrowDown/>-->
      <!--        </el-icon>-->
      <!--      </el-button>-->

      <div class="smart-page-tag-operate">
        <div class="smart-page-tag-operate-icon">
          <AppstoreOutlined/>
        </div>
      </div>


      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="closeOther">关闭其他</el-dropdown-item>
          <el-dropdown-item command="closeAll">关闭全部</el-dropdown-item>
          <el-dropdown-item command="closeLeft">关闭左侧</el-dropdown-item>
          <el-dropdown-item command="closeRight">关闭右侧</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup lang="ts">
import {Close, ArrowDown} from '@element-plus/icons-vue'
import {useTabsStore} from '@/store/main/tabs/tabs.ts'
import {storeToRefs} from 'pinia'
import {useRouter} from 'vue-router'
import {computed} from 'vue'
import {AppstoreOutlined} from "@ant-design/icons-vue";

const router = useRouter()
const tabsStore = useTabsStore()
const {tabs, currentTab} = storeToRefs(tabsStore)


// 当前激活的tab索引
const activeIndex = computed(() => {
  console.log('activeIndex tabs', tabs)
  return tabs.value.findIndex(tab => tab.path === currentTab.value)
})

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
      router.push('/dashboard') // 关闭后默认跳转到仪表盘
    }
  }
}

const handleTabCommand = (command: string) => {
  switch (command) {
    case 'closeOther':
      closeOtherTabs()
      break
    case 'closeAll':
      closeAllTabs()
      break
    case 'closeLeft':
      closeLeftTabs()
      break
    case 'closeRight':
      closeRightTabs()
      break
  }
}

const closeOtherTabs = () => {
  const activeTab = tabs.value[activeIndex.value]
  tabsStore.$patch({
    tabs: [activeTab],
    currentTab: activeTab.path
  })
}

const closeAllTabs = () => {
  tabsStore.$patch({
    tabs: [],
    currentTab: ''
  })

  // 先跳转到首页，再清空页签
  router.push('/main/analysis/overview').then(() => {
    tabsStore.resetTabs()

    // 添加首页到页签
    tabsStore.addTab({
      path: '/main/analysis/overview',
      meta: {title: '首页'}
    } as any)

  })

  // router.push('/main/analysis/overview') // 关闭全部后跳转到仪表盘
}

const closeLeftTabs = () => {
  const newTabs = tabs.value.slice(activeIndex.value)
  tabsStore.$patch({
    tabs: newTabs,
    currentTab: currentTab.value
  })
}

const closeRightTabs = () => {
  const newTabs = tabs.value.slice(0, activeIndex.value + 1)
  tabsStore.$patch({
    tabs: newTabs,
    currentTab: currentTab.value
  })
}
</script>

<style scoped lang="less">
.tabs-container {
  position: relative; /* 添加相对定位 */
  display: flex;
  align-items: center;
  background: #fff;
  padding: 8px 10px;
  border-bottom: 1px solid #e6e6e6;
  margin-bottom: 10px;
}

.tab-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  margin-right: 4px;
  border: 1px solid #e6e6e6;
  border-radius: 3px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.tab-item:hover {
  background-color: #f5f5f5;
}

.tab-item.active {
  border-bottom: 2px solid #409eff;
  background-color: #ecf5ff;
}

.tab-item .el-icon {
  margin-left: 5px;
  font-size: 12px;
  color: #999;
  transition: all 0.3s;
}

.tab-item .el-icon:hover {
  color: #666;
  background-color: #e6e6e6;
  border-radius: 50%;
}

.tabs-dropdown {
  margin-left: 10px;
  padding: 5px;
}

.tabs-dropdown-container {
  margin-left: auto; /* 关键：将下拉菜单推到右侧 */
}


@smart-page-tag-operate-width: 40px;
@page-tag-height: 40px;
@color-primary: undefined;

.smart-page-tag-operate {
  width: @smart-page-tag-operate-width;
  height: @smart-page-tag-operate-width;
  font-size: 17px;
  text-align: center;
  vertical-align: middle;
  line-height: @smart-page-tag-operate-width;
  padding-right: 10px;
  cursor: pointer;
  color: #606266;

  position: absolute; /* 绝对定位 */
  right: 0; /* 固定在右侧 */
  top: 50%; /* 垂直居中 */
  transform: translateY(-50%); /* 垂直居中 */
  /* 其他原有样式保持不变 */
  background: transparent; /* 可选：背景透明 */

  .smart-page-tag-operate-icon {
    width: 20px;
    height: 20px;
    transition: all 1s;
    transform-origin: 10px 20px;
  }

  .smart-page-tag-operate-icon:hover {
    width: 20px;
    height: 20px;
    transform: rotate(360deg);
  }
}

.smart-page-tag-operate:hover {
  color: @color-primary;
}


</style>