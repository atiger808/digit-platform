<script setup lang="ts">
import {ref, reactive} from 'vue'
import useMainStore from '@/store/main/main.ts'
import useSystemStore from "@/store/main/system/system.ts";
import {storeToRefs} from "pinia";
import {type FormRules, type ElForm, ElMessage} from "element-plus";

// 1.获取roles/departments数据
const mainStore = useMainStore()
const {listRoles, listDepartments} = storeToRefs(mainStore)



const dialogVisible = ref(false)
const formData = reactive<any>({
  username: '',
  real_name: '',
  gender: 0,
  is_active: '',
  password: '',
  mobile: '',
  department_id: '',
  role_id: '',
})
const isNewRef = ref(true)
const editData = ref()

// 定义校验规则
const newUserRules: FormRules = {
  username: [
    {required: true, message: '请输入用户名', trigger: 'blur'},
    {min: 3, max: 10, message: '长度在 3 到 10 个字符', trigger: 'change'},
  ],
  real_name: [
    {required: true, message: '请输入真实姓名', trigger: 'blur'},
    {min: 2, max: 10, message: '长度在 2 到 10 个字符', trigger: 'blur'},
  ],
  mobile: [
    {required: true, message: '请输入手机号', trigger: 'blur'},
    {pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'change'},
  ],
  password: [
    {required: true, message: '请输入密码', trigger: 'blur'},
    {min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'change'},
  ],
  role_id: [
    {required: true, message: '请选择角色', trigger: 'blur'},
  ],
  department_id: [
    {required: true, message: '请选择部门', trigger: 'blur'},
  ],
}


// 2.定义设置dialogVisible方法
const setModalVisible = (isNew: boolean = true, itemData?: any) => {
  dialogVisible.value = true
  isNewRef.value = isNew
  if (!isNew && itemData) {  //编辑用户
    console.log('编辑用户 itemData', itemData)
    formData.id = itemData.id
    formData.username = itemData.username
    formData.real_name = itemData.real_name
    formData.is_active = itemData.is_active
    formData.gender = itemData.gender
    formData.password = itemData.password
    formData.mobile = itemData.mobile
    formData.department_id = itemData.department_info?.id
    formData.role_id = itemData.roles.length > 0? itemData.roles?.[0].id : ''
    editData.value = itemData

    // //编辑
    // for (const key in formData) {
    //   formData[key] = itemData[key]
    // }
    // editData.value = itemData


  } else { // 新增用户
    for (const key in formData) {
      formData[key] = ''
    }
    editData.value = null
  }


}


const systemStore = useSystemStore()
// 3.点击确定的逻辑
const formRef = ref<InstanceType<typeof ElForm>>()
const handleConfirmClick = () => {
  console.log('handleConfirmClick')
  formRef.value?.validate(async (valid: any) => {
    if (valid) {
      console.log(isNewRef.value ? '新增用户' : '编辑用户')
      // 2.发送请求
      if (!isNewRef.value && editData.value) {
        // 编辑用户数据
        console.log('编辑用户', editData.value.id)
        console.log(formData)
        await systemStore.editUserDataAction(editData.value.id, formData)
      } else {
        // 新增用户
        console.log('新增用户')
        console.log(formData)
        await systemStore.addUserDataAction(formData)
      }

      // 1.关闭dialog
      dialogVisible.value = false

    } else {
      console.log('验证失败,请检查输入格式是否正确~')
      ElMessage.error('验证失败,请检查输入格式是否正确~')
    }
  })
}


// 暴漏属性和方法
defineExpose({setModalVisible})

</script>

<template>
  <div class="modal">
    <el-dialog v-model="dialogVisible" :title="isNewRef ? '新增用户' : '编辑用户'" width="30%" center>
      <el-divider border-style="double" />
      <div class="form">
        <el-form
            :model="formData"
            :rules="newUserRules"
            ref="formRef"
            status-icon
            label-width="80px"
            size="large">

          <el-form-item label="用户名" prop="username">
            <el-input v-model="formData.username" placeholder="请输入用户名"></el-input>
          </el-form-item>

          <el-form-item label="真实姓名" prop="real_name">
            <el-input v-model="formData.real_name" placeholder="请输入真实姓名"></el-input>
          </el-form-item>

          <el-form-item label="性别" prop="gender">
            <el-select v-model="formData.gender" placeholder="请选择性别">
              <el-option label="未知" :value="0"/>
              <el-option label="男" :value="1"/>
              <el-option label="女" :value="2"/>
            </el-select>
          </el-form-item>

          <el-form-item v-if="isNewRef" label="密码" prop="password">
            <el-input v-model="formData.password" show-password placeholder="请输入密码"></el-input>
          </el-form-item>

          <el-form-item label="手机号" prop="mobile">
            <el-input v-model="formData.mobile" placeholder="请输入手机号"></el-input>
          </el-form-item>

          <el-form-item label="状态" prop="is_active">
            <el-select
                v-model="formData.is_active"
                placeholder="选择状态"
            >
              <el-option label="启用" :value="true"></el-option>
              <el-option label="禁用" :value="false"></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="角色" prop="role_id">
            <el-select v-model="formData.role_id" placeholder="请选择角色" style="width: 100%">
              <template v-for="item in listRoles" :key="item.id">
                <el-option :label="item.name" :value="item.id"/>
              </template>
            </el-select>
          </el-form-item>



          <el-form-item label="部门" prop="department_id">
            <el-select v-model="formData.department_id" placeholder="请选择部门" style="width: 100%">
              <template v-for="item in listDepartments" :key="item.id">
                <el-option :label="item.name" :value="item.id"/>
              </template>
            </el-select>
          </el-form-item>

        </el-form>
      </div>

      <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmClick">
          确定
        </el-button>
      </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">

.form {
  padding: 0 20px;
}


</style>