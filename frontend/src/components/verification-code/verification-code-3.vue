<template>
  <div class="code-input">
    <el-input v-model="code" v-bind="$attrs">
      <template #append>
        <el-button
          :disabled="countdown > 0 || sending"
          @click="sendCode"
        >
          {{ buttonText }}
        </el-button>
      </template>
    </el-input>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import axios from 'axios'

const props = defineProps({
  type: {
    type: String,
    required: true
  },
  identifier: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'send'])

const code = ref('')
const countdown = ref(0)
const sending = ref(false)

const buttonText = computed(() => {
  return countdown.value > 0
    ? `${countdown.value}秒后重发`
    : '获取验证码'
})

const sendCode = async () => {
  sending.value = true
  try {
    await emit('send')
    startCountdown()
  } finally {
    sending.value = false
  }
}

const startCountdown = (seconds = 60) => {
  countdown.value = seconds
  const timer = setInterval(() => {
    if (countdown.value <= 0) {
      clearInterval(timer)
      return
    }
    countdown.value--
  }, 1000)
}

watch(code, (val) => {
  emit('update:modelValue', val)
})
</script>