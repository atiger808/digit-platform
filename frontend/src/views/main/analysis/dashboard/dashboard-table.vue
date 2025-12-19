<template>
  <div class="dashboard">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="label">今日新增素材</div>
            <div class="value">{{ summary.today_file_count }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="label">今日新增时长 (秒)</div>
            <div class="value">{{ formatDuration(summary.today_duration) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="label">全部素材数量</div>
            <div class="value">{{ summary.total_file_count }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="label">全部总时长</div>
            <div class="value">{{ formatDuration(summary.total_duration) }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- 素材数 TOP10 -->
      <el-col :span="8">
        <el-card shadow="hover" header="素材数量 TOP10">
          <el-table :data="fileCountTop10" size="small" height="400">
            <el-table-column prop="rank" label="排名" width="60" />
            <el-table-column prop="real_name" label="用户" />
            <el-table-column prop="file_count" label="素材数" width="100" />
          </el-table>
        </el-card>
      </el-col>

      <!-- 时长 TOP10 -->
      <el-col :span="8">
        <el-card shadow="hover" header="素材时长 TOP10">
          <el-table :data="durationTop10" size="small" height="400">
            <el-table-column prop="rank" label="排名" width="60" />
            <el-table-column prop="real_name" label="用户" />
            <el-table-column label="时长" width="120">
              <template #default="{ row }">
                {{ formatDuration(row.total_duration) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 大小 TOP10 -->
      <el-col :span="8">
        <el-card shadow="hover" header="素材大小 TOP10">
          <el-table :data="sizeTop10" size="small" height="400">
            <el-table-column prop="rank" label="排名" width="60" />
            <el-table-column prop="real_name" label="用户" />
            <el-table-column label="大小" width="120">
              <template #default="{ row }">
                {{ formatBytes(row.total_size) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 在线用户 -->
    <el-row style="margin-top: 20px;">
      <el-col :span="24">
        <el-card shadow="hover" header="在线用户">
          <el-tag
            v-for="user in onlineUsers"
            :key="user.user_id"
            style="margin-right: 8px; margin-bottom: 8px;"
            type="success"
          >
            {{ user.real_name || user.username }}
          </el-tag>
          <span v-if="onlineUsers.length === 0">暂无在线用户</span>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed } from 'vue';
import { getSummary, getUserVideoStats, getOnlineUsers } from '@/service/main/files/files'
import type { DashboardSummary, UserVideoStat, OnlineUser } from '@/types/dashboard';

// 响应式数据
const summary = ref<DashboardSummary>({
  today_file_count: 0,
  today_duration: 0,
  total_file_count: 0,
  total_duration: 0,
});

const allStats = ref<UserVideoStat[]>([]);
const onlineUsers = ref<OnlineUser[]>([]);

// 计算属性（TOP10）
const fileCountTop10 = computed(() => {
  return [...allStats.value]
    .sort((a, b) => b.file_count - a.file_count)
    .slice(0, 10)
    .map((item, index) => ({ ...item, rank: index + 1 }));
});

const durationTop10 = computed(() => {
  return [...allStats.value]
    .sort((a, b) => b.total_duration - a.total_duration)
    .slice(0, 10)
    .map((item, index) => ({ ...item, rank: index + 1 }));
});

const sizeTop10 = computed(() => {
  return [...allStats.value]
    .sort((a, b) => b.total_size - a.total_size)
    .slice(0, 10)
    .map((item, index) => ({ ...item, rank: index + 1 }));
});

// 工具函数
const formatDuration = (seconds: number): string => {
  if (!seconds) return '0秒';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}时 ${m}分 ${s}秒`;
  if (m > 0) return `${m}分 ${s}秒`;
  return `${s}秒`;
};

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// 加载数据
onMounted(async () => {
  try {
    const [summaryRes, statsRes, onlineRes] = await Promise.all([
      getSummary(),
      getUserVideoStats(),
      getOnlineUsers(),
    ]);
    console.log('summaryRes', summaryRes);
    console.log('statsRes', statsRes);
    console.log('onlineRes', onlineRes);
    summary.value = summaryRes.data.data;
    allStats.value = statsRes.data.data.data;
    onlineUsers.value = onlineRes.data.data;
  } catch (error) {
    console.error('加载仪表盘数据失败:', error);
    ElMessage.error('加载仪表盘数据失败');
  }
});
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-item {
  text-align: center;
}

.label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}
</style>