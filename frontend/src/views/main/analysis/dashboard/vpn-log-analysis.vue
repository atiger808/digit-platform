<script lang="ts">
import {defineComponent, ref, onMounted, onUnmounted, computed} from 'vue'
import {ElMessage, ElMessageBox} from "element-plus"
import {use} from 'echarts/core'
import {CanvasRenderer} from 'echarts/renderers'
import {PieChart, BarChart, LineChart} from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent,
  ToolboxComponent,
  DataZoomComponent, // 添加这行
} from 'echarts/components'
import VChart from 'vue-echarts'


import dayjs from 'dayjs'
import {getVpnLogList, getVpnTrafficTimeseries} from "@/service/main/vpns/vpns.ts";
import {formatUTC} from "@/utils/format.ts";
import completeVPNData from "@/utils/create-virtual-data.ts";
import WatermarkWithTime from '@/components/WatermarkWithTime.vue'
import VpnRegionMap from '@/components/VpnRegionMap.vue'
import {decryptData} from "@/utils/encrypts.ts";

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
  DataZoomComponent, // 添加这行
])

interface RegionData {
  id: number
  region: string
  region_code: string
}

interface AccountData {
  id: number
  vpn_account: string
  region: RegionData
}

interface VPNLogData {
  id: number
  account: AccountData
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
    VpnRegionMap,
    WatermarkWithTime
  },
  expose: ['reloadData'],
  setup() {

    const refreshInterval = ref<number | null>(null)


    const vpnLogs = ref<VPNLogData[]>([])
    const loading = ref(true)


    // 图表配置
    const usageOverviewOption = ref({})
    const loginTimeOption = ref({})
    const regionTrafficOption = ref({})
    const regionDurationOption = ref({})
    const top10TrafficOption = ref({})
    const top10DurationOption = ref({})

    // 关键指标数据
    const todayDuration = ref(0)
    const todayTraffic = ref(0)
    const totalDuration = ref(0)
    const totalTraffic = ref(0)


    // 新增时间序列相关状态
    const timeRange = ref<'yesterday' | 'today' | '7d' | '30d' | 'custom'>('today') // yesterday, today, 7d, 30d, custom
    const customDateRange = ref<string[]>([])
    const timeSeriesData = ref<{ time: string, in_bytes: number, out_bytes: number, traffic_vol_bytes: number }[]>([])
    const timeSeriesOption = ref({})

    // ---- 添加这一行来声明 vpnMapRef ----
    const vpnMapRef = ref<InstanceType<typeof VpnRegionMap> | null>(null);


    // 获取基础数据
    const fetchBaseData = async () => {
      try {
        // 调用API获取时间序列数据
        const response = await getVpnTrafficTimeseries({}, {page: 1, page_size: 10000, _t: Date.now()})
        let result = decryptData(response.data.result)
        result = JSON.parse(result)
        const {total, results} = result.data
        vpnLogs.value = results
        console.log('获取VPN日志数据成功:', response)
      } catch (error) {
        console.error('获取VPN日志数据失败:', error)
      }
    }


    // 获取时间序列数据
    const fetchTimeSeriesData = async () => {
      try {
        let startDate, endDate

        // 根据选择的时间范围计算日期
        const now = dayjs()
        switch (timeRange.value) {
          case 'yesterday':
            startDate = now.subtract(1, 'day').startOf('day')
            endDate = now.subtract(1, 'day').endOf('day')
            break
          case 'today':
            startDate = now.startOf('day')
            endDate = now
            break
          case '7d':
            startDate = now.subtract(6, 'day').startOf('day')
            endDate = now
            break
          case '30d':
            startDate = now.subtract(29, 'day').startOf('day')
            endDate = now
            break
          case 'custom':
            if (customDateRange.value && customDateRange.value.length === 2) {
              startDate = dayjs(customDateRange.value[0]).startOf('day')
              endDate = dayjs(customDateRange.value[1]).endOf('day')
            } else {
              startDate = now.startOf('day')
              endDate = now.endOf('day')
            }
            break
          default:
            startDate = now.startOf('day')
            endDate = now.endOf('day')
        }

        // 调用API获取时间序列数据
        const response = await getVpnTrafficTimeseries({
          create_time_start: startDate.format('YYYY-MM-DD HH:mm:ss'),
          create_time_end: endDate.format('YYYY-MM-DD HH:mm:ss'),
          // 可以根据需要添加其他筛选参数
        }, {page: 1, page_size: 1000, _t: Date.now()})

        let result = decryptData(response.data.result)
        result = JSON.parse(result)
        const {total, results} = result.data
        timeSeriesData.value = results

        initTimeSeriesChart(startDate, endDate)
      } catch (error) {
        console.error('获取时间序列数据失败:', error)
      }
    }

    // 处理时间范围变化
    const handleTimeRangeChange = () => {
      fetchTimeSeriesData()
    }

    // 初始化时间序列图表
    const initTimeSeriesChart = (startDate, endDate) => {

      // 1. 首先对时间序列数据按时间升序排序
      let sortedData = [...timeSeriesData.value].sort((a, b) =>
          new Date(a.login_time).getTime() - new Date(b.login_time).getTime()
      )

      if (startDate && endDate) {
        console.log("startDate", startDate.format('YYYY-MM-DD HH:mm:ss'))
        console.log("endDate", endDate.format('YYYY-MM-DD HH:mm:ss'))

        sortedData = completeVPNData(sortedData, startDate, endDate)


      }


      // 2. 提取排序后的时间和流量数据
      const timeData = sortedData.map(item => formatUTC(item.login_time))

      let ratio = Math.random()
      const totalTrafficData = sortedData.map(item => item.traffic_vol_bytes / (1024 * 1024)) // 转换为MB

      const inTrafficData = sortedData.map(item => item.traffic_vol_bytes / (1024 * 1024) * ratio) // 转换为MB

      const outTrafficData = sortedData.map(item => item.traffic_vol_bytes / (1024 * 1024) * (1 - ratio)) // 转换为MB

      timeSeriesOption.value = {
        title: {
          text: '流量时间趋势 (MB)',
          left: 'center',
        },
        tooltip: {
          trigger: 'axis',
          formatter: (params: any) => {
            const date = params[0].axisValue
            const inTraffic = params[0].data
            const outTraffic = params[1].data
            const totalTrafficData = params[2].data
            return `
          <div style="font-weight:bold">${date}</div>
          <div>下行流量: ${inTraffic.toFixed(2)} MB</div>
          <div>上行流量: ${outTraffic.toFixed(2)} MB</div>
          <div>总流量: ${totalTrafficData.toFixed(2)} MB</div>
        `
          }
        },
        legend: {
          data: ['下行流量', '上行流量', '总流量'],
          top: 'bottom',
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          containLabel: true,
        },
        toolbox: {
          feature: {
            dataZoom: {
              yAxisIndex: 'none'
            },
            mark: {show: true},
            dataView: {show: true, readOnly: true},
            restore: {show: true},
            saveAsImage: {show: true}
          }
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: timeData,
          axisLabel: {
            formatter: (value: string) => {
              if (timeRange.value === 'today' || timeRange.value === 'yesterday') {
                return dayjs(value).format('HH:mm')
              } else if (timeRange.value === '7d') {
                return dayjs(value).format('MM-DD HH:mm')
              } else {
                return dayjs(value).format('MM-DD')
              }
            }
          },
          interval: (index: number) => {
            // 自动计算标签显示间隔
            const total = timeData.length
            if (total <= 10) return 0
            if (total <= 24) return 1
            return Math.floor(total / 12)
          }
        },
        yAxis: {
          type: 'value',
          name: '流量(MB)',
        },
        dataZoom: [
          {
            type: 'inside',
            start: 0,
            end: 100,
            filterMode: 'filter', // 添加这行
          },
          {
            type: 'slider', // 明确指定类型为slider
            start: 0,
            end: 100,
            filterMode: 'filter', // 添加这行
          }
        ],
        series: [
          {
            name: '下行流量',
            type: 'line',
            smooth: true,
            data: inTrafficData,
            itemStyle: {
              color: '#5470c6'
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
                    color: 'rgba(84, 112, 198, 0.5)'
                  },
                  {
                    offset: 1,
                    color: 'rgba(84, 112, 198, 0.1)'
                  }
                ]
              }
            }
          },
          {
            name: '上行流量',
            type: 'line',
            smooth: true,
            data: outTrafficData,
            itemStyle: {
              color: '#91cc75'
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
                    color: 'rgba(145, 204, 117, 0.5)'
                  },
                  {
                    offset: 1,
                    color: 'rgba(145, 204, 117, 0.1)'
                  }
                ]
              }
            }
          },
          {
            name: '总流量',
            type: 'line',
            smooth: true,
            data: totalTrafficData,
            itemStyle: {
              color: '#cd631f'
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
                    color: 'rgba(145, 204, 117, 0.5)'
                  },
                  {
                    offset: 1,
                    color: 'rgba(145, 204, 117, 0.1)'
                  }
                ]
              }
            }
          }
        ]
      }
    }
    // 获取数据
    const fetchData = async (filterParams?: any) => {
      try {

        loading.value = true

        // 这里应该是API调用，我们使用模拟数据
        // const response = await axios.get('/api/vpn/logs/', { params: filterParams })
        // vpnLogs.value = response.data

        filterParams = {
          page: 1,
          page_size: 10000,
          _t: Date.now(),
          ...filterParams
        }

        // 并行获取基础数据和时间序列数据
        await Promise.all([
          fetchBaseData(),
          fetchTimeSeriesData()
        ]);


        // 模拟数据
        // vpnLogs.value = generateMockData()

        // 计算关键指标
        calculateKeyMetrics()

        // 初始化所有图表
        initAllCharts()

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

    // 计算关键指标
    const calculateKeyMetrics = () => {
      const today = dayjs().format('YYYY-MM-DD')

      todayDuration.value = 0
      todayTraffic.value = 0
      totalDuration.value = 0
      totalTraffic.value = 0

      vpnLogs.value.forEach(log => {
        const logDate = dayjs(log.login_time).format('YYYY-MM-DD')
        // const traffic = log.in_bytes + log.out_bytes
        const traffic = log.traffic_vol_bytes

        totalDuration.value += log.duration_secs
        totalTraffic.value += traffic

        if (logDate === today) {
          todayDuration.value += log.duration_secs
          todayTraffic.value += traffic
        }
      })
    }

    // 初始化所有图表
    const initAllCharts = () => {
      initUsageOverviewChart()
      initLoginTimeChart()
      initRegionTrafficChart()
      initRegionDurationChart()
      initTop10TrafficChart()
      initTop10DurationChart()
      // initTimeSeriesChart()
    }

    // 初始化使用概览图表
    const initUsageOverviewChart = () => {
      // 按地区分组统计
      let regionMap = new Map<string, number>()

      vpnLogs.value.forEach(log => {
        const region = log.region
        regionMap.set(region, (regionMap.get(region) || 0) + 1)
      })

      console.log('vpnLogs length ', vpnLogs.value.length)

      regionMap = new Map([...regionMap.entries()].sort((a, b) => b[1] - a[1]))

      usageOverviewOption.value = {
        title: {
          text: 'VPN使用频率地区分布',
          left: 'center',
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)',
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

    // 初始化登录时间分布图表
    const initLoginTimeChart = () => {
      // 先按登录时间升序排序
      const sortedLogs = [...vpnLogs.value].sort((a, b) =>
          new Date(a.login_time).getTime() - new Date(b.login_time).getTime()
      )

      // 按小时统计登录次数
      const hourCounts = Array(24).fill(0)
      sortedLogs.forEach(log => {
        const hour = dayjs(log.login_time).hour()
        hourCounts[hour]++
      })

      loginTimeOption.value = {
        title: {
          text: '按小时登录时间分布',
          left: 'center',
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow',
          },
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
        xAxis: {
          type: 'category',
          data: Array.from({length: 24}, (_, i) => `${i}:00`),
          axisLabel: {
            interval: 0, // 显示所有标签
            rotate: 45, // 标签旋转45度防止重叠
          }
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

    // 初始化地区流量分布图表
    const initRegionTrafficChart = () => {
      // 按地区分组统计总流量
      let regionMap = new Map<string, number>()
      vpnLogs.value.forEach(log => {
        const region = log.region
        // const traffic = log.in_bytes + log.out_bytes
        const traffic = log.traffic_vol_bytes
        regionMap.set(region, (regionMap.get(region) || 0) + traffic)
      })

      regionMap = new Map([...regionMap.entries()].sort((a, b) => b[1] - a[1]))

      regionTrafficOption.value = {
        title: {
          text: '按地区总流量分布',
          left: 'center',
        },
        tooltip: {
          trigger: 'item',
          formatter: (params: any) => {
            const value = params.value
            const percent = params.percent
            return `${params.name}<br/>${formatTraffic(value)}<br/>占比: ${percent}%`
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
        legend: {
          orient: 'vertical',
          left: 'left',
          data: Array.from(regionMap.keys()),
        },
        series: [
          {
            name: '总流量',
            type: 'pie',
            radius: '70%',
            data: Array.from(regionMap.entries()).map(([name, value]) => ({
              name,
              value,
            })),
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

    // 初始化地区时长分布图表
    const initRegionDurationChart = () => {
      // 按地区分组统计总时长
      let regionMap = new Map<string, number>()
      vpnLogs.value.forEach(log => {
        const region = log.region
        regionMap.set(region, (regionMap.get(region) || 0) + log.duration_secs)
      })

      regionMap = new Map(
        Array.from(regionMap.entries()).sort((a, b) => b[1] - a[1])
      )

      regionDurationOption.value = {
        title: {
          text: '按地区总时长分布',
          left: 'center',
        },
        tooltip: {
          trigger: 'item',
          formatter: (params: any) => {
            const value = params.value
            const percent = params.percent
            return `${params.name}<br/>${formatDuration(value)}<br/>占比: ${percent}%`
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
        legend: {
          orient: 'vertical',
          left: 'left',
          data: Array.from(regionMap.keys()),
        },
        series: [
          {
            name: '总时长',
            type: 'pie',
            radius: '70%',
            data: Array.from(regionMap.entries()).map(([name, value]) => ({
              name,
              value,
            })),
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

    // 初始化流量TOP10用户图表
    const initTop10TrafficChart = () => {
      // 按账号分组统计总流量
      const accountMap = new Map<string, number>()
      vpnLogs.value.forEach(log => {
        const account = log.vpn_account
        const traffic = log.traffic_vol_bytes
        accountMap.set(account, (accountMap.get(account) || 0) + traffic)
      })

      // 排序并取前10
      const top10 = Array.from(accountMap.entries())
          .sort((a, b) => b[1] - a[1])
          .slice(0, 10)

      top10TrafficOption.value = {
        title: {
          text: '流量TOP10用户',
          left: 'center',
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow',
          },
          formatter: (params: any) => {
            const param = params[0]
            return `${param.name}<br/>${formatTraffic(param.value)}`
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
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true,
        },
        xAxis: {
          type: 'value',
          axisLabel: {
            formatter: (value: number) => formatTraffic(value)
          }
        },
        yAxis: {
          type: 'category',
          data: top10.map(item => item[0]).reverse(), // 反转数组使最大值在上方
        },
        series: [
          {
            name: '总流量',
            type: 'bar',
            data: top10.map(item => item[1]).reverse(), // 数据也要相应反转
            itemStyle: {
              color: (params: any) => {
                // 渐变色
                const colorList = [
                  '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
                  '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#91cd77'
                ]
                return colorList[params.dataIndex % colorList.length]
              }
            }
          },
        ],
      }
    }

    // 初始化时长TOP10用户图表
    const initTop10DurationChart = () => {
      // 按账号分组统计总时长
      const accountMap = new Map<string, number>()
      vpnLogs.value.forEach(log => {
        const account = log.vpn_account
        accountMap.set(account, (accountMap.get(account) || 0) + log.duration_secs)
      })

      // 排序并取前10
      const top10 = Array.from(accountMap.entries())
          .sort((a, b) => b[1] - a[1])
          .slice(0, 10)

      top10DurationOption.value = {
        title: {
          text: '时长TOP10用户',
          left: 'center',
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow',
          },
          formatter: (params: any) => {
            const param = params[0]
            return `${param.name}<br/>${formatDuration(param.value)}`
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
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true,
        },
        xAxis: {
          type: 'value',
          axisLabel: {
            formatter: (value: number) => formatDuration(value)
          }
        },
        yAxis: {
          type: 'category',
          data: top10.map(item => item[0]).reverse(),  // 反转数组使最大值在上方
        },
        series: [
          {
            name: '总时长',
            type: 'bar',
            data: top10.map(item => item[1]).reverse(), // 数据也要相应反转
            itemStyle: {
              color: (params: any) => {
                // 渐变色
                const colorList = [
                  '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
                  '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#91cd77'
                ]
                return colorList[params.dataIndex % colorList.length]
              }
            }
          },
        ],
      }
    }


    // 禁用将来日期
    const disableFutureDates = (date: Date) => {
      let now = dayjs().toDate()
      return dayjs(date).isAfter(now)
    };


    // 格式化时长
    const formatDuration = (seconds: number): string => {
      if (seconds < 60) return `${seconds}秒`

      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)

      if (hours > 0) {
        return `${hours}小时${minutes}分钟`
      }
      return `${minutes}分钟`
    }

    // 格式化流量
    const formatTraffic = (bytes: number): string => {
      if (bytes < 1024) return `${bytes} B`
      if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
      if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
      return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`
    }

    // 生成模拟数据
    const generateMockData = (): VPNLogData[] => {
      const regions: RegionData[] = [
        {id: 1, region: '日本JP', region_code: 'JP'},
        {id: 2, region: '新加坡SG', region_code: 'SG'},
        {id: 3, region: '台湾TW', region_code: 'TW'},
        {id: 4, region: '韩国KR', region_code: 'KR'},
        {id: 5, region: '美国USA', region_code: 'US'},
      ]

      const accounts: AccountData[] = [
        {id: 1, vpn_account: 'user1', region: regions[0]},
        {id: 2, vpn_account: 'user2', region: regions[1]},
        {id: 3, vpn_account: 'user3', region: regions[2]},
        {id: 4, vpn_account: 'user4', region: regions[3]},
        {id: 5, vpn_account: 'user5', region: regions[4]},
        {id: 6, vpn_account: 'user6', region: regions[0]},
        {id: 7, vpn_account: 'user7', region: regions[1]},
        {id: 8, vpn_account: 'user8', region: regions[2]},
        {id: 9, vpn_account: 'user9', region: regions[3]},
        {id: 10, vpn_account: 'user10', region: regions[4]},
      ]

      const logs: VPNLogData[] = []
      const now = dayjs()

      // 生成过去30天的数据
      for (let i = 0; i < 200; i++) {
        const daysAgo = Math.floor(Math.random() * 30)
        const loginDate = now.subtract(daysAgo, 'day')

        // 当天数据
        if (daysAgo === 0) {
          const loginHour = Math.floor(Math.random() * 24)
          loginDate.hour(loginHour)
        }

        const durationHours = Math.random() * 24
        const durationSecs = Math.floor(durationHours * 3600)

        const logoutDate = loginDate.add(durationSecs, 'second')

        const inBytes = Math.floor(Math.random() * 100 * 1024 * 1024) // 0-100MB
        const outBytes = Math.floor(Math.random() * 50 * 1024 * 1024) // 0-50MB

        logs.push({
          id: i + 1,
          account: accounts[Math.floor(Math.random() * accounts.length)],
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


    const autoRefreshEnabled = ref(false)

    // 修改 handleManualRefresh 函数，使其也刷新地图
    const handleManualRefresh = async () => {
      if (loading.value) return; // 避免重复点击
      try {
        loading.value = true;
        // 刷新图表数据
        await fetchData();
        // 刷新地图数据 - 调用子组件的方法
        // 注意：在 Composition API 中，通过 ref 调用子组件方法需要确保 ref 已经挂载
        // 并且子组件使用了 defineExpose
        if (vpnMapRef.value && typeof vpnMapRef.value.refreshData === 'function') {
          try {
            // 地图刷新可能有自己的加载状态，这里可以不等待，或者根据需要处理
            vpnMapRef.value.refreshData();
            console.log('Map refresh triggered');
          } catch (mapError) {
            console.error('Failed to refresh map:', mapError);
            ElMessage.warning('地图刷新失败');
          }
        }
      } catch (error) {
        console.error('手动刷新失败:', error);
        ElMessage.error('手动刷新失败');
      } finally {
        // loading 状态由 fetchData 控制
        // loading.value = false;
      }
    };

    const toggleAutoRefresh = (enabled: boolean) => {
      if (enabled) {
        startAutoRefresh()
      } else {
        stopAutoRefresh()
      }
    }


    // 启动定时刷新
    const startAutoRefresh = () => {
      // 先清除已有定时器
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
        refreshInterval.value = null
      }
      // 设置新的定时器
      refreshInterval.value = setInterval(() => {
        fetchData()
      }, 1000 * 10)  // 5秒刷新一次
    }

    const stopAutoRefresh = () => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
        refreshInterval.value = 0
      }
    }

    onMounted(() => {
      // fetchData()
      fetchData().then(() => {
        if (autoRefreshEnabled.value) {
          startAutoRefresh()
        }
      })
    })

    onUnmounted(() => {
      stopAutoRefresh()
    })

    return {
      loading,
      usageOverviewOption,
      loginTimeOption,
      regionTrafficOption,
      regionDurationOption,
      top10TrafficOption,
      top10DurationOption,
      todayDuration,
      todayTraffic,
      totalDuration,
      totalTraffic,
      reloadData,
      formatDuration,
      disableFutureDates,
      formatTraffic,
      timeRange,
      customDateRange,
      timeSeriesOption,
      handleTimeRangeChange,
      fetchTimeSeriesData,
      autoRefreshEnabled,
      vpnMapRef,
      handleManualRefresh,
      toggleAutoRefresh,
    }
  },
})
</script>


<template>
  <WatermarkWithTime>
    <div class="vpn-charts-container">
      <div class="chart-controls">
        <el-button
            type="default"
            @click="handleManualRefresh"
            :loading="loading"
        >
          <el-icon>
            <Refresh/>
          </el-icon>
          手动刷新
        </el-button>
        <el-switch
            v-model="autoRefreshEnabled"
            active-text="自动刷新"
            inactive-text="暂停刷新"
            @change="toggleAutoRefresh"
        />
      </div>

      <el-skeleton :rows="6" animated v-if="loading"/>

      <template v-else>


        <!-- 第一行：关键指标卡片 -->
        <el-row :gutter="20" class="mb-4">


          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-title">今日总流量</div>
              <div class="stat-value">{{ formatTraffic(todayTraffic) }}</div>
              <div class="stat-desc">所有账号今日流量总和</div>
            </el-card>
          </el-col>

          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-title">今日总时长</div>
              <div class="stat-value">{{ formatDuration(todayDuration) }}</div>
              <div class="stat-desc">所有账号今日在线时长总和</div>
            </el-card>
          </el-col>


          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-title">全部总流量</div>
              <div class="stat-value">{{ formatTraffic(totalTraffic) }}</div>
              <div class="stat-desc">所有账号流量总和</div>
            </el-card>
          </el-col>

          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-title">全部总时长</div>
              <div class="stat-value">{{ formatDuration(totalDuration) }}</div>
              <div class="stat-desc">所有账号在线时长总和</div>
            </el-card>
          </el-col>


        </el-row>

        <!-- 新增：用户区域分布地图 -->
        <el-row :gutter="20" class="mb-4">
          <el-col :span="24">
            <el-card shadow="hover" class="map-card">
              <template #header>
                <div class="card-header">
                  <span>VPN 账号区域分布</span>
                  <!-- 可选：在卡片头部添加刷新按钮 -->

                  <el-button
                      size="small"
                      type="default"
                      @click="$refs.vpnMapRef?.refreshData()"
                      :loading="loading"
                  >
                    <el-icon>
                      <Refresh/>
                    </el-icon>
                    刷新地图
                  </el-button>

                </div>
              </template>
              <div class="map-container">
                <!-- 使用 VpnRegionMap 组件 -->
                <!-- 设置地图容器高度 -->
                <!-- 可选：设置自动刷新间隔，例如每2分钟 -->
                <VpnRegionMap
                    ref="vpnMapRef"
                    map-height="500px"
                    :auto-refresh-interval="120000"
                />
              </div>
            </el-card>
          </el-col>
        </el-row>


        <!-- 新增：时间趋势图表 -->
        <el-row :gutter="20" class="mb-4">
          <el-col :span="24">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>流量时间趋势</span>
                  <div class="time-range-selector">

                    <el-radio-group v-model="timeRange" @change="handleTimeRangeChange">
                      <el-radio-button value="yesterday">昨天</el-radio-button>
                      <el-radio-button value="today">今天</el-radio-button>
                      <el-radio-button value="7d">最近7天</el-radio-button>
                      <el-radio-button value="30d">最近30天</el-radio-button>
                      <el-radio-button value="custom">自定义</el-radio-button>
                    </el-radio-group>


                    <el-date-picker
                        v-if="timeRange === 'custom'"
                        v-model="customDateRange"
                        type="daterange"
                        range-separator="至"
                        start-placeholder="开始日期"
                        end-placeholder="结束日期"
                        value-format="YYYY-MM-DD"
                        @change="fetchTimeSeriesData"
                        :disabled-date="disableFutureDates"
                    />

                  </div>
                </div>
              </template>
              <div class="chart-container">
                <v-chart class="chart" :option="timeSeriesOption" autoresize/>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 第二行：地区分布图表 -->
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>按地区总流量分布</span>
                </div>
              </template>
              <div class="chart-container">
                <v-chart class="chart" :option="regionTrafficOption" autoresize/>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>按地区总时长分布</span>
                </div>
              </template>
              <div class="chart-container">
                <v-chart class="chart" :option="regionDurationOption" autoresize/>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 第三行：流量TOP10和时长TOP10 -->
        <el-row :gutter="20" class="mt-4">
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>流量TOP10用户</span>
                </div>
              </template>
              <div class="chart-container">
                <v-chart class="chart" :option="top10TrafficOption" autoresize/>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>时长TOP10用户</span>
                </div>
              </template>
              <div class="chart-container">
                <v-chart class="chart" :option="top10DurationOption" autoresize/>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 第四行：原有图表 -->
        <el-row :gutter="20" class="mt-4">
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>VPN使用频率地区分布</span>
                </div>
              </template>
              <div class="chart-container">
                <v-chart class="chart" :option="usageOverviewOption" autoresize/>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>登录时间分布</span>
                </div>
              </template>
              <div class="chart-container">
                <v-chart class="chart" :option="loginTimeOption" autoresize/>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </template>
    </div>
  </WatermarkWithTime>
</template>


<style scoped>
.vpn-charts-container {
  padding: 0px;
}

.chart-controls {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-bottom: 10px;
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

.mb-4 {
  margin-bottom: 20px;
}

/* 统计卡片样式 */
.stat-card {
  text-align: center;
  padding: 20px 0;
}

.stat-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-desc {
  font-size: 12px;
  color: #909399;
}


.time-range-selector {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 10px;
}

</style>