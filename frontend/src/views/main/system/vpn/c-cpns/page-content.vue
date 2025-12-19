<script setup lang="ts">
import useVpnStore from "@/store/main/vpns/vpns.ts";
import {ref, onMounted, onUnmounted, reactive} from 'vue'
import {Edit, Search} from "@element-plus/icons-vue";
import {ElMessage, ElMessageBox} from "element-plus"
import {storeToRefs} from "pinia";
import {formatUTC, formatBytes} from '@/utils/format.ts'

import {usePermissions} from '@/hooks/usePermissions.ts'
import {copyToClipboard} from "@/utils/tool.ts";
import {exportExcel} from "@/utils/exportExcel.ts";
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

// ##### 表格数据导出开始 #####
const tableColumns = props.contentConfig.propsList.filter(item =>
    item.prop && item.prop.trim() !== ''
);
// 可用字段（从列配置生成）
const availableFields = ref(tableColumns.map(col => ({
  key: col.prop,
  label: col.label
})));

// 选中的字段（默认全选）
const selectedFields = ref<string[]>(availableFields.value.map(f => f.key))
// 控制对话框显示
const dialogVisible = ref(false)
// 处理导出
const handleExport = () => {
  // 根据选中的字段过滤表头配置
  const headers = availableFields.value.filter(field =>
      selectedFields.value.includes(field.key)
  );

  const exportName = props.contentConfig.header.title + '_' + formatUTC(new Date())

  // 调用导出函数
  exportExcel(pageList.value, headers, exportName)

  ElMessage.success('导出成功')
  // 关闭对话框
  dialogVisible.value = false
}
// ##### 表格数据导出结束 #####

// 自定义事件
const emit = defineEmits(['newClick', 'editClick', 'searchClick'])


// 0.获取是否有对应的增删改查权限
const isCreate = usePermissions(`${props.contentConfig.pageName}:create`)
const isDelete = usePermissions(`${props.contentConfig.pageName}:delete`)
const isUpdate = usePermissions(`${props.contentConfig.pageName}:update`)
const isCopy = usePermissions(`${props.contentConfig.pageName}:copy`)
const isQuery = usePermissions(`${props.contentConfig.pageName}:query`)
const isExport = usePermissions(`${props.contentConfig.pageName}:export`)

console.log('isCreate', isCreate)
console.log('isDelete', isDelete)
console.log('isUpdate', isUpdate)
console.log('isCopy', isCopy)
console.log('isQuery', isQuery)
console.log('isExport', isExport)


// 1. 发起action, 请求usersList的数据
const vpnStore = useVpnStore()
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 100,
})

const loading = ref(false)
const selectedFiles = ref([])

// 6.监听vpnStore.pageList的更新，重新渲染table
vpnStore.$onAction(({name, after}) => {
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
const {pageList, pageTotalCount} = storeToRefs(vpnStore)
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
  vpnStore.postPageListAction(props.contentConfig.pageName, data, params)
}


// 5.删除/新建/编辑操作
const handleDeleteBtnClick = (id: number) => {
  console.log('delete id: ', id)
  ElMessageBox.confirm("确定要删除吗？", "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  }).then(() => {
    vpnStore.deletePageByIdAction(props.contentConfig.pageName, id)
  }).catch(() => {
    ElMessage.info("已取消删除");
  })
}


const handleNewBtnClick = () => {
  console.log('new btn click')
  emit('newClick')
}


const handleEditBtnClick = (itemData: any) => {
  console.log('edit btn click')
  emit('editClick', itemData)
}

const handleStatusChange = async (itemData: any) => {
  console.log("itemData.id: ", itemData.id, itemData)

  let infoData = reactive({})
  for (const key in itemData) {
    if (typeof itemData[key] === 'string' && itemData[key].trim() === '') {
      continue
    } else {
      infoData[key] = itemData[key]
    }
  }
  console.log("infoData: ", infoData)
  const {success, error} = await vpnStore.patchPageDataAction(props.contentConfig.pageName, itemData.id, infoData)
  if (success) {
    ElMessage.success('更新成功')
  } else {
    ElMessage.error(error || '更新失败')
  }
}

