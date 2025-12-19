<script setup lang="ts">
import {ref, computed, watch} from "vue";
import {api} from '@/service/request.ts'
import {ElMessage} from "element-plus";
import {errorParse} from '@/utils/errorParse.ts'

const props = defineProps({
  type: { // register | login | reset
    type: String,
    required: true
  },
  identifier: { // 邮箱 / 手机号
    type: String,
    required: true
  },
  needCaptcha: { // 是否需要验证码
    type: Boolean,
    required: true
  }
})

console.log('props: ', props)

const emit = defineEmits(['update:code', 'send-success'])

const code = ref('')
const countdown = ref(0)
const sending = ref(false)
let timer: number

// 按钮显示文本
const buttonText = computed(() => {
  return countdown.value > 0
      ? `${countdown.value}秒后重发`
      : '获取验证码'
})

// 发送验证码
const sendCode = async () => {
  if (!validateIdentifier()) return

  sending.value = true
  try {
    const response  = await api.post('user/api/sms-captcha/', {
      identifier: props.identifier,
      code_type: props.type
    })
    console.log('sendCode response: ', response)
    if (response.data.success) {
      ElMessage.success('验证码发送成功')
      startCountdown()
      emit('send-success')
    }

  } catch (error){
    console.log('sendCode error: ', error)
    const errorInfo = errorParse(error)
    ElMessage.error(errorInfo || '发送失败，请重试')
  } finally {
    sending.value = false
  }

}

// 开始倒计时
const startCountdown = (seconds = 60) => {
  countdown.value = seconds
  timer = window.setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--
    } else {
      clearInterval(timer)
    }
  }, 1000)
}

// 验证码标识格式
const validateIdentifier = () => {
  const isEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(props.identifier)
  const isMobile = /^1[3-9]\d{9}$/.test(props.identifier)

  if (!isEmail && !isMobile){
    ElMessage.warning('请输入正确的邮箱或手机号')
    return false
  }
  return true
}


// 监听code变化
watch(code, (newValue) => {
  emit('update:code', newValue)
})

// 自动发送验证码（当需要强制验证时）
watch(() => props.needCaptcha, (newValue) => {
  if (newValue) sendCode()
})


</script>

<template>
  <div class="verification-container">
    <!--    验证码输入-->
    <el-input
        v-model="code"
        :placeholder="placeholder"
        clearable
        class="code-input"
    >
      <template #append>
        <el-button
            :disabled="countdown > 0 || sending"
            @click="sendCode"
            class="send-btn"
        >
          {{ buttonText }}

        </el-button>
      </template>

    </el-input>
  </div>
</template>

<style scoped lang="scss">
.verification-container {
  display: flex;
  gap: 10px;
}

.code-input {
  flex: 1;
}
.send-btn {
  width: 120px;
}

</style>