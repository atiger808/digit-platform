<script setup lang="ts">
import {onBeforeUnmount, onMounted, reactive, ref} from 'vue'

// 定时器
let timer: number
const props = reactive( {
  updateInterval: 60000
})
// 添加水印
const watermarkTime = ref('')
const updateTime = () => {
  const date = new Date()
  watermarkTime.value = `大岳数智：${date.toLocaleDateString()} ${date.toLocaleTimeString()}`
}

onMounted(() => {
  updateTime()
  if (props.updateInterval > 0) {
    timer = setInterval(updateTime, props.updateInterval)
  }
})

onBeforeUnmount(() => {
  console.log("onBeforeUnmount timer", timer)
  if (timer) {
    clearInterval(timer)
  }
})


</script>

<template>
  <el-watermark
      :content="[watermarkTime]"
      :font="{ color: 'rgba(0, 0, 0, 0.1)' }"
  >
    <slot/>
  </el-watermark>
</template>

<style scoped lang="scss">

</style>