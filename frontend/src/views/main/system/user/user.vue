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
import useSystemStore from "@/store/main/system/system.ts";


// 对modalConfig进行操作
const modalConfigRef = computed(() => {
  const systemStore = useSystemStore()
  const departments = systemStore.listDepartments.map(item => {
    return {label: item.name, value: item.id}
  })

  console.log('departments', departments)


  const roles = systemStore.listRoles.map(item => {
    return {label: item.name, value: item.id}
  })

  console.log('roles', roles)

  modalConfig.formItems.forEach(item => {
    if (item.prop === 'department_id') {
      item.options = []
      item.options.push(...departments)
    }
    if (item.prop === 'role_id') {
      item.options = []
      item.options.push(...roles)
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
  <div class="user">
    <PageSearch
        :search-config="searchConfig"
        @query-click="handleQueryClick"
        @reset-click="handleResetClick"
        v-show="isSearchVisible"
    />
    <PageContent
        :content-config="contentConfig"
        ref="contentRef"
        @new-click="handleNewBtnClick"
        @edit-click="handleEditBtnClick"
        @search-click="handleSearchBtnClick"
    >

      <!--          自定义插槽-->
      <template #online="scope">
        <el-tag :type="scope.row[scope.prop] ? 'success' : 'info'">
          {{ scope.row[scope.prop] ? '在线' : '离线' }}
        </el-tag>
      </template>

      <template #department_name="scope">
        <span class="department_name">{{ scope.row[scope.prop]?.name }}</span>
      </template>
      <template #roles="scope">
        <!--        <span class="department_name">{{ scope.row[scope.prop]?.name }}</span>-->
        <span class="roles">{{
            typeof scope.row[scope.prop] === 'object' && scope.row[scope.prop].length > 0 ? scope.row[scope.prop].map(item => item.name).join(',') : '暂无'
          }}</span>
      </template>

    </PageContent>

    <PageModal
        :modal-config="modalConfigRef"
        ref="modalRef"
    />

  </div>
</template>


<style lang="scss" scoped>
.user {
  border-radius: 8px;
  overflow: hidden;
}
</style>