<template>
  <div class="auth-container">
    <el-tabs v-model="activeTab">
      <!-- 账号密码登录 -->
      <el-tab-pane label="账号登录" name="account">
        <account-login @success="onLoginSuccess" />
      </el-tab-pane>

      <!-- 手机号登录 -->
      <el-tab-pane label="手机登录" name="mobile">
        <mobile-login @success="onLoginSuccess" />
      </el-tab-pane>

      <!-- 邮箱登录 -->
      <el-tab-pane label="邮箱登录" name="email">
        <email-login @success="onLoginSuccess" />
      </el-tab-pane>
    </el-tabs>

    <!-- 图形验证码组件 -->
    <captcha-dialog
      v-model:visible="showCaptcha"
      :key="captchaKey"
      @verified="handleCaptchaVerified"
    />
  </div>
</template>

<script setup>
import { ref, provide } from 'vue'
import AccountLogin from './c-cpns/AccountLogin.vue'
import MobileLogin from './c-cpns/MobileLogin.vue'
import EmailLogin from './c-cpns/EmailLogin.vue'
import CaptchaDialog from './c-cpns/CaptchaDialog.vue'

const activeTab = ref('account')
const showCaptcha = ref(false)
const captchaKey = ref('')
const pendingRequest = ref(null)

// 全局提供验证码触发方法
provide('requireCaptcha', (callback) => {
  pendingRequest.value = callback
  showCaptcha.value = true
})

const handleCaptchaVerified = (captchaData) => {
  pendingRequest.value?.(captchaData)
  pendingRequest.value = null
  showCaptcha.value = false
}

const onLoginSuccess = () => {
  // 处理登录成功逻辑
}
</script>