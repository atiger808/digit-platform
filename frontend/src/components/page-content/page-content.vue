<script setup lang="ts">
import useSystemStore from "@/store/main/system/system.ts";
import {onMounted, reactive, ref} from 'vue'
import {Edit, Search} from "@element-plus/icons-vue";
import {ElMessage, ElMessageBox} from "element-plus"
import {storeToRefs} from "pinia";
import {formatUTC} from '@/utils/format.ts'

import {usePermissions} from '@/hooks/usePermissions.ts'
import {copyToClipboard} from "@/utils/tool.ts";
import WatermarkWithTime from '@/components/WatermarkWithTime.vue'


export interface IContentProps {
  contentConfig: {
    pageName: string
    header?: {
      title?: string
      btnTitle?: string
    },
    propsList: any[],
    childrenTree?: any
  }
}

const props = defineProps<IContentProps>()

console.log('props ==>', props)

// 自定义事件
const emit = defineEmits(['newClick', 'editClick', 'searchClick'])


// 0.获取是否有对应的增删改查权限
const isCreate = usePermissions(`${props.contentConfig.pageName}:create`)
const isDelete = usePermissions(`${props.contentConfig.pageName}:delete`)
const isUpdate = usePermissions(`${props.contentConfig.pageName}:update`)
const isCopy = usePermissions(`${props.contentConfig.pageName}:isCopy`)
const isQuery = usePermissions(`${props.contentConfig.pageName}:query`)

console.log('isCreate', isCreate)
console.log('isDelete', isDelete)
console.log('isUpdate', isUpdate)
console.log('isCopy', isCopy)
console.log('isQuery', isQuery)


// 1. 发起action, 请求usersList的数据
const systemStore = useSystemStore()
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 100,
})

const loading = ref(false)
const selectedFiles = ref([])
const isSearch = ref(false)

// 6.监听systemStore.pageList的更新，重新渲染table
systemStore.$onAction(({name, after}) => {
  after(() => {
    console.log('action', name)
    if (
        name === 'deletePageByIdAction' ||
        name === 'addPageDataAction' ||
        name === 'editPageDataAction'
    ) {
      pagination.value.currentPage = 1
      pagination.value.pageSize = 10
    }
  })
})


fetchPageListData()

// 2. 获取usersList数据， 进行渲染,storeToRefs实现响应式
const {pageList, pageTotalCount} = storeToRefs(systemStore)
pagination.value.total = pageTotalCount

// 3.分页相关逻辑
const handleSizeChange = (val: number) => {
  fetchPageListData()
}
const handleCurrentChange = (val: number) => {
  fetchPageListData()
}

// 4.发送网络请求获取usersList数据
function fetchPageListData(formData: any = {}) {
  if (!isQuery) return
  const params = {
    page: pagination.value.currentPage,
    page_size: pagination.value.pageSize,
  }
  const data = {...formData}
  if (formData.createAt) {
    data.create_time_start = formatUTC(formData.createAt?.[0])
    data.create_time_end = formatUTC(formData.createAt?.[1])
  }
  systemStore.postPageListAction(data, params, props.contentConfig.pageName)
}


