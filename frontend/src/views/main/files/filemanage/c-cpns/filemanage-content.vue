<script setup lang="ts">
import axios from 'axios'

import useSystemStore from "@/store/main/system/system.ts";
import useFileStore from "@/store/main/files/files.ts";
import {ref, computed} from 'vue'
import {Edit, Search} from "@element-plus/icons-vue";
import {ElMessage, ElMessageBox} from "element-plus"
import {storeToRefs} from "pinia";
import {formatBytes, formatDuration, formatUTC} from '@/utils/format.ts'

import {usePermissions} from '@/hooks/usePermissions.ts'
import FileUpload from "@/components/files/FileUpload.vue";
import MultiFileUpload from "@/components/files/MultiFileUpload.vue";
import {downloadFileById, retrieveFileById} from '@/service/main/files/files'
import {parseContentDisposition} from '@/utils/tool.ts'

import {api} from '@/service/request.ts'
import {chunkedDownload} from "@/utils/chunkedDownload.ts";
import WatermarkWithTime from '@/components/WatermarkWithTime.vue'
import EditableCell from '@/components/files/EditableCell.vue'

export interface IContentProps {
  contentConfig: {
    pageName: string
    header?: {
      title?: string
      btnTitle?: string
      icon?: string
    },
    propsList: any[],
    childrenTree?: any
  }
}

const props = defineProps<IContentProps>()

// 自定义事件
const emit = defineEmits(['newClick', 'editClick', 'searchClick'])


// 0.获取是否有对应的增删改查权限
const isCreate = usePermissions(`${props.contentConfig.pageName}:create`)
const isDelete = usePermissions(`${props.contentConfig.pageName}:delete`)
const isUpdate = usePermissions(`${props.contentConfig.pageName}:update`)
const isQuery = usePermissions(`${props.contentConfig.pageName}:query`)
const isDownload = usePermissions(`${props.contentConfig.pageName}:download`)
const isView = usePermissions(`${props.contentConfig.pageName}:view`)


console.log('isCreate', isCreate)
console.log('isDelete', isDelete)
console.log('isUpdate', isUpdate)
console.log('isQuery', isQuery)
console.log('isDownload', isDownload)
console.log('isView', isView)



// 1. 发起action, 请求usersList的数据
const fileStore = useFileStore()
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 100,
})

const loading = ref(false)
const selectedFiles = ref([])
const showUploadDialog = ref(false)


// 6.fileStore.fileList的更新，重新渲染table
fileStore.$onAction(({name, after}) => {
  after(() => {
    console.log('action', name)
    if (
        name === 'deleteFileAction' ||
        name === 'editFileAction' ||
        name === 'renameFileAction' ||
        name === 'downloadFileAction'
    ) {
      pagination.value.currentPage = 1
    }
  })
})


fetchPageListData()

// 2. 获取usersList数据， 进行渲染,storeToRefs实现响应式
const {fileList, totalCount} = storeToRefs(fileStore)
pagination.value.total = totalCount

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
  fileStore.postFileListAction(data, params, props.contentConfig.pageName)
}


// 5.删除/新建/编辑操作
const handleDeleteBtnClick = (id: number) => {
  console.log('delete id: ', id)
  ElMessageBox.confirm("确定要删除吗？", "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  }).then(() => {
    fileStore.deleteFileAction(id, props.contentConfig.pageName)
  }).catch(() => {
    ElMessage.info("已取消删除");
  })
}

const handleRenameBtnClick = (id: number) => {
  console.log('rename id: ', id)
  ElMessageBox.confirm("确定要修改吗？", "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  }).then(() => {
    fileStore.renameFileAction(id, props.contentConfig.pageName)
  }).catch(() => {
    ElMessage.info("已取消重命名");
  })
}

// 重命名文件
const handleRename = async (row, newName) => {
  console.log("row: ", row)
  console.log("newName: ", newName)
  try {
    if (!newName || newName === row.description) {
      return
    }
    fileStore.renameFileAction(row.id, {new_description: newName}, props.contentConfig.pageName)
    ElMessage.success('重命名成功')
    console.log('重命名成功')
  } catch (error) {
    ElMessage.error('重命名文件失败：' + error.message)
    console.log('重命名文件失败：', error)
    // 恢复原名
    row.description = row.description
  }
}


