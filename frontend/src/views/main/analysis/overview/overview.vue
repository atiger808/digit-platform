<template>
  <el-card class="box-card">
    <template #header>
      <div class="card-header">
        <h2>欢迎来到大岳数智平台</h2>
      </div>
    </template>

    <div class="content">
      <div class="stats">
        <el-alert
            title="系统提示"
            type="info"
            description="当前版本：1.0.0"
            show-icon
            :closable="false"
        />
      </div>


      <div class="stats">
        <el-statistic ref="count1Ref" :title="title" :value="number1"/>
        <el-statistic ref="count2Ref" :title="subtitle" :value="number2"/>
      </div>


    </div>
  </el-card>
</template>

<script setup lang="ts">

import {Warning} from "@element-plus/icons-vue";
import {onMounted, ref} from "vue";
import {CountUp} from "countup.js";

interface IProps {
  amount?: string
  title?: string
  tips?: string
  number1?: number
  number2: number
  subtitle?: string
}

const props = withDefaults(defineProps<IProps>(), {
  title: '今日访问量',
  number1: 12682,
  subtitle: '系统用户数',
  number2: 3686,
  tips: 'tips'
})

const count1Ref = ref<HTMLElement>()
const count2Ref = ref<HTMLElement>()
const countOptions = {
  prefix: props.amount === 'saleroom' ? '￥' : ''
}
onMounted(() => {
  // 数据递增动画实现
  // 创建CountUp的实例对象  npm install countup.js --save
  const countup1 = new CountUp(count1Ref.value!, props.number1, countOptions)
  countup1.start()
  const countup2 = new CountUp(count2Ref.value!, props.number2, countOptions)
  countup2.start()
})



</script>

<style scoped>
.box-card {
  width: 100%;
  height: 100%;
}


.card-header {
  text-align: center;
}

.stats {
  margin-top: 30px;
  margin-bottom: 30px;
  display: flex;
  gap: 50px;
  justify-content: center;
}
</style>