<template>
  <div class="vpn-charts-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>VPN 使用情况概览</span>
            </div>
          </template>
          <div class="chart-container">
            <v-chart class="chart" :option="usageOverviewOption" autoresize />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-4">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>流量统计</span>
            </div>
          </template>
          <div class="chart-container">
            <v-chart class="chart" :option="trafficOption" autoresize />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>在线时长分布</span>
            </div>
          </template>
          <div class="chart-container">
            <v-chart class="chart" :option="durationOption" autoresize />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-4">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>登录时间分布</span>
            </div>
          </template>
          <div class="chart-container">
            <v-chart class="chart" :option="loginTimeOption" autoresize />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent,
  ToolboxComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'

import {getVpnLogList} from '@/service/main/vpns/vpns.ts'

use([
  CanvasRenderer,
  PieChart,
  BarChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent,
  ToolboxComponent,
])

interface VPNLogData {
  id: number
  account: {
    id: number
    vpn_account: string
    region: {
      id: number
      region: string
      region_code: string
    }
  }
  duration_secs: number
  in_bytes: number
  out_bytes: number
  traffic_vol_bytes: number
  login_time: string
  logout_time: string | null
  virtual_ip: string
  login_terminal: string
  login_ip: string
}

export default defineComponent({
  name: 'VPNCharts',
  components: {
    VChart,
  },
  // 暴露方法给父组件
  expose: ['reloadData'],
  setup() {
    // 模拟数据 - 实际应用中应该从API获取
    const vpnLogs = ref<VPNLogData[]>([])
    const loading = ref(true)

    // 图表配置
    const usageOverviewOption = ref({})
    const trafficOption = ref({})
    const durationOption = ref({})
    const loginTimeOption = ref({})

    // 获取数据
    const fetchData = async () => {
      try {
        // 这里应该是API调用，我们使用模拟数据
        const response = await getVpnLogList({page: 1, page_size: 100})
        console.log('获取VPN日志数据成功:', response)
        vpnLogs.value = response.data.data.results


        
        // 模拟数据
        // vpnLogs.value = generateMockData()
        
        // 初始化图表
        initUsageOverviewChart()
        initTrafficChart()
        initDurationChart()
        initLoginTimeChart()
        
        loading.value = false
      } catch (error) {
        console.error('获取VPN日志数据失败:', error)
        loading.value = false
      }
    }

    // 添加 reloadData 方法
    const reloadData = (filterParams?: any) => {
      loading.value = true
      fetchData(filterParams)
    }

    // 初始化使用概览图表
    const initUsageOverviewChart = () => {
      // 按地区分组统计
      const regionMap = new Map<string, number>()
      vpnLogs.value.forEach(log => {
        // const region = log.account.region.region
        const region = log.account.region
        console.log("log", log)
        console.log("region", region)
        regionMap.set(region, (regionMap.get(region) || 0) + 1)
      })

      usageOverviewOption.value = {
        title: {
          text: 'VPN使用地区分布',
          left: 'center',
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)',
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: Array.from(regionMap.keys()),
        },
        series: [
          {
            name: '使用次数',
            type: 'pie',
            radius: ['50%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2,
            },
            label: {
              show: false,
              position: 'center',
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '18',
                fontWeight: 'bold',
              },
            },
            labelLine: {
              show: false,
            },
            data: Array.from(regionMap.entries()).map(([name, value]) => ({
              name,
              value,
            })),
          },
        ],
      }
    }

    // 初始化流量统计图表
    const initTrafficChart = () => {
      // 按账号分组统计流量
      const accountMap = new Map<string, { in: number; out: number }>()
      vpnLogs.value.forEach(log => {
        const account = log.account.vpn_account
        if (!accountMap.has(account)) {
          accountMap.set(account, { in: 0, out: 0 })
        }
        const data = accountMap.get(account)!
        data.in += log.in_bytes
        data.out += log.out_bytes
      })

      const accounts = Array.from(accountMap.keys())
      const inData = Array.from(accountMap.values()).map(v => v.in / (1024 * 1024)) // 转换为MB
      const outData = Array.from(accountMap.values()).map(v => v.out / (1024 * 1024)) // 转换为MB

      trafficOption.value = {
        title: {
          text: '账号流量统计(MB)',
          left: 'center',
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow',
          },
        },
        legend: {
          data: ['下行流量', '上行流量'],
          top: 'bottom',
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          containLabel: true,
        },
        xAxis: {
          type: 'value',
        },
        yAxis: {
          type: 'category',
          data: accounts,
        },
        series: [
          {
            name: '下行流量',
            type: 'bar',
            stack: 'total',
            label: {
              show: true,
              formatter: '{c} MB',
            },
            emphasis: {
              focus: 'series',
            },
            data: inData,
            itemStyle: {
              color: '#5470c6',
            },
          },
          {
            name: '上行流量',
            type: 'bar',
            stack: 'total',
            label: {
              show: true,
              formatter: '{c} MB',
            },
            emphasis: {
              focus: 'series',
            },
            data: outData,
            itemStyle: {
              color: '#91cc75',
            },
          },
        ],
      }
    }

    // 初始化在线时长分布图表
    const initDurationChart = () => {
      // 将时长按小时分组
      const durationGroups = [0, 0, 0, 0, 0] // 0-1h, 1-3h, 3-6h, 6-12h, 12h+
      vpnLogs.value.forEach(log => {
        const hours = log.duration_secs / 3600
        if (hours <= 1) durationGroups[0]++
        else if (hours <= 3) durationGroups[1]++
        else if (hours <= 6) durationGroups[2]++
        else if (hours <= 12) durationGroups[3]++
        else durationGroups[4]++
      })

      durationOption.value = {
        title: {
          text: '在线时长分布',
          left: 'center',
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)',
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: ['0-1小时', '1-3小时', '3-6小时', '6-12小时', '12小时以上'],
        },
        series: [
          {
            name: '会话数量',
            type: 'pie',
            radius: '70%',
            center: ['50%', '60%'],
            data: [
              { value: durationGroups[0], name: '0-1小时' },
              { value: durationGroups[1], name: '1-3小时' },
              { value: durationGroups[2], name: '3-6小时' },
              { value: durationGroups[3], name: '6-12小时' },
              { value: durationGroups[4], name: '12小时以上' },
            ],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)',
              },
            },
          },
        ],
      }
    }

    // 初始化登录时间分布图表
    const initLoginTimeChart = () => {
      // 按小时统计登录次数
      const hourCounts = Array(24).fill(0)
      vpnLogs.value.forEach(log => {
        const hour = new Date(log.login_time).getHours()
        hourCounts[hour]++
      })

      loginTimeOption.value = {
        title: {
          text: '按小时登录次数分布',
          left: 'center',
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow',
          },
        },
        xAxis: {
          type: 'category',
          data: Array.from({ length: 24 }, (_, i) => `${i}:00`),
        },
        yAxis: {
          type: 'value',
          name: '登录次数',
        },
        series: [
          {
            name: '登录次数',
            type: 'line',
            smooth: true,
            data: hourCounts,
            itemStyle: {
              color: '#ee6666',
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  {
                    offset: 0,
                    color: 'rgba(238, 102, 102, 0.5)',
                  },
                  {
                    offset: 1,
                    color: 'rgba(238, 102, 102, 0.1)',
                  },
                ],
              },
            },
          },
        ],
      }
    }

    // 生成模拟数据
    const generateMockData = (): VPNLogData[] => {
      const regions = [
        { id: 1, region: '日本JP', region_code: 'JP' },
        { id: 2, region: '新加坡SG', region_code: 'SG' },
        { id: 3, region: '台湾TW', region_code: 'TW' },
        { id: 4, region: '韩国KR', region_code: 'KR' },
        { id: 5, region: '美国USA', region_code: 'US' },
      ]
      
      const accounts = [
        { id: 1, vpn_account: 'user1', region: regions[0] },
        { id: 2, vpn_account: 'user2', region: regions[1] },
        { id: 3, vpn_account: 'user3', region: regions[2] },
        { id: 4, vpn_account: 'user4', region: regions[3] },
        { id: 5, vpn_account: 'user5', region: regions[4] },
      ]
      
      const logs: VPNLogData[] = []
      const now = new Date()
      
      // 生成过去30天的数据
      for (let i = 0; i < 100; i++) {
        const daysAgo = Math.floor(Math.random() * 30)
        const loginDate = new Date(now)
        loginDate.setDate(now.getDate() - daysAgo)
        
        const loginHour = Math.floor(Math.random() * 24)
        loginDate.setHours(loginHour)
        
        const durationHours = Math.random() * 24
        const durationSecs = Math.floor(durationHours * 3600)
        
        const logoutDate = new Date(loginDate)
        logoutDate.setSeconds(logoutDate.getSeconds() + durationSecs)
        
        const inBytes = Math.floor(Math.random() * 100 * 1024 * 1024, 2) // 0-100MB
        const outBytes = Math.floor(Math.random() * 50 * 1024 * 1024, 2) // 0-50MB
        
        logs.push({
          id: i + 1,
          account: accounts[Math.floor(Math.random() * accounts.length, 2)],
          duration_secs: durationSecs,
          in_bytes: inBytes,
          out_bytes: outBytes,
          traffic_vol_bytes: inBytes + outBytes,
          login_time: loginDate.toISOString(),
          logout_time: Math.random() > 0.2 ? logoutDate.toISOString() : null, // 20%的会话可能还在线
          virtual_ip: `10.0.0.${Math.floor(Math.random() * 255)}`,
          login_terminal: ['Windows', 'Mac', 'iPhone', 'Android'][Math.floor(Math.random() * 4)],
          login_ip: `192.168.1.${Math.floor(Math.random() * 255)}`,
        })
      }
      
      return logs
    }

    onMounted(() => {
      fetchData()
    })

    return {
      loading,
      usageOverviewOption,
      trafficOption,
      durationOption,
      loginTimeOption,
      reloadData,
    }
  },
})
</script>

<style scoped>
.vpn-charts-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  position: relative;
  width: 100%;
  height: 400px;
}

.chart {
  width: 100%;
  height: 100%;
}

.mt-4 {
  margin-top: 20px;
}
</style>