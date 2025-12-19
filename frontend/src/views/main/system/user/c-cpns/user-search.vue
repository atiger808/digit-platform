<script setup lang="ts">
import {reactive, ref} from "vue";
import type {ElForm} from "element-plus";

// 定义自定义事件
const emit = defineEmits(['queryClick', 'resetClick'])

const searchForm = reactive({
  username: '',
  real_name: '',
  mobile: '',
  is_active: 1,
  createAt: '',
})


// 重置
const formRef = ref<InstanceType<typeof ElForm>>()
const handleResetClick = () => {
  formRef.value?.resetFields()
  emit('resetClick')
}

const handleQueryClick = () => {
  console.log(searchForm)
  emit('queryClick', searchForm)
}


</script>

<template>
  <div class="search">
    <!--    1.输入搜索关键字的表单-->
    <el-form :model="searchForm" ref="formRef" label-width="80px" size="large">

      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="searchForm.username" placeholder="请输入用户名"/>
          </el-form-item>

        </el-col>
        <el-col :span="8">
          <el-form-item label="真实姓名" prop="real_name">
            <el-input v-model="searchForm.real_name" placeholder="请输入真实姓名"/>
          </el-form-item>

        </el-col>
        <el-col :span="8">
          <el-form-item label="电话号码" prop="mobile">
            <el-input v-model="searchForm.mobile" placeholder="请输入电话号码"/>
          </el-form-item>
        </el-col>

        <el-col :span="8">
          <el-form-item label="状态" prop="is_active">
            <el-select
                placeholder="选择状态"
                v-model="searchForm.is_active"
            >
              <el-option label="启用" :value="1"></el-option>
              <el-option label="禁用" :value="0"></el-option>
            </el-select>
          </el-form-item>

        </el-col>
        <el-col :span="8">
          <el-form-item label="创建时间" prop="createAt">
            <el-date-picker
                type="daterange"
                range-separator="-"
                start-placeholder="开始时间"
                end-placeholder="结束时间"
                v-model="searchForm.createAt"
            />
          </el-form-item>
        </el-col>
      </el-row>


    </el-form>

    <!--    2.重置和搜索按钮-->
    <div class="btns">
      <el-button size="large" icon="Refresh" @click="handleResetClick">重置</el-button>
      <el-button size="large" icon="Search" type="primary" @click="handleQueryClick">查询</el-button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.search {
  background-color: #fff;
  padding: 20px;

  .el-form-item {
    padding: 20px 30px;
    margin-bottom: 0;
  }
}

.btns {
  text-align: right;
  padding: 0 50px 10px 0;
}


</style>