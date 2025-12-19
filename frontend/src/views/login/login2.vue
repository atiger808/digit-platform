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
        <p>欢迎登录 大岳数智平台</p>
        <p class="sub-welcome">「洞见数据，智启未来」</p>
      </div>
    </div>
    <div class="box-item login">
      <img class="login-qr" :src="loginQR"/>
      <div class="login-title">账号登录</div>
      <a-form ref="formRef" class="login-form" :model="loginForm" :rules="rules">
        <a-form-item name="loginName">
          <a-input v-model:value.trim="loginForm.loginName" placeholder="请输入用户名"/>
        </a-form-item>
        <a-form-item name="emailCode" v-if="emailCodeShowFlag">
          <a-input-group compact>
            <a-input style="width: calc(100% - 110px)" v-model:value="loginForm.emailCode" autocomplete="on"
                     placeholder="请输入邮箱验证码"/>
            <a-button @click="sendSmsCode" class="code-btn" type="primary" :disabled="emailCodeButtonDisabled">
              {{ emailCodeTips }}
            </a-button>
          </a-input-group>
        </a-form-item>
        <a-form-item name="password">
          <a-input-password
              v-model:value="loginForm.password"
              autocomplete="on"
              :type="showPassword ? 'text' : 'password'"
              placeholder="请输入密码"
          />
        </a-form-item>
        <a-form-item name="captchaCode">
          <a-input class="captcha-input" v-model:value.trim="loginForm.captchaCode" placeholder="请输入验证码"/>
          <img class="captcha-img" :src="captchaBase64Image" @click="getCaptcha"/>
        </a-form-item>
        <a-form-item>
          <a-checkbox v-model:checked="rememberPwd">记住密码</a-checkbox>
          <span> ( 账号：admin, 密码：123456)</span>
        </a-form-item>
        <a-form-item>
          <div class="btn" :loading="loginLoading" @click="onLogin">登录</div>
        </a-form-item>
      </a-form>
      <div class="more">
        <div class="title-box">
          <p class="line"></p>
          <p class="title">其他方式登录</p>
          <p class="line"></p>
        </div>
        <div class="login-type">
          <img :src="wechatIcon"/>
          <img :src="aliIcon"/>
          <img :src="douyinIcon"/>
          <img :src="qqIcon"/>
          <img :src="weiboIcon"/>
          <img :src="feishuIcon"/>
          <img :src="googleIcon"/>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import {message, notification, Button} from 'ant-design-vue';
import {onMounted, onUnmounted, reactive, ref, watch, computed} from 'vue';
import {useRouter} from 'vue-router';
import {useLoginStore} from "@/store/login/login.ts";
import {SmartLoading} from '@/components/framework/smart-loading';
import {LOGIN_DEVICE_ENUM} from '@/global/login-device-const';
import zhuoda from '@/assets/images/1024lab/zhuoda-wechat.jpg';
import loginQR from '@/assets/images/login/login-qr.png';
import gzh from '@/assets/images/1024lab/gzh.jpg';
import wechatIcon from '@/assets/images/login/wechat-icon.png';
import aliIcon from '@/assets/images/login/ali-icon.png';
import douyinIcon from '@/assets/images/login/douyin-icon.png';
import qqIcon from '@/assets/images/login/qq-icon.png';
import weiboIcon from '@/assets/images/login/weibo-icon.png';
import feishuIcon from '@/assets/images/login/feishu-icon.png';
import googleIcon from '@/assets/images/login/google-icon.png';


import {encryptData} from '@/utils/encrypts.ts';
import {type ElForm, ElLoading, ElMessage} from "element-plus";
import {api} from '@/service/request.ts'


import {sessionCache} from "@/utils/cache.ts";
import {IS_REMEMBER} from "@/global/constants.ts";
import {formatAxis} from '@/utils/format.ts'

//--------------------- 登录表单 ---------------------------------

const loginStore = useLoginStore()

const loginForm = reactive({
  loginName: '',
  password: '',
  captchaCode: '',
  captchaUuid: '',
  loginDevice: LOGIN_DEVICE_ENUM.PC.value,
});
const rules = {
  loginName: [{required: true, message: '用户名不能为空'}],
  password: [{required: true, message: '密码不能为空'}],
  captchaCode: [{required: true, message: '验证码不能为空'}],
};

const loginLoading = ref(false);
let loadingInstance: ReturnType<typeof ElLoading.service> | null = null;
const showPassword = ref(false);
const router = useRouter();
const formRef = ref();
// const formRef = ref<InstanceType<typeof ElForm>>()
const rememberPwd = ref<boolean>(sessionCache.getCache(IS_REMEMBER) ?? false)

// 时间获取
const currentTime = computed(() => {
  return formatAxis(new Date());
});

watch(rememberPwd, (newValue) => {
  console.log('isRemember: ', newValue)
  if (newValue) {
    sessionCache.setCache(IS_REMEMBER, newValue)
  } else {
    sessionCache.removeCache(IS_REMEMBER)
  }
})

