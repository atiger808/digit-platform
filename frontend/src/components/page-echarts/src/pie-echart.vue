<script setup lang="ts">

import {computed, ref} from "vue";
import BaseEchart from "./base-echart.vue";
import type {EChartsOption} from 'echarts';
import type {IEchartValueType} from "@/components/page-echarts/types";

interface IProps {
  pieData: IEchartValueType[]
}

const props = defineProps<IProps>()


const option = computed<EChartsOption>(() => {
  return {
    title: {
      text: '',
      subtext: '',
      left: 'center'
    },
    tooltip: {
      trigger: 'item'
    },
    toolbox: {
      show: true,
      feature: {
        mark: {show: true},
        dataView: {show: true, readOnly: true},
        restore: {show: true},
        saveAsImage: {show: true}
      }
    },
    legend: {
      orient: 'vertical', //horizontal & vertical
      left: 'left'
    },
    series: [
      {
        name: 'Access From',
        type: 'pie',
        radius: '50%',
        data: props.pieData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
})

console.log('options', option)

</script>

<template>
  <div class="pie-echart">
    <base-echart :option="option"/>
  </div>
</template>

<style scoped lang="scss">

</style>