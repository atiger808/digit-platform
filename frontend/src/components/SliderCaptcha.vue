<template>
  <div class="slider-captcha">
    <div class="captcha-container" ref="captchaContainer">
      <!-- 背景图 -->
      <div class="captcha-bg" ref="bgRef">
        <canvas
          ref="bgCanvasRef"
          :width="canvasWidth"
          :height="canvasHeight"
          class="bg-canvas"
        ></canvas>
        <!-- 拖拽块 -->
        <div
          class="drag-block"
          :style="{
            left: dragBlockLeft + 'px',
            top: gapPosition.top * scale + 'px'
          }"
          ref="dragBlockRef"
        >
          <canvas
            ref="blockCanvasRef"
            :width="blockSizeScaled"
            :height="blockSizeScaled"
            class="block-canvas"
          ></canvas>
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
import { ref, onMounted, onBeforeUnmount, nextTick, computed, withDefaults } from 'vue'
import { ArrowRight, SuccessFilled, CircleCloseFilled, WarnTriangleFilled, Refresh } from '@element-plus/icons-vue'

// 定义 props
interface Props {
  width?: number
  height?: number
  diff?: number // 验证误差范围（像素）
  blockSize?: number // 缺口块大小
  responsive?: boolean // 是否开启响应式
  maxFailCount?: number
}
const props = withDefaults(defineProps<Props>(), {
  width: 442,
  height: 160,
  diff: 10,
  blockSize: 42,
  responsive: true, // 默认开启响应式
  maxFailCount: 2
})

// 定义 emits
const emit = defineEmits<{
  (e: 'success'): void
  (e: 'fail'): void
  (e: 'refresh'): void
}>()

// 响应式数据
const bgCanvasRef = ref<HTMLCanvasElement | null>(null)
const blockCanvasRef = ref<HTMLCanvasElement | null>(null)
const dragBlockLeft = ref(0)
const sliderLeft = ref(0)
const progressWidth = ref(0)
const isDragging = ref(false)
const status = ref<'normal' | 'success' | 'fail'>('normal')
// 验证缺口位置
const gapPosition = ref({ left: 0, top: 0 })
// DOM 引用
const captchaContainer = ref<HTMLElement | null>(null)
const trackRef = ref<HTMLElement | null>(null)

// 响应式尺寸
const containerWidth = ref(props.width)

// 缩放比例
const scale = computed(() => containerWidth.value / props.width)
// 实际渲染尺寸
const canvasWidth = computed(() => containerWidth.value)
const canvasHeight = computed(() => props.height * scale.value)
const blockSizeScaled = computed(() => props.blockSize * scale.value)

// 计算属性
const maxSliderLeft = computed(() => {
  return containerWidth.value - 40 // 40是滑块按钮的宽度
})

// 生成随机位置
const generateRandomPosition = () => {
  const left = Math.floor(Math.random() * (props.width - props.blockSize - 30)) + 15
  const top = Math.floor(Math.random() * (props.height - props.blockSize - 30)) + 15
  return { left, top }
}

// 绘制背景图
const drawBackground = () => {
  if (!bgCanvasRef.value) return
  const canvas = bgCanvasRef.value
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const w = canvas.width
  const h = canvas.height
  const scaleVal = w / props.width

  // 清除画布
  ctx.clearRect(0, 0, w, h)

  // 保存上下文状态
  ctx.save()
  // 应用缩放，使绘制基于原始设计尺寸
  ctx.scale(scaleVal, scaleVal)

  // 绘制背景图案
  drawBackgroundPattern(ctx)

  // 生成缺口位置
  const pos = generateRandomPosition()
  gapPosition.value = pos
  const { left, top } = pos
  const size = props.blockSize

  // 在背景上绘制缺口（白色区域）
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(left, top, size, size)

  // 绘制缺口边框（半透明）
  ctx.strokeStyle = 'rgba(0, 0, 0, 0.1)'
  ctx.lineWidth = 1
  ctx.strokeRect(left, top, size, size)

  // 恢复上下文状态
  ctx.restore()
}

