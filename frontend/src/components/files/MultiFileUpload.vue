<script setup lang="ts">
import {ref, computed, reactive} from 'vue'
import {ElMessage, ElLoading, type UploadProps} from 'element-plus'
import {UploadFilled, Document, Plus} from '@element-plus/icons-vue'
import SparkMD5 from 'spark-md5'
import {api} from '@/service/request.ts'
import {useRouter} from "vue-router";

const router = useRouter()

const form = reactive({
  name: '',
  file: '',
})

const dialogVisible = ref(false)  //缩放弹窗
const dialogImageUrl = ref('')  //弹窗图片路径

const handlePreview: UploadProps['onPreview'] = (uploadFile) => {
  dialogVisible.value = true
  dialogImageUrl.value = uploadFile.url
  ElMessage.warning('handlePreview')

}


const props = defineProps({
  maxFiles: {
    type: Number,
    default: 20
  },
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

const uploadButtonText = computed(() => {
  if (uploading.value) {
    const uploadingCount = fileList.value.filter(f => f.status === 'uploading').length
    return `上传中 (${uploadingCount}/${fileList.value.length})`
  }
  return '开始上传'
})

const isImage = (file) => {
  const imageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  return imageTypes.includes(file.raw?.type)
}

const getPreviewUrl = (file) => {
  return file.raw ? URL.createObjectURL(file.raw) : ''
}

const shortMd5 = (md5) => {
  return md5 ? `${md5.substring(0, 6)}...${md5.substring(30)}` : ''
}

const progressFormat = (percentage) => {
  return `${percentage}%`
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const beforeUpload = (file) => {
  const isOverSize = file.size > props.maxSizeMB * 1024 * 1024
  if (isOverSize) {
    ElMessage.error(`文件 ${file.name} 超过 ${props.maxSizeMB}MB 限制`)
    return false
  }
  return true
}


const handleExceed = (files, fileList) => {
  ElMessage.warning(`上传文件数量超过限制，最多只能上传 ${props.maxFiles} 个文件`)
  console.log('文件数量超过限制')
}

const handleFileChange = async (file, files) => {
  if (files.length > props.maxFiles) {
    ElMessage.warning(`最多只能上传 ${props.maxFiles} 个文件`)
    uploadRef.value.handleRemove(file)
    return false
  }

  try {
    md5Calculating.value = true
    md5Progress.value = 0

    // 计算MD5
    file.md5 = await calculateMD5(file.raw)

    // 检查所有文件（现有列表+新文件）中的重复
    const allFiles = [...fileList.value, ...files]
    const duplicateIndex = allFiles.findIndex(
        (f, index) => f.md5 === file.md5 &&
            f.uid !== file.uid && // 排除自己
            index < allFiles.length - files.length // 只检查已存在的文件
    )

    if (duplicateIndex !== -1) {
      const duplicateFile = allFiles[duplicateIndex]
      ElMessage.warning(`文件 ${file.name} 与 ${duplicateFile.name} 重复，已保留第一个文件`)
      console.log(`文件 ${file.name} 与 ${duplicateFile.name} 重复，已保留第一个文件`)
      uploadRef.value.handleRemove(file)
      return false
    }

    // 更新文件列表，确保没有重复
    const uniqueFiles = []
    const md5Set = new Set()

    // 先保留现有文件
    fileList.value.forEach(f => {
      if (!md5Set.has(f.md5)) {
        md5Set.add(f.md5)
        uniqueFiles.push(f)
      }
    })

    // 再添加新文件
    files.forEach(f => {
      if (!md5Set.has(f.md5)) {
        md5Set.add(f.md5)
        uniqueFiles.push({
          ...f,
          progress: 0,
          status: 'pending',
          md5: f.uid === file.uid ? file.md5 : f.md5 || ''
        })
      }
    })

    fileList.value = uniqueFiles
    return true
  } catch (error) {
    ElMessage.error(`计算文件MD5失败: ${error.message}`)
    return false
  } finally {
    md5Calculating.value = false
  }

}

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

const handleRemove = (file) => {
  const index = fileList.value.findIndex(f => f.uid === file.uid)
  if (index !== -1) {
    fileList.value.splice(index, 1)
  }
}

const clearFiles = () => {
  fileList.value = []
  uploadRef.value?.clearFiles()
}

const submitUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择要上传的文件')
    return
  }

  uploading.value = true
  const results = []
  const loadingInstance = ElLoading.service({
    lock: true,
    text: '文件上传中...',
    background: 'rgba(0, 0, 0, 0.7)'
  })

  try {
    // 并行上传
    await Promise.all(fileList.value.map(async (file) => {
      if (file.status === 'exists') {
        results.push({success: true, file: file.name, exists: true})
        return
      }

      try {
        file.status = 'uploading'

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

        results.push({
          success: true,
          file: file.name,
          data: response.data
        })
        file.status = 'success'

        ElMessage.success('文件上传成功！');
        router.push('/main/files/filemanage')


      } catch (error) {
        results.push({
          success: false,
          file: file.name,
          error: error.message
        })
        file.status = 'error'
      }
    }))

    // 处理结果
    const successCount = results.filter(r => r.success).length
    if (successCount > 0) {
      ElMessage.success(`成功上传 ${successCount} 个文件`)
      emit('success', results)
    }
  } catch (error) {
    emit('error', error)
    ElMessage.error('上传过程中出错: ' + error.message)
  } finally {
    uploading.value = false
    loadingInstance.close()
  }
}
</script>

<template>
  <div class="mult-upload-container">
    <el-upload
        ref="uploadRef"
        multiple
        :auto-upload="false"
        accept="video/*"
        :on-change="handleFileChange"
        :on-remove="handleRemove"
        :file-list="fileList"
        :limit="maxFiles"
        :on-exceed="handleExceed"
        :before-upload="beforeUpload"
        :on-preview="handlePreview"
        list-type="picture-card"
        action=""
        :class="{ 'disabled': uploading }"
    >
      <el-icon>
        <Plus/>
      </el-icon>

      <template #tip>
        <div class="el-upload__tip" slot="tip">
          支持多文件上传，最多 {{ maxFiles }} 个文件，单个文件不超过 {{ maxSizeMB }}MB
          <div v-if="md5Calculating" class="md5-calculating">
            <el-progress :percentage="md5Progress" :show-text="false"/>
            <span>计算MD5: {{ md5Progress }}%</span>
          </div>
        </div>

      </template>


    </el-upload>

    <!-- 自定义文件卡片 -->
    <div v-for="file in fileList" :key="file.uid" class="custom-file-card">
      <div class="card-content">
        <!-- 图片预览 -->
        <div class="preview" v-if="isImage(file)">
          <img :src="getPreviewUrl(file)" alt="预览"/>
        </div>

        <!-- 非图片文件图标 -->
        <div class="file-icon" v-else>
          <el-icon :size="50">
            <Document/>
          </el-icon>
        </div>

        <!-- 文件信息 -->
        <div class="file-info">
          <div class="file-name">{{ file.name }}</div>
          <div class="file-size">{{ formatFileSize(file.size) }}</div>
          <div class="file-md5" v-if="file.md5">MD5: {{ shortMd5(file.md5) }}</div>
        </div>

        <!-- 上传进度 -->
        <div class="file-progress">
          <el-progress
              v-if="file.status === 'uploading'"
              :percentage="file.progress"
              :stroke-width="4"
              :format="progressFormat"
          />
          <div v-else class="file-status">
            <el-tag v-if="file.status === 'success'" type="success" size="small">完成</el-tag>
            <el-tag v-else-if="file.status === 'exists'" type="info" size="small">已存在</el-tag>
            <el-button
                v-else
                size="small"
                type="danger"
                link
                @click="handleRemove(file)"
            >
              移除
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="upload-actions">
      <el-button
          type="primary"
          @click="submitUpload"
          :loading="uploading"
          :disabled="fileList.length === 0"
      >
        {{ uploadButtonText }}
      </el-button>
      <el-button @click="clearFiles" :disabled="uploading || fileList.length === 0">
        清空
      </el-button>
    </div>

    <el-dialog v-model="dialogVisible">
      <img w-full :src="dialogImageUrl" alt="预览图片" style="max-width: 100%;"/>
    </el-dialog>

  </div>
</template>


<style scoped>
.multi-upload-container {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

/* 自定义卡片样式 */
.custom-file-card {
  display: inline-block;
  width: 148px;
  height: 148px;
  margin: 0 8px 8px 0;
  border: 1px solid #c0ccda;
  border-radius: 6px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12);
  transition: all 0.3s;
}

.custom-file-card:hover {
  border-color: #409EFF;
}

.card-content {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.preview {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.file-icon {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}

.file-info {
  padding: 5px;
  background: #f5f7fa;
  border-top: 1px solid #e4e7ed;
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500;
}

.file-size, .file-md5 {
  color: #909399;
  font-size: 10px;
}

.file-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 5px;
  background: rgba(255, 255, 255, 0.9);
}

.file-status {
  text-align: center;
  padding: 2px 0;
}

/* 上传区域样式 */
:deep(.el-upload--picture-card) {
  width: 148px;
  height: 148px;
  line-height: 148px;
}

:deep(.el-upload-list--picture-card .el-upload-list__item) {
  width: 148px;
  height: 148px;
}

/* 计算MD5进度样式 */
.md5-calculating {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #606266;
  font-size: 12px;
}

/* 上传按钮组 */
.upload-actions {
  margin-top: 20px;
}

/* 禁用状态 */
.disabled :deep(.el-upload--picture-card) {
  display: none;
}
</style>