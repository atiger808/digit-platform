<template>
  <div class="file-download-container">
    <div class="file-card">
      <div class="file-info">
        <div class="file-icon">
          <el-icon :size="48">
            <component :is="fileIcon" />
          </el-icon>
        </div>
        <div class="file-details">
          <h3>{{ file.name }}</h3>
          <div class="file-meta">
            <span>{{ formatFileSize(file.size) }}</span>
            <span>·</span>
            <span>{{ file.type }}</span>
          </div>
        </div>
      </div>

      <div class="download-controls">
        <el-button
          v-if="!isDownloading"
          type="primary"
          @click="startDownload"
          :icon="Download"
        >
          下载文件
        </el-button>

        <div v-else class="progress-container">
          <el-progress
            :percentage="downloadProgress"
            :status="downloadStatus"
            :stroke-width="12"
            :text-inside="true"
          />

          <div class="progress-details">
            <span>{{ formatFileSize(downloadedSize) }} / {{ formatFileSize(file.size) }}</span>
            <span>{{ downloadSpeed }} MB/s</span>
            <span>{{ timeRemaining }}</span>
          </div>

          <div class="action-buttons">
            <el-button
              v-if="!isPaused"
              @click="pauseDownload"
              :icon="VideoPause"
            >
              暂停
            </el-button>
            <el-button
              v-else
              type="success"
              @click="resumeDownload"
              :icon="VideoPlay"
            >
              继续
            </el-button>
            <el-button
              type="danger"
              @click="cancelDownload"
              :icon="Close"
            >
              取消
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="downloadComplete" class="success-message">
      <el-result icon="success" title="下载完成">
        <template #extra>
          <el-button type="primary" @click="saveFile">保存文件</el-button>
          <el-button @click="resetDownload">重新下载</el-button>
        </template>
      </el-result>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue';
import {
  Document,
  Download,
  VideoPause,
  VideoPlay,
  Close,
  Picture,
  Folder,
  VideoCamera,
  Headset
} from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import axios from 'axios';

// 文件类型图标映射
const FILE_ICONS: Record<string, any> = {
  'pdf': Document,
  'doc': Document,
  'docx': Document,
  'xls': Document,
  'xlsx': Document,
  'ppt': Document,
  'pptx': Document,
  'jpg': Picture,
  'jpeg': Picture,
  'png': Picture,
  'gif': Picture,
  'bmp': Picture,
  'zip': Folder,
  'rar': Folder,
  '7z': Folder,
  'tar': Folder,
  'gz': Folder,
  'mp4': VideoCamera,
  'avi': VideoCamera,
  'mov': VideoCamera,
  'mp3': Headset,
  'wav': Headset,
  'flac': Headset
};

// Props
const props = defineProps({
  file: {
    type: Object,
    required: true,
    default: () => ({
      id: 0,
      name: 'example.txt',
      size: 0,
      type: 'txt',
      url: ''
    })
  }
});

// 状态变量
const isDownloading = ref(false);
const isPaused = ref(false);
const downloadProgress = ref(0);
const downloadedSize = ref(0);
const downloadSpeed = ref(0);
const timeRemaining = ref('计算中...');
const downloadStatus = ref<'success' | 'exception' | 'warning' | ''>('');
const downloadComplete = ref(false);
const chunks: Uint8Array[] = [];
const controller = ref<AbortController | null>(null);
const startTime = ref(0);
const lastUpdateTime = ref(0);
const lastDownloadedSize = ref(0);

// 计算文件图标
const fileIcon = computed(() => {
  const extension = props.file.name.split('.').pop()?.toLowerCase() || 'file';
  return FILE_ICONS[extension] || Document;
});

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// 开始下载
const startDownload = async () => {
  // 重置状态
  resetDownloadState();
  isDownloading.value = true;
  downloadStatus.value = '';

  try {
    // 创建AbortController以便可以取消请求
    controller.value = new AbortController();
    const signal = controller.value.signal;

    // 开始时间记录
    startTime.value = Date.now();
    lastUpdateTime.value = Date.now();
    lastDownloadedSize.value = 0;

    // 使用Fetch API进行流式下载
    const response = await fetch(props.file.url, {
      signal,
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      }
    });

    if (!response.ok) {
      throw new Error(`下载失败: ${response.status} ${response.statusText}`);
    }

    if (!response.body) {
      throw new Error('响应体不可读');
    }

    // 获取文件总大小
    const contentLength = response.headers.get('Content-Length');
    const totalSize = contentLength ? parseInt(contentLength) : props.file.size;

    // 创建可读流
    const reader = response.body.getReader();

    // 读取数据流
    while (true) {
      if (isPaused.value) {
        // 如果暂停，等待恢复
        await new Promise(resolve => {
          const interval = setInterval(() => {
            if (!isPaused.value) {
              clearInterval(interval);
              resolve(true);
            }
          }, 100);
        });
      }

      const { done, value } = await reader.read();

      if (done) break;

      // 保存数据块
      chunks.push(value);
      downloadedSize.value += value.length;

      // 更新进度
      updateProgress(totalSize);
    }

    // 下载完成
    downloadComplete.value = true;
    downloadProgress.value = 100;
    downloadStatus.value = 'success';
    isDownloading.value = false;

  } catch (error: any) {
    if (error.name === 'AbortError') {
      ElMessage.info('下载已取消');
    } else {
      console.error('下载错误:', error);
      ElMessage.error(`下载失败: ${error.message}`);
      downloadStatus.value = 'exception';
    }
    isDownloading.value = false;
  }
};

