<script setup lang="ts">

import {computed, ref} from "vue";
import BaseEchart from "./base-echart.vue";
import type {EChartsOption} from 'echarts'


interface IProps {
  labels: string[]
  values: string[]
}

const props = defineProps<IProps>()

const option = computed<EChartsOption>(() => {
  return {
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: props.labels
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        data: props.values,
        type: 'line',
        areaStyle: {}
      }
    ]
  }
})

</script>

<template>
  <div class="line-eachart">
    <base-echart :option="option"/>
  </div>
</template>

<style scoped lang="scss">

</style>