<script setup lang="ts">
import {ref} from 'vue'
import PageSearch from "../c-cpns/page-search.vue";
import PageContent from "../c-cpns/page-content.vue";
import PageModal from "../c-cpns/page-modal.vue";

import searchConfig from "./config/search.config.ts";
import contentConfig from "./config/content.config.ts";
import modalConfig from "./config/modal.config.ts";


import {computed} from "vue";

console.log('contentConfig ==>', contentConfig)

// 对modalConfig进行操作
const modalConfigRef = computed(() => {
  return modalConfig
})

// 对content组件的操作
const contentRef = ref<InstanceType<typeof PageContent>>()
const handleQueryClick = (formData) => {
  contentRef.value?.fetchPageListData(formData)
}

const handleResetClick = () => {
  contentRef.value?.fetchPageListData()
}

// 对modal组件的操作
const modalRef = ref<InstanceType<typeof PageModal>>()
const handleNewBtnClick = () => {
  modalRef.value?.setModalVisible()
}

const handleEditBtnClick = (itemData?:any) => {
  console.log('handleEditBtnClick', itemData)
  modalRef.value?.setModalVisible(false, itemData)
}

const isSearchVisible = ref(false)
const handleSearchBtnClick = () => {
  console.log('handleSearchBtnClick')
  isSearchVisible.value = !isSearchVisible.value
}

</script>

<template>
  <div class="device">
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