<script setup lang="ts">
import BaseEchart from "./base-echart.vue";
import {computed, ref} from "vue";

import {convertData} from '@/utils/convert-data'
import type {EChartsOption} from "echarts";
// import type {IEchartValueType} from "@/components/page-echarts/types";

// --- 类型定义 ---
interface RegionSummaryData {
  name: string // 区域显示名称 (例如 "日本")
  region_english: string // 区域英文名称 (例如 "Japan")
  region_code: string // 区域代码 (例如 "JP")
  value: [number, number] // [总用户数, 在线用户数]
}

interface IEchartValueType {
    name: string
    value: number
}


const props = defineProps<{
  scatterMapData: IEchartValueType,
  mapSeriesData: any,
}>()

const mapHeight = ref("600px")

const options = computed<EChartsOption>(() => {
  console.log("props.mapSeriesData ", props.mapSeriesData)
  // 总用户数
  const totalUsers = props.mapSeriesData.reduce((acc, cur) => acc + cur.value[0], 0);
  // 在线用户数
  const onlineUsers = props.mapSeriesData.reduce((acc, cur) => acc + cur.value[1], 0);
  // 到期用户数
  const expireUsers = props.mapSeriesData.reduce((acc, cur) => acc + cur.value[2], 0);

  console.log("totalUsers ", totalUsers)
  console.log("onlineUsers ", onlineUsers)
  return {
    backgroundColor: '#fff',
    title: {
      text: 'VPN 区域统计',
      left: 'left',
      textStyle: {
        color: '#aaabbb'
      },
      subtext: `总用户数：${totalUsers} | 在线用户数：${onlineUsers} | 到期用户数：${expireUsers}`
    },
    tooltip: {
      trigger: 'item',
      formatter: function (params: any) {

        if (!params) return '无数据';

        if (params.componentType === 'series') {
          if (params.seriesType === 'map') {
            // 来自地图区域
            const value = params.data?.value;
            if (Array.isArray(value) && value.length >= 2) {
              const displayName = params.data?.zhName || params.data?.name || params.name || '未知';
              return `${displayName}<br/>总用户数: ${value[0]}<br/>在线用户数: ${value[1]}`;
            }
          } else if (params.seriesType === 'scatter') {
            const value = params.data?.value;
            if (Array.isArray(value) && value.length >= 2) {
              const displayName = params.data?.zhName || params.data?.name || params.name || '未知';
              return `${displayName}<br/>总用户数: ${value[2]}`;
            }
          }
        }

        // 默认 fallback
        const name = params.name || params.data?.name || '未知';
        // 尝试显示任何可用的 value
        const valueStr = Array.isArray(params.value) ? params.value.join(', ') : params.value;
        return `${name}${valueStr ? `<br/>值: ${valueStr}` : ''}`;
      }
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

    visualMap: {
      min: 0,
      max: 30,
      left: 20,
      bottom: 20,
      calculable: true,
      dimension: 0,
      text: ['高', '低'],
      inRange: {
        // color: ['rgb(70, 240, 252)', 'rgb(250, 220, 46)', 'rgb(245, 38, 186)']
        color: ['#ffffff', '#33ccff', '#0066cc']
      },
      textStyle: {
        color: '#000'
      }
    },
    geo: {
      // 设置使用的地图（注册过的china地址）
      map: 'world',
      // 漫步：支持鼠标缩放效果
      // roam: 'scale',
      // emphasis: {
      //   areaColor: '#f4cccc',
      //   borderColor: 'rgb(9, 54, 95)',
      //   itemStyle: {
      //     areaColor: '#f4cccc'
      //   }
      // },

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

    },
    series: [
      {
        name: 'VPN 用户数',
        // 散点图在地图上展示数据
        type: 'scatter',
        coordinateSystem: 'geo',
        data: props.scatterMapData,
        // 散点的大小（可以根据数据不同显示不同的大小，设置为一个函数）
        symbolSize: 12,
        emphasis: {
          itemStyle: {
            borderColor: '#fff',
            borderWidth: 1
          }
        }
      },
      {
        // 会自动生成geo地理坐标系统
        type: 'map',
        // 设置的地图名称，服用的是第0个坐标系统
        mmap: 'world',
        data: props.mapSeriesData,
        geoIndex: 0,
        // 缩放地图
        aspectScale: 2,

        tooltip: {
          show: true
        }
      }
    ]
  }
})

</script>

<template>
  <div class="world-map-echart">
    <base-echart :option="options"/>
    <!-- 信息说明 -->
    <div class="map-info">
      <p><strong>数据说明:</strong></p>
      <ul>
        <li>区域颜色深浅代表 <strong>总用户数</strong></li>
        <li>鼠标<strong>悬浮</strong>在区域上可查看详细数值。</li>
        <li><strong>滚动</strong>鼠标进行地图缩放操作。</li>
      </ul>
    </div>
  </div>
</template>

<style scoped lang="scss">

.world-map-echart {
  width: 100%;
  flex: 1;
  min-height: 500px;
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