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
        ref="mapChartRef"
        class="map-chart"
        :style="{ height: mapHeight }"
        v-show="!loading && !error"
    ></div>

    <!-- 信息说明 -->
    <div class="map-info" v-show="!loading && !error">
      <p><strong>数据说明:</strong></p>
      <ul>
        <li>区域颜色深浅代表 <strong>用户数</strong></li>
        <li>鼠标<strong>悬浮</strong>在区域上可查看详细数值。</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
// 使用更精确的按需导入，避免引入可能冲突的组件
import * as echarts from 'echarts/core';
import {CanvasRenderer} from 'echarts/renderers';
import {MapChart} from 'echarts/charts'; // 如果你用 scatter
// 只导入 VpnRegionMap 必需的组件
import {
  TitleComponent,
  TooltipComponent,
  VisualMapComponent,
  ToolboxComponent,
  // 关键：显式排除 GridComponent, DataZoomComponent, DatasetComponent
  // 这些组件可能与地图交互产生冲突
} from 'echarts/components';

// --- 在 <script setup> 的最顶部，在任何其他逻辑之前，调用 echarts.use ---
echarts.use([
  CanvasRenderer,
  MapChart,
  TitleComponent,
  TooltipComponent,
  VisualMapComponent,
  ToolboxComponent,
]);


import {ref, onMounted, onBeforeUnmount, watch, nextTick} from 'vue'
import worldGeoJSON from '@/assets/maps/world.json' // 确保路径正确

import {getVpnRegionSummary} from "@/service/main/vpns/vpns.ts";
import {decryptData} from "@/utils/encrypts.ts";
import {worldNameMap} from "@/utils/nmap-en-zh-data.ts";


// --- 类型定义 ---
interface RegionSummaryData {
  name: string // 区域显示名称 (例如 "日本")
  region_english: string // 区域英文名称 (例如 "Japan")
  region_code: string // 区域代码 (例如 "JP")
  value: [number, number] // [总用户数, 在线用户数]
}

// --- Props ---
const props = withDefaults(
    defineProps<{
      mapHeight?: string // 地图容器高度
      autoRefreshInterval?: number // 自动刷新间隔 (毫秒), 0 或负数表示不自动刷新
    }>(),
    {
      mapHeight: '600px',
      autoRefreshInterval: 0 // 默认不自动刷新
    }
)

// --- 响应式数据 ---
const mapChartRef = ref<HTMLElement | null>(null)
let myChart: echarts.ECharts | null = null
const loading = ref(false)
const error = ref('')
const regionData = ref<RegionSummaryData[]>([])


// --- 方法 ---
// 1. 获取后端数据 (与之前相同)
const fetchRegionData = async () => {
  loading.value = true
  error.value = ''
  try {
    // --- 替换为你的实际 API 地址 ---
    const response = await getVpnRegionSummary({_t: Date.now()})
    let result = decryptData(response.data.result)
    result = JSON.parse(result)


    if (result.code === 200 || result.code === 2000) {
      regionData.value = result.data.data || []
      await nextTick() // 确保 DOM 更新
      updateChart()
    } else {
      throw new Error(result.msg || '获取数据失败')
    }
  } catch (err: any) {
    console.error('获取区域统计数据失败:', err)
    error.value = `获取数据失败: ${err.message || err}`
    // ElMessage.error(`获取数据失败: ${err.message || err}`)
  } finally {
    loading.value = false
  }
}

