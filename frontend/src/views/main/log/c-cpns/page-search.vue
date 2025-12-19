<script setup lang="ts">
import {reactive, ref} from "vue";
import type {ElForm} from "element-plus";
import {usePermissions} from "@/hooks/usePermissions.ts";
import WatermarkWithTime from '@/components/WatermarkWithTime.vue'

export interface ISearchProps {
  searchConfig: {
    pageName: string,
    labelWidth?: string,
    formItems: any[]
  }
}

// 定义自定义事件/接受的属性
const emit = defineEmits(['queryClick', 'resetClick'])
const props = defineProps<ISearchProps>()

// 获取权限
const isQuery = usePermissions(`${props.searchConfig.pageName}:query`)


// 定义form数据
const initialForm: any = {}
for (const item of props.searchConfig.formItems) {
  initialForm[item.prop] = item.initialValue ?? ''
}
const searchForm = reactive(initialForm)


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
  <WatermarkWithTime>
    <div class="search" v-if="isQuery">
      <!--    1.输入搜索关键字的表单-->
      <el-form
          :model="searchForm"
          ref="formRef"
          :label-width="searchConfig.labelWidth ?? '80px'"
          size="default">

        <el-row :gutter="20">
          <template v-for="item in searchConfig.formItems" :key="item.prop">
            <el-col :span="8" :xs="24" :sm="12" :md="8" :lg="8">
              <el-form-item :label="item.label" :prop="item.prop">
                <template v-if="item.type === 'input'">
                  <el-input
                      v-model="searchForm[item.prop]"
                      :placeholder="item.placeholder"
                  />
                </template>
                <template v-if="item.type === 'select'">
                  <el-select
                      v-model="searchForm[item.prop]"
                      :placeholder="item.placeholder"
                      style="width: 100%"
                  >

                    <template v-for="option in item.options" :key="option.value">
                      <el-option :label="option.label" :value="option.value"/>
                    </template>

                  </el-select>
                </template>
                <template v-if="item.type === 'date-picker'">
                  <el-date-picker
                      v-model="searchForm[item.prop]"
                      type="daterange"
                      range-separator="至"
                      start-placeholder="开始日期"
                      end-placeholder="结束日期"
                  />
                </template>
              </el-form-item>
            </el-col>
          </template>
        </el-row>


      </el-form>

      <!--    2.重置和搜索按钮-->
      <div class="btns">
        <el-button size="large" icon="Refresh" @click="handleResetClick">重置</el-button>
        <el-button size="large" icon="Search" type="primary" @click="handleQueryClick">查询</el-button>
      </div>
    </div>
  </WatermarkWithTime>
</template>

<style scoped lang="scss">
.search {
  background-color: #fff;
  padding: 10px;

  .el-form-item {
    padding: 10px 30px;
    margin-bottom: 0;
  }
}

.btns {
  text-align: right;
  padding: 0 50px 10px 0;
}


</style>