// 5.删除/新建/编辑操作
const handleDeleteBtnClick = async (id: number) => {
  console.log('delete id: ', id)
  await ElMessageBox.confirm("确定要删除吗？", "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })

  const {success, error} = await systemStore.deletePageByIdAction(id, props.contentConfig.pageName)
  console.log('success', success)
  console.log('error', error)
  if (success) {
    ElMessage.success("删除成功")
  } else {
    ElMessage.error(error)
  }

}

const handleNewBtnClick = () => {
  console.log('new btn click')
  emit('newClick')
}


const handleEditBtnClick = (itemData: any) => {
  console.log('edit btn click')
  emit('editClick', itemData)
}

const handleSearchBtnClick = () => {
  console.log('search btn click')
  emit('searchClick')
}


const handleStatusChange = async (itemData: any) => {
  console.log("itemData.id: ", itemData.id, itemData)
  let infoData = reactive({})
  for (const key in itemData) {
    if (typeof itemData[key] != 'object') {
      infoData[key] = itemData[key]
    }
  }
  console.log('infoData', infoData)
  const {success, error} = await systemStore.patchPageDataAction(itemData.id, infoData, props.contentConfig.pageName)
  if (success) {
    ElMessage.success('更新成功')
  } else {
    ElMessage.error(error || '更新失败')
  }
}


const handleCopyBtnClick = (itemData: any) => {
  let textValue = ''
  console.log('copy btn click itemData', itemData)
  props.contentConfig.propsList.forEach(item => {
    if (item.type === 'timer') {
      textValue += `${item.label}: ${formatUTC(itemData[item.prop])}\n`
    } else if (item.type === 'normal' || item.slotName === 'password') {
      textValue += `${item.label}: ${itemData[item.prop]}\n`
    }
  })

  copyToClipboard(textValue)

}

// 批量删除
const batchDelete = async () => {
  try {
    console.log('批量删除 selectedFiles ', selectedFiles.value)
    await ElMessageBox.confirm(
        `确定要删除选中的${selectedFiles.value.length}个吗？此操作不可恢复！`,
        '提示',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
    )
    const deletePromises = selectedFiles.value.map(file =>
        systemStore.deletePageByIdAction(file.id, props.contentConfig.pageName)
    )
    await Promise.all(deletePromises)
    ElMessage.success('批量删除成功')
    console.log('批量删除成功')
    selectedFiles.value = []
    fetchPageListData()
  } catch (error) {
    if (error !== 'cancel') {
      console.log('批量删除文件失败：', error)
      ElMessage.error('批量删除文件失败：' + error.message)
    }
  }
}

const handleSelectionChange = (val: any) => {
  console.log('selection change', val)
  selectedFiles.value = val
}

// 刷新功能
const handleRefresh = () => {
  // 重置到第一页
  fetchPageListData()
  ElMessage.success('列表已刷新')
}


defineExpose({
  fetchPageListData
})


</script>

<template>
  <WatermarkWithTime>
    <div class="content">
      <div class="header">
        <h3 class="title">{{ contentConfig?.header?.title ?? '数据列表' }}</h3>
        <el-row class="header-control">

          <el-button
              @click="handleRefresh"
              icon="Refresh"
              :loading="loading"
              plain
          >
            刷新
          </el-button>


          <el-button v-if="isCreate" type="primary" @click="handleNewBtnClick">
            <el-icon>
              <Plus/>
            </el-icon>
            {{ contentConfig?.header?.btnTitle ?? '新建数据' }}
          </el-button>

          <!--  批量操作栏-->
          <el-button type="danger" @click="batchDelete" v-if="isDelete && selectedFiles.length > 0">
            批量删除 ({{ selectedFiles.length }})
          </el-button>

          <el-button type="default" @click="handleSearchBtnClick">
            <el-icon>
              <Search/>
            </el-icon>
          </el-button>

        </el-row>
      </div>
      <div class="table">
        <el-table
            style="width: 100%"
            :height="contentConfig.tableHeight"
            border
            stripe
            :data="pageList"
            v-bind="contentConfig.childrenTree"
            v-loading="loading"
            @selection-change="handleSelectionChange"

        >
          <template v-for="item in contentConfig?.propsList" :key="item.prop">

            <template v-if="item.type === 'timer'">
              <el-table-column align="center" v-bind="item">
                <!--          作用域插槽-->
                <template #default="scope">
                  {{ formatUTC(scope.row[item.prop]) }}
                </template>
              </el-table-column>
            </template>

            <template v-else-if="item.type === 'status'">
              <el-table-column align="center" v-bind="item">
                <!--          作用域插槽-->
                <template #default="scope">
                  <!--                <el-tag :type="scope.row[item.prop] ? 'success' : 'danger'">{{-->
                  <!--                    scope.row[item.prop] ? '启用' : '禁用'-->
                  <!--                  }}-->
                  <!--                </el-tag>-->

                  <el-switch
                      v-model="scope.row[item.prop]"
                      @change="handleStatusChange(scope.row)"
                      :title="scope.row[item.prop] ? '已启用' : '已禁用'"
                  />

                </template>
              </el-table-column>
            </template>

            <template v-else-if="item.type === 'tag'">
              <el-table-column align="center" v-bind="item">
                <!--          作用域插槽-->
                <template #default="scope">
                  <el-tag>
                    {{ scope.row[item.prop] }}
                  </el-tag>

                </template>
              </el-table-column>
            </template>

            <template v-else-if="item.type === 'tooltip'">
              <el-table-column align="center" v-bind="item">
                <!--          作用域插槽-->
                <template #default="scope">
                  <el-tooltip effect="dark" :content="scope.row[item.prop]" placement="top">
                    <div class="ellipsis-text">{{ scope.row[item.prop] }}</div>
                  </el-tooltip>
                </template>
              </el-table-column>
            </template>

            <template v-else-if="item.type === 'handler'">
              <el-table-column v-if="isUpdate || isDelete" align="center" v-bind="item">
                <template #default="scope">
                  <el-button v-if="isUpdate" type="primary" icon="Edit" size="default" text
                             @click="handleEditBtnClick(scope.row)">
                    编辑
                  </el-button>
                  <el-button v-if="isCopy" type="success" icon="CopyDocument" size="default" text
                             @click="handleCopyBtnClick(scope.row)">
                    复制
                  </el-button>
                  <el-button v-if="isDelete" type="danger" icon="Delete" size="default" text
                             @click="handleDeleteBtnClick(scope.row.id)">
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </template>

            <!--          自定义插槽-->
            <template v-else-if="item.type === 'custom'">
              <el-table-column align="center" v-bind="item">
                <template #default="scope">
                  <slot
                      :name="item.slotName"
                      v-bind="scope"
                      :prop="item.prop"
                      hName="test"
                  ></slot>
                </template>
              </el-table-column>
            </template>

            <template v-else>
              <el-table-column align="center" v-bind="item"/>
            </template>

          </template>


        </el-table>
      </div>
      <div class="pagination">
        <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[5, 10, 20, 30]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="pagination.total"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </WatermarkWithTime>

</template>

<style scoped lang="scss">
.content {
  background-color: #fff;
  margin-top: 20px;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 10px;
}



.table {
  :deep(.el-table__cell) {
    padding: 6px 0;
  }

  .el-button {
    margin-left: 0;
    padding-left: 5px 8px;
  }

}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

:deep(.el-table .el-checkbox__inner) {
  width: 16px;
  height: 16px;
}

:deep(.el-table .el-checkbox__inner::after) {
  height: 8px;
  left: 6px;
}

.ellipsis-text {
  white-space: nowrap; /* 禁止换行 */
  overflow: hidden; /* 超出隐藏 */
  text-overflow: ellipsis; /* 显示省略号 */
  max-width: 200px; /* 限制宽度（可选） */
}

</style>