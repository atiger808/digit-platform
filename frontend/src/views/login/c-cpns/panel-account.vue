<script setup lang="ts">
import {ref, reactive} from "vue";
import type {FormRules, ElForm} from "element-plus";
import {ElMessage, ElMessageBox} from 'element-plus'
import {useLoginStore} from "@/store/login/login.ts";
import type {IAccount} from '@/types/types.ts'
import {onMounted} from "vue";
import VerificationCode from "@/components/verification-code/verification-code.vue";
import {verifyCaptcha} from "@/service/login/login.ts";

const loginStore = useLoginStore()

const loading = ref(false)
const accountForm = reactive<IAccount>({
  identifier: '',
  password: '',
  code: ''
})
const captchaKey = ref('')
const handleCaptchaSuccess = (code: string) => {
  captchaKey.value = code
}


const emits = defineEmits(['enterPressed'])

onMounted(() => {
  const userInfo = loginStore.getUserInfo()
  if (userInfo) {
    accountForm.identifier = userInfo.username
    accountForm.password = userInfo.password
  }
})


// 2.定义校验规则
const accountRules: FormRules = {
  username: [
    {required: true, message: '请输入账号', trigger: 'blur'},
    {min: 3, max: 10, message: '长度在 3 到 10 个字符', trigger: 'change'}
  ],
  password: [
    {required: true, message: '请输入密码', trigger: 'blur'},
    {min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'change'}
  ],
  code: [
    {required: true, message: '请输入验证码', trigger: 'blur'},
    {min: 4, max: 4, message: '长度为 4 个字符', trigger: 'change'}
  ]
}

// 3.执行账号的登录逻辑
const formRef = ref<InstanceType<typeof ElForm>>()
const loginAction = async (isRemember: boolean) => {
  console.log('accountForm: ', accountForm)
  accountForm.key = captchaKey.value
  console.log('accountForm: ', accountForm)
  const data = {
    identifier: accountForm.username,
    password: accountForm.password,
    key: accountForm.key,
    code: accountForm.code
  }

  try {
    // const response = await verifyCaptcha(data)
    // console.log('verifyCaptcha response: ', response)
    // console.log('verifyCaptcha response.data: ', response.data)
    // console.log('verifyCaptcha response.status: ', response.status)
    // if (response.status !== 200) {
    //   ElMessage.error('验证码错误')
    //   return
    // }
    formRef.value?.validate(async (valid: any) => {
      if (valid) {
        loading.value = true
        let {success, error} = await loginStore.loginAccountAction(data)
        if (!success) {
          ElMessage.error(error)
        } else {
          ElMessage.success('登录成功')
          console.log('登录成功 isRemember: ', isRemember)
          if (isRemember) {
            console.log('保存用户信息')
            loginStore.saveUserInfo(data)
          } else {
            console.log('清除用户信息')
            loginStore.clearUserInfo()
          }
        }
        loading.value = false;
      } else {
        console.log('验证失败,请检查输入格式是否正确~')
        ElMessage.error('验证失败,请检查输入格式是否正确~')
      }
    })
  } catch (error) {
    console.log('verifyCaptcha error: ', error)
    ElMessage.error(error)
  }


}


const handleEnter = () => {
  emits('enterPressed')
}


defineExpose({
  loginAction,
})

</script>

<template>
  <div class="panel-account">
    <el-form
        :model="accountForm"
        :rules="accountRules"
        label-width="60px"
        size="large"
        status-icon
        ref="formRef"
    >
      <el-form-item prop="username">
        <el-input
            v-model="accountForm.username"
            clearable
            autocomplete="off"
            :placeholder="accountRules.username[0].message"
        >
          <template #prefix>
            <el-icon class="el-input__icon">
              <User/>
            </el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item prop="password">
        <el-input
            v-model="accountForm.password"
            show-password
            @keyup.enter="handleEnter"
            :placeholder="accountRules.password[0].message"
        >
          <template #prefix>
            <el-icon class="el-input__icon">
              <Unlock/>
            </el-icon>
          </template>
        </el-input>
      </el-form-item>

      <el-form-item prop="code">
        <VerificationCode
            v-model="accountForm.code"
            type="image"
            @success="handleCaptchaSuccess"
            @enterPressed="handleEnter"
        />
      </el-form-item>


    </el-form>
  </div>
</template>

<style scoped lang="scss">
.panel-account {

}
</style>