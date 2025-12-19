<script setup lang="ts">
import {ref, reactive} from 'vue'
import useLogStore from "@/store/main/logs/logs.ts";
import {type FormRules, type ElForm, ElMessage} from "element-plus";
// 定义props
interface IModalProps {
  modalConfig: {
    pageName: string
    header: {
      newTitle: string
      editTitle: string
    }
    formItems: any[]
  },
  otherInfo?: any
}

const props = defineProps<IModalProps>()

// 1.自定义内部属性
const dialogVisible = ref(false)
const initialData: any = {}
for (const item of props.modalConfig.formItems) {
  initialData[item.prop] = item.initialValue ?? ''
}

const formData = reactive<any>(initialData)
const isNewRef = ref(true)
const editData = ref()

// 1.获取roles/departments数据
const logStore = useLogStore()

// 定义校验规则
const modalRules: FormRules = props.modalConfig.rules
console.log('modalRules', modalRules)


// 2.定义设置dialogVisible方法
const setModalVisible = (isNew: boolean = true, itemData?: any) => {
  dialogVisible.value = true
  isNewRef.value = isNew
  if (!isNew && itemData) {
    //编辑
    for (const key in formData) {
      formData[key] = itemData[key]
    }
    editData.value = itemData
  } else {
    // 新增
    for (const key in formData) {
      const item = props.modalConfig.formItems.find((item: any) => item.prop === key)
      formData[key] = item ? item.initialValue : ''
    }
    editData.value = null
  }

}

// 3.点击确定的逻辑
const formRef = ref<InstanceType<typeof ElForm>>()
const handleConfirmClick = () => {
  console.log('handleConfirmClick')
  formRef.value?.validate(async (valid: any) => {
    if (valid) {

      let infoData = formData
      if (props.otherInfo) {
        infoData = {...formData, ...props.otherInfo}
      }

      // 2.发送请求
      if (!isNewRef.value && editData.value) {
        // 编辑
        console.log('编辑部门', editData.value.id)
        console.log(infoData)
        const {
          success,
          error
        } = await logStore.editPageDataAction(props.modalConfig.pageName, editData.value.id, infoData)
        if (success) {
          ElMessage.success('修改成功')
          // 1.关闭dialog
          dialogVisible.value = false
        } else {
          ElMessage.error(error)
        }
      } else {
        // 新增
        console.log('新增部门')
        console.log(infoData)
        const {success, error} = await logStore.addPageDataAction(props.modalConfig.pageName, infoData)
        if (success) {
          ElMessage.success('新增成功')
          // 1.关闭dialog
          dialogVisible.value = false
        } else {
          ElMessage.error(error)
        }
      }

    } else {
      console.log('验证失败,请检查输入格式是否正确~')
      ElMessage.error('验证失败,请检查输入格式是否正确~')
    }
  })
}


// 禁用过去日期
const disablePastDates = (time) => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return time.getTime() < today.getTime();
};

// 全屏显示
const isFullscreen = ref(false)
const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
}
const handleClose = () => {
  // 关闭时自动退出全屏
  isFullscreen.value = false
}

// 暴漏属性和方法
defineExpose({setModalVisible})

</script>

<template>
  <div class="modal">
    <el-dialog v-model="dialogVisible" :title="isNewRef ? modalConfig.header.newTitle : modalConfig.header.editTitle"
               :width="isFullscreen ? '90%' :modalConfig.tableWidth"
               :fullscreen="isFullscreen"
               :draggable="true"
               @confirm="handleConfirmClick"
               @close="handleClose">


      <!-- 自定义标题栏，包含全屏按钮 -->
      <template #header="{ titleId, titleClass }">
        <div class="dialog-header">
          <span :id="titleId" :class="titleClass">
            {{ isNewRef ? modalConfig.header.newTitle : modalConfig.header.editTitle }}
          </span>
          <div class="dialog-header-actions">
            <el-tooltip :content="isFullscreen ? '退出全屏' : '全屏'">

              <el-icon @click="toggleFullscreen" size="large">
                <FullScreen/>
              </el-icon>

            </el-tooltip>
          </div>
        </div>
      </template>

      <el-divider border-style="double"/>
      <div class="form">
        <el-form
            :model="formData"
            :rules="modalRules"
            ref="formRef"
            status-icon
            :label-width="modalConfig.labelWidth"
            size="large">
          <el-row :gutter="20">
            <template v-for="(item, index) in modalConfig.formItems" :key="index">
              <el-col :span="12" :xs="24" :sm="12" :md="12" :lg="12">

                <el-form-item :label="item.label" :prop="item.prop">
                  <template v-if="item.type === 'input' || item.type === 'password'">
                    <el-input
                        v-model="formData[item.prop]"
                        :placeholder="item.placeholder"
                        :show-password="item.type === 'password'"
                        :disabled="modalConfig.disabled"
                    />
                  </template>
                  <template v-if="item.type === 'select'">
                    <el-select
                        v-model="formData[item.prop]"
                        :placeholder="item.placeholder"
                        style="width: 100%"
                    >

                      <template v-for="option in item.options" :key="option.value">
                        <el-option :label="option.label" :value="option.value"/>
                      </template>

                    </el-select>
                  </template>


                  <!--              自定义插槽-->
                  <template v-if="item.type === 'custom'">
                    <slot :name="item.slotName"></slot>
                  </template>

                  <template v-if="item.type === 'date-picker'">
                    <el-date-picker
                        v-model="formData[item.prop]"
                        type="daterange"
                        range-separator="至"
                        start-placeholder="开始日期"
                        end-placeholder="结束日期"
                    />
                  </template>

                  <template v-if="item.type === 'date-select'">
                    <el-date-picker
                        v-model="formData[item.prop]"
                        type="datetime"
                        placeholder="请选择日期"
                        value-format="YYYY-MM-DD HH:mm:ss"
                        :disabled-date="disablePastDates"
                        :disabled="modalConfig.disabled"
                    />
                  </template>

                  <template v-if="item.type === 'textarea'">
                    <el-input
                        v-model="formData[item.prop]"
                        :placeholder="item.placeholder"
                        type="textarea"
                        :rows="5"
                        :disabled="modalConfig.disabled"
                    />
                  </template>

                </el-form-item>
              </el-col>
            </template>
          </el-row>

        </el-form>
      </div>

      <template #footer>
      <span class="dialog-footer">

        <template v-if="modalConfig?.isView">
          <el-button type="primary" @click="dialogVisible = false">确定</el-button>
        </template>
        <template v-else>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleConfirmClick">确定</el-button>
        </template>


      </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">

.form {
  padding: 0 20px;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-right: 16px;
}

.dialog-header-actions {
  display: flex;
  gap: 2px;
}

.dialog-content {
  padding: 20px 0;
  line-height: 1.5;
}

/* 全屏模式下调整内容区域高度 */
:deep(.el-dialog__body) {
  max-height: calc(100vh - 120px);
  overflow-y: auto;
}

</style>