// 2. 初始化 ECharts 图表 (主要变化在这里)
const initChart = async () => {
  if (mapChartRef.value) {
    // --- 关键步骤：注册地图 ---
    try {
      // 确保在初始化图表前注册地图
      echarts.registerMap('world', worldGeoJSON as any); // 类型断言，因为类型可能不完全匹配
      console.log('World map registered successfully.');
    } catch (e) {
      console.error('Failed to register world map:', e);
      error.value = '地图数据加载失败';
      return;
    }

    if (myChart) {
      echarts.dispose(myChart)
    }
    myChart = echarts.init(mapChartRef.value)

    const baseOption: echarts.EChartsOption = {
      title: {
        text: 'VPN 区域统计',
        subtext: '颜色: 总用户数 | 在线用户数',
        left: 'right',
        // textStyle: {
        //   color: '#aaabbb'
        // }
      },
      tooltip: {
        trigger: 'item', // 'item' 可以触发地图区域和散点图系列
        formatter: (params: any) => {
          // --- 简化并加强健壮性 ---
          if (!params) return '无数据';

          // 区分是地图区域还是 markPoint
          if (params.componentType === 'series' && params.seriesType === 'map') {
            // 来自地图区域
            const value = params.data?.value;
            if (Array.isArray(value) && value.length >= 2) {
              const displayName = params.data?.zhName || params.data?.name || params.name || '未知';
              return `${displayName}<br/>总用户数: ${value[0]}<br/>在线用户数: ${value[1]}`;
            }
          } else if (params.componentType === 'markPoint') {
            console.log('Debug Tooltip Params (on hover/zoom):', params);
            console.log('Debug Tooltip Params.componentType:', params.componentType);
            // 来自 markPoint (气泡)
            // 使用我们放在 value[2] 的在线数
            const onlineCount = params.data?.value?.[2] ?? params.data?.value?.[0] ?? 'N/A';

            // 通过 name 找到中文名
            const originalItem = regionData.value.find(
                item => item.region_english === params.name
            );
            const displayName = originalItem ? originalItem.name : (params.name || '未知区域');

            return `${displayName}<br/>在线用户数: ${onlineCount}`;
          }

          // 默认 fallback
          const name = params.name || params.data?.name || '未知';
          // 尝试显示任何可用的 value
          const valueStr = Array.isArray(params.value) ? params.value.join(', ') : params.value;
          return `${name}${valueStr ? `<br/>值: ${valueStr}` : ''}`;
        }
      },
      visualMap: {
        min: 0,
        max: 100, // 初始值，后续会根据数据动态更新
        inRange: {
          color: ['#ffffff', '#33ccff', '#0066cc'],
          // color: ['lightskyblue', 'yellow', 'orangered'],
          // color: [
          //   '#313695',
          //   '#4575b4',
          //   '#74add1',
          //   '#abd9e9',
          //   '#e0f3f8',
          //   '#ffffbf',
          //   '#fee090',
          //   '#fdae61',
          //   '#f46d43',
          //   '#d73027',
          //   '#a50026'
          // ]
        },
        text: ['高', '低'],
        calculable: true,
        dimension: 0, // 使用 value 数组的第一个元素 (总用户数) 来映射颜色
        left: 'left',
        top: 'bottom',
        textStyle: {
          color: '#000'
        }
      },
      toolbox: {
        show: true,
        orient: 'vertical',
        left: 'right',
        top: 'center',
        feature: {
          mark: {show: true},
          dataView: {show: true, readOnly: true},
          restore: {show: true},
          saveAsImage: {show: true}
        }
      },
      series: [
        {
          name: 'VPN 用户',
          type: 'map',
          map: 'world', // 使用注册的地图名称 'world'
          roam: true,
          zoom: 1.2,
          scaleLimit: {
            min: 0.5,
            max: 3
          },
          label: {
            show: false
          },
          emphasis: {
            label: {
              show: true
            },
            itemStyle: {
              areaColor: '#ffeb3b' // 高亮时的区域颜色
            }
          },
          // data 和 markPoint.data 将在 updateChart 中动态设置
          data: []
        }
      ]
    };

    myChart.setOption(baseOption, true) // notMerge: true

    const handleResize = () => myChart?.resize()
    window.addEventListener('resize', handleResize)

    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize)
    })
  }
}

