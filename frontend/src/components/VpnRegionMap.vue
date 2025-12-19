<!-- VpnRegionMap.vue -->

<script setup lang="ts">
import {ref, onMounted, onBeforeUnmount, watch, nextTick, computed} from 'vue';
import * as echarts from 'echarts/core';
import {CanvasRenderer} from 'echarts/renderers';
import {MapChart} from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  VisualMapComponent,
  ToolboxComponent,
} from 'echarts/components';
import worldGeoJSON from '@/assets/maps/world.json';
import {getVpnmonitorsRegionSummary} from "@/service/main/vpns/vpns.ts";
import {decryptData} from "@/utils/encrypts.ts";

echarts.use([
  CanvasRenderer,
  MapChart,
  TitleComponent,
  TooltipComponent,
  VisualMapComponent,
  ToolboxComponent,
]);

// --- 类型定义 ---
// 假设后端返回的数据结构包含所有需要的字段
interface RegionSummaryData {
  name: string;              // 区域显示名称 (例如 "日本")
  region_english: string;    // 区域英文名称 (例如 "Japan")
  region_code: string;       // 区域代码 (例如 "JP")
  total_users: number;       // 总用户数
  total_traffic_bytes: number; // 总流量 (字节)
  total_duration_secs: number; // 总时长 (秒)
  online_users: number;      // 在线用户数
  // value: [number, number]; // [总用户数, 在线用户数] (旧结构，可以移除或保留用于兼容)
}

// --- Props ---
const props = withDefaults(
    defineProps<{
      mapHeight?: string;
      autoRefreshInterval?: number;
    }>(),
    {
      mapHeight: '600px',
      autoRefreshInterval: 0,
    }
);

// --- 响应式数据 ---
const mapChartRef = ref<HTMLElement | null>(null);
let myChart: echarts.ECharts | null = null;
const loading = ref(false);
const error = ref('');
const regionData = ref<RegionSummaryData[]>([]);

// --- 新增：视图模式状态 ---
type ViewMode = 'users' | 'traffic' | 'duration' | 'online';
const currentViewMode = ref<ViewMode>('users'); // 默认显示总用户数

// --- 新增：为不同视图模式定义颜色方案 ---
const viewModeColors = {
  // users: ['#ffffff', '#a6d8ff', '#4da6ff'],       // 蓝色系 - 用户数
  users: ['#ffffff', '#33ccff', '#0066cc'],       // 蓝色系 - 用户数
  traffic: ['#ffffff', '#a6ffd8', '#4dffbf'],     // 青绿色系 - 流量
  duration: ['#ffffff', '#ffd8a6', '#ffbf4d'],    // 橙黄色系 - 时长
  online: ['#ffffff', '#ffa6d8', '#ff4dbf'],      // 粉红色系 - 在线用户
};


// --- 修改：更新 maxVisualMapValue 的计算以包含 min ---
// 虽然 min 通常为 0，但显式包含更清晰
const maxVisualMapValue = computed(() => {
  if (regionData.value.length === 0) return {min: 0, max: 10};
  let maxVal = 10;
  switch (currentViewMode.value) {
    case 'users':
      maxVal = Math.max(...regionData.value.map(item => item.total_users), 10);
      break;
    case 'traffic':
      maxVal = Math.max(...regionData.value.map(item => item.total_traffic_bytes), 10);
      break;
    case 'duration':
      maxVal = Math.max(...regionData.value.map(item => item.total_duration_secs), 10);
      break;
    case 'online':
      maxVal = Math.max(...regionData.value.map(item => item.online_users), 10);
      break;
    default:
      maxVal = Math.max(...regionData.value.map(item => item.total_users), 10);
  }
  return {min: 0, max: maxVal};
});

// --- 新增：计算属性，根据当前模式返回用于 tooltip 的值和单位 ---
const getDisplayValueAndUnit = (item: RegionSummaryData): { value: number, unit: string, label: string } => {
  switch (currentViewMode.value) {
    case 'users':
      return {value: item.total_users, unit: '人', label: '总用户数', 'onlineUsers': item.online_users};
    case 'traffic':
      return {value: item.total_traffic_bytes, unit: 'B', label: '总流量'}; // 可以在 formatter 中格式化
    case 'duration':
      return {value: item.total_duration_secs, unit: 's', label: '总时长'}; // 可以在 formatter 中格式化
    case 'online':
      return {value: item.online_users, unit: '人', label: '在线用户数'};
    default:
      return {value: item.total_users, unit: '人', label: '总用户数'};
  }
};

