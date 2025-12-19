<!--
  * 登录
  *
  * @Author:    1024创新实验室-主任：卓大
  * @Date:      2022-09-12 22:34:00
  * @Wechat:    zhuda1024
  * @Email:     lab1024@163.com
  * @Copyright  1024创新实验室 （ https://1024lab.net ），Since 2012
  *
-->
<template>
  <div class="login-container">
    <div class="box-item desc">
      <div class="welcome">
        <p>欢迎注册 大岳数智平台 </p>
        <p class="sub-welcome">「洞见数据，智启未来」</p>
      </div>
<!--      <img class="welcome-img" :src="loginGif"/>-->
    </div>
    <div class="box-item login">
      <img class="login-qr" :src="loginQR"/>
      <div class="login-title">账号注册</div>

      <div class="tabs">
        <el-tabs v-model="activeName" class="demo-tabs" @tab-click="handleClick">

          <el-tab-pane label="用户名" name="username">
            <PanelAccount ref="accountRef" />
          </el-tab-pane>

          <el-tab-pane label="邮箱" name="email">
            <PanelEmail ref="emailRef" />
          </el-tab-pane>

          <el-tab-pane label="手机号" name="mobile">
            <PanelMobile ref="mobileRef" />
          </el-tab-pane>

        </el-tabs>
      </div>

    </div>
  </div>
</template>
<script setup lang="ts">
import {message, notification, Button} from 'ant-design-vue';
import {onMounted, onUnmounted, reactive, ref, watch} from 'vue';

import loginQR from '@/assets/images/login/login-qr.png';
import loginGif from '@/assets/images/login/login-min.gif';
import gzh from '@/assets/images/1024lab/gzh.jpg';
import wechatIcon from '@/assets/images/login/wechat-icon.png';
import aliIcon from '@/assets/images/login/ali-icon.png';
import douyinIcon from '@/assets/images/login/douyin-icon.png';
import qqIcon from '@/assets/images/login/qq-icon.png';
import weiboIcon from '@/assets/images/login/weibo-icon.png';
import feishuIcon from '@/assets/images/login/feishu-icon.png';
import googleIcon from '@/assets/images/login/google-icon.png';
import PanelAccount from "@/views/register/components/panel-account.vue";
import PanelEmail from "@/views/register/components/panel-email.vue";
import PanelMobile from "@/views/register/components/panel-mobile.vue";
import type { TabsPaneContext } from 'element-plus'


// 获取子组件实例
const accountRef = ref<InstanceType<typeof PanelAccount>>();
const emailRef = ref<InstanceType<typeof PanelEmail>>();
const mobileRef = ref<InstanceType<typeof PanelMobile>>();

const activeName = ref('username')



const handleClick = (tab: TabsPaneContext, event: Event) => {
  console.log(tab, event, 'handleClick', 'activeName', activeName.value)
}


onMounted(() => {
  document.onkeyup = (e) => {
    if (e.keyCode === 13) {
      console.log('activeName', activeName.value)
      if (activeName.value === 'username') {
        accountRef.value?.onRegister();
      } else if (activeName.value === 'email') {
        emailRef.value?.onRegister();
      } else if (activeName.value === 'mobile') {
        mobileRef.value?.onRegister();
      }
    }
  };

});

onUnmounted(() => {
  document.onkeyup = null;
});


</script>
<style lang="less" scoped>
.demo-tabs > .el-tabs__content {
  padding: 32px;
  color: #6b778c;
  font-size: 32px;
  font-weight: 600;
}

@import './register3.less';
</style>
