<template>
  <div class="editable-cell" @click="startEditing">
    <span v-if="!editing">{{ modelValue }}</span>
    <el-input
      v-else
      ref="inputRef"
      v-model="inputValue"
      size="small"
      @blur="saveEdit"
      @keyup.enter="saveEdit"
    />
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const props = defineProps({
  modelValue: String
})

const emit = defineEmits(['update:model-value'])

const editing = ref(false)
const inputValue = ref(props.modelValue)
const inputRef = ref(null)

const startEditing = () => {
  editing.value = true
  inputValue.value = props.modelValue
  nextTick(() => inputRef.value?.focus())
}

const saveEdit = () => {
  editing.value = false
  if (inputValue.value !== props.modelValue) {
    emit('update:model-value', inputValue.value)
  }
}
</script>

<style scoped>
.editable-cell {
  display: inline-block;
  width: 100%;
  min-height: 22px;
  line-height: 22px;
  cursor: pointer;
}
</style>