// --- 新增：辅助函数，格式化流量和时长 ---
const formatTraffic = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
  if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  if (bytes < 1024 * 1024 * 1024 * 1024) return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
  if (bytes < 1024 * 1024 * 1024 * 1024 * 1024) return (bytes / (1024 * 1024 * 1024 * 1024)).toFixed(2) + ' TB';
  if (bytes < 1024 * 1024 * 1024 * 1024 * 1024 * 1024) return (bytes / (1024 * 1024 * 1024 * 1024 * 1024)).toFixed(2) + ' PB';
  if (bytes < 1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024) return (bytes / (1024 * 1024 * 1024 * 1024 * 1024 * 1024)).toFixed(2) + ' EB';
  if (bytes < 1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024) return (bytes / (1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024)).toFixed(2) + ' ZB';
  return (bytes / (1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024)).toFixed(2) + ' YB';
};

const formatDuration = (seconds: number): string => {
  const days = Math.floor(seconds / (24 * 3600));
  const hours = Math.floor((seconds % (24 * 3600)) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  let result = '';
  if (days > 0) result += days + '天';
  if (hours > 0) result += hours + '小时';
  if (minutes > 0) result += minutes + '分钟';
  if (secs > 0 || result === '') result += secs + '秒'; // 如果都是0，显示0秒
  return result;
};

// --- 方法 ---
// 1. 获取后端数据
const fetchRegionData = async () => {
  loading.value = true;
  error.value = '';
  try {
    // --- 假设你的 API 现在返回包含所有字段的数据 ---
    const response = await getVpnmonitorsRegionSummary({_t: Date.now()});
    let result = decryptData(response.data.result);
    result = JSON.parse(result);

    if (result.code === 200 || result.code === 2000) {
      // --- 确保后端返回的数据结构匹配 RegionSummaryData ---
      regionData.value = result.data?.data || [];

      await nextTick(); // 确保 DOM 更新
      updateChart();
    } else {
      throw new Error(result.msg || '获取数据失败');
    }
  } catch (err: any) {
    console.error('获取区域统计数据失败:', err);
    error.value = `获取数据失败: ${err.message || err}`;
  } finally {
    loading.value = false;
  }
};

// 2. 初始化 ECharts 图表
const initChart = async () => {
  if (mapChartRef.value) {
    try {
      echarts.registerMap('world', worldGeoJSON as any);
      console.log('World map registered successfully.');
    } catch (e) {
      console.error('Failed to register world map:', e);
      error.value = '地图数据加载失败';
      return;
    }

    if (myChart) {
      echarts.dispose(myChart);
    }
    myChart = echarts.init(mapChartRef.value);

    const baseOption: echarts.EChartsOption = {
      title: {
        text: 'VPN 用户区域分布',
        // --- 动态更新副标题 ---
        subtext: computed(() => {
          const modeTextMap = {
            users: '颜色: 总用户数',
            traffic: '颜色: 总流量',
            duration: '颜色: 总时长',
            online: '颜色: 在线用户数',
          };
          return modeTextMap[currentViewMode.value] || modeTextMap.users;
        }).value,
        left: 'right',
      },
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          if (params?.componentType === 'series' && params?.seriesType === 'map') {
            if (params?.name) {
              const regionName = params.name; // 英文名
              // 找到对应的数据项
              const dataItem = regionData.value.find(
                  item => item.region_english === regionName
              );
              if (dataItem) {
                const displayInfo = getDisplayValueAndUnit(dataItem);
                let formattedValue = displayInfo.value.toString();
                if (currentViewMode.value === 'traffic') {
                  formattedValue = formatTraffic(displayInfo.value);
                } else if (currentViewMode.value === 'duration') {
                  formattedValue = formatDuration(displayInfo.value);
                }
                let onlineUsers = ''
                if (displayInfo.onlineUsers) {
                  onlineUsers = `<br/>在线用户：${displayInfo.onlineUsers}`;
                }
                return `${dataItem.name}<br/>${displayInfo.label}: ${formattedValue} ${onlineUsers}`;
              }
            }
          }
          return `${params?.name || '未知'}<br/>无数据`;
        },
      },
      // --- visualMap 将在 updateChart 中动态更新 ---
      visualMap: {
        min: 0,
        max: 100, // 初始值，会被 maxVisualMapValue 覆盖
        inRange: {
          color: ['#ffffff', '#33ccff', '#0066cc'],
        },
        text: ['高', '低'],
        calculable: true,
        left: 'left',
        top: 'bottom',
        textStyle: {
          color: '#000',
        },
      },
      toolbox: {
        show: true,
        orient: 'vertical',
        left: 'right',
        top: 'center',
        feature: {
          dataView: {readOnly: false},
          restore: {},
          saveAsImage: {},
        },
      },
      series: [
        {
          name: 'VPN 数据',
          type: 'map',
          map: 'world',
          roam: true,
          zoom: 1.2,
          scaleLimit: {
            min: 0.5,
            max: 3,
          },
          label: {
            show: false,
          },
          emphasis: {
            label: {
              show: true,
            },
            itemStyle: {
              areaColor: '#ffeb3b',
            },
          },
          data: [], // 初始为空
        },
      ],
    };

    myChart.setOption(baseOption, true);

    const handleResize = () => myChart?.resize();
    window.addEventListener('resize', handleResize);

    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize);
    });
  }
};

