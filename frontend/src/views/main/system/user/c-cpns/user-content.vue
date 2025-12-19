<script setup lang="ts">
import useSystemStore from "@/store/main/system/system.ts";
import {reactive, ref} from 'vue'

import {ElMessage, ElMessageBox} from "element-plus"
import {storeToRefs} from "pinia";
import {formatUTC} from '@/utils/format.ts'

import {usePermissions} from '@/hooks/usePermissions.ts'


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

console.log('props ==}', props)

// 自定义事件
const emit = defineEmits(['newClick', 'editClick'])

// 0.获取是否有对应的增删改查权限
const isCreate = usePermissions(`${props.contentConfig.pageName}:create`)
const isDelete = usePermissions(`${props.contentConfig.pageName}:delete`)
const isUpdate = usePermissions(`${props.contentConfig.pageName}:update`)
const isQuery = usePermissions(`${props.contentConfig.pageName}:query`)

console.log('isCreate', isCreate)
console.log('isDelete', isDelete)
console.log('isUpdate', isUpdate)
console.log('isQuery', isQuery)


// 1. 发起action, 请求usersList的数据
const systemStore = useSystemStore()
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 100,
})

fetchUsersListData()

// 2. 获取usersList数据， 进行渲染,storeToRefs实现响应式
const {usersList, usersTotalCount} = storeToRefs(systemStore)
pagination.value.total = usersTotalCount
console.log('usersTotalCount', usersTotalCount)
// 3.分页相关逻辑
const handleSizeChange = (val: number) => {
  fetchUsersListData()
}
const handleCurrentChange = (val: number) => {
  fetchUsersListData()
}

// 4.发送网络请求获取usersList数据
function fetchUsersListData(formData: any = {}) {
  const params = {
    page: pagination.value.currentPage,
    page_size: pagination.value.pageSize,
  }
  const data = {
    username: formData.username,
    mobile: formData.mobile,
    real_name: formData.real_name,
    is_active: formData.is_active,
    department: formData.department,
  }
  if (formData.createAt) {
    data.create_time_start = formatUTC(formData.createAt?.[0])
    data.create_time_end = formatUTC(formData.createAt?.[1])
  }
  systemStore.postUsersListAction(data, params)
}


// 5.删除/新建/编辑操作
const handleDeleteBtnClick = (id: number) => {
  console.log('delete id: ', id)
  ElMessageBox.confirm("确定要删除吗？", "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  }).then(() => {
    systemStore.deleteUserByIdAction(id)
  }).catch(() => {
    ElMessage.info("已取消删除");
  })
}

const handleNewBtnClick = () => {
  console.log('new btn click')
  emit('newClick')
}


const handleEditBtnClick = (itemData: any) => {
  emit('editClick', itemData)
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


defineExpose({
  fetchUsersListData
})


</script>

<template>
  <div class="content">
    <div class="header">
      <h3> {{ props.contentConfig?.header?.title ?? '用户列表' }} </h3>
      <el-button v-if="isCreate" type="primary" @click="handleNewBtnClick">
        <el-icon>
          <Plus/>
        </el-icon>
        {{ props.contentConfig?.header?.btnTitle ?? '新增用户' }}
      </el-button>
    </div>
    <div class="table">

      <el-table
          style="width: 100%"
          height="640px"
          border
          :data="usersList"
          v-bind="contentConfig.childrenTree"

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

          <template v-else-if="item.type === 'handler'">
            <el-table-column align="center" v-bind="item">
              <template #default="scope">
                <el-button v-if="isUpdate" type="primary" icon="Edit" size="default" text
                           @click="handleEditBtnClick(scope.row)">
                  编辑
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
    padding: 12px 0;
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

</style>