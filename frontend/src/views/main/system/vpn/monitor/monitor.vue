<script setup lang="ts">
import {ref, onMounted, onUnmounted} from 'vue'
import PageSearch from "../c-cpns/page-search.vue";
import PageContent from "../c-cpns/page-content.vue";
import PageModal from "../c-cpns/page-modal.vue";

import searchConfig from "./config/search.config.ts";
import contentConfig from "./config/content.config.ts";
import modalConfig from "./config/modal.config.ts";
import useVpnStore from '@/store/main/vpns/vpns.ts'

import {computed} from "vue";

console.log('contentConfig ==>', contentConfig)

// 对modalConfig进行操作
const modalConfigRef = computed(() => {
  const vpnStore = useVpnStore()
  const listDevices = vpnStore.listDevices.filter(item => item.used)
  const devices = listDevices.map(item => {
    return {label: item.device_name, value: item.id}
  })

  const region = vpnStore.listRegions.map(item => {
    return {label: item.region, value: item.id}
  })

  modalConfig.formItems.forEach(item => {
    if (item.prop === 'device_id') {
      item.options = []
      item.options.push(...devices)
    }
    if (item.prop === 'region_id') {
      item.options = []
      item.options.push(...region)
    }
  })

  return modalConfig
})

// 对searchConfig进行操作
const searchConfigRef = computed(() => {
  const vpnStore = useVpnStore()
  const listDevices = vpnStore.listDevices.filter(item => item.used)
  const devices = listDevices.map(item => {
    return { label: item.device_name, value: item.device_name}
  })

  const region = vpnStore.listRegions.map(item => {
    return { label: item.region, value: item.region }
  })

  searchConfig.formItems.forEach(item => {
    if (item.prop === 'device_name') {
      item.options = []
      item.options.push(...devices)
    }
    if (item.prop === 'region') {
      item.options = []
      item.options.push(...region)
    }
  })

  return searchConfig
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

const handleEditBtnClick = (itemData?: any) => {
  console.log('handleEditBtnClick', itemData)
  modalRef.value?.setModalVisible(false, itemData)
}

const isSearchVisible = ref(false)
const handleSearchBtnClick = () => {
  console.log('handleSearchBtnClick')
  isSearchVisible.value = !isSearchVisible.value
}


let timer: any = null
function autoRefresh() {
  timer = setInterval(() => {
    console.log('自动刷新')
    contentRef.value?.fetchPageListData()
  }, 5000)
}

onMounted(() => {
  // autoRefresh()
})
onUnmounted(() => {
  clearInterval(timer)
})

</script>

<template>
  <div class="monitor">
        <page-search
            :search-config="searchConfigRef"
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

      <template #password="scope">
        <span>******</span>
      </template>

      <template #online="scope">
        <el-tag :type="scope.row[scope.prop] ? 'success' : 'info'">
          {{ scope.row[scope.prop] ? '在线' : '离线' }}
        </el-tag>
      </template>

      <template #logo="scope">
        <img :src=scope.row[scope.prop] alt=""
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