// 3. 更新图表数据 (与之前基本相同，主要是 regionCoords)
const updateChart = () => {
  if (myChart && regionData.value.length > 0) {
    const data = regionData.value

    // 动态计算 visualMap 的最大值 (基于总用户数 data.value[0])
    const maxTotalUsers = Math.max(...data.map((item) => item.value[0]), 10)

    // 计算所有地区用户数总和
    const totalUsers = data.reduce((acc, item) => acc + item.value[0], 0)

    // 计算所有地区在线用户数总和
    const totalOnlineUsers = data.reduce((acc, item) => acc + item.value[1], 0)


    // --- 气泡数据 (用于 scatter 系列) ---
    const regionCoords: Record<string, [number, number]> = {
      'Germany': [10.4515, 51.1657],
      'Indonesia': [113.9213, -0.7893],
      'Japan': [138.2529, 36.2048],
      'South Korea': [127.7669, 35.9078],
      'Malaysia': [101.9758, 4.2105],
      'Singapore': [103.8198, 1.3521],
      'Thailand': [100.9925, 15.87],
      'Taiwan': [120.9605, 23.6978],
      'United Kingdom': [-3.436, 55.3781],
      'United States of America': [-95.7129, 37.0902],
      'Philippines': [122.4343, 13.1607],
      'Vietnam': [106.6297, 10.8231],
      // ... 添加更多你支持的区域 ...
    };


    // --- 修改 1: 确保 mapSeriesData 使用与 world.json 匹配的名称 ---
    // 假设调试发现 world.json 使用 NAME 字段，且名称可能需要调整
    const geoJsonNameMap: Record<string, string> = {
      // Key: 你后端返回的 region_english
      // Value: world.json 中对应的 NAME
      'Germany': 'Germany',
      'Indonesia': 'Indonesia',
      'Japan': 'Japan',
      'South Korea': 'South Korea', // 假设调试发现是这个
      'Malaysia': 'Malaysia',
      'Singapore': 'Singapore',
      'Thailand': 'Thailand',
      'Taiwan': 'Taiwan', // 或 'Taiwan, Province of China' 检查调试输出
      'United Kingdom': 'United Kingdom', // 或 'United Kingdom of Great Britain and Northern Ireland'
      'United States of America': 'United States of America', // 关键修改点
      'Vietnam': 'Vietnam',
      'Philippines': 'Philippines',
      // ... 其他需要映射的国家 ...
    };

    // // --- 地图区域着色数据 ---
    // // mapSeriesData 的 name 必须与 world.json 中的国家名称 (通常是 NAME 字段) 一致
    // const mapSeriesData = data.map((item) => {
    //   // 使用映射查找 world.json 中的正确名称
    //   const geoJsonName = geoJsonNameMap[item.region_english] || item.region_english;
    //   return {
    //     name: geoJsonName, // 使用 world.json 中的名称
    //     zhName: item.name, // 使用 world.json 中的名称
    //     value: item.value // [总用户数, 在线用户数]
    //   };
    // });
    // console.log("Debug: mapSeriesData:", mapSeriesData); // 添加日志


    // --- 构造地图系列数据，包含柱状图 ---
    // 每个区域的数据项需要包含 name, value (用于 visualMap 和 tooltip), 以及 bar 或 pie 配置
    const mapSeriesData = data.map((item) => {
      // 从 regionCoords 获取坐标，用于放置柱状图
      const coords = regionCoords[item.region_english];

      const regionDataItem: any = {
        name: item.region_english,     // 用于匹配 GeoJSON
        zhName: item.name,             // 用于 tooltip 显示中文
        value: item.value,          // [总用户数, 在线用户数] -> 取总用户数用于区域着色和 tooltip
      };

      // 如果坐标存在，则为该区域添加柱状图
      if (coords) {
        regionDataItem.bar = {
          // --- 关键：设置柱状图的值 ---
          // 这里可以是单个值，也可以是数组（如果是堆叠柱状图）
          value: item.value[0], // 使用总用户数作为柱状图的高度

          // --- 可选：自定义柱状图样式 ---
          itemStyle: {
            color: '#e67e22', // 橙色柱子
            // opacity: 0.8
          },

          // --- 可选：自定义柱状图标签 ---
          label: {
            show: true,
            position: 'top', // 标签位置
            formatter: item.value[0].toString(), // 显示用户数
            fontSize: 10,
            color: '#333'
          },

          // --- 可选：设置柱状图的大小 ---
          // ECharts 会根据 value 自动调整大小，但可以设置一些限制
          // barWidth, barHeight 等属性可能不直接用于 map series 的 bar
          // 通常通过 value 的大小来控制
        };
      } else {
        console.warn(`未找到区域 "${item.region_english}" (${item.name}) 的坐标`);
      }

      return regionDataItem;
    });


    // --- 分步更新图表 ---
    // 1. 首先更新地图区域数据
    myChart.setOption({
      title: {subtext: `总用户数：${totalUsers} | 在线用户数：${totalOnlineUsers}`},
      visualMap: {max: maxTotalUsers},
      series: [{
        name: 'VPN 用户',
        data: mapSeriesData, // 只更新地图数据
        // 自定义名称映射
        nameMap: {}
      }]
    }, {notMerge: false});


    // 2. 稍微延迟后，再更新 markPoint 数据
    setTimeout(() => {
      if (myChart) {
        myChart.setOption({
          series: [{
            name: 'VPN 用户',
            markPoint: {
              data: [] // 更新气泡数据
            }
          }]
        }, {notMerge: false}); // 或者使用 { notMerge: false, replaceMerge: ['series'] } 如果支持

        // --- 再次触发 resize 确保更新后布局正确 ---
        myChart.resize();
      }
    }, 50); // 延迟 50ms


    // --- 添加强制 resize ---
    // 使用 nextTick 确保 DOM 更新后再 resize
    nextTick(() => {
      if (myChart) {
        myChart.resize();
      }
    });

    // myChart.resize();
  }


}

// 4. 刷新数据
const refreshData = () => {
  fetchRegionData()
}
defineExpose({refreshData})

// --- 生命周期 ---
let refreshTimer: number | null = null

onMounted(async () => {
  // --- 关键：先初始化图表（注册地图），再获取数据 ---
  await initChart() // 等待图表初始化完成
  if (!error.value) { // 只有在地图初始化没有出错的情况下才获取数据
    await fetchRegionData()
  }

  // // --- 添加延迟 ---
  // await new Promise(resolve => setTimeout(resolve, 500)); // 延迟 500ms
  // initChart();
  // await fetchRegionData();

  if (props.autoRefreshInterval > 0) {
    refreshTimer = window.setInterval(() => {
      if (!loading.value) {
        fetchRegionData()
      }
    }, props.autoRefreshInterval)
  }
})

onBeforeUnmount(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  if (myChart) {
    echarts.dispose(myChart)
    myChart = null
  }
})

watch(
    () => props.autoRefreshInterval,
    (newInterval, oldInterval) => {
      if (refreshTimer) {
        clearInterval(refreshTimer)
        refreshTimer = null
      }
      if (newInterval > 0) {
        refreshTimer = window.setInterval(() => {
          if (!loading.value) {
            fetchRegionData()
          }
        }, newInterval)
      }
    }
)

</script>

<style scoped>
.vpn-region-map {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.map-chart {
  width: 100%;
  flex: 1;
  min-height: 500px;
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