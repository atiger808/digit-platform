<script setup lang="ts">
import {ref, nextTick} from 'vue'
import type {ElTree} from "element-plus";
import {storeToRefs} from "pinia";

import PageSearch from "@/components/page-search/page-search.vue";
import PageContent from "@/components/page-content/page-content.vue";
import PageModal from "@/components/page-modal/page-modal.vue";

import searchConfig from './config/search.config.ts'
import contentConfig from './config/content.config.ts'
import modalConfig from './config/modal.config.ts'

import usePageContent from "@/hooks/usePageContent.ts";
import usePageModal from "@/hooks/usePageModal.ts";
import useMainStore from "@/store/main/main.ts";
import { mapMenuListToIds } from '@/utils/map-menus.ts'


// setup相同的逻辑的抽取: hooks
// 点击search, content的操作
const {contentRef, handleQueryClick, handleResetClick} = usePageContent()

// 点击conent中的按钮, modal的操作
const {modalRef, handleNewBtnClick, handleEditBtnClick} = usePageModal(newCallback, editCallback)

const isSearchVisible = ref(false)
const handleSearchBtnClick = () => {
  console.log('handleSearchBtnClick')
  isSearchVisible.value = !isSearchVisible.value
}

// 获取完整菜单
const mainStore = useMainStore()
const {listMenus} = storeToRefs(mainStore)
const otherInfo = ref({})
const handleElTreeCheck = (data1: any, data2: any) => {
  const menu_ids = [...data2.checkedKeys, ...data2.halfCheckedKeys]
  otherInfo.value = {menu_ids}
}

console.log('listMenus.value', listMenus.value)


const treeRef = ref<InstanceType<typeof ElTree>>()
function newCallback() {
  treeRef.value?.setCheckedKeys([])
}
function editCallback(itemData: any) {
  nextTick(() => {
    const menuIds = mapMenuListToIds(itemData.menus)
    treeRef.value?.setCheckedKeys(menuIds)
  })
}

</script>

<template>
  <div class="role">
    <page-search
        :search-config="searchConfig"
        @query-click="handleQueryClick"
        @reset-click="handleResetClick"
        v-show="isSearchVisible"
    />

    <page-content
        :content-config="contentConfig"
        ref="contentRef"
        @new-click="handleNewBtnClick"
        @edit-click="handleEditBtnClick"
        @search-click="handleSearchBtnClick"
    >
      <!--      自定义插槽-->
      <template #menus="scope">
        <el-tree
            :data="scope.row[scope.prop]"
            node-key="id"
            highlight-current
            :props="{ children: 'children', label: 'name' }"
        />
      </template>
    </page-content>

    <page-modal
        :modal-config="modalConfig"
        :other-info="otherInfo"
        ref="modalRef"
    >

      <template #menusList>
        <span style="font-weight: bold; margin-left: 10px">角色权限: </span>
        <el-tree
            ref="treeRef"
            :data="listMenus"
            show-checkbox
            node-key="id"
            highlight-current
            :props="{ children: 'children', label: 'name' }"
            @check="handleElTreeCheck"
        />
      </template>


    </page-modal>

  </div>

</template>

<style scoped lang="scss">

</style>