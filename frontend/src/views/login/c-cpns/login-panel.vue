<script setup lang="ts">

import {ref, watch} from 'vue'
import {sessionCache} from "@/utils/cache.ts";
import {IS_REMEMBER} from "@/global/constants.ts";
import PanelAccount from "@/views/login/c-cpns/panel-account.vue";
import PanelPhone from "@/views/login/c-cpns/panel-phone.vue";
import router from "@/router";

const isRemember = ref<boolean>(sessionCache.getCache(IS_REMEMBER) ?? false)
const activeName = ref('account')
const accountRef = ref<InstanceType<typeof PanelAccount>>()
const phoneRef = ref<InstanceType<typeof PanelPhone>>()

watch(isRemember, (newValue) => {
  console.log('isRemember: ', newValue)
  if (newValue) {
    sessionCache.setCache(IS_REMEMBER, newValue)
  } else {
    sessionCache.removeCache(IS_REMEMBER)
  }
})


const handleLoginBtnClick = () => {
  if (activeName.value === 'account') {
    console.log('账号登录')
    console.log(accountRef.value)
    console.log('isRemember: ', isRemember.value)
    // 1.获取到子组件的实例
    accountRef.value?.loginAction(isRemember.value)
    // 2.调用子组件的实例方法

  } else {
    console.log('手机号登录')
    console.log(phoneRef.value)
    phoneRef.value?.phoneLoginAction(isRemember.value)
  }
}

const handleRegisterBtnClick = () => {
  console.log('注册')
  router.push('/register')
}


</script>

<template>
  <div class="login-panel">
    <h2 class="title">后台管理系统登录</h2>


    <div class="tabs">
      <el-tabs type="border-card" stretch v-model="activeName">
        <!--        1.账号登录-->
        <el-tab-pane label="账号登录" name="account">
          <template #label>
            <div class="icon">
              <el-icon>
                <UserFilled/>
              </el-icon>
              <span class="text">账号密码登录</span>
            </div>
          </template>

          <PanelAccount ref="accountRef" @enterPressed="handleLoginBtnClick"/>
        </el-tab-pane>

        <!--        2.手机号登录-->
        <el-tab-pane label="手机号登录" name="phone">
          <template #label>
            <div class="icon">
              <el-icon>
                <Phone/>
              </el-icon>
              <span class="text">邮箱/手机号登录</span>
            </div>
          </template>
          <PanelPhone ref="phoneRef"/>
        </el-tab-pane>

      </el-tabs>

    </div>
    <div class="controls">
      <el-checkbox v-model="isRemember" label="记住密码" size="large"/>
      <el-link type="primary">忘记密码</el-link>
    </div>

    <div class="operator-btn">
      <el-button class="login-btn" type="primary" size="large" @click="handleLoginBtnClick">立即登录</el-button>
      <el-button class="login-btn" type="default" size="large" @click="handleRegisterBtnClick">注册账号</el-button>
    </div>

  </div>
</template>

<style scoped lang="scss">

.login-panel {
  width: 500px;
  margin-bottom: 150px;

  .title {
    text-align: center;
    margin-bottom: 15px;
  }

  .icon {
    display: flex;
    align-items: center;
    justify-content: center;

    .text {
      margin-left: 5px;
    }
  }

  .controls {
    margin-top: 12px;
    display: flex;
    justify-content: space-between;
  }

  .operator-btn{
    align-items: center;
    justify-content: space-between;
    display: flex;
  }

  .login-btn {
    margin-top: 10px;
    width: 100%;
  }

}


</style>