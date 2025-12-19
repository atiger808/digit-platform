<!--
  * 使用ant design <a-tabs> 组件
  *
  * @Author:    1024创新实验室-主任：卓大
  * @Date:      2022-09-06 20:29:12
  * @Wechat:    zhuda1024
  * @Email:     lab1024@163.com
  * @Copyright  1024创新实验室 （ https://1024lab.net ），Since 2012
-->
<template>
  <!-- 标签页，共两部分：1、标签 ；2、标签操作区 -->
  <a-row style="border-bottom: 1px solid #eeeeee; position: relative; display: flex" v-show="pageTagFlag">
    <a-dropdown :trigger="['contextmenu']">
      <div class="smart-page-tag">
        <a-tabs style="width: 100%" type="card" :tab-position="mode" v-model:activeKey="activeIndex" size="small"
                @tabClick="handleTabClick">
          <a-tab-pane
              v-for="item in tabs"
              :key="item.path"
              :class="['ant-tabs-tab-active', { active: currentTab === item.path }]"
          >
            <template #tab>
              <span>
                {{ item.title }}
                <close-outlined @click.stop="handleTabClose(item.path)" v-if="item.path !== HOME_PAGE_NAME"
                                class="smart-page-tag-close"/>
              </span>
            </template>
          </a-tab-pane>
        </a-tabs>
      </div>
      <template #overlay>
        <a-menu>
          <a-menu-item @click="closeOtherTabs">关闭其他</a-menu-item>
          <a-menu-item @click="closeAllTabs">关闭全部</a-menu-item>
          <a-menu-item @click="closeLeftTabs">关闭左侧</a-menu-item>
          <a-menu-item @click="closeRightTabs">关闭右侧</a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>

    <a-dropdown @command="handleTabCommand" trigger="click">
      <!--标签页操作区-->
      <div class="smart-page-tag-operate">
        <div class="smart-page-tag-operate-icon">
          <AppstoreOutlined/>
        </div>
      </div>
      <template #overlay>
        <a-menu>
          <a-menu-item @click="closeOtherTabs">关闭其他</a-menu-item>
          <a-menu-item @click="closeAllTabs">关闭全部</a-menu-item>
          <a-menu-item @click="closeLeftTabs">关闭左侧</a-menu-item>
          <a-menu-item @click="closeRightTabs">关闭右侧</a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>
  </a-row>
</template>

<script setup lang="ts">
import {AppstoreOutlined, CloseOutlined} from '@ant-design/icons-vue';
import {computed, ref, watch} from 'vue';
import {useRoute, useRouter} from 'vue-router';
import {useTabsStore} from '@/store/main/tabs/tabs.ts'
import {theme} from 'ant-design-vue';
import {storeToRefs} from "pinia";

//标签页 是否显示
const pageTagFlag = ref(true)
const HOME_PAGE_NAME = '/main/analysis/overview'


const route = useRoute();
const mode = ref('top');
const router = useRouter()
const tabsStore = useTabsStore()
const {tabs, currentTab} = storeToRefs(tabsStore)
const selectedKey = ref(route.path);
// watch(
//     () => route.path,
//     (newPath) => {
//       // 确保当前路由被添加到标签页
//       tabsStore.addTab({
//         path: newPath,
//         meta: {title: route.meta.title} // 从路由元信息获取标题
//       });
//
//       // 更新当前激活标签
//       tabsStore.setCurrentTab(newPath);
//     },
//     {immediate: true}
// );

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

const {useToken} = theme;
const {token} = useToken();
const borderRadius = computed(() => {
  return token.value.borderRadius + 'px';
});
console.log('token.colorPrimary', token.colorPrimary)
</script>
<style scoped lang="less">
@smart-page-tag-operate-width: 40px;
@page-tag-height: 40px;
@color-primary: v-bind('token.colorPrimary');

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

.smart-page-tag {
  position: relative;
  box-sizing: border-box;
  display: flex;
  align-content: center;
  align-items: center;
  justify-content: space-between;
  min-height: @page-tag-height;
  padding-right: 20px;
  padding-left: 20px;
  user-select: none;
  background: #fff;
  //width: calc(100% - @smart-page-tag-operate-width);

  /* 移除 width: calc(100% - ...) */
  flex: 1; /* 占据剩余空间 */
  overflow-x: auto; /* 允许横向滚动 */
  /* 其他原有样式保持不变 */

  .smart-page-tag-close {
    margin-left: 5px;
    font-size: 10px;
    color: #666666;
  }

  /**  覆盖 ant design vue的 tabs 样式，变小一点 **/

  :deep(.ant-tabs-nav) {
    margin: 0;
    margin-bottom: 10px;
    padding: 0 0 4px;
  }

  //:deep(.ant-tabs-nav::before) {
  //  border-bottom: 1px solid #ffffff;
  //}

  :deep(.ant-tabs-small > .ant-tabs-nav .ant-tabs-tab) {
    padding: 5px 8px 3px 15px;
    margin: 8px 0 0 5px;
    min-width: 60px;
    height: 32px;
    border-radius: v-bind(borderRadius) v-bind(borderRadius) 0 0;
    border-bottom: 0;
  }

  :deep(.ant-tabs-tab-active) {
    .smart-page-tag-close {
      color: @color-primary;
    }
  }

  :deep(.ant-tabs-nav .ant-tabs-tab:hover) {
    background-color: white;

    .smart-page-tag-close {
      color: @color-primary;
    }
  }
}

/* 在 <style> 部分增加以下样式 */


/* 激活状态样式 */
:deep(.ant-tabs-tab.ant-tabs-tab-active) {
  background-color: #f0faff !important; /* 浅蓝色背景 */

  .ant-tabs-tab-btn {
    color: #1890ff !important; /* 字体颜色 */
  }

  .smart-page-tag-close {
    color: #1890ff !important;
  }
}

/* 底部下划线 */
:deep(.ant-tabs-ink-bar) {
  background: #1890ff !important;
  height: 3px !important; /* 可调整下划线高度 */
}

/* 鼠标悬停样式 */
:deep(.ant-tabs-tab:hover) {
  .ant-tabs-tab-btn {
    color: #1890ff !important;
  }
}

</style>