// 3. 更新图表数据和配置
const updateChart = () => {
  if (myChart && regionData.value.length > 0) {
    const data = regionData.value;

    // 计算所有地区用户数总和
    const totalUsers = data.reduce((acc, item) => acc + item.total_users, 0);
    const totalOnlineUsers = data.reduce((acc, item) => acc + item.online_users, 0);

    // 计算所有地区用到期用户数总和
    const totalExpiredUsers = data.reduce((acc, item) => acc + item.expire_users, 0);

    const maxTotalUsers = Math.max(...data.map((item) => item.total_users), 10);
    const maxOnlineUsers = Math.max(...data.map((item) => item.online_users), 10);

    // 总流量
    const totalTraffic = data.reduce((acc, item) => acc + item.total_traffic_bytes, 0);
    console.log("totalTraffic ", totalTraffic)
    const maxTotalTraffic = Math.max(...data.map((item) => item.total_traffic_bytes), 10);
    const totalTrafficPercentage = (totalTraffic / maxTotalTraffic) * 100;
    const totalTrafficPercentageText = `${totalTrafficPercentage.toFixed(2)}%`;
    // 总时长
    const totalDuration = data.reduce((acc, item) => acc + item.total_duration_secs, 0);
    console.log("totalDuration ", totalDuration)
    const maxTotalDuration = Math.max(...data.map((item) => item.total_duration_secs), 10);
    const totalDurationPercentage = (totalDuration / maxTotalDuration) * 100;
    const totalDurationPercentageText = `${totalDurationPercentage.toFixed(2)}%`;




    // --- 计算当前模式下的 min/max ---
    const {min, max} = maxVisualMapValue.value;
    console.log(`Debug: Calculated min/max for ${currentViewMode.value}:`, min, max);

    // --- 准备地图系列数据 ---
    const mapSeriesData = data.map((item) => {
      // 根据当前视图模式选择用于着色的值
      let valueForColoring: number;
      switch (currentViewMode.value) {
        case 'users':
          valueForColoring = item.total_users;
          break;
        case 'traffic':
          valueForColoring = item.total_traffic_bytes;
          break;
        case 'duration':
          valueForColoring = item.total_duration_secs;
          break;
        case 'online':
          valueForColoring = item.online_users;
          break;
        default:
          valueForColoring = item.total_users;
      }

      return {
        name: item.region_english, // 用于匹配 GeoJSON
        value: valueForColoring,   // 用于 visualMap 着色
        // 可以添加其他用于 tooltip 的原始数据
        originalData: item,        // 保留原始数据供 tooltip 使用
      };
    });

    console.log("Debug: Prepared mapSeriesData for current mode:", currentViewMode.value, mapSeriesData);
    console.log("Debug: Prepared mapSeriesData for maxVisualMapValue:", maxVisualMapValue.value)


    // --- 更新图表 ---
    // 使用 notMerge: false (默认) 来更新特定部分
    myChart.setOption(
        {
          title: {
            // 动态更新主标题和副标题
            text: 'VPN 用户区域分布',
            subtext: (() => {
              const modeTextMap = {
                users: `总用户数：${totalUsers} | 在线用户数：${totalOnlineUsers} | 到期用户数：${totalExpiredUsers}`,
                traffic: `总流量：${formatTraffic(totalTraffic)}`,
                duration: `总时长：${formatDuration(totalDuration)}`,
                online: `总在线用户数：${totalOnlineUsers}`,
              };
              console.log("currentViewMode.value ", currentViewMode.value)
              return modeTextMap[currentViewMode.value] || modeTextMap.users;
            })(),
          },
          visualMap: {
            // --- 关键修改：使用计算出的 min/max 和对应的颜色方案 ---
            min: min,
            max: max,
            inRange: {
              // --- 根据 currentViewMode.value 选择颜色 ---
              color: viewModeColors[currentViewMode.value] || viewModeColors.users
            }
            // 如果你有其他 visualMap 属性需要保持，也在这里添加
            // min: 0, // 通常 min 保持 0 即可
          },
          series: [
            {
              name: 'VPN 数据',
              type: 'map',
              map: 'world',
              // --- 更新地图区域数据 ---
              data: mapSeriesData,
            },
          ],
        },
        {notMerge: false} // 使用 merge 更新
    );
    console.log("Debug: ECharts option updated for mode:", currentViewMode.value);
  } else {
    console.log("Debug: Skipping chart update, no data or chart not ready.");
  }
};

