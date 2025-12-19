<script setup lang="ts">
import CountCard from "./c-cpns/count-card/count-card.vue";
import ChartCard from "./c-cpns/chart-card/chart-card.vue";
import {
  PieEchart,
  LineEchart,
  RoseEchart,
  BarEchart,
  MapEchart,
  WorldMapEchart
} from "@/components/page-echarts";


import WatermarkWithTime from '@/components/WatermarkWithTime.vue'
import useAnalysisStore from "@/store/main/analysis/analysis.ts";
import {computed, ref} from 'vue'
import {storeToRefs} from "pinia";
import VpnRegionMap from "@/components/VpnRegionMap.vue";


// 1.发起数据的请求
const analysisStore = useAnalysisStore()
analysisStore.fetchAnalysisDataAction()


// 2.从store获取数据
const {
  amountList,
  goodsCategoryCount,
  goodsCategorySale,
  goodsCategoryFavor,
  goodsAddressSale,
  vpnRegionSummary,
  fileSummary
} = storeToRefs(analysisStore)


// 3.获取数据
const showUserFileCount = computed(() => {
  return fileSummary.value.map(item => {
    return {
      name: item.username,
      nickname: item.real_name,
      value: item.file_count
    }
  })
})

const showUserDurationCount = computed(() => {
  return fileSummary.value.map(item => {
    return {
      name: item.username,
      nickname: item.real_name,
      value: item.total_duration
    }
  })
})

const showUserSizeCount = computed(() => {
  return fileSummary.value.map(item => {
    return {
      name: item.username,
      nickname: item.real_name,
      value: item.total_size
    }
  })
})



// 3.获取数据
const showGoodsCategoryCount = computed(() => {
  return goodsCategoryCount.value.map(item => {
    return {
      name: item.name,
      value: item.goodsCount
    }
  })
})


const showGoodsCategorySale = computed(() => {
  const labels = goodsCategorySale.value.map(item => item.name)
  const values = goodsCategorySale.value.map(item => item.saleCount)
  return {labels, values}
})

const showGoodsCategoryFavor = computed(() => {
  const labels = goodsCategoryFavor.value.map(item => item.name)
  const values = goodsCategoryFavor.value.map(item => item.favorCount)
  return {labels, values}
})

const showGoodsAddressSale = computed(() => {
  return goodsAddressSale.value.map(item => {
    return {
      name: item.name,
      value: item.saleCount
    }
  })
})


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

const showVpnRegionSummary = computed(() => {
  return vpnRegionSummary.value.map(item => {
    const coords = regionCoords[item.region_english]
    return {
      name: item.region_english,
      zhName: item.name,
      value: [...coords, item.value[0]]
    }
  })
})


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


const showMapSeriesData = computed(() => {
  return vpnRegionSummary.value.map(item => {
    // 使用映射查找 world.json 中的正确名称
    const geoJsonName = geoJsonNameMap[item.region_english] || item.region_english;
    return {
      name: geoJsonName, // 使用 world.json 中的名称
      zhName: item.name, // 使用 world.json 中的名称
      value: item.value // [总用户数, 在线用户数]
    }
  })
})


// 刷新数据
const loading = ref(false)
const refreshData = async (target: string) => {
  console.log('refreshData')
  loading.value = true
  if (target === 'vpn') {
    await analysisStore.fetchVPNRegionSummary()
  } else if (target === 'CategoryCount') {
    await analysisStore.fetchGoodsCategoryCount()
  } else if (target === 'fileSummary') {
    await analysisStore.fetchFileSummary()
  }
  loading.value = false
}


</script>

<template>
  <WatermarkWithTime>
    <div class="statistics">

      <!-- 1.顶部数据展示 数字滚动 -->
      <el-row :gutter="10">

        <template v-for="item in amountList" :key="item.amount">
          <el-col :span="6" :xs="24" :sm="12" :md="8" :lg="6">
            <count-card v-bind="item"/>
          </el-col>
        </template>

      </el-row>


      <!-- 2. 中间的echart图表 -->
      <el-row :gutter="10">
        <el-col :span="7">
          <chart-card title="用户素材数">
            <!-- 使用具名插槽添加额外内容 -->
<!--            <template #header-extra>-->
<!--              <el-button size="small">导出数据</el-button>-->
<!--            </template>-->

            <template #header-extra>
              <el-button
                  size="small"
                  type="default"
                  @click="refreshData('fileSummary')"
                  :loading="loading"
              >
                <el-icon>
                  <Refresh/>
                </el-icon>
                刷新
              </el-button>
            </template>

            <!-- 饼图组件 -->
            <pie-echart :pie-data="showUserFileCount"/>


            <!-- 底部内容 -->
            <!--          <template #footer>-->
            <!--            <div>-->
            <!--              <div class="footer-note">数据更新于: {{ updateTime }}</div>-->
            <!--            </div>-->
            <!--          </template>-->

          </chart-card>
        </el-col>

        <el-col :span="10">
          <chart-card title="用户素材时长">
            <map-echart :map-data="showUserDurationCount"/>
          </chart-card>
        </el-col>

        <el-col :span="7">
          <chart-card title="用户素材大小">
            <rose-echart :rose-data="showUserSizeCount"/>
          </chart-card>
        </el-col>

      </el-row>

      <!-- 3. 底部的echart图表 -->
      <el-row :gutter="10">
        <el-col :span="12">
          <chart-card title="用户素材数">
            <line-echart v-bind="showUserFileCount"
            />

          </chart-card>
        </el-col>
        <el-col :span="12">
          <chart-card title="用户素材时长">
            <bar-echart v-bind="showUserDurationCount"
            />
          </chart-card>
        </el-col>
      </el-row>

      <!-- 4. 底部的echart图表 -->
      <el-row :gutter="10" class="mb-4">
        <el-col :span="24">


          <chart-card title="VPN账号区域分布">
            <template #header-extra>
              <el-button
                  size="small"
                  type="default"
                  @click="refreshData('vpn')"
                  :loading="loading"
              >
                <el-icon>
                  <Refresh/>
                </el-icon>
                刷新地图
              </el-button>
            </template>
            <world-map-echart :scatter-map-data="showVpnRegionSummary" :map-series-data="showMapSeriesData"/>
          </chart-card>


        </el-col>
      </el-row>

    </div>
  </WatermarkWithTime>
</template>

<style scoped lang="scss">

.statistics {
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

</style>