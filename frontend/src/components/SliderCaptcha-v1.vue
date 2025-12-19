<template>
  <div class="slider-captcha">
    <div class="captcha-container" ref="captchaContainer">
      <!-- 背景图 -->
      <div class="captcha-bg" ref="bgRef">
        <img
          ref="bgImgRef"
          :src="bgImageData"
          alt="验证码背景"
          @load="onBgLoad"
          class="bg-image"
        />
        <!-- 拖拽块 -->
        <div
          class="drag-block"
          :style="{
            left: dragBlockLeft + 'px',
            top: gapPosition.top + 'px'
          }"
          ref="dragBlockRef"
        >
          <img
            ref="blockImgRef"
            :src="blockImageData"
            alt="拖拽块"
            class="block-image"
          />
        </div>
      </div>

      <!-- 滑块轨道 -->
      <div class="slider-track" ref="trackRef">
        <div
          class="slider-progress"
          :style="{ width: progressWidth + 'px' }"
        ></div>
        <div
          class="slider-btn"
          :class="{ 'slider-btn-active': isDragging }"
          :style="{ left: sliderLeft + 'px' }"
          @mousedown="startDrag"
          @touchstart="startDrag"
        >
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>

      <!-- 提示文字 -->
      <div class="slider-text">
        <span v-if="status === 'success'" class="success-text">
          <el-icon color="#67c23a"><SuccessFilled /></el-icon>
          验证成功
        </span>
        <span v-else-if="status === 'fail'" class="fail-text">
          <el-icon color="#f56c6c"><CircleCloseFilled /></el-icon>
          验证失败，请重试
        </span>
        <span v-else class="normal-text">
          <el-icon><WarnTriangleFilled /></el-icon>
          拖动滑块完成验证
        </span>
      </div>

      <!-- 刷新按钮 -->
      <div class="refresh-btn" @click="refreshCaptcha">
        <el-icon><Refresh /></el-icon>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { ArrowRight, SuccessFilled, CircleCloseFilled, WarnTriangleFilled, Refresh } from '@element-plus/icons-vue'

// 定义 props
interface Props {
  width?: number
  height?: number
  diff?: number // 验证误差范围（像素）
}

const props = withDefaults(defineProps<Props>(), {
  width: 442,
  height: 160,
  diff: 10
})

// 定义 emits
const emit = defineEmits<{
  (e: 'success'): void
  (e: 'fail'): void
  (e: 'refresh'): void
}>()

// 响应式数据
const bgImgRef = ref<HTMLImageElement | null>(null)
const blockImgRef = ref<HTMLImageElement | null>(null)
const bgImageData = ref('')
const blockImageData = ref('')
const dragBlockLeft = ref(0)
const sliderLeft = ref(0)
const progressWidth = ref(0)
const isDragging = ref(false)
const status = ref<'normal' | 'success' | 'fail'>('normal')

// 验证缺口位置
const gapPosition = ref({
  left: 0,
  top: 0
})

// DOM 引用
const captchaContainer = ref<HTMLElement | null>(null)
const bgRef = ref<HTMLElement | null>(null)
const dragBlockRef = ref<HTMLElement | null>(null)
const trackRef = ref<HTMLElement | null>(null)

// 计算属性
const maxSliderLeft = computed(() => {
  return props.width - 40 // 40是滑块按钮的宽度
})

// 生成随机验证码数据
const generateCaptchaData = () => {
  // 生成背景图（这里使用Canvas生成模拟图片）
  const bgCanvas = document.createElement('canvas')
  bgCanvas.width = props.width
  bgCanvas.height = props.height
  console.log("props ", props)
  const bgCtx = bgCanvas.getContext('2d')

  if (bgCtx) {
    // 绘制背景
    bgCtx.fillStyle = '#f0f0f0'
    bgCtx.fillRect(0, 0, props.width, props.height)

    // 添加随机图案
    for (let i = 0; i < 15; i++) {
      const x = Math.random() * props.width
      const y = Math.random() * props.height
      const radius = Math.random() * 20 + 10
      bgCtx.fillStyle = `hsl(${Math.random() * 360}, 60%, 70%)`
      bgCtx.beginPath()
      bgCtx.arc(x, y, radius, 0, Math.PI * 2)
      bgCtx.fill()
    }

    // 生成缺口位置
    const gapLeft = Math.floor(Math.random() * (props.width - 80)) + 40
    const gapTop = Math.floor(Math.random() * (props.height - 80)) + 40
    gapPosition.value = { left: gapLeft, top: gapTop }

    // 绘制缺口（白色区域）
    bgCtx.fillStyle = '#ffffff'
    bgCtx.fillRect(gapLeft, gapTop, 40, 40)

    // 绘制缺口边框
    bgCtx.strokeStyle = '#cccccc'
    bgCtx.lineWidth = 1
    bgCtx.strokeRect(gapLeft, gapTop, 40, 40)
  }

  bgImageData.value = bgCanvas.toDataURL()

  // 生成拖拽块
  const blockCanvas = document.createElement('canvas')
  blockCanvas.width = 42
  blockCanvas.height = 42
  const blockCtx = blockCanvas.getContext('2d')

  if (blockCtx) {
    // 绘制拖拽块
    blockCtx.fillStyle = '#409eff'
    blockCtx.fillRect(1, 1, 40, 40)

    blockCtx.strokeStyle = '#409eff'
    blockCtx.lineWidth = 2
    blockCtx.strokeRect(1, 1, 40, 40)

    // 添加文字
    blockCtx.fillStyle = 'white'
    blockCtx.font = '12px Arial'
    blockCtx.textAlign = 'center'
    blockCtx.textBaseline = 'middle'
    blockCtx.fillText('→', 21, 21)
  }

  blockImageData.value = blockCanvas.toDataURL()
}

