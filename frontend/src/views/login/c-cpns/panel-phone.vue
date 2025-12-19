<script setup lang="ts">
import {ref, reactive, computed} from "vue";
import {useRouter} from 'vue-router'
import type {FormRules, ElForm} from "element-plus";
import type {IPhone} from "@/types/types.ts";
import {useLoginStore} from "@/store/login/login.ts";
import {PhoneFilled, Unlock} from "@element-plus/icons-vue";
import VerificationCode from "@/components/verification-code/verification-code.vue";

const router = useRouter()


// 登录失败计数器（使用localStorage持久化）
const loginFailedCount = ref(
    parseInt(localStorage.getItem('loginFailedCount') || 0)
);


const loginStore = useLoginStore()

// 表单数据
const accountForm = reactive({
  identifier: '',
  password: '',
  code: ''
})

// 是否显示验证码
const showCaptcha = computed(() => loginFailedCount >= 3)

// 验证规则
const rules = reactive({
  identifier: [
    {required: true, message: '请输入邮箱/手机号', trigger: 'blur'},
    {
      validator: (_, value, callback) => {
        const isEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
        const isMobile = /^1[3-9]\d{9}$/.test(value)
        if (!isEmail && !isMobile) {
          callback(new Error('格式不正确'))
        } else {
          callback()
        }
      },
      trigger: ['blur', 'change']
    }
  ],
  password: [
    {required: true, message: '请输入密码', trigger: 'blur'},
    {min: 6, max: 20, message: '长度6-20位', trigger: 'blur'}
  ],
  code: [
    {
      required: showCaptcha,
      message: '请输入验证码',
      trigger: 'blur'
    }
  ]
})

// 3.执行手机号登录逻辑
const formRef = ref<InstanceType<typeof ElForm>>()
const phoneLoginAction = () => {
  console.log('手机号登录')
  formRef.value?.validate(async (valid: any) => {
    if (valid) {
      console.log('手机号登录成功')
      // accountForm.code = 'aaaa'
      const params = showCaptcha.value
          ? {...accountForm, need_captcha: true}
          : accountForm
      console.log('panel-phone phoneLoginAction excute', params)
      let {success, error} = await loginStore.loginPhoneAction(params)
      if (!success) {
        loginFailedCount.value++
        localStorage.setItem('loginFailedCount', loginFailedCount.value.toString())
        ElMessage.error(`${error}，剩余尝试次数：${3 - loginFailedCount.value}`)

        // 强制显示验证码
        if (loginFailedCount.value >= 3) {
          ElMessage.warning('请输入验证码继续登录')
        }

      } else {
        localStorage.setItem('loginFailedCount', '0')
        loginFailedCount.value = 0
        ElMessage.success('登录成功')
      }
    } else {
      console.log('手机号验证失败,请检查输入格式是否正确~')
      ElMessage.error('手机号验证失败,请检查输入格式是否正确~')
    }
  })

  console.log('panel-phone phoneLoginAction excute', accountForm)

}

// 当标识改变时重置验证码
const handleIdentifierChange = () => {
  accountForm.code = ''
  loginFailedCount.value = 0
  localStorage.setItem('loginFailedCount', '0')
}

// 验证码发送成功处理
const handleSendSuccess = () => {
  ElMessage.info('验证码已发送，请注意查收')
}

const handleGetCode = () => {
  console.log('获取验证码')
}

defineExpose({
  phoneLoginAction
})

</script>

<template>
  <div class="panel-phone">

    <el-form
        :model="accountForm"
        :rules="rules"
        label-width="60px"
        size="large"
        status-icon
        ref="formRef"
    >
      <el-form-item prop="identifier">
        <!-- 账号输入 -->
        <el-input
            v-model="accountForm.identifier"
            :placeholder="rules.identifier[0].message"
            @change="handleIdentifierChange"
        >
          <template #prefix>
            <el-icon class="el-input__icon">
              <Phone/>
            </el-icon>
          </template>
        </el-input>
      </el-form-item>

      <!-- 密码输入 -->
      <el-form-item prop="password">
        <el-input
            v-model="accountForm.password"
            type="password"
            :placeholder="rules.password[0].message"
            show-password
        >
          <template #prefix>
            <el-icon class="el-input__icon">
              <Unlock/>
            </el-icon>
          </template>

        </el-input>

      </el-form-item>

      <!-- 验证码组件 -->
      <el-form-item v-if="showCaptcha" prop="code">
        <VerificationCode
            v-model:code="accountForm.code"
            :type="'login'"
            :identifier="accountForm.identifier"
            :need-captcha="true"
            @send-success="handleSendSuccess"
        />
      </el-form-item>


    </el-form>

  </div>
</template>

<style scoped lang="scss">
.panel-phone {
}

.verify-code {
  display: flex;

  .get-code {
    margin-left: 8px;
  }
}

</style>