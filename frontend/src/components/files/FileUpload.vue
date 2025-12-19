<script setup lang="ts">
import {ref, reactive, onMounted, computed} from 'vue'
import {ElMessage, ElMessageBox, ElNotification} from 'element-plus'
import type {UploadProps, UploadUserFile} from 'element-plus'
import api from '@/service/request.ts'
import {useRouter} from 'vue-router'
import {Plus, UploadFilled} from '@element-plus/icons-vue'
import SparkMD5 from 'spark-md5'


const dialogVisible = ref(false);
const emit = defineEmits(['close', 'success']);
// 暴露给父组件的方法
const openDialog = () => {
  dialogVisible.value = true;
};



const router = useRouter()


// 上传状态数据
const file = ref(null);
const fileMd5 = ref('');
const uploadId = ref('');
const uploading = ref(false);
const progress = ref(0);
const uploadedChunks = ref(0);
const totalChunks = ref(0);
const uploadStatus = ref('');
const uploadStatusType = ref('info');

// 计算属性
const uploadButtonText = computed(() => {
  if (uploading.value) {
    return `上传中 (${progress.value}%)`;
  }
  return uploadedChunks.value > 0 ? '继续上传' : '开始上传';
});

const progressStatus = computed(() => {
  if (progress.value === 100) return 'success';
  return undefined;
});

// 方法
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const handleFileChange = (uploadFile) => {
  resetUploadState();
  file.value = uploadFile.raw;
  console.log('file ==> ', file)
  startUpload()
};

const resetUploadState = () => {
  fileMd5.value = '';
  uploadId.value = '';
  uploading.value = false;
  progress.value = 0;
  uploadedChunks.value = 0;
  totalChunks.value = 0;
  uploadStatus.value = '';
};

const calculateFileMd5 = async (file) => {
  return new Promise((resolve) => {
    const spark = new SparkMD5.ArrayBuffer()
    const fileReader = new FileReader();
    const chunkSize = 2 * 1024 * 1024; // 2MB chunks for MD5 calculation
    let currentChunk = 0;
    const chunks = Math.ceil(file.size / chunkSize);


    fileReader.onload = (e) => {
      spark.append(e.target.result)
      currentChunk++;
      progress.value = Math.min(30, Math.round((currentChunk / chunks) * 30));

      if (currentChunk < chunks) {
        loadNext();
      } else {
        resolve(spark.end())
      }
    };

    const loadNext = () => {
      const start = currentChunk * chunkSize;
      const end = Math.min(start + chunkSize, file.size);
      fileReader.readAsArrayBuffer(file.slice(start, end));
    };

    loadNext();
  });
};

const startUpload = async () => {
  if (!file.value) return;
  try {
    uploading.value = true;
    uploadStatus.value = '正在准备上传...';
    uploadStatusType.value = 'info';

    // 1. 计算文件MD5（如果尚未计算）
    if (!fileMd5.value) {
      uploadStatus.value = '正在计算文件MD5...';
      fileMd5.value = await calculateFileMd5(file.value);
    }

    // 2. 初始化上传
    const chunkSize = 5 * 1024 * 1024; // 5MB chunks
    totalChunks.value = Math.ceil(file.value.size / chunkSize);

    uploadStatus.value = '正在初始化上传...';
    const initResponse = await api.post('file/api/upload/init/', {
      filename: file.value.name,
      file_md5: fileMd5.value,
      total_chunks: totalChunks.value
    });

    console.log('initResponse ==> ', initResponse)
    // 处理已存在文件
    if (initResponse.data.data.is_existing) {
      uploadStatus.value = '文件已存在，上传完成！';
      uploadStatusType.value = 'success';
      progress.value = 100;
      ElMessage.success('文件已存在，无需重复上传');
      emit('success');
      return;
    }

    uploadId.value = initResponse.data.data.upload_id;
    uploadedChunks.value = initResponse.data.data.uploaded_chunks || 0;

    // 3. 上传分片
    await uploadChunks(chunkSize);

    // 4. 完成上传
    uploadStatus.value = '正在完成上传...';
    const completeResponse = await api.post('file/api/upload/complete/', {
      upload_id: uploadId.value,
      file_md5: fileMd5.value,
      filename: file.value.name
    });
    console.log("completeResponse", completeResponse)
    uploadStatus.value = '文件上传成功！' || completeResponse.data.data.msg;
    uploadStatusType.value = 'success';
    progress.value = 100;
    ElMessage.success('文件上传成功！');
    emit('success');
    router.push('/main/files/filemanage')
  } catch (error) {
    handleUploadError(error);
  } finally {
    uploading.value = false;
  }
};

