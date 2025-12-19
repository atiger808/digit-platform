<script setup lang="ts">
import {ref, reactive, computed, watch} from "vue";
import {useRouter, useRoute} from "vue-router";
import {mapPathToMenu} from "@/utils/map-menus.ts";
import {useLoginStore} from "@/store/login/login.ts";
import {storeToRefs} from "pinia";


// 0.定义props
defineProps({
  isFold: {
    type: Boolean,
    default: false
  }
})


// 1.获取动态的菜单
const loginStore = useLoginStore()
const {userMenus} = storeToRefs(loginStore)

// 1.定义方法
const handleOpen = (key, keyPath) => {
  console.log(key, keyPath)
}
const handleClose = (key, keyPath) => {
  console.log(key, keyPath)
}
// 2.监听item的点击
const router = useRouter()
const handleItemClick = (item: any) => {
  const url = item.path
  router.push(url)
}

// 2.定义响应式数据
const isCollapse = ref(false)


// 3.ElMenu的默认菜单
const route = useRoute()
const defaultActive = computed(() => {
  const pathMenu = mapPathToMenu(route.path, userMenus.value)
  console.log('defaultActive pathMenu', pathMenu)
  return pathMenu?.id + ''
})

const menuKey = ref(Date.now())

// 退出时重置key
watch(() => loginStore.userMenus, () => {
  menuKey.value = Date.now()
})


</script>

<template>
  <div class="main-menu">
    <!--    1.logo-->
    <div class="logo">
      <img class="img" src="@/assets/img/logo.png" alt="">
      <h2 v-show="!isFold" class="title">大岳数智平台</h2>
    </div>
    <!--    2.menu-->
    <div class="menu">
      <el-menu
          :default-active="defaultActive"
          :key="menuKey"
          :collapse="isFold"
          class="el-menu-vertical-demo"
          @open="handleOpen"
          @close="handleClose"
          text-color="#b7bdc3"
          active-text-color="#fff"
          background-color="#001529"
      >

        <template v-for="item in userMenus" :key="item.id">
          <el-sub-menu :index="item.id + ''">
            <template #title>
              <!--              字符串：el-icon-monitor => 组件 component动态组件-->
              <el-icon>
                <component :is="item.icon.split('el-icon-')[1]"></component>
              </el-icon>
              <span>{{ item.name }}</span>
            </template>
            <template v-for="subitem in item.children" :key="subitem.id">
              <el-menu-item :index="subitem.id + ''" @click="handleItemClick(subitem)">
                <el-icon v-if="subitem.icon">
                  <component :is="subitem.icon.split('el-icon-')[1]"></component>
                </el-icon>
                <span>{{ subitem.name }}</span>
              </el-menu-item>
            </template>
          </el-sub-menu>
        </template>

      </el-menu>
    </div>
  </div>
</template>

<style scoped lang="scss">

.main-menu {
  height: 100%;
  background-color: #001529;
}

.logo {
  display: flex;
  height: 28px;
  padding: 12px 10px 8px 10px;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
  overflow: hidden;

  .img {
    height: 100%;
    margin: 0 10px;
  }

  .title {
    font-size: 16px;
    font-weight: 700;
    color: white;
    white-space: nowrap;
  }
}

.el-menu {
  border-right: none;
  user-select: none;
}

.el-sub-menu {
  .el-menu-item {
    padding-left: 50px !important;
    background-color: #0c2135;
  }

  .el-menu-item:hover {
    color: #fff;
  }

  .el-menu-item.is-active {
    background-color: #0a60bd;
  }
}


</style>