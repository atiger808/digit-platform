<script lang="ts" setup>
import {ref} from 'vue'
import PageSearch from "./c-cpns/filemanage-search.vue";
import PageContent from "./c-cpns/filemanage-content.vue";
import PageModal from "./c-cpns/filemanage-modal.vue";

import searchConfig from "./config/search.config.ts";
import contentConfig from "./config/content.config.ts";
import modalConfig from "./config/modal.config.ts";
import {computed} from "vue";
import useMainStore from "@/store/main/main.ts";
import {capitalize} from "@/utils/format.ts";

// 对modalConfig进行操作
const modalConfigRef = computed(() => {
  const mainStore = useMainStore()
  const users = mainStore.listUsers.map(item => {
    return {label: item.username, value: item.id}
  })

  modalConfig.formItems.forEach(item => {
    if (item.prop === 'user_id') {
      item.options = []
      item.options.push(...users)
    }

    if (item.prop === 'user_list') {
      item.options = []
      item.options.push(...users)
    }

  })
  return modalConfig
})

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

const handleEditBtnClick = (itemData?: any) => {
  console.log('handleEditBtnClick', itemData)
  modalRef.value?.setModalVisible(false, itemData)
}


const handleViewBtnClick = (itemData?: any) => {
  console.log('handleViewBtnClick', itemData)
  modalRef.value?.setModalVisible(false, itemData)
}



const isSearchVisible = ref(false)
const handleSearchBtnClick = () => {
  console.log('handleSearchBtnClick')
  isSearchVisible.value = !isSearchVisible.value
}


</script>

<template>
  <div class="user">
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
        @view-click="handleViewBtnClick"
        @search-click="handleSearchBtnClick"
    >

      <!--          自定义插槽-->
      <template #image="scope">
          <el-image
              :src="scope.row[scope.prop]"
              fit="contain"

          />


        <!--        <el-tag v-if="scope.row.os">{{ capitalize(scope.row.os) }} 版</el-tag>-->
        <!--        <el-tag v-else>文件</el-tag>-->

        <!--        <div class="button-red" v-if="scope.row.os">下载<br>{{ capitalize(scope.row.os) }} 版</div>-->
        <!--        <div class="button-red" v-else>文件</div>-->

      </template>

      <!--      <template #image="scope">-->
      <!--        <span class="roles">自定义插槽: {{ typeof scope.row[scope.prop] === 'object' && scope.row[scope.prop].length>0? scope.row[scope.prop].map(item => item.name).join(',') : '暂无' }}</span>-->
      <!--        <img src="@/assets/vue.svg" alt=""-->
      <!--             style="width: 20px; height: auto; align-items: center; justify-content: center">-->
      <!--      </template>-->

    </page-content>

    <page-modal
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

.button-red {
  background: #dc291e;
  border-color: transparent;
  color: #fff;
  height: inherit;
  padding: 8px 12px;
  //margin-bottom: 30px;
  //justify-content: center;
  //align-items: center;

  font-size: 0.7rem;
  height: auto;
  line-height: 1.2rem;
  font-weight: bold;
  text-transform: initial;
  border-radius: 0;
  display: inline-block;

}

</style>