// 更新下载进度
const updateProgress = (totalSize: number) => {
  const now = Date.now();
  const timeDelta = (now - lastUpdateTime.value) / 1000; // 秒
  const sizeDelta = downloadedSize.value - lastDownloadedSize.value;

  // 计算下载速度 (MB/s)
  if (timeDelta > 0) {
    downloadSpeed.value = parseFloat((sizeDelta / (timeDelta * 1024 * 1024)).toFixed(2));
  }

  // 计算剩余时间
  if (downloadSpeed.value > 0 && totalSize > downloadedSize.value) {
    const remainingBytes = totalSize - downloadedSize.value;
    const secondsRemaining = Math.ceil(remainingBytes / (downloadSpeed.value * 1024 * 1024));

    if (secondsRemaining < 60) {
      timeRemaining.value = `${secondsRemaining}秒`;
    } else {
      const minutes = Math.floor(secondsRemaining / 60);
      const seconds = secondsRemaining % 60;
      timeRemaining.value = `${minutes}分${seconds}秒`;
    }
  }

  // 更新进度百分比
  downloadProgress.value = Math.round((downloadedSize.value / totalSize) * 100);

  // 更新记录
  lastUpdateTime.value = now;
  lastDownloadedSize.value = downloadedSize.value;
};

// 暂停下载
const pauseDownload = () => {
  isPaused.value = true;
  downloadStatus.value = 'warning';
  ElMessage.info('下载已暂停');
};

// 恢复下载
const resumeDownload = () => {
  isPaused.value = false;
  downloadStatus.value = '';
  ElMessage.info('下载已恢复');
};

// 取消下载
const cancelDownload = () => {
  if (controller.value) {
    controller.value.abort();
    controller.value = null;
  }
  isDownloading.value = false;
  isPaused.value = false;
  resetDownloadState();
};

// 保存文件
const saveFile = () => {
  try {
    // 合并所有数据块
    const blob = new Blob(chunks);
    const url = window.URL.createObjectURL(blob);

    // 创建下载链接
    const a = document.createElement('a');
    a.href = url;

    // 从Content-Disposition解析文件名
    let fileName = props.file.name;
    const contentDisposition = 'attachment; filename="' + fileName + '"';

    if (contentDisposition) {
      const fileNameMatch = contentDisposition.match(/filename="?(.+)"?/);
      if (fileNameMatch && fileNameMatch.length > 1) {
        fileName = fileNameMatch[1];
      }
    }

    a.download = fileName;
    document.body.appendChild(a);
    a.click();

    // 清理
    setTimeout(() => {
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    }, 100);

    ElMessage.success('文件保存成功');

  } catch (error) {
    console.error('保存文件失败:', error);
    ElMessage.error('文件保存失败');
  }
};

// 重置下载
const resetDownload = () => {
  downloadComplete.value = false;
  resetDownloadState();
};

// 重置下载状态
const resetDownloadState = () => {
  downloadProgress.value = 0;
  downloadedSize.value = 0;
  downloadSpeed.value = 0;
  timeRemaining.value = '计算中...';
  downloadStatus.value = '';
  chunks.length = 0;

  if (controller.value) {
    controller.value.abort();
    controller.value = null;
  }
};

// 组件卸载时取消下载
onUnmounted(() => {
  if (isDownloading.value) {
    cancelDownload();
  }
});
</script>

<style scoped>
.file-download-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.file-card {
  background: white;
  border-radius: 10px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.file-info {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
}

.file-icon {
  margin-right: 16px;
  color: #409eff;
}

.file-details h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #303133;
}

.file-meta {
  display: flex;
  gap: 8px;
  color: #909399;
  font-size: 14px;
}

.download-controls {
  margin-top: 24px;
}

.progress-container {
  margin-top: 16px;
}

.progress-details {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  color: #606266;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 16px;
}

.success-message {
  margin-top: 24px;
  text-align: center;
}

.el-progress {
  margin-top: 10px;
}

.el-button {
  font-weight: 500;
}
</style>