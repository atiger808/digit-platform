<script setup lang="ts">

import {ref, onMounted, watchEffect} from 'vue'
import * as echarts from 'echarts';

import worldGeoJSON from '@/assets/maps/world.json' // 确保路径正确

// 引入 EChartsOption 类型
import type { EChartsOption } from 'echarts';

interface IProps {
  option: EChartsOption
}

const props = defineProps<IProps>()

const echartRef = ref<HTMLElement>()
onMounted(() => {

  // --- 关键步骤：注册地图 ---
    try {
      // 确保在初始化图表前注册地图
      echarts.registerMap('world', worldGeoJSON as any); // 类型断言，因为类型可能不完全匹配
      console.log('World map registered successfully.');
    } catch (e) {
      console.error('Failed to register world map:', e);
      return;
    }

  // 1.初始化echarts实例
  const echartInstance = echarts.init(echartRef.value!, 'light', {renderer: 'canvas'})

  // 2.第一次进行setOption
  // watchEffect监听option变化，重新执行
  watchEffect(() => echartInstance.setOption(props.option))

  // 3.监听windows缩放
  window.addEventListener('resize', () => {
    echartInstance.resize()
  })
})
</script>

<template>
  <div class="base-echart">
    <div class="echart" ref="echartRef"></div>
  </div>
</template>

<style scoped lang="scss">

.echart {
  width: 100%;
  flex: 1;
  min-height: 400px;
}
</style>