<script setup lang="ts">
import {ref} from 'vue'
import PageSearch from "@/components/page-search/page-search.vue";
import PageContent from "@/components/page-content/page-content.vue";
import PageModal from "@/components/page-modal/page-modal.vue";

import searchConfig from "./config/search.config.ts";
import contentConfig from "./config/content.config.ts";
import modalConfig from "./config/modal.config.ts";

import usePageContent from "@/hooks/usePageContent.ts";
import usePageModal from "@/hooks/usePageModal.ts";

import {computed} from "vue";
import useMainStore from "@/store/main/main.ts";

console.log('contentConfig ==>', contentConfig)

// 对modalConfig进行操作
const modalConfigRef = computed(() => {
  const mainStore = useMainStore()
  const departments = mainStore.listDepartments.map(item => {
    return { label: item.name, value: item.id }
  })
  modalConfig.formItems.forEach(item => {
    if (item.prop === 'parent') {
      item.options = []
      item.options.push(...departments)
    }
  })
  return modalConfig
})

// setup相同的逻辑的抽取: hooks
// 点击search, content的操作
const { contentRef, handleQueryClick, handleResetClick } = usePageContent()

// 点击conent中的按钮, modal的操作
const { modalRef, handleNewBtnClick, handleEditBtnClick } = usePageModal()


const isSearchVisible = ref(false)
const handleSearchBtnClick = () => {
  console.log('handleSearchBtnClick')
  isSearchVisible.value = !isSearchVisible.value
}

</script>

<template>
  <div class="department">
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
      <!--          自定义插槽-->
      <template #name="scope">
        <span class="leader">自定义插槽: {{ scope.row[scope.prop] }}</span>
        <span> {{ scope.hName }} </span>
      </template>
      <template #parent_name="scope">
        <span class="parentName">自定义插槽: {{ scope.row[scope.prop] }}</span>
        <img src="@/assets/vue.svg" alt=""
             style="width: 20px; height: auto; align-items: center; justify-content: center">
      </template>
    </page-content>

    <page-modal
        :modal-config="modalConfigRef"
        ref="modalRef"
    />

  </div>
</template>

<style scoped lang="scss">

.leader {
  color: red;
}

.parentName {
  color: blue;
}

</style>