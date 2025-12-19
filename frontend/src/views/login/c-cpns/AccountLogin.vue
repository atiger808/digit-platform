<template>
  <el-form :model="form" :rules="rules" ref="formRef">
    <el-form-item prop="username">
      <el-input v-model="form.username" placeholder="用户名/邮箱/手机号" />
    </el-form-item>

    <el-form-item prop="password">
      <el-input
        v-model="form.password"
        type="password"
        show-password
        placeholder="密码"
      />
    </el-form-item>

    <el-button type="primary" @click="submit">登录</el-button>
  </el-form>
</template>

<script setup>
import { ref, inject } from 'vue'
import {api} from '@/service/request.js'

const form = ref({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const requireCaptcha = inject('requireCaptcha')
const errorCount = ref(0)

const submit = async () => {
  try {
    let params = { ...form.value }

    // 需要验证码时的处理
    const doRequest = (captcha) => {
      if (captcha) params = { ...params, ...captcha }
      return api.post('user/api/auth/login/', params)
    }

    // 触发验证码校验
    if (errorCount.value >= 3) {
      await new Promise((resolve) => {
        requireCaptcha(async (captcha) => {
          try {
            await doRequest(captcha)
            resolve()
          } catch (e) {
            errorCount.value++
          }
        })
      })
    } else {
      await doRequest()
    }

    // 登录成功处理...

  } catch (error) {
    errorCount.value++
  }
}
</script>