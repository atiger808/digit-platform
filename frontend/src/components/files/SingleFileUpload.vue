<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Document } from '@element-plus/icons-vue'
import SparkMD5 from 'spark-md5'
import {api} from '@/service/request.ts'

const props = defineProps({
  maxSizeMB: {
    type: Number,
    default: 100
  }
})

const emit = defineEmits(['success', 'error'])

const uploadRef = ref(null)
const fileList = ref([])
const uploading = ref(false)
const md5Calculating = ref(false)
const md5Progress = ref(0)

// 文件类型判断
const isImage = (file) => {
  const imageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  return file.raw && imageTypes.includes(file.raw.type)
}

// 获取预览URL
const getPreviewUrl = (file) => {
  return file.raw ? URL.createObjectURL(file.raw) : ''
}

// 缩略显示MD5
const shortMd5 = (md5) => {
  return md5 ? `${md5.substring(0, 6)}...${md5.substring(30)}` : ''
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

// 上传前校验
const beforeUpload = (file) => {
  const isOverSize = file.size > props.maxSizeMB * 1024 * 1024
  if (isOverSize) {
    ElMessage.error(`文件大小超过 ${props.maxSizeMB}MB 限制`)
    return false
  }
  return true
}

// 文件变化处理
const handleFileChange = async (file, files) => {
  try {
    md5Calculating.value = true
    md5Progress.value = 0

    // 计算文件MD5
    file.md5 = await calculateMD5(file.raw)

    // 更新文件列表（自动替换旧文件）
    fileList.value = [{
      ...file,
      progress: 0,
      status: 'pending'
    }]

    return true
  } catch (error) {
    ElMessage.error(`文件校验失败: ${error.message}`)
    return false
  } finally {
    md5Calculating.value = false
  }
}

// 计算MD5（分块计算）
const calculateMD5 = (file) => {
  return new Promise((resolve) => {
    const spark = new SparkMD5.ArrayBuffer()
    const fileReader = new FileReader()
    const chunkSize = 2 * 1024 * 1024 // 2MB chunks
    let currentChunk = 0
    const chunks = Math.ceil(file.size / chunkSize)

    fileReader.onload = (e) => {
      spark.append(e.target.result)
      currentChunk++
      md5Progress.value = Math.round((currentChunk / chunks) * 100)

      if (currentChunk < chunks) {
        loadNext()
      } else {
        resolve(spark.end())
      }
    }

    const loadNext = () => {
      const start = currentChunk * chunkSize
      const end = Math.min(start + chunkSize, file.size)
      fileReader.readAsArrayBuffer(file.slice(start, end))
    }

    loadNext()
  })
}

// 移除文件
const handleRemove = () => {
  fileList.value = []
  uploadRef.value?.clearFiles()
}

// 提交上传
const submitUpload = async () => {
  if (fileList.value.length === 0) return

  uploading.value = true
  const file = fileList.value[0]
  file.status = 'uploading'

  try {
    const formData = new FormData()
    formData.append('file', file.raw)
    formData.append('filename', file.name)
    formData.append('file_md5', file.md5)

    const response = await api.post('file/api/multifile/upload/', formData, {
      onUploadProgress: (progressEvent) => {
        file.progress = Math.round(
          (progressEvent.loaded / progressEvent.total) * 100
        )
      }
    })

    file.status = 'success'
    ElMessage.success('文件上传成功')
    emit('success', {
      file: file.name,
      data: response.data
    })
  } catch (error) {
    file.status = 'error'
    ElMessage.error(`上传失败: ${error.message}`)
    emit('error', error)
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <div class="single-upload-container">
    <el-upload
      ref="uploadRef"
      :auto-upload="false"
      accept="video/*"
      :on-change="handleFileChange"
      :on-remove="handleRemove"
      :file-list="fileList"
      :limit="1"
      :before-upload="beforeUpload"
      :on-preview="handlePreview"
      drag
      action=""
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        将文件拖到此处，或<em>点击选择文件</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          单个文件上传，大小不超过 {{ maxSizeMB }}MB
          <div v-if="md5Calculating">
            <el-progress
              :percentage="md5Progress"
              :show-text="false"
              :stroke-width="2"
            />
            <span>计算文件校验码: {{ md5Progress }}%</span>
          </div>
        </div>
      </template>
    </el-upload>

    <!-- 文件信息展示 -->
    <div v-if="fileList.length > 0" class="file-info-card">
      <div class="file-preview">
        <el-icon v-if="!isImage(fileList[0])" size="60"><Document /></el-icon>
        <img v-else :src="getPreviewUrl(fileList[0])" alt="文件预览">
      </div>
      <div class="file-details">
        <div class="file-name">{{ fileList[0].name }}</div>
        <div class="file-size">{{ formatFileSize(fileList[0].size) }}</div>
        <div class="file-md5" v-if="fileList[0].md5">校验码: {{ shortMd5(fileList[0].md5) }}</div>
        <el-progress
          v-if="fileList[0].status === 'uploading'"
          :percentage="fileList[0].progress"
          :stroke-width="6"
          style="margin-top: 10px"
        />
        <div class="file-actions">
          <el-button
            v-if="fileList[0].status !== 'uploading'"
            size="small"
            type="danger"
            @click="handleRemove(fileList[0])"
          >
            移除文件
          </el-button>
        </div>
      </div>
    </div>

    <div class="upload-actions">
      <el-button
        type="primary"
        @click="submitUpload"
        :loading="uploading"
        :disabled="fileList.length === 0"
      >
        {{ uploading ? '上传中...' : '开始上传' }}
      </el-button>
    </div>


  </div>
</template>



<style scoped>
.single-upload-container {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.file-info-card {
  margin-top: 20px;
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  display: flex;
  gap: 15px;
  background-color: #fafafa;
}

.file-preview {
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed #d9d9d9;
  border-radius: 4px;
  overflow: hidden;
}

.file-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.file-details {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-size, .file-md5 {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.upload-actions {
  margin-top: 20px;
  text-align: right;
}

.el-upload__tip {
  margin-top: 10px;
  font-size: 12px;
  color: #606266;
}
</style>