const handleSearchBtnClick = () => {
  console.log('search btn click')
  emit('searchClick')
}

const handleCopyBtnClick = (itemData: any) => {
  let textValue = ''
  console.log('copy btn click itemData', itemData)
  props.contentConfig.propsList.forEach(item => {

    if (props.contentConfig?.copyList.includes(item.prop)) {
      if (item.type === 'timer') {
        textValue += `${item.label}: ${formatUTC(itemData[item.prop])}\n`
      } else if (item.type === 'normal' || item.slotName === 'password') {
        textValue += `${item.label}: ${itemData[item.prop]}\n`
      }
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
        vpnStore.deletePageByIdAction(props.contentConfig.pageName, file.id)
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

// 定时刷新功能
const refreshTips = ref('')
const refreshInterval = ref<number | null>(null)
const autoRefreshEnabled = ref(false)

const toggleAutoRefresh = (enabled: boolean) => {
  if (enabled) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}


// 启动定时刷新
const startAutoRefresh = () => {
  // 先清除已有定时器
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = 0
  }
  refreshTips.value = '每5秒更新一次数据'
  // 设置新的定时器
  refreshInterval.value = setInterval(() => {
    refreshTips.value = '最近一次更新时间: ' + formatUTC(new Date())
    fetchPageListData()
  }, 1000 * 5)  // 5秒刷新一次
}

// 停止定时刷新
const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = 0
  }
}

onMounted(() => {
  if (autoRefreshEnabled.value) {
    startAutoRefresh()
  }
})

onUnmounted(() => {
  stopAutoRefresh()
})


defineExpose({
  fetchPageListData
})


</script>

<template>
  <WatermarkWithTime>
    <div class="content">
      <div class="header">
        <h3 class="title">{{ contentConfig?.header?.title ?? '数据列表' }}</h3>
        <el-tag v-if="contentConfig?.header?.isRefresh && refreshTips">{{ refreshTips }}</el-tag>
        <el-row class="header-control">

          <el-button
              @click="handleRefresh"
              icon="Refresh"
              :loading="loading"
              plain
          >
            刷新
          </el-button>

          <el-switch v-if="contentConfig?.header?.isRefresh"
                     v-model="autoRefreshEnabled"
                     active-text="自动刷新"
                     inactive-text="暂停刷新"
                     @change="toggleAutoRefresh"
          />

          <el-button v-if="isCreate" type="primary" @click="handleNewBtnClick">
            <el-icon>
              <Plus/>
            </el-icon>
            {{ contentConfig?.header?.btnTitle ?? '新建数据' }}
          </el-button>

          <!-- 导出Excel 字段选择对话框 -->
          <el-dialog v-model="dialogVisible" title="选择导出字段" width="50%">
            <el-checkbox-group v-model="selectedFields">
              <el-checkbox
                  v-for="field in availableFields"
                  :key="field.key"
                  :value="field.key"
              >
                {{ field.label }}
              </el-checkbox>
            </el-checkbox-group>

            <template #footer>
              <el-button @click="dialogVisible = false">取消</el-button>
              <el-button type="primary" @click="handleExport">确认导出</el-button>
            </template>
          </el-dialog>

          <!--  导出Excel 导出按钮 -->
          <el-button v-if="isExport" type="success" @click="dialogVisible = true">
            <el-icon>
              <Download/>
            </el-icon>
            导出Excel
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

            <template v-else-if="item.type === 'bytes'">
              <el-table-column align="center" v-bind="item">
                <!--          作用域插槽-->
                <template #default="scope">
                  {{ formatBytes(scope.row[item.prop]) }}
                </template>
              </el-table-column>
            </template>

            <template v-else-if="item.type === 'switch'">
              <el-table-column align="center" v-bind="item">
                <!--          作用域插槽-->
                <template #default="scope">
                  <!--                <el-tag :type="scope.row[item.prop] ? 'success' : 'danger'">-->
                  <!--                  {{ scope.row[item.prop] ? '启用' : '禁用' }}-->
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
              <el-table-column v-if="isUpdate || isCopy || isDelete" align="center" v-bind="item">
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
            :page-sizes="[5, 10, 20, 30, 50, 100, 200, 500, 1000]"
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

.header-control {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
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