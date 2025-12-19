<script setup lang="ts">

import { mapPathToBreads } from '@/utils/map-menus.ts'
import {useRoute} from 'vue-router'
import {useLoginStore} from "@/store/login/login.ts";
import {computed} from "vue";

const useMenus = useLoginStore().userMenus
const route = useRoute()
const breadcrumbs  = computed(() => {
  return mapPathToBreads(route.path, useMenus)
})

</script>

<template>
  <div class="crumb">
    <el-breadcrumb
        separator-icon="ArrowRight">
      <template v-for="item in breadcrumbs " :key="item.name">
        <el-breadcrumb-item :to="item.path">{{ item.name }}</el-breadcrumb-item>
      </template>
    </el-breadcrumb>
  </div>
</template>

<style scoped lang="scss">

</style>