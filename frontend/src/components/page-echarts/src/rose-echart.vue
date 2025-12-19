<script setup lang="ts">
import {computed, ref} from "vue";
import BaseEchart from "./base-echart.vue";
import * as echarts from 'echarts'
import type {EChartsOption} from 'echarts'

import type {IEchartValueType} from "@/components/page-echarts/types/index.ts";
import ChinaJSON from '../data/china.json'

echarts.registerMap('china', ChinaJSON as any)

interface IProps {
  roseData: IEchartValueType[]
}

const props = defineProps<IProps>()

const option = computed<EChartsOption>(() => {
  return {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    toolbox: {
      show: true,
      feature: {
        mark: {show: true},
        dataView: {show: true, readOnly: false},
        restore: {show: true},
        saveAsImage: {show: true}
      }
    },
    series: [
      {
        name: '访问来源',
        type: 'pie',
        radius: [10, 140],
        center: ['50%', '50%'],
        bottom: '-15%',
        roseType: 'area',
        itemStyle: {
          borderRadius: 8
        },
        data: props.roseData,
        label: {
          show: true
        }
      }
    ]
  }
})
</script>

<template>
  <div class="rose-chart">
    <base-echart :option="option"/>
  </div>
</template>

<style scoped lang="scss">

</style>