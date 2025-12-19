<template>
  <el-form :model="form" :rules="rules" ref="formRef">
    <el-form-item prop="mobile">
      <el-input v-model="form.mobile" placeholder="手机号">
        <template #prefix>+86</template>
      </el-input>
    </el-form-item>

    <el-form-item prop="code">
      <verification-code
        v-model="form.code"
        type="sms"
        :identifier="form.mobile"
        @send="sendSmsCode"
      />
    </el-form-item>

    <el-button type="primary" @click="submit">登录/注册</el-button>
  </el-form>
</template>

<script setup>
import { ref, watch } from 'vue'
import {api} from '@/service/request.js'

const form = ref({
  mobile: '',
  code: ''
})

const rules = {
  mobile: [
    {
      pattern: /^1[3-9]\d{9}$/,
      message: '手机号格式错误',
      trigger: 'blur'
    }
  ],
  code: [
    {
      pattern: /^\d{6}$/,
      message: '验证码为6位数字',
      trigger: 'blur'
    }
  ]
}

const sendSmsCode = async () => {
  await api.post('user/api/send-captcha/', {
    mobile: form.value.mobile,
    type: 'login'
  })
}

const submit = async () => {
  await api.post('user/api/auth/login/', form.value)
  // 处理成功逻辑
}
</script>