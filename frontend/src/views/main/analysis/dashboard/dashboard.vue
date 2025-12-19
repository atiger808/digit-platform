<template>
  <WatermarkWithTime>

    <div class="dashboard">
      <!-- 刷新按钮 -->
      <div style="text-align: right; margin-bottom: 6px;">
        <el-button
            :icon="Refresh"
            :loading="loading"
            @click="handleRefresh"
            circle
        />
      </div>

      <!-- 顶部卡片（保持不变） -->
      <el-row :gutter="20" class="mb-4">
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="stat-item">
              <div class="label">今日新增素材</div>
              <div class="value">{{ summary.today_file_count }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="stat-item">
              <div class="label">今日新增时长</div>
              <div class="value">{{ formatDuration(summary.today_duration) }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="stat-item">
              <div class="label">全部素材数量</div>
              <div class="value">{{ summary.total_file_count }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="stat-item">
              <div class="label">全部总时长</div>
              <div class="value">{{ formatDuration(summary.total_duration) }}</div>
            </div>
          </el-card>
        </el-col>
      </el-row>


      <!-- 新增：用户素材创作趋势 -->
      <el-row :gutter="20" class="mb-4">
        <el-col :span="24">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>素材创作趋势</span>
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


      <!-- 柱状图区域 数量TOP10, 时长TOP10, 大小TOP10 -->
      <el-row :gutter="20" class="mb-4" v-if="isShow">
        <el-col :span="8">
          <el-card shadow="hover" header="素材数量 TOP10">
            <div ref="chartCountRef" class="chart-container"></div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" header="素材时长 TOP10">
            <div ref="chartDurationRef" class="chart-container"></div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" header="素材大小 TOP10">
            <div ref="chartSizeRef" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>


      <!-- 条状图区域：数量TOP10, 时长TOP10, 大小TOP10 -->
      <!--    <el-row :gutter="20" class="mb-4" v-if="isShow">-->
      <!--      <el-col :span="8">-->
      <!--        <el-card shadow="hover">-->
      <!--          <template #header>-->
      <!--            <div class="card-header">-->
      <!--              <span>数量TOP10用户</span>-->
      <!--            </div>-->
      <!--          </template>-->
      <!--          <div class="chart-container">-->
      <!--            <v-chart class="chart" :option="top10CountOption" autoresize/>-->
      <!--          </div>-->
      <!--        </el-card>-->
      <!--      </el-col>-->

      <!--      <el-col :span="8">-->
      <!--        <el-card shadow="hover">-->
      <!--          <template #header>-->
      <!--            <div class="card-header">-->
      <!--              <span>时长TOP10用户</span>-->
      <!--            </div>-->
      <!--          </template>-->
      <!--          <div class="chart-container">-->
      <!--            <v-chart class="chart" :option="top10DurationOption" autoresize/>-->
      <!--          </div>-->
      <!--        </el-card>-->
      <!--      </el-col>-->

      <!--      <el-col :span="8">-->
      <!--        <el-card shadow="hover">-->
      <!--          <template #header>-->
      <!--            <div class="card-header">-->
      <!--              <span>大小TOP10用户</span>-->
      <!--            </div>-->
      <!--          </template>-->
      <!--          <div class="chart-container">-->
      <!--            <v-chart class="chart" :option="top10SizeOption" autoresize/>-->
      <!--          </div>-->
      <!--        </el-card>-->
      <!--      </el-col>-->
      <!--    </el-row>-->

      <!-- 在线用户（保持不变） -->
      <el-row class="mb-4" v-if="isShow">
        <el-col :span="24">
          <el-card shadow="hover" header="在线用户">
            <el-tag
                v-for="user in onlineUsers"
                :key="user.user_id"
                style="margin-right: 8px; margin-bottom: 8px;"
                type="success"
            >
              {{ user.real_name || user.username }}
            </el-tag>
            <span v-if="onlineUsers.length === 0">暂无在线用户</span>
          </el-card>
        </el-col>
      </el-row>
    </div>

  </WatermarkWithTime>
</template>

<script lang="ts" setup>
import {ref, onMounted, onBeforeUnmount, nextTick, computed} from 'vue';
import {Refresh} from '@element-plus/icons-vue';
import {ElMessage} from 'element-plus'; // ✅ 新增：用于错误提示
import * as echarts from 'echarts';
import dayjs from 'dayjs'
import {getSummary, getUserVideoStats, getOnlineUsers, getUserStatsByTime} from '@/service/main/files/files';
import type {DashboardSummary, UserVideoStat, OnlineUser} from '@/types/dashboard';
import {formatBytes, formatDuration, toLocalISOString, formatUTC} from '@/utils/format'
import VChart from 'vue-echarts'
import {decryptData} from "@/utils/encrypts.ts";
import completeVirtualData from "@/utils/create-virtual-file-data.ts";
import {useLoginStore} from "@/store/login/login.ts";
import {storeToRefs} from "pinia";
import type {UserProfile} from "@/types/user.ts";
import WatermarkWithTime from "@/components/WatermarkWithTime.vue";


const userProfile = ref({});

// 发起action
const loginStore = useLoginStore()
const {profile} = storeToRefs(loginStore)
userProfile.value = profile.value
loginStore.loadLocalUserProfile()
const isShow = computed(() => {
  return userProfile.value.is_staff || userProfile.value.is_superuser
})


// ✅ 新增 loading 状态
const loading = ref(false);

// 数据
const summary = ref<DashboardSummary>({
  today_file_count: 0,
  today_duration: 0,
  total_file_count: 0,
  total_duration: 0,
});
const allStats = ref<UserVideoStat[]>([]);
const onlineUsers = ref<OnlineUser[]>([]);

// 图表 DOM 引用
const chartCountRef = ref<HTMLDivElement | null>(null);
const chartDurationRef = ref<HTMLDivElement | null>(null);
const chartSizeRef = ref<HTMLDivElement | null>(null);

// ECharts 实例
let chartCount: echarts.ECharts | null = null;
let chartDuration: echarts.ECharts | null = null;
let chartSize: echarts.ECharts | null = null;

// 图表配置

const top10CountOption = ref({})
const top10DurationOption = ref({})
const top10SizeOption = ref({})


// 初始化素材数量TOP10用户图表
const initTop10CountChart = () => {
  // 按素材数量分组统计总时长

  const stats = Array.isArray(allStats.value) ? allStats.value : [];

  // console.log('stats:', stats)

  const accountMap = new Map<string, number>()
  stats.forEach(item => {
    const account = item.real_name || item.username
    accountMap.set(account, (accountMap.get(account) || 0) + item.file_count)
  })

  // 排序并取前10
  const top10 = Array.from(accountMap.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)

  top10CountOption.value = {
    title: {
      text: '素材数量TOP10用户',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
      formatter: (params: any) => {
        const param = params[0]
        return `${param.name}<br/>${param.value}`
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
        formatter: (value: number) => value
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

// 初始化时长TOP10用户图表
const initTop10DurationChart = () => {
  // 按账号分组统计总时长

  const stats = Array.isArray(allStats.value) ? allStats.value : [];

  // console.log('stats:', stats)

  const accountMap = new Map<string, number>()
  stats.forEach(item => {
    const account = item.real_name || item.username
    accountMap.set(account, (accountMap.get(account) || 0) + item.total_duration)
  })

  // 排序并取前10
  const top10 = Array.from(accountMap.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)

  top10DurationOption.value = {
    title: {
      text: '素材时长TOP10用户',
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

// 初始化素材大小TOP10用户图表
const initTop10SizeChart = () => {
  // 按账号分组统计总大小

  const stats = Array.isArray(allStats.value) ? allStats.value : [];

  const accountMap = new Map<string, number>()
  stats.forEach(item => {
    const account = item.real_name || item.username
    accountMap.set(account, (accountMap.get(account) || 0) + item.total_size)
  })

  // 排序并取前10
  const top10 = Array.from(accountMap.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)

  top10SizeOption.value = {
    title: {
      text: '素材大小TOP10用户',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
      formatter: (params: any) => {
        const param = params[0]
        return `${param.name}<br/>${formatBytes(param.value)}`
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
        formatter: (value: number) => formatBytes(value)
      }
    },
    yAxis: {
      type: 'category',
      data: top10.map(item => item[0]).reverse(),  // 反转数组使最大值在上方
    },
    series: [
      {
        name: '总大小',
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


// 渲染图表
const renderCharts = () => {
  const stats = Array.isArray(allStats.value) ? allStats.value : [];

  const countTop10 = [...stats].sort((a, b) => b.file_count - a.file_count).slice(0, 10);
  const countNames = countTop10.map(item => item.real_name || item.username);
  const countValues = countTop10.map(item => item.file_count);

  const durationTop10 = [...stats].sort((a, b) => b.total_duration - a.total_duration).slice(0, 10);
  const durationNames = durationTop10.map(item => item.real_name || item.username);
  const durationValues = durationTop10.map(item => item.total_duration);

  const sizeTop10 = [...stats].sort((a, b) => b.total_size - a.total_size).slice(0, 10);
  const sizeNames = sizeTop10.map(item => item.real_name || item.username);
  const sizeValues = sizeTop10.map(item => item.total_size);

  if (chartCountRef.value) {
    chartCount?.dispose();
    chartCount = echarts.init(chartCountRef.value);
    chartCount.setOption({
      tooltip: {trigger: 'axis', axisPointer: {type: 'shadow'}},
      xAxis: {type: 'category', data: countNames, axisLabel: {rotate: 30}},
      yAxis: {type: 'value'},
      series: [{data: countValues, type: 'bar', showBackground: true, itemStyle: {color: '#409EFF'}}],
      grid: {left: '10%', right: '10%', bottom: '20%'}
    });
  }

  if (chartDurationRef.value) {
    chartDuration?.dispose();
    chartDuration = echarts.init(chartDurationRef.value);
    chartDuration.setOption({
      tooltip: {
        trigger: 'axis',
        formatter: (params) => {
          const val = (params[0] as any).value;
          return `${(params[0] as any).name}<br/>时长: ${formatDuration(val)}`;
        }
      },
      xAxis: {type: 'category', data: durationNames, axisLabel: {rotate: 30}},
      yAxis: {type: 'value', axisLabel: {formatter: (value: number) => formatDuration(value)}},
      series: [{data: durationValues, type: 'bar', showBackground: true, itemStyle: {color: '#67C23A'}}],
      grid: {left: '10%', right: '10%', bottom: '20%'}
    });
  }

  if (chartSizeRef.value) {
    chartSize?.dispose();
    chartSize = echarts.init(chartSizeRef.value);
    chartSize.setOption({
      tooltip: {
        trigger: 'axis',
        formatter: (params) => {
          const val = (params[0] as any).value;
          return `${(params[0] as any).name}<br/>大小: ${formatBytes(val)}`;
        }
      },
      xAxis: {type: 'category', data: sizeNames, axisLabel: {rotate: 30}},
      yAxis: {
        type: 'value',
        axisLabel: {
          rotate: 45,
          interval: 0,
          fontSize: 12,
          margin: 8,
          formatter: (value: number) => formatBytes(value).length > 6 ? formatBytes(value).slice(0, 6) + '...' : formatBytes(value)
        }
      },
      series: [{data: sizeValues, type: 'bar', showBackground: true, itemStyle: {color: '#E6A23C'}}],
      grid: {left: '10%', right: '10%', bottom: '20%'}
    });
  }
};

const resizeCharts = () => {
  chartCount?.resize();
  chartDuration?.resize();
  chartSize?.resize();
};


// --- 用户时间趋势图表 start ---

// 新增时间序列相关状态
const timeRange = ref<'yesterday' | 'today' | '7d' | '30d' | 'custom'>('today') // yesterday, today, 7d, 30d, custom
const customDateRange = ref<string[]>([])
const timeSeriesData = ref<{
  create_time: string, file_count: number, total_duration: number, total_size
      : number
}[]>([])
const timeSeriesOption = ref({})


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
    const response = await getUserStatsByTime({
      start_time: startDate.format('YYYY-MM-DD HH:mm:ss'),
      end_time: endDate.format('YYYY-MM-DD HH:mm:ss'),
      granularity: 'auto',
      // 可以根据需要添加其他筛选参数
    }, {page: 1, page_size: 1000, _t: Date.now()})


    let result = decryptData(response.data.result)
    result = JSON.parse(result)
    const {total, results} = result.data
    // console.log("results", results)
    // console.log("total",total)
    timeSeriesData.value = results
    // console.log('timeSeriesData:', timeSeriesData.value)
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
      new Date(a.time).getTime() - new Date(b.time).getTime()
  )

  if (startDate && endDate) {
    console.log("startDate", startDate.format('YYYY-MM-DD HH:mm:ss'))
    console.log("endDate", endDate.format('YYYY-MM-DD HH:mm:ss'))
    sortedData = completeVirtualData(sortedData, startDate, endDate)
  }


  // 2. 提取排序后的时间和流量数据
  const timeData = sortedData.map(item => formatUTC(item.create_time))

  let ratio = Math.random()
  const totalCountData = sortedData.map(item => item.file_count) // 数量

  const durationData = sortedData.map(item => item.total_duration) // 时长

  const sizeData = sortedData.map(item => item.total_size / (1024 * 1024)) // 字节大小

  timeSeriesOption.value = {
    title: {
      text: '素材创作趋势',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const date = params[0].axisValue
        const duration = params[0].data
        const size = params[1].data
        const totalCount = params[2].data

        return `
        <div style="font-weight:bold">${date}</div>
        <div>时长: ${formatDuration(duration)} </div>
        <div>字节数: ${size.toFixed(2)} MB </div>
        <div>数量: ${totalCount} </div>
    `
      }
    },
    legend: {
      data: ['时长', '字节数', '数量'],
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
      name: '时长(秒)',
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
        name: '时长',
        type: 'line',
        smooth: true,
        data: durationData,
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
        name: '字节数',
        type: 'line',
        smooth: true,
        data: sizeData,
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
        name: '数量',
        type: 'line',
        smooth: true,
        data: totalCountData,
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


// --- 用户时间趋势图表  end ---


// ✅ 核心：加载数据函数（可复用）
const loadDashboardData = async (showLoading = true) => {
  if (showLoading) loading.value = true;
  try {
    const [summaryRes, statsRes, onlineRes] = await Promise.all([
      getSummary(),
      getUserVideoStats(),
      getOnlineUsers(),
    ]);

    // ✅ 修复：根据你 DRF 的实际返回结构解析
    // 假设格式为 { code: 200, msg: "...", data: { ... } }
    summary.value = summaryRes.data?.data || {
      today_file_count: 0,
      today_duration: 0,
      total_file_count: 0,
      total_duration: 0,
    };

    allStats.value = Array.isArray(statsRes.data?.data.data) ? statsRes.data.data.data : [];
    onlineUsers.value = Array.isArray(onlineRes.data?.data) ? onlineRes.data.data : [];

    await nextTick();
    renderCharts();
    initTop10CountChart();
    initTop10DurationChart();
    initTop10SizeChart()
  } catch (error) {
    console.error('加载仪表盘数据失败:', error);
    ElMessage.error('加载仪表盘数据失败');
  } finally {
    loading.value = false;
  }
};

// 初始加载
onMounted(() => {
  loadDashboardData(false); // 首次加载不显示按钮 loading
  window.addEventListener('resize', resizeCharts);
  fetchTimeSeriesData()
  // 默认加载今天
});

// ✅ 刷新按钮处理
const handleRefresh = () => {
  if (loading.value) return; // 防重入
  loadDashboardData(true);
  fetchTimeSeriesData()
};

// 清理
onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts);
  chartCount?.dispose();
  chartDuration?.dispose();
  chartSize?.dispose();
});
</script>

<style scoped>

.dashboard {
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
.stat-item {
  text-align: center;
}

.label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
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