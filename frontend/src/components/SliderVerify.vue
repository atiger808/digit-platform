<template>
  <div class="slider-verify">
    <div
      class="slider-bg"
      :style="{ backgroundColor: bgColor }"
    >
      <div
        class="slider-btn"
        @mousedown="handleMouseDown"
        :style="{ left: btnLeft + 'px' }"
      >
        <span>{{ btnText }}</span>
      </div>
      <div
        class="slider-text"
        :style="{ color: textColor }"
      >
        {{ text }}
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, toRefs } from 'vue'

export default defineComponent({
  name: 'SliderVerify',
  props: {
    width: {
      type: Number,
      default: 300
    },
    height: {
      type: Number,
      default: 40
    }
  },
  emits: ['success'],
  setup(props, { emit }) {
    const state = reactive({
      btnLeft: 0,
      btnText: '→',
      text: '请按住滑块，拖动到最右边',
      textColor: '#666',
      bgColor: '#f7f7f7',
      isMoving: false,
      startX: 0,
      maxLeft: props.width - 0 // 滑块最大移动距离
    })

    const handleMouseDown = (e: MouseEvent) => {
      state.isMoving = true
      state.startX = e.clientX - state.btnLeft
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    }

    const handleMouseMove = (e: MouseEvent) => {
      if (!state.isMoving) return

      let left = e.clientX - state.startX
      if (left < 0) left = 0
      if (left > state.maxLeft) left = state.maxLeft

      state.btnLeft = left

      // 滑动到最右边验证成功
      if (left >= state.maxLeft - 2) {
        state.isMoving = false
        state.btnText = '✓'
        state.text = '验证通过'
        state.textColor = '#fff'
        state.bgColor = '#67c23a'
        emit('success')

        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
    }

    const handleMouseUp = () => {
      if (!state.isMoving) return

      state.isMoving = false
      state.btnLeft = 0

      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }

    const reset = () => {
      state.btnLeft = 0
      state.btnText = '→'
      state.text = '请按住滑块，拖动到最右边'
      state.textColor = '#666'
      state.bgColor = '#f7f7f7'
      state.isMoving = false
    }

    return {
      ...toRefs(state),
      handleMouseDown,
      reset
    }
  }
})
</script>

<style scoped>
.slider-bg {
  position: relative;
  width: 100%;
  height: 40px;
  line-height: 40px;
  background-color: #f7f7f7;
  color: #666;
  text-align: center;
  border-radius: 20px;
  overflow: hidden;
}

.slider-text {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 1;
  pointer-events: none;
}

.slider-btn {
  position: absolute;
  width: 40px;
  height: 40px;
  top: 0;
  left: 0;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  cursor: move;
  z-index: 2;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
}
</style>