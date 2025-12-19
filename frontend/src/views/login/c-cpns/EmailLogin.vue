<template>
  <el-form :model="form" :rules="rules" ref="formRef">
    <el-form-item prop="email">
      <el-input v-model="form.email" placeholder="邮箱地址" />
    </el-form-item>

    <el-form-item prop="code">
      <verification-code
        v-model="form.code"
        type="email"
        :identifier="form.email"
        @send="sendEmailCode"
      />
    </el-form-item>

    <el-button type="primary" @click="submit">登录/注册</el-button>
  </el-form>
</template>

<script setup>
import { ref } from 'vue'
import {api} from '@/service/request.js'

const form = ref({
  email: '',
  code: ''
})

const rules = {
  email: [
    { type: 'email', message: '邮箱格式错误', trigger: 'blur' }
  ],
  code: [
    { len: 6, message: '验证码为6位字符', trigger: 'blur' }
  ]
}

const sendEmailCode = async () => {
  await api.post('user/api/send-captcha/', {
    email: form.value.email,
    type: 'login'
  })
}

const submit = async () => {
  await api.post('user/api/auth/login/', form.value)
  // 处理成功逻辑
}
</script>