// 绘制背景图案
const drawBackgroundPattern = (ctx: CanvasRenderingContext2D) => {
  // 绘制渐变背景
  const gradient = ctx.createLinearGradient(0, 0, props.width, props.height)
  gradient.addColorStop(0, '#f8f9fa')
  gradient.addColorStop(1, '#e9ecef')
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, props.width, props.height)

  // 绘制随机彩色方块
  for (let i = 0; i < 30; i++) {
    const x = Math.random() * props.width
    const y = Math.random() * props.height
    const size = Math.random() * 20 + 5
    const hue = Math.floor(Math.random() * 360)
    ctx.fillStyle = `hsl(${hue}, 60%, 70%)`
    ctx.fillRect(x, y, size, size)
  }

  // 绘制随机圆形
  for (let i = 0; i < 20; i++) {
    const x = Math.random() * props.width
    const y = Math.random() * props.height
    const radius = Math.random() * 15 + 5
    const hue = Math.floor(Math.random() * 360)
    ctx.fillStyle = `hsl(${hue}, 60%, 80%)`
    ctx.beginPath()
    ctx.arc(x, y, radius, 0, Math.PI * 2)
    ctx.fill()
  }
}

// 绘制拖拽块
const drawBlock = () => {
  if (!blockCanvasRef.value || !bgCanvasRef.value) return
  const blockCanvas = blockCanvasRef.value
  const blockCtx = blockCanvas.getContext('2d')
  const bgCanvas = bgCanvasRef.value
  if (!blockCtx) return

  const size = blockSizeScaled.value
  // 清除拖拽块画布
  blockCtx.clearRect(0, 0, size, size)

  const { left, top } = gapPosition.value
  const scaleVal = containerWidth.value / props.width

  // 从背景图中抠出对应区域绘制到拖拽块上
  try {
    blockCtx.drawImage(
      bgCanvas,
      left * scaleVal, top * scaleVal, // 源区域的起始坐标（按比例缩放）
      props.blockSize * scaleVal, props.blockSize * scaleVal, // 源区域的宽高（按比例缩放）
      0, 0, // 目标区域的起始坐标
      size, size // 目标区域的宽高
    )
  } catch (error) {
    console.warn('绘制拖拽块失败:', error)
    // 如果绘制失败，绘制默认样式
    blockCtx.fillStyle = '#409eff'
    blockCtx.fillRect(0, 0, size, size)
  }

  // 绘制拖拽块阴影效果
  blockCtx.shadowColor = 'rgba(0, 0, 0, 0.3)'
  blockCtx.shadowBlur = 4 * scaleVal
  blockCtx.shadowOffsetX = 2 * scaleVal
  blockCtx.shadowOffsetY = 2 * scaleVal
  blockCtx.strokeStyle = '#409eff'
  blockCtx.lineWidth = 2 * scaleVal
  blockCtx.strokeRect(0, 0, size, size)
  blockCtx.shadowColor = 'transparent'
  blockCtx.shadowBlur = 0
  blockCtx.shadowOffsetX = 0
  blockCtx.shadowOffsetY = 0
}