onMounted(() => {
  document.onkeyup = (e) => {
    if (e.keyCode === 13) {
      onLogin();
    }
  };

  const userInfo = loginStore.getUserInfo()
  if (userInfo) {
    console.log('用户信息', userInfo)
    loginForm.loginName = userInfo.identifier
    loginForm.password = userInfo.password
  }

  // notification['success']({
  //   message: '温馨提示',
  //   description: 'SmartAdmin 提供 9种 登录背景风格哦！',
  //   duration: 8,
  //   onClick: () => {},
  //   btn: () =>
  //     h(
  //       Button,
  //       {
  //         type: 'primary',
  //         target: '_blank',
  //         size: 'small',
  //         href: 'https://smartadmin.vip/views/doc/front/Login.html',
  //         onClick: () => {},
  //       },
  //       { default: () => '去看看' }
  //     ),
  // });

});

onUnmounted(() => {
  document.onkeyup = null;
});

//登录
async function onLogin() {
  if (loginLoading.value) return; // 防止重复点击
  loginLoading.value = true; // 开始加载
  // 开启全屏加载
  loadingInstance = ElLoading.service({
    lock: true, // 是否锁定
    text: '登录中...', // 加载文字
    background: 'rgba(0, 0, 0, 0.7)', // 背景色
  });

  formRef.value.validate().then(async () => {
    try {
      // SmartLoading.show();
      // 密码加密
      let encryptPasswordForm = Object.assign({}, loginForm, {
        password: encryptData(loginForm.password),
      });
      let data = {
        identifier: loginForm.loginName,
        password: encryptPasswordForm.password,
        key: loginForm.captchaUuid,
        code: loginForm.captchaCode,
        loginDevice: loginForm.loginDevice
      }
      let {success, error} = await loginStore.loginAccountAction(data)

      if (!success) {
        message.error(error)
        return
      }

      stopRefreshCaptchaInterval();
      if (rememberPwd.value) {
        data.password = loginForm.password
        loginStore.saveUserInfo(data)
      } else {
        loginStore.clearUserInfo()
      }
      // 初始化登录成功时间问候语
      let currentTimeInfo = currentTime.value;
      let signInText = '欢迎回来！';
      message.success(`${currentTimeInfo}，${signInText}`);
    } catch (e) {
      if (e.data && e.data.code !== 0) {
        loginForm.captchaCode = '';
        getCaptcha();
      }
      console.log('error: ', e)
    } finally {
      // SmartLoading.hide();
    }
  }).finally(() => {
    loginLoading.value = false; // 结束加载
    // 关闭全屏加载
    if (loadingInstance) {
      loadingInstance.close();
      loadingInstance = null;
    }
    getCaptcha()
  });
}

//--------------------- 验证码 ---------------------------------

const captchaBase64Image = ref('');

async function getCaptcha() {
  try {
    let captchaResult = await api.get('user/api/captcha/', {responseType: 'blob', params: {_t: Date.now()}})
    let blob = new Blob([captchaResult.data], {type: captchaResult.headers['content-type']})
    captchaBase64Image.value = URL.createObjectURL(blob)
    loginForm.captchaUuid = captchaResult.headers.get('Captcha-Key')
    // beginRefreshCaptchaInterval(captchaResult.data.expireSeconds || 300);
  } catch (e) {
    console.log(e);
  }
}

let refreshCaptchaInterval = null;

function beginRefreshCaptchaInterval(expireSeconds) {
  if (refreshCaptchaInterval === null) {
    refreshCaptchaInterval = setInterval(getCaptcha, (expireSeconds - 5) * 1000);
  }
}

function stopRefreshCaptchaInterval() {
  if (refreshCaptchaInterval != null) {
    clearInterval(refreshCaptchaInterval);
    refreshCaptchaInterval = null;
  }
}

onMounted(() => {
  getCaptcha();
});

//--------------------- 邮箱验证码 ---------------------------------

const emailCodeShowFlag = ref(false);
let emailCodeTips = ref('获取邮箱验证码');
let emailCodeButtonDisabled = ref(false);
// 定时器
let countDownTimer = null;

// 开始倒计时
function runCountDown() {
  emailCodeButtonDisabled.value = true;
  let countDown = 60;
  emailCodeTips.value = `${countDown}秒后重新获取`;
  countDownTimer = setInterval(() => {
    if (countDown > 1) {
      countDown--;
      emailCodeTips.value = `${countDown}秒后重新获取`;
    } else {
      clearInterval(countDownTimer);
      emailCodeButtonDisabled.value = false;
      emailCodeTips.value = '获取验证码';
    }
  }, 1000);
}


// 发送邮箱验证码
async function sendSmsCode() {
  try {
    // SmartLoading.show();
    let result = api.post('user/api/sms-code/', {mobile: loginForm.loginName})
    message.success('验证码发送成功!请登录邮箱查看验证码~');
    runCountDown();
  } catch (e) {
    console.log("error: ", e)
  } finally {
    // SmartLoading.hide();
  }
}
</script>
<style lang="less" scoped>
@import './login2.less';
</style>
