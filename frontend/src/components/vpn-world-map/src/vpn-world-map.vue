// VpnWorldMap.vue (使用 GeoJSON)
<template>
  <div ref="mapChartRef" class="map-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import * as echarts from 'echarts';

const mapChartRef = ref<HTMLElement | null>(null);
let myChart: echarts.ECharts | null = null;

// 如果放在 public 目录下
const loadMapData = async () => {
  try {
    // 从 public 目录获取
    const response = await fetch('/world.json'); // 确保路径正确
    const worldGeoJSON = await response.json();

    // 注册地图
    echarts.registerMap('world', worldGeoJSON);

    // 初始化图表
    initChart();
  } catch (error) {
    console.error('Failed to load map data:', error);
  }
};

// 如果放在 src/assets 目录下 (需要类型声明)
// declare module '*.json' {
//   const value: any;
//   export default value;
// }
// import worldGeoJSON from '@/assets/world.json';
// const loadMapData = () => {
//   echarts.registerMap('world', worldGeoJSON);
//   initChart();
// };

const initChart = () => {
  if (mapChartRef.value) {
    if (myChart) {
      echarts.dispose(myChart);
    }
    myChart = echarts.init(mapChartRef.value);

    const option: echarts.EChartsOption = {
      // ... (同上) ...
      series: [
        {
          name: 'VPN Users',
          type: 'map',
          map: 'world', // 使用注册的地图名称
          // ... (同上) ...
        }
      ]
    };

    myChart.setOption(option);
    // ... (同上) ...
  }
};

onMounted(() => {
  loadMapData(); // 加载地图数据并初始化
});

onBeforeUnmount(() => {
  // ... (同上) ...
});

</script>

<style scoped>
.map-chart {
  width: 100%;
  height: 600px;
}
</style>