// 生成验证码
const generateCaptcha = () => {
  try {
    // 重置状态
    resetState()

    // 生成验证码数据
    generateCaptchaData()

  } catch (error) {
    console.error('生成验证码失败:', error)
  }
}

// 重置状态
const resetState = () => {
  dragBlockLeft.value = 0
  sliderLeft.value = 0
  progressWidth.value = 0
  status.value = 'normal'
}

// 刷新验证码
const refreshCaptcha = () => {
  generateCaptcha()
  emit('refresh')
}

// 背景图加载完成
const onBgLoad = () => {
  // 可以在这里做一些初始化操作
}

// 开始拖拽
const startDrag = (event: MouseEvent | TouchEvent) => {
  if (status.value === 'success') return

  isDragging.value = true
  status.value = 'normal'

  const startX = 'touches' in event ? event.touches[0].clientX : event.clientX
  const startLeft = sliderLeft.value

  const handleMove = (moveEvent: MouseEvent | TouchEvent) => {
    if (!isDragging.value) return

    const currentX = 'touches' in moveEvent ? moveEvent.touches[0].clientX : moveEvent.clientX
    const diffX = currentX - startX
    const newLeft = Math.max(0, Math.min(startLeft + diffX, maxSliderLeft.value))

    sliderLeft.value = newLeft
    progressWidth.value = newLeft
    dragBlockLeft.value = newLeft
  }

  const handleEnd = () => {
    if (!isDragging.value) return
    stopDrag()

    // 验证位置
    verifyPosition()
  }

  const stopDrag = () => {
    isDragging.value = false
    document.removeEventListener('mousemove', handleMove)
    document.removeEventListener('touchmove', handleMove)
    document.removeEventListener('mouseup', handleEnd)
    document.removeEventListener('touchend', handleEnd)
  }

  document.addEventListener('mousemove', handleMove)
  document.addEventListener('touchmove', handleMove)
  document.addEventListener('mouseup', handleEnd)
  document.addEventListener('touchend', handleEnd)

  event.preventDefault()
}

// 验证位置
const verifyPosition = () => {
  const currentLeft = dragBlockLeft.value
  const targetLeft = gapPosition.value.left
  const diff = Math.abs(currentLeft - targetLeft)

  console.log('当前位置:', currentLeft, '目标位置:', targetLeft, '误差:', diff)

  if (diff <= props.diff) {
    verifySuccess()
  } else {
    verifyFail()
  }
}

// 验证成功
const verifySuccess = () => {
  status.value = 'success'
  emit('success')
}

// 验证失败
const verifyFail = () => {
  status.value = 'fail'
  emit('fail')

  // 1秒后自动重置
  setTimeout(() => {
    if (status.value === 'fail') {
      resetState()
    }
  }, 1000)
}

// 组件挂载时生成验证码
onMounted(() => {
  generateCaptcha()
})

// 组件卸载时清理事件监听
onUnmounted(() => {
  isDragging.value = false
})

// 暴露方法给父组件
defineExpose({
  refresh: refreshCaptcha,
  reset: resetState
})
</script>

<style scoped lang="scss">
.slider-captcha {
  .captcha-container {
    position: relative;
    border: 1px solid #dcdfe6;
    border-radius: 8px;
    overflow: hidden;
    background: white;

    .captcha-bg {
      position: relative;
      width: 100%;
      height: v-bind('props.height + "px"');
      overflow: hidden;
      background: #f5f5f5;

      .bg-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
      }

      .drag-block {
        position: absolute;
        width: 42px;
        height: 42px;
        transition: left 0.1s linear;
        z-index: 10;
        box-shadow: 0 0 8px rgba(0, 0, 0, 0.3);
        border-radius: 4px;
        cursor: move;

        .block-image {
          width: 100%;
          height: 100%;
          object-fit: cover;
          display: block;
          border-radius: 4px;
        }
      }
    }

    .slider-track {
      position: relative;
      width: 100%;
      height: 40px;
      background: #f5f7fa;
      border-top: 1px solid #dcdfe6;
      cursor: pointer;

      .slider-progress {
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        background: #ecf5ff;
        transition: width 0.1s linear;
      }

      .slider-btn {
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 40px;
        height: 36px;
        background: #fff;
        border: 1px solid #dcdfe6;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: grab;
        transition: all 0.2s;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        z-index: 5;

        &:hover {
          border-color: #409eff;
        }

        &.slider-btn-active {
          cursor: grabbing;
          border-color: #409eff;
          background: #ecf5ff;
        }

        .el-icon {
          font-size: 16px;
          color: #909399;
        }
      }
    }

    .slider-text {
      padding: 12px;
      font-size: 12px;
      text-align: center;
      min-height: 20px;

      .success-text {
        color: #67c23a;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
      }

      .fail-text {
        color: #f56c6c;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
      }

      .normal-text {
        color: #909399;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
      }
    }

    .refresh-btn {
      position: absolute;
      top: 10px;
      right: 10px;
      width: 30px;
      height: 30px;
      background: rgba(255, 255, 255, 0.9);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.3s;
      z-index: 20;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);

      &:hover {
        background: rgba(255, 255, 255, 1);
        transform: rotate(180deg);
      }

      .el-icon {
        font-size: 16px;
        color: #909399;
      }
    }
  }
}
</style>