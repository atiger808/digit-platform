<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="总访问量" :value="12680" />
          <div class="stat-footer">
            <el-icon><User /></el-icon>
            <span class="compare">周同比 12% ↑</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="销售额" :value="5680" precision="2" suffix="¥" />
          <div class="stat-footer">
            <el-icon><Money /></el-icon>
            <span class="compare">日环比 5% ↑</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="订单量" :value="326" />
          <div class="stat-footer">
            <el-icon><ShoppingCart /></el-icon>
            <span class="compare">转化率 68%</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="用户数" :value="1456" />
          <div class="stat-footer">
            <el-icon><Avatar /></el-icon>
            <span class="compare">月增长 23%</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card shadow="hover">
          <h3>访问趋势</h3>
          <div ref="lineChart" style="height: 400px"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <h3>流量来源</h3>
          <div ref="pieChart" style="height: 400px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import {
  User,
  Money,
  ShoppingCart,
  Avatar
} from '@element-plus/icons-vue'
// 在Dashboard.vue中添加
import { onBeforeUnmount } from 'vue'

onMounted(() => {
  window.addEventListener('resize', handleResize)
  initCharts()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})

const handleResize = () => {
  lineInstance.resize()
  pieInstance.resize()
}

const lineChart = ref<HTMLElement>()
const pieChart = ref<HTMLElement>()



const initCharts = () => {
  // 折线图
  const lineInstance = echarts.init(lineChart.value!)
  lineInstance.setOption({
    xAxis: {
      type: 'category',
      data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    },
    yAxis: { type: 'value' },
    series: [{
      data: [820, 932, 901, 934, 1290, 1330, 1320],
      type: 'line',
      smooth: true
    }]
  })

  // 饼图
  const pieInstance = echarts.init(pieChart.value!)
  pieInstance.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: '50%',
      data: [
        { value: 1048, name: '直接访问' },
        { value: 735, name: '搜索引擎' },
        { value: 580, name: '邮件营销' },
        { value: 484, name: '联盟广告' }
      ]
    }]
  })
}
</script>

<style scoped>
.dashboard {
  background-color: #fff;
  margin-top: 20px;
  padding: 20px;
}
.stats-row {
  margin-bottom: 20px;
}
.stat-footer {
  margin-top: 15px;
  display: flex;
  align-items: center;
  color: #999;
  font-size: 14px;
}
.stat-footer .el-icon {
  margin-right: 5px;
}
.compare {
  margin-left: auto;
}
.chart-row {
  margin-top: 20px;
}
</style>