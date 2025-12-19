<script setup lang="ts">
import {ref, computed, onMounted, watch} from "vue";
import {ElMessage} from "element-plus";
import {api} from '@/service/request.ts'
import {errorParse} from "@/utils/errorParse.ts";

const props = defineProps({
  type: {
    type: String,
    default: 'image', // 默认值
    validator: (value: string) => ['image', 'sms', 'email'].includes(value)
  },
  placeholder: {
    type: String,
    default: '请输入验证码'
  },
  maxLength: {
    type: Number,
    default: 6
  },
  modelValue: String, // 必须使用 modelValue
  mobile: String,
  email: String
})

console.log('Received type:', props.type)

const emit = defineEmits(['update:modelValue', 'success', 'enterPressed'])

// 使用计算属性处理双向绑定 内部值和外部值同步
const innerCode = ref(props.modelValue)

// 同步到父组件
watch(innerCode, (newValue) =>{
  emit('update:modelValue', newValue)
})

// 监听外部值变化
watch(() => props.modelValue, (newValue) => {
  innerCode.value = newValue
})

// 输入时触发更新
const handleInput = (value) => {
  emit('update:modelValue', value)
}

const handleEnter = () => {
  emit('enterPressed')
}


const captchaImage = ref('')
const countdown = ref(0)
const sending = ref(false)
const timer = ref<number>()

// 短信按钮文本
const buttonText = computed(() => {
  return countdown.value > 0 ? `${countdown.value}秒后重发` : '获取验证码'
})

// 初始化图形验证码
const refreshCaptcha = async () => {
  try {
    const response = await api.get('user/api/captcha/', {responseType: 'blob', params: {_t: Date.now()}})
    const key = response.headers.get('Captcha-Key')
    const blob = new Blob([response.data], {type: response.headers['content-type']})
    captchaImage.value = URL.createObjectURL(blob)
    console.log('captchaImage.key', key)
    console.log('captchaImage.value', captchaImage.value)
    emit('success', key)
  } catch (error) {
    console.log('captchaImage error', error)
    ElMessage.error('图形验证码获取失败')
  }
}

// 发送短信验证码
const sendSmsCode = async () => {
  console.log('sendSmsCode mobile: ', props.mobile)
  if (!props.mobile) {
    ElMessage.warning('请输入手机号码')
    return
  }

  sending.value = true
  try {
    await api.post('user/api/sms-code/', {mobile: props.mobile})
    ElMessage.success('短信验证码发送成功')
    startCountdown()
    emit('success')
  } catch (error) {
    const errorInfo = errorParse(error)
    ElMessage.error(errorInfo || '发送失败，请重试')
  } finally {
    sending.value = false
  }
}

// 发送邮箱验证码
const sendEmailCode = async () => {
  console.log('sendEmailCode email address: ', props.email)
  if (!validateEmail(props.email)) {
    ElMessage.warning('请输入正确的邮箱地址')
    return
  }

  sending.value = true
  try {
    await api.post('user/api/email-code/', {email: props.email})
    ElMessage.success('邮箱验证码发送成功')
    startCountdown()
  } catch (error) {
    ElMessage.error('发送失败，请重试')
  } finally {
    sending.value = false
  }

}

// 邮箱验证正则
const validateEmail = (email: string) => {
  const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  return re.test(email)
}


// 倒计时处理
const startCountdown = () => {
  countdown.value = 60
  timer.value = window.setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--
    } else {
      clearInterval(timer.value)
    }
  }, 1000)
}

onMounted(() => {
  if (props.type === 'image') {
    refreshCaptcha()
  }
})

defineExpose({
  getCode: () => code.value,
  clear: () => {
    code.value = ''
  }
})


</script>

<template>
  <div class="vertication-code">
    <!--图形验证码  -->
    <div v-if="props.type === 'image'" class="captcha-box">
      <el-input
          v-model="innerCode"
          placeholder="请输入验证码"
          :maxlength="4"
          clearable
          @input="handleInput"
          @keyup.enter="handleEnter"
      >
        <template #prefix>
          <el-icon class="el-input__icon">
            <Position/>
          </el-icon>
        </template>
        <template #suffix>

          <el-button class="login-content-captcha">
            <el-image :src="captchaImage" @click="refreshCaptcha"/>
          </el-button>

        </template>
      </el-input>
    </div>

    <!-- 邮箱验证码 -->
    <div v-if="props.type === 'email'" class="email-code">
      <el-input
          v-model="code"
          :placeholder="placeholder"
          :maxlength="6"
          clearable
          @input="handleInput"
          @keyup.enter="handleEnter"
      >
        <template #prefix>
          <el-icon class="el-input__icon">
            <Position/>
          </el-icon>
        </template>
        <template #append>
          <el-button
              :disabled="countdown > 0 || sending"
              @click="sendEmailCode"
          >
            {{ buttonText }}
          </el-button>
        </template>
      </el-input>
    </div>

    <!--    短信验证码-->
    <div v-if="props.type === 'sms'" class="sms-code">
      <el-input
          v-model="code"
          placeholder="请输入短信验证码"
          :maxlength="6"
          clearable
          @input="handleInput"
          @keyup.enter="handleEnter"
      >
        <template #prefix>
          <el-icon class="el-input__icon">
            <Position/>
          </el-icon>
        </template>
        <template #append>
          <el-button
              :disabled="countdown > 0 || sending"
              @click="sendSmsCode"
          >
            {{ buttonText }}

          </el-button>
        </template>

      </el-input>
    </div>


  </div>
</template>

<style scoped lang="scss">
.captcha-box {
  display: flex;
  align-items: center;
  gap: 10px;
}

.captcha-image {
  height: 32px;
  cursor: pointer;
  border-radius: 4px;
}

.sms-code {
  display: flex;
  gap: 10px;
}


.login-content-captcha {
  width: 100%;
  padding: 0;
  font-weight: bold;
  letter-spacing: 5px;
}

</style>