// 批量删除
const batchDelete = async () => {
  try {
    console.log('批量删除 selectedFiles ', selectedFiles.value)
    await ElMessageBox.confirm(
        `确定要删除选中的${selectedFiles.value.length}个文件吗？此操作不可恢复！`,
        '提示',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
    )
    const deletePromises = selectedFiles.value.map(file =>
        fileStore.deleteFileAction(file.id, props.contentConfig.pageName)
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


const handleNewBtnClick = () => {
  console.log('new btn click')
  emit('newClick')
}


const handleEditBtnClick = (itemData: any) => {
  console.log('edit btn click')
  emit('editClick', itemData)
}

const handleViewBtnClick = (itemData: any) => {
  console.log('View btn click')
  emit('viewClick', itemData)
}

const handleSearchBtnClick = () => {
  console.log('search btn click')
  emit('searchClick')
}


const handleSelectionChange = (val: any) => {
  console.log('selection change', val)
  selectedFiles.value = val
}

// 刷新功能
const handleRefresh = () => {
  // 重置到第一页
  fetchPageListData()
  ElMessage.success('文件列表已刷新')
}

// 上传成功回调 (增加自动刷新)
const handleUploadSuccess = () => {
  console.log('upload success')
  handleRefresh() // 上传成功后自动刷新列表
  showUploadDialog.value = false
}


// 分块下载
const downloadingId = ref<number | null>(null)
const downloadProgress = ref(0) // 下载进度百分比
const showProgress = ref(false) // 是否显示进度条
const isDownloading = ref(false);
const cancelToken = ref<ReturnType<typeof api.CancelToken.source>>(null);

const downloadStatus = computed(() => {
  if (downloadProgress.value === 100) return 'success';
  return '';
});


const startChunkedDownload = async (itemData: any) => {
  downloadingId.value = itemData.id;
  isDownloading.value = true;
  downloadProgress.value = 0;
  console.log("itemData: ", itemData)
  console.log("itemData.id: ", itemData.id)

  // 每次下载前创建新的取消令牌
  cancelToken.value = api.CancelToken.source();  // 使用api的CancelToken

  try {
    // 2. 开始分块下载
    const data = await chunkedDownload({
      url: `file/api/download/${itemData.id}/download/`,
      fileSize: itemData.file_size,
      fileId: itemData.id,
      chunkSize: 1 * 1024 * 1024, // 1MB分块
      cancelToken: cancelToken.value,
      onProgress: (progress) => {
        downloadProgress.value = progress;
      },
      onChunk: (chunk, loaded) => {
        console.log(`Downloaded chunk: ${loaded}/${itemData.size}`);
      }
    });

    // 3. 创建下载链接
    const blob = new Blob([data], {type: 'application/octet-stream'});
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = itemData.original_filename;
    link.click();

    // 4. 清理
    setTimeout(() => {
      URL.revokeObjectURL(url);
      isDownloading.value = false;
      downloadProgress.value = 100;
      ElMessage.success('下载完成');
    }, 500);

  } catch (error) {
    console.error('分块下载失败:', error);
    ElMessage.error(`${error.message}`);
    isDownloading.value = false;
  }
};

const cancelDownload = () => {

  if (cancelToken.value) {
    cancelToken.value.cancel('用户取消下载');
  }
  isDownloading.value = false;
  downloadProgress.value = 0;
};

const getFileInfo = async (fileId: number) => {
  console.log('fileId ', fileId)
  const response = await retrieveFileById(props.contentConfig.pageName, fileId, {params: {_t: Date.now()}});
  console.log('获取文件信息成功:', response.data);
  return {
    size: response.data.data.file_size,
    name: response.data.data.original_filename
  };
};


defineExpose({
  fetchPageListData
})


</script>

<template>
  <WatermarkWithTime>
    <div class="content">
      <div class="header">

        <el-row style="align-items: center; gap: 6px;">
          <h3 class="title">{{ contentConfig?.header?.title ?? '数据列表' }}</h3>


        </el-row>

        <el-row class="header-control">

          <el-button
              @click="handleRefresh"
              icon="Refresh"
              :loading="loading"
              plain
          >
            刷新
          </el-button>

          <el-button type="success" @click="showUploadDialog = true">
            <el-icon>
              <Upload/>
            </el-icon>
            上传文件
          </el-button>


          <el-button v-if="isCreate" type="primary" @click="handleNewBtnClick">
            <el-icon>
              <Plus/>
            </el-icon>
            {{ contentConfig?.header?.btnTitle ?? '新建数据' }}
          </el-button>

          <!--  批量操作栏-->
          <el-button type="danger" @click="batchDelete" v-if="selectedFiles.length > 0">
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
            stripe
            :data="fileList"
            v-bind="contentConfig.childrenTree"
            v-loading="loading"
            @selection-change="handleSelectionChange"
        >

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

            <template v-else-if="item.type === 'editable'">
              <el-table-column align="center" v-bind="item">
                <!--          作用域插槽-->
                <template #default="scope">
                  <editable-cell
                      :model-value="scope.row[item.prop]"
                      @update:model-value="handleRename(scope.row, $event)"
                  />

                </template>
              </el-table-column>
            </template>

            <template v-else-if="item.type === 'bytes'">
              <el-table-column align="center" v-bind="item">
                <!--          作用域插槽-->
                <template #default="scope">
                  {{ formatBytes(parseFloat(scope.row[item.prop])) }}
                </template>
              </el-table-column>
            </template>

            <template v-else-if="item.type === 'duration'">
              <el-table-column align="center" v-bind="item">
                <!--          作用域插槽-->
                <template #default="scope">
                  {{ formatDuration(parseFloat(scope.row[item.prop])) }}
                </template>
              </el-table-column>
            </template>

            <template v-else-if="item.type === 'link'">
              <el-table-column align="center" v-bind="item">
                <!--          作用域插槽-->
                <template #default="scope">
                  <el-link underline
                           :href="scope.row[item.prop]" target="_blank">观看视频
                  </el-link>

                </template>
              </el-table-column>
            </template>

            <template v-else-if="item.type === 'status'">
              <el-table-column align="center" v-bind="item">
                <!--          作用域插槽-->
                <template #default="scope">
                  <el-tag :type="scope.row[item.prop] === 'completed' ? 'success' : 'danger'">{{
                      scope.row[item.prop] === 'completed' ? '已完成' : '上传中'
                    }}
                  </el-tag>
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

            <template v-else-if="item.type === 'handler'">
              <el-table-column v-if="isUpdate || isDelete || isDownload || isView" align="center" v-bind="item">
                <template #default="scope">
                  <el-button v-if="isUpdate" type="primary" icon="Edit" size="default" text
                             @click="handleEditBtnClick(scope.row)">
                    编辑
                  </el-button>

                  <el-button v-if="isView" type="primary" icon="View" size="default" text
                             @click="handleViewBtnClick(scope.row)">
                    查看
                  </el-button>

                  <el-button v-if="isDelete" type="danger" icon="Delete" size="default" text
                             @click="handleDeleteBtnClick(scope.row.id)">
                    删除
                  </el-button>


                  <template v-if="isDownload">
                    <el-button type="success" icon="Download" size="default" text
                               @click="startChunkedDownload(scope.row)"
                               :disabled="isDownloading"
                    >
                      {{ isDownloading && downloadingId === scope.row.id ? '下载中...' : '下载' }}
                    </el-button>

                    <el-button type="warning" icon="Download" size="default" text
                               v-if="isDownloading && downloadingId === scope.row.id"
                               @click="cancelDownload"
                    >
                      取消下载
                    </el-button>


                    <el-progress
                        v-if="isDownloading && downloadingId === scope.row.id"
                        :percentage="downloadProgress"
                        :stroke-width="10"
                        :status="downloadStatus"
                    />
                  </template>


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


      <!--  上传对话框-->
      <el-dialog title="上传文件" v-model="showUploadDialog" width="50%">
        <file-upload @success="handleUploadSuccess"/>
<!--        <MultiFileUpload @success="handleUploadSuccess"/>-->
      </el-dialog>

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
  width: 18px;
  height: 18px;
}

:deep(.el-table .el-checkbox__inner::after) {
  height: 9px;
  left: 6px;
}


</style>