const uploadChunks = async (chunkSize) => {
  for (let i = uploadedChunks.value; i < totalChunks.value; i++) {
    const start = i * chunkSize;
    const end = Math.min(start + chunkSize, file.value.size);
    const chunk = file.value.slice(start, end);

    const formData = new FormData();
    formData.append('chunk', chunk, `chunk_${i + 1}`);
    formData.append('chunk_number', i + 1);
    formData.append('upload_id', uploadId.value);
    formData.append('file_md5', fileMd5.value);

    try {
      uploadStatus.value = `正在上传分片 ${i + 1}/${totalChunks.value}...`;

      await api.post('file/api/upload/chunk/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const chunkProgress = Math.round(
              (progressEvent.loaded / progressEvent.total) * 100
          );
          const overallProgress = Math.round(
              ((i * 100) + chunkProgress) / totalChunks.value
          );
          progress.value = Math.max(progress.value, overallProgress);
        }
      });

      uploadedChunks.value = i + 1;
    } catch (error) {
      // 如果是401错误，尝试刷新token后继续上传
      if (error.response?.status === 401) {
        try {
          // 重新尝试当前分片
          i--;
          continue;
        } catch (refreshError) {
          throw new Error('会话已过期，请重新登录');
        }
      }
      throw error;
    }
  }
};

const handleUploadError = (error) => {
  console.error('上传失败:', error);

  let errorMessage = error.response?.data?.error || error.message;
  if (error.response?.status === 401) {
    errorMessage = '认证失败，请重新登录';
  }

  uploadStatus.value = `上传失败: ${errorMessage}`;
  uploadStatusType.value = 'error';
  ElMessage.error(`上传失败: ${errorMessage}`);
};

const beforeUpload = (file) => {
  // 检查 MIME 类型是否为 video 开头
  if (!file.type.startsWith('video/')) {
    ElMessage.error('请上传视频文件（如 MP4、AVI、MOV 等）');
    return false; // 阻止上传
  }

  // 可选：限制文件大小（例如 100MB）
  const maxSize = 100 * 1024 * 1024; // 100MB
  if (file.size > maxSize) {
    ElMessage.error('视频文件不能超过 100MB');
    return false;
  }

  return true; // 允许上传
};

</script>

<template>
  <div class="upload-container">
    <el-upload
        class="upload-demo"
        drag
        :auto-upload="false"
        accept="video/*"
        :before-upload="beforeUpload"
        :on-change="handleFileChange"
        :show-file-list="false"
        :disabled="uploading"
    >
      <el-icon class="el-icon--upload">
        <upload-filled/>
      </el-icon>
      <div class="el-upload__text">
        将文件拖到此处，或<em>点击选择文件</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持大文件上传，自动分片，断点续传，最大支持10GB文件
        </div>
      </template>
    </el-upload>

    <div v-if="file" class="file-info">
      <div class="file-name">{{ file.name }}</div>
      <div class="file-size">{{ formatFileSize(file.size) }}</div>
      <div class="file-md5" v-if="fileMd5">MD5: {{ fileMd5 }}</div>
    </div>

    <el-button
        type="primary"
        @click="startUpload"
        :disabled="!file || uploading"
        :loading="uploading"
    >
      {{ uploadButtonText }}
    </el-button>

    <el-progress
        v-if="uploading"
        :percentage="progress"
        :stroke-width="8"
        :status="progressStatus"
    />

    <div class="upload-details">
      <div v-if="uploadStatus" class="upload-status">
        <el-alert :title="uploadStatus" :type="uploadStatusType" :closable="false"/>
      </div>
      <div v-if="uploadedChunks > 0" class="chunks-info">
        分片进度: {{ uploadedChunks }}/{{ totalChunks }}
      </div>
    </div>
  </div>
</template>


<style scoped lang="scss">

</style>