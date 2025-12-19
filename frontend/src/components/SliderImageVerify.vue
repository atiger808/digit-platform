<template>
  <div class="slider-image-verify">
    <!-- 背景图片容器 -->
    <div class="image-container" ref="imageContainer">
      <img :src="bgImage" alt="验证背景图" class="bg-image" ref="bgImage" />
      <!-- 滑块图片 -->
      <div
        class="slider-image"
        :style="{ left: `${sliderLeft}px`, backgroundImage: `url(${sliderImage})` }"
      ></div>
      <!-- 提示文字 -->
      <div class="verify-text" :style="{ color: textColor }">
        {{ verifyText }}
      </div>
      <!-- 刷新按钮 -->
      <div class="refresh-btn" @click="refreshImages">
        <el-icon><Refresh /></el-icon>
      </div>
    </div>

    <!-- 滑块轨道 -->
    <div class="slider-track">
      <div
        class="slider-btn"
        ref="sliderBtn"
        :style="{ left: `${sliderLeft}px` }"
        @mousedown="onSliderDown"
      >
        <el-icon><Right /></el-icon>
      </div>
      <div class="slider-bar" :style="{ width: `${sliderLeft}px` }"></div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { Refresh, Right } from '@element-plus/icons-vue'

// 定义Props
const props = defineProps({
  width: {
    type: Number,
    default: 320
  },
  height: {
    type: Number,
    default: 160
  }
})

// 定义事件
const emit = defineEmits(['success', 'error'])

// 图片URL - 实际项目中应从后端获取
const bgImage = ref('https://picsum.photos/320/160?random=1')
const sliderImage = ref('')
// 滑块位置
const sliderLeft = ref(0)
// 缺口位置
const gapPosition = ref(0)
// 验证文字
const verifyText = ref('拖动滑块完成拼图')
// 文字颜色
const textColor = ref('#666')
// 是否正在拖动
const isDragging = ref(false)
// 开始位置
const startX = ref(0)

// 获取DOM元素
const imageContainer = ref<HTMLElement | null>(null)
const bgImageRef = ref<HTMLImageElement | null>(null)
const sliderBtn = ref<HTMLElement | null>(null)

// 初始化验证
const initVerify = () => {
  sliderLeft.value = 0
  verifyText.value = '拖动滑块完成拼图'
  textColor.value = '#666'

  // 随机生成缺口位置 (20-280)
  gapPosition.value = Math.floor(Math.random() * 260) + 20

  // 实际项目中应从后端获取带缺口的图片
  sliderImage.value = `https://picsum.photos/40/${props.height}?random=${Math.floor(Math.random() * 100)}`
}

// 刷新图片
const refreshImages = () => {
  bgImage.value = `https://picsum.photos/${props.width}/${props.height}?random=${Math.floor(Math.random() * 100)}`
  initVerify()
}

// 鼠标按下事件
const onSliderDown = (e: MouseEvent) => {
  if (isDragging.value) return

  isDragging.value = true
  startX.value = e.clientX - sliderLeft.value

  document.addEventListener('mousemove', onSliderMove)
  document.addEventListener('mouseup', onSliderUp)
}

// 鼠标移动事件
const onSliderMove = (e: MouseEvent) => {
  if (!isDragging.value) return

  const newLeft = e.clientX - startX.value
  const maxLeft = props.width - 40 // 滑块宽度为40px

  // 限制滑块在轨道内移动
  if (newLeft < 0) {
    sliderLeft.value = 0
  } else if (newLeft > maxLeft) {
    sliderLeft.value = maxLeft
  } else {
    sliderLeft.value = newLeft
  }
}

// 鼠标释放事件
const onSliderUp = () => {
  if (!isDragging.value) return

  isDragging.value = false
  document.removeEventListener('mousemove', onSliderMove)
  document.removeEventListener('mouseup', onSliderUp)

  // 验证结果
  const tolerance = 5 // 允许的误差范围
  if (Math.abs(sliderLeft.value - gapPosition.value) <= tolerance) {
    // 验证成功
    verifyText.value = '验证通过'
    textColor.value = '#67c23a'
    emit('success')
  } else {
    // 验证失败
    verifyText.value = '验证失败，请重试'
    textColor.value = '#f56c6c'
    setTimeout(() => {
      sliderLeft.value = 0
      verifyText.value = '拖动滑块完成拼图'
      textColor.value = '#666'
    }, 1000)
    emit('error')
  }
}

// 初始化
onMounted(() => {
  initVerify()
})

// 组件卸载前移除事件监听
onBeforeUnmount(() => {
  document.removeEventListener('mousemove', onSliderMove)
  document.removeEventListener('mouseup', onSliderUp)
})

// 暴露方法供父组件调用
defineExpose({
  refreshImages
})
</script>

<style scoped>
.slider-image-verify {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.image-container {
  position: relative;
  width: 100%;
  height: 160px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.bg-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.slider-image {
  position: absolute;
  top: 0;
  width: 40px;
  height: 100%;
  background-size: cover;
  background-position: center;
  border-radius: 4px;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.3);
  z-index: 2;
  pointer-events: none;
}

.verify-text {
  position: absolute;
  bottom: 10px;
  left: 0;
  width: 100%;
  text-align: center;
  font-size: 14px;
  font-weight: bold;
  text-shadow: 0 0 2px white;
  z-index: 3;
}

.refresh-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 3;
  transition: all 0.3s;
}

.refresh-btn:hover {
  background-color: rgba(255, 255, 255, 1);
  transform: rotate(90deg);
}

.slider-track {
  position: relative;
  width: 100%;
  height: 40px;
  background-color: #f5f7fa;
  border-radius: 20px;
  overflow: hidden;
}

.slider-bar {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  background-color: #409eff;
  transition: width 0.1s;
}

.slider-btn {
  position: absolute;
  top: 0;
  width: 40px;
  height: 40px;
  background-color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: move;
  z-index: 2;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  user-select: none;
  transition: background-color 0.3s;
}

.slider-btn:hover {
  background-color: #f5f7fa;
}
</style>