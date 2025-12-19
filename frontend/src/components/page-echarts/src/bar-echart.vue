<script setup lang="ts">
import {computed} from "vue";
import BaseEchart from "@/components/page-echarts";
import type {EChartsOption} from "echarts";
import * as echarts from 'echarts'

interface IProps {
  labels: string[]
  values: string[]
}

const props = defineProps<IProps>()

const option = computed<EChartsOption>(() => {
  return {
    title: {
      text: '支持鼠标滚动缩放'
    },
    grid: {
      // left: '3%',
      // right: '4%',
      bottom: '7%',
      // containLabel: true
    },
    xAxis: {
      type: 'category',
      data: props.labels
    },
    yAxis: {
      type: 'value'
    },
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100
      },
    ],
    series: [
      {
        data: props.values,
        type: 'bar',
        showBackground: true,
        backgroundStyle: {
          color: 'rgba(180, 180, 180, 0.2)'
        },
        // 系列图形的样式（每个item的样式）
        // 可以被放到每一项中，针对每一项设置
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#83bff6' },
              { offset: 0.7, color: '#188df0' },
              { offset: 1, color: '#188df0' }
          ])
        }
      }
    ]
  }
})


</script>

<template>
  <div class="bar-chart">
    <BaseEchart :option="option"/>
  </div>
</template>

<style scoped lang="scss">

</style>