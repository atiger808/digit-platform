<template>
  <el-dialog v-model="visible" title="安全验证">
    <div class="captcha-container">
      <img :src="captchaImage" @click="refreshCaptcha">
      <el-input v-model="inputCode" placeholder="输入图形验证码" />
    </div>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="verify">验证</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import {api} from '@/service/request.js'

const props = defineProps(['key'])
const emit = defineEmits(['verified'])

const visible = defineModel('visible')
const captchaImage = ref('')
const inputCode = ref('')
let currentKey = ''



const refreshCaptcha = async () => {
  const res = await api.get('user/api/captcha/', {responseType: 'blob', params: {_t: Date.now()}})
  currentKey = res.headers['captcha-key']
  captchaImage.value = URL.createObjectURL(res.data)
}

const verify = async () => {
  emit('verified', {
    key: currentKey,
    code: inputCode.value
  })
  visible.value = false
}

watch(() => props.key, refreshCaptcha)

</script>