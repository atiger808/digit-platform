<!-- EditableCell.vue -->
<template>
  <div
    class="editable-cell"
    @click="startEditing"
    @mouseenter="hovering = true"
    @mouseleave="hovering = false"
    :title="modelValue || ''"
  >
    <!-- 非编辑状态：文本 + 图标 -->
    <span v-if="!editing" class="editable-content">
      <span
        class="editable-text"
        :class="{ 'hover-highlight': hovering }"
        >{{ modelValue || '点击编辑' }}</span
      >
      <el-icon class="editable-icon" @click.stop="startEditing">
        <Edit />
      </el-icon>
    </span>

    <!-- 编辑状态：多行文本框 -->
    <el-input
      v-else
      ref="inputRef"
      v-model="inputValue"
      type="textarea"
      :autosize="{ minRows: 2, maxRows: 6 }"
      resize="vertical"
      @blur="saveEdit"
      @keyup.ctrl.enter="saveEdit"
      @keyup.meta.enter="saveEdit"
      class="editable-textarea"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { Edit } from '@element-plus/icons-vue'

interface Props {
  modelValue?: string
}

interface Emits {
  (e: 'update:modelValue', value: string): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: ''
})

const emit = defineEmits<Emits>()

const editing = ref<boolean>(false)
const hovering = ref<boolean>(false)
const inputValue = ref<string>(props.modelValue)
const inputRef = ref<HTMLInputElement | HTMLTextAreaElement | null>(null)

watch(
  () => props.modelValue,
  (newVal) => {
    inputValue.value = newVal ?? ''
  }
)

const startEditing = (): void => {
  editing.value = true
  inputValue.value = props.modelValue ?? ''
  nextTick(() => {
    // 聚焦到 textarea
    if (inputRef.value?.focus) {
      inputRef.value.focus()
      // 可选：自动全选内容
      // ;(inputRef.value as HTMLTextAreaElement)?.select?.()
    }
  })
}

const saveEdit = (): void => {
  editing.value = false
  hovering.value = false
  const newValue = inputValue.value // 可选：是否 trim？多行通常不 trim
  const oldValue = props.modelValue ?? ''
  if (newValue !== oldValue) {
    emit('update:modelValue', newValue)
  }
}
</script>

<style scoped>
.editable-cell {
  display: flex;
  align-items: flex-start; /* 适配多行高度 */
  width: 100%;
  min-height: 24px;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.editable-cell:hover {
  background-color: #f0f9ff;
}

.editable-content {
  display: flex;
  align-items: center;
  width: 100%;
}

.editable-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 13px;
  color: inherit;
  line-height: 1.4;
}

.editable-icon {
  color: #909399;
  font-size: 14px;
  margin-left: 6px;
  flex-shrink: 0;
}

.editable-icon:hover {
  color: #409eff;
}

/* 多行文本框样式 */
.editable-textarea {
  width: 100%;
  /* 移除默认点击样式 */
  cursor: text;
}

.editable-textarea :deep(.el-textarea__inner) {
  padding: 6px 8px;
  font-size: 13px;
  line-height: 1.4;
  resize: vertical; /* 允许用户手动调整高度 */
  min-height: 40px;
}
</style>