// --- 新增：切换视图模式的方法 ---
const switchViewMode = (mode: ViewMode) => {
  if (currentViewMode.value !== mode) {
    currentViewMode.value = mode;
    console.log("Switched to view mode:", mode);
    // 数据已经加载，直接更新图表
    if (regionData.value.length > 0) {
      updateChart();
    }
    // 如果数据未加载或需要刷新数据，可以调用 fetchRegionData()
    // 但根据你的后端 API 设计，一次请求应该能获取所有需要的数据
    // fetchRegionData();
  }
};

// 4. 刷新数据 (暴露给父组件或内部定时器调用)
const refreshData = () => {
  fetchRegionData();
};
defineExpose({refreshData});

// --- 生命周期 ---
let refreshTimer: number | null = null;

onMounted(async () => {
  await initChart();
  await fetchRegionData(); // 组件挂载后立即获取数据

  // 设置自动刷新
  if (props.autoRefreshInterval > 0) {
    refreshTimer = window.setInterval(() => {
      if (!loading.value) {
        fetchRegionData();
      }
    }, props.autoRefreshInterval);
  }
});

onBeforeUnmount(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
  }
  if (myChart) {
    echarts.dispose(myChart);
    myChart = null;
  }
});

// 如果 props 变化需要重新设置定时器 (可选)
watch(
    () => props.autoRefreshInterval,
    (newInterval, oldInterval) => {
      if (refreshTimer) {
        clearInterval(refreshTimer);
        refreshTimer = null;
      }
      if (newInterval > 0) {
        refreshTimer = window.setInterval(() => {
          if (!loading.value) {
            fetchRegionData();
          }
        }, newInterval);
      }
    }
);

// --- 监听视图模式变化，自动更新图表 ---
watch(currentViewMode, (newMode, oldMode) => {
  console.log(`View mode changed from ${oldMode} to ${newMode}`);
  if (regionData.value.length > 0) {
    updateChart(); // 数据已存在，只需更新图表
  }
});

</script>


<template>
  <div class="vpn-region-map">
    <!-- 加载指示器 -->
    <div v-if="loading" class="loading">
      <el-skeleton :rows="5" animated/>
    </div>

    <!-- 错误提示 -->
    <el-alert
        v-else-if="error"
        :title="error"
        type="error"
        show-icon
        closable
        @close="error = ''"
    />

    <!-- 地图容器 -->
    <div
        v-show="!loading && !error"
        class="map-wrapper"
    >
      <!-- 按钮组 -->
      <div class="map-controls">
        <el-button
            size="small"
            :type="currentViewMode === 'users' ? 'primary' : 'default'"
            @click="switchViewMode('users')"
        >
          总用户分布
        </el-button>
        <el-button
            size="small"
            :type="currentViewMode === 'traffic' ? 'primary' : 'default'"
            @click="switchViewMode('traffic')"
        >
          流量分布
        </el-button>
        <el-button
            size="small"
            :type="currentViewMode === 'duration' ? 'primary' : 'default'"
            @click="switchViewMode('duration')"
        >
          时长分布
        </el-button>
        <el-button
            size="small"
            :type="currentViewMode === 'online' ? 'primary' : 'default'"
            @click="switchViewMode('online')"
        >
          在线用户分布
        </el-button>
        <!-- 可选：添加一个刷新按钮 -->
        <!--        <el-button-->
        <!--            size="small"-->
        <!--            type="success"-->
        <!--            :loading="loading"-->
        <!--            @click="refreshData"-->
        <!--            style="margin-left: auto;"-->
        <!--        >-->
        <!--          刷新-->
        <!--        </el-button>-->
      </div>

      <!-- 地图本身 -->
      <div
          ref="mapChartRef"
          class="map-chart"
          :style="{ height: mapHeight }"
      ></div>

    </div>

    <!-- 信息说明 -->
    <div class="map-info" v-show="!loading && !error">
      <p><strong>数据说明:</strong></p>
      <ul>
        <li>区域<strong>颜色深浅</strong>代表当前选定维度的数值大小。</li>
        <li>鼠标<strong>悬浮</strong>在区域上可查看详细数值。</li>
        <li><strong>滚动</strong>鼠标进行地图缩放操作。</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.vpn-region-map {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.map-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 440px; /* 确保有最小高度 */
}

.map-controls {
  padding: 10px 0;
  display: flex;
  gap: 10px; /* 按钮之间的间距 */
  flex-wrap: wrap; /* 如果空间不够，按钮可以换行 */
}

.map-chart {
  flex: 1;
  width: 100%;
  /* height 由 style 绑定控制 */
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.map-info {
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
  margin-top: 10px;
  font-size: 14px;
}

.map-info ul {
  margin: 5px 0;
  padding-left: 20px;
}
</style>