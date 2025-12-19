<script setup lang="ts">
import MainMenu from "@/components/main-menu/main-menu.vue";
import SideMenu from "@/components/main-menu/side-menu.vue";
import MainHeader from "@/components/main-header/main-header.vue";
import MainTab from "@/components/main-tab/main-tab1.vue";
import {ref, computed} from 'vue'
import {useTabsStore} from '@/store/main/tabs/tabs.ts'

const isFold = ref(false)

const tabsStore = useTabsStore()
const cachedTabs = computed(() => tabsStore.tabs.map(tab => tab.path))

// 处理侧边栏折叠事件
const handleFoldChange = (flag: boolean) => {
  console.log(flag);
  isFold.value = flag
};

</script>

<template>

  <div class="main">
    <el-container class="main-content">
      <!--      侧边栏-->
      <el-aside :width="isFold ? '62px' : '240px'">
        <SideMenu :is-fold="isFold"/>
      </el-aside>


      <el-container>
        <el-header height="50px">
          <MainHeader @fold-change="handleFoldChange"/>
        </el-header>
        <MainTab/>
        <el-main>

          <router-view v-slot="{ Component }">
            <keep-alive :include="cachedTabs">
              <component :is="Component"/>
            </keep-alive>
          </router-view>
        </el-main>
      </el-container>

    </el-container>
  </div>
</template>

<style scoped lang="scss">

.main {
  width: 100%;
  height: 100%;
}

.main-content {
  height: 100%;

  .el-aside {
    background-color: #001529;
    overflow-x: hidden;
    overflow-y: auto;
    line-height: 200px;
    text-align: left;
    cursor: pointer;
    transition: width 0.3s linear;
    scrollbar-width: none; /* firefox */
    -ms-overflow-style: none; /* IE 10+ */

    /* 删除滚动条 */
    &::-webkit-scrollbar {
      display: none;
    }
  }

  .el-main {
    background-color: #f0f2f5;
  }
}
</style>