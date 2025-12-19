<template>
  <el-sub-menu v-if="item.children && item.children.length > 0 && item.children[0].type!=2" :index="item.id+''">
    <template #title>
      <el-icon v-if="item.icon">
        <component :is="item.icon.split('el-icon-')[1]"/>
      </el-icon>
      <span>{{ item.name }}</span>
    </template>

    <MenuItem
        v-for="child in item.children"
        :key="child.id"
        :item="child"
    />

  </el-sub-menu>

  <el-menu-item v-else :index="item.id+''" @click="handleItemClick(item)">
    <template #title>
      <!--              字符串：el-icon-monitor => 组件 component动态组件-->
      <el-icon v-if="item.icon">
        <component :is="item.icon.split('el-icon-')[1]"></component>
      </el-icon>
      <span>{{ item.name }}</span>
    </template>
  </el-menu-item>

</template>

<script setup lang="ts">
import {defineProps} from 'vue'
import {type MenuItemType} from '@/types/menu.ts'
import {useRouter, useRoute} from "vue-router";

// 2.监听item的点击
const router = useRouter()
const handleItemClick = (item: any) => {
  const url = item.path
  console.log('handleItemClick ', item, 'path=> ', url)
  router.push(url)
}

defineProps<{
  item: MenuItemType
}>()
</script>


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