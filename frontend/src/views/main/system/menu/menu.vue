<script setup lang="ts">
import PageSearch from "@/components/page-search/page-search.vue";
import PageContent from "@/components/page-content/page-content.vue";
import PageModal from "@/components/page-modal/page-modal.vue";

import searchConfig from './config/search.config.ts'
import contentConfig from './config/content.config.ts'
import modalConfig from './config/modal.config.ts'

import usePageContent from "@/hooks/usePageContent.ts";
import usePageModal from "@/hooks/usePageModal.ts";

import {computed, ref} from "vue";
import useMainStore from "@/store/main/main.ts";
import {mapMenuListToLeaf} from '@/utils/map-menus.ts'

// 对modalConfig进行操作
const modalConfigRef = computed(() => {
  const mainStore = useMainStore()

  const listMenus = mapMenuListToLeaf(mainStore.listMenus)
  console.log('listMenus ', listMenus)
  const menus = listMenus.map(item => {
    return {label: item.name, value: item.id}
  })

  console.log('menus ', menus)

  modalConfig.formItems.forEach(item => {
    if (item.prop === 'parent') {
      item.options = []
      item.options.push(...menus)
    }
  })
  return modalConfig
})

// setup相同的逻辑的抽取: hooks
// 点击search, content的操作
const {contentRef, handleQueryClick, handleResetClick} = usePageContent()

// 点击conent中的按钮, modal的操作
const {modalRef, handleNewBtnClick, handleEditBtnClick} = usePageModal()

const isSearchVisible = ref(false)
const handleSearchBtnClick = () => {
  console.log('handleSearchBtnClick')
  isSearchVisible.value = !isSearchVisible.value
}

</script>

<template>
  <div class="menu">
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
      <template #parent="scope">
        <span>{{ scope.row[scope.prop] }}</span>
      </template>

      <template #icon="scope">
        <span>{{ scope.row[scope.prop] }}</span>

        <template v-if="scope.row[scope.prop]">
          <el-icon>
            <component :is="scope.row[scope.prop].split('el-icon-')[1]"></component>
          </el-icon>
        </template>


      </template>

    </page-content>

    <page-modal
        :modal-config="modalConfigRef"
        ref="modalRef"
    />
  </div>
</template>

<style scoped lang="scss">

</style>