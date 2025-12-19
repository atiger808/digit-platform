<script setup lang="ts">
import {ref, computed} from 'vue'
import {Download} from "@element-plus/icons-vue";
import {api} from '@/service/request.ts'
import {chunkedDownload} from "@/utils/chunkedDownload.ts";
import {retrieveFileById} from "@/service/main/files/files.ts";
import {ElMessage} from "element-plus";


// 分块下载
const downloadingId = ref<number | null>(null)
const downloadProgress = ref(0) // 下载进度百分比
const showProgress = ref(false) // 是否显示进度条
const isDownloading = ref(false);
const cancelToken = ref<ReturnType<typeof api.CancelToken.source>>(null);

const downloadStatus = computed(() => {
  if (downloadProgress.value === 100) return 'success';
  return '';
});


const startChunkedDownload = async (itemData: any) => {
  downloadingId.value = itemData.id;
  isDownloading.value = true;
  downloadProgress.value = 0;
  ElMessage.info('开始下载');

  // 每次下载前创建新的取消令牌
  cancelToken.value = api.CancelToken.source();  // 使用api的CancelToken

  try {

    let fileInfo = await getFileInfo(itemData.id);

    // 2. 开始分块下载
    const data = await chunkedDownload({
      url: `file/api/download/${itemData.id}/download/`,
      fileSize: fileInfo.file_size,
      fileId: itemData.id,
      chunkSize: 1 * 1024 * 1024, // 1MB分块
      cancelToken: cancelToken.value,
      onProgress: (progress) => {
        downloadProgress.value = progress;
      },
      onChunk: (chunk, loaded) => {
        console.log(`Downloaded chunk: ${loaded}/${fileInfo.file_size}`);
      }
    });

    // 3. 创建下载链接
    const blob = new Blob([data], {type: 'application/octet-stream'});
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = fileInfo.name;
    link.click();

    // 4. 清理
    setTimeout(() => {
      URL.revokeObjectURL(url);
      isDownloading.value = false;
      downloadProgress.value = 100;
      ElMessage.success('下载完成');
    }, 500);

  } catch (error) {
    console.error('分块下载失败:', error);
    ElMessage.error(`下载失败: ${error.message}`);
    isDownloading.value = false;
  }
};

const cancelDownload = () => {

  if (cancelToken.value) {
    cancelToken.value.cancel('用户取消下载');
  }
  isDownloading.value = false;
  downloadProgress.value = 0;
};


const getFileInfo = async (fileId: number) => {
  console.log('fileId ', fileId)
  const response = await retrieveFileById('', fileId, {params: {_t: Date.now()}});
  console.log('获取文件信息成功:', response.data);
  return {
    file_size: response.data.data.file_size,
    name: response.data.data.original_filename
  };
};

</script>

<template>

  <div class="tool">
    <el-dropdown>
        <span class="user-info">
          <el-tooltip content="工具包下载" placement="top">
    <el-button
        type="success"
        :icon="Download"
        circle
        :loading="isDownloading"
    />
  </el-tooltip>
        </span>

      <template #dropdown>
        <el-dropdown-menu>
          <el-progress
              v-if="isDownloading"
              :percentage="downloadProgress"
              :stroke-width="10"
              :status="downloadStatus"
          />
          <el-dropdown-item
              @click="startChunkedDownload({id:42})"
              :disabled="isDownloading"
          >
            <el-icon>
              <Check/>
            </el-icon>
            <!--            <el-link href="https://material.newdmy.com:4433/media/boba/Forticlient_安卓手机安装包.zip">安卓客户端下载</el-link>-->
            <el-link>安卓客户端下载</el-link>
          </el-dropdown-item>

          <el-dropdown-item
              divided
              @click="startChunkedDownload({id: 27})"
              :disabled="isDownloading"
          >
            <el-icon>
              <Check/>
            </el-icon>
            <el-link>MacOS客户端下载</el-link>
          </el-dropdown-item>

          <el-dropdown-item
              divided
              @click="startChunkedDownload({id: 4})"
              :disabled="isDownloading"
          >
            <el-icon>
              <Check/>
            </el-icon>
            <!--            <el-link href="https://material.newdmy.com:4433/media/boba/FortiClient_Windows客户端安装包.rar">Windows客户端下载</el-link>-->
            <el-link>Windows客户端下载</el-link>
          </el-dropdown-item>

        </el-dropdown-menu>
      </template>

    </el-dropdown>
  </div>

</template>

<style scoped lang="scss">

</style>