// 生成验证码
const generateCaptcha = () => {
  try {
    // 重置状态
    resetState()
    // 绘制背景
    drawBackground()
    // 延迟绘制拖拽块，确保背景绘制完成
    nextTick(() => {
      drawBlock()
    })
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

// 开始拖拽
const startDrag = (event: MouseEvent | TouchEvent) => {
  if (status.value === 'success') return
  isDragging.value = true
  status.value = 'normal'

  const startX = 'touches' in event ? event.touches[0].clientX : event.clientX
  const startLeft = sliderLeft.value

  event.preventDefault()

  const handleMove = (moveEvent: MouseEvent | TouchEvent) => {
    if (!isDragging.value) return

    const currentX = 'touches' in moveEvent ? moveEvent.touches[0].clientX : moveEvent.clientX
    const diffX = currentX - startX
    const newLeft = Math.max(0, Math.min(startLeft + diffX, maxSliderLeft.value))

    // 平滑更新
    sliderLeft.value = newLeft
    progressWidth.value = newLeft
    dragBlockLeft.value = newLeft

    moveEvent.preventDefault()
    moveEvent.stopPropagation()
  }

  const handleEnd = () => {
    if (!isDragging.value) return
    stopDrag()
    // 验证位置
    verifyPosition()
  }

  const stopDrag = () => {
    isDragging.value = false
    document.removeEventListener('mousemove', handleMove, { passive: false })
    document.removeEventListener('touchmove', handleMove, { passive: false })
    document.removeEventListener('mouseup', handleEnd)
    document.removeEventListener('touchend', handleEnd)
  }

  // 添加事件监听器
  document.addEventListener('mousemove', handleMove, { passive: false })
  document.addEventListener('touchmove', handleMove, { passive: false })
  document.addEventListener('mouseup', handleEnd)
  document.addEventListener('touchend', handleEnd)
}

const failCount = ref(1)

// 验证位置
const verifyPosition = () => {
  // 获取滑块当前位置（已缩放）
  const currentLeft = sliderLeft.value
  // 获取缺口的目标位置（原始坐标，需要按比例缩放）
  const targetLeft = gapPosition.value.left * scale.value
  // 计算误差（原始误差值也需要按比例缩放）
  const diff = Math.abs(currentLeft - targetLeft)
  const allowedDiff = props.diff * scale.value // 误差范围也按比例缩放

  console.log('当前位置:', currentLeft, '目标位置:', targetLeft, '误差:', diff, '允许误差:', allowedDiff)

  if (diff <= allowedDiff) {
    verifySuccess()
  } else {
    verifyFail()
    if (failCount.value >= props.maxFailCount) {
      refreshCaptcha()
      failCount.value = 0
    }
    failCount.value++
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
  setTimeout(() => {
    if (status.value === 'fail') {
      resetState()
    }
  }, 500)
}

// 动态调整尺寸
const updateSize = () => {
  if (!props.responsive || !captchaContainer.value) {
    containerWidth.value = props.width
    return
  }
  const rect = captchaContainer.value.getBoundingClientRect()
  containerWidth.value = Math.min(rect.width, window.innerWidth * 0.9)
}

// 组件挂载时生成验证码
onMounted(() => {
  // 监听窗口大小变化
  window.addEventListener('resize', updateSize)
  // 先更新一次尺寸
  updateSize()
  // 再生成验证码
  nextTick(() => {
    generateCaptcha()
  })
})

// 组件卸载时清理
onBeforeUnmount(() => {
  window.removeEventListener('resize', updateSize)
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
    user-select: none; // 防止拖拽时选中文本
    width: 100%; // 确保占满父容器宽度
    max-width: 442px; // 限制最大宽度，与PC端一致

    .captcha-bg {
      position: relative;
      width: 100%;
      height: v-bind('canvasHeight + "px"');
      overflow: hidden;

      .bg-canvas {
        width: 100%;
        height: 100%;
        display: block;
        background: #f8f9fa;
      }

      .drag-block {
        position: absolute;
        width: v-bind('blockSizeScaled + "px"');
        height: v-bind('blockSizeScaled + "px"');
        transition: none;
        z-index: 10;
        cursor: move;
        pointer-events: none;

        .block-canvas {
          width: 100%;
          height: 100%;
          display: block;
          border-radius: 2px;
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
        //background: linear-gradient(90deg, #ecf5ff, #d9ecff);
        //background: linear-gradient(90deg, #ecf5ff, #62a9f3);
        background: #91c6fd;
        border-bottom: 1px solid #529fef;
        transition: width 0.05s linear;
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
        transition: all 0.1s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        z-index: 5;

        &:hover {
          border-color: #409eff;
          box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
        }

        &.slider-btn-active {
          cursor: grabbing;
          border-color: #409eff;
          background: #ecf5ff;
          transform: translateY(-50%) scale(1.05);
        }

        .el-icon {
          font-size: 16px;
          color: #909399;
          transition: all 0.1s ease;
        }
      }
    }

    .slider-text {
      padding: 12px;
      font-size: 12px;
      text-align: center;
      min-height: 20px;

      .success-text,
      .fail-text,
      .normal-text {
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
      background: rgba(255, 255, 255, 0.95);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      z-index: 20;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);

      &:hover {
        background: rgba(255, 255, 255, 1);
        transform: rotate(180deg);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }

      .el-icon {
        font-size: 16px;
        color: #909399;
      }
    }
  }
}

// 动画
@keyframes successPulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

@keyframes failShake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}
</style>