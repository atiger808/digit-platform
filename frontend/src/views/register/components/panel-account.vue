<script setup lang="ts">
import {message, notification, Button} from 'ant-design-vue';
import {onMounted, onUnmounted, reactive, ref, watch} from 'vue';
import {ElLoading, ElMessage} from "element-plus";
import type {FormInstance} from "element-plus";
import {useRouter} from 'vue-router';
import {useRegisterStore} from "@/store/register/register.ts";
import {api} from '@/service/request.ts'
import {LOGIN_DEVICE_ENUM} from "@/global/login-device-const.ts";
import {sessionCache} from "@/utils/cache.ts";
import {IS_REMEMBER} from "@/global/constants.ts";
import {encryptData} from "@/utils/encrypts.ts";

//--------------------- 登录表单 ---------------------------------

const registerStore = useRegisterStore()

const registerForm = reactive({
  identifier: '',
  password: '',
  password2: '',
  mobile: '',
  email: '',
  code: '',
  emailCode: '',
  mobileCode: '',
  key: '',
  identifier_type: 'username',
  loginDevice: LOGIN_DEVICE_ENUM.PC.value
});
const rules = {
  identifier: [{required: true, message: '用户名不能为空'}, {
    min: 4,
    max: 20,
    message: '长度在 4 到 20 个字符',
    trigger: 'change'
  }],
  password: [{required: true, message: '密码不能为空'}, {
    min: 6,
    max: 20,
    message: '长度在 6 到 20 个字符',
    trigger: 'change'
  }],
  password2: [{required: true, message: '确认密码不能为空'}],
  mobile: [{required: true, message: '手机号不能为空'}, {
    pattern: /^1[3-9]\d{9}$/,
    message: '请输入正确的手机号',
    trigger: 'change'
  }],
  email: [{required: true, message: '邮箱不能为空'}, {
    pattern: /^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/,
    message: '请输入正确的邮箱',
    trigger: 'change'
  }],
  code: [{required: true, message: '验证码不能为空'}],
};

const loginLoading = ref(false);
let loadingInstance: ReturnType<typeof ElLoading.service> | null = null;
const showPassword = ref(false);
const router = useRouter();
// const formRef = ref(null);
const formRef = ref<InstanceType<typeof FormInstance>>()
const rememberPwd = ref<boolean>(sessionCache.getCache(IS_REMEMBER) ?? false)

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
      onRegister();
    }
  };

});

onUnmounted(() => {
  document.onkeyup = null;
});


//登录
async function onRegister() {
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
      console.log('registerForm: ', registerForm)
      if (registerForm.password !== registerForm.password2) {
        message.error('两次密码不一致');
        return;
      }
      if (!registerForm.code) {
        message.error('验证码不能为空');
        return;
      }


      // 密码加密
      let encryptPasswordForm = Object.assign({}, registerForm, {
        password: encryptData(registerForm.password),
      });
      let {success, error} = await registerStore.registerAccountAction(registerForm)

      if (!success) {
        message.error(error)
        return
      }

      stopRefreshCaptchaInterval();
      message.success('注册成功');
    } catch (e) {
      if (e.data && e.data.code !== 0) {
        registerForm.code = '';
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

// 重置
const resetForm = () => {
  formRef.value?.resetFields();
};

//--------------------- 验证码 ---------------------------------

const captchaBase64Image = ref('');

async function getCaptcha() {
  try {
    let captchaResult = await api.get('user/api/captcha/', {responseType: 'blob', params: {_t: Date.now()}})
    let blob = new Blob([captchaResult.data], {type: captchaResult.headers['content-type']})
    captchaBase64Image.value = URL.createObjectURL(blob)

    if ('get' in captchaResult.headers && typeof captchaResult.headers.get === 'function') {
      registerForm.key = captchaResult.headers.get('Captcha-Key') as string
      // beginRefreshCaptchaInterval(captchaResult?.data?.expireSeconds || 300);
    }


  } catch (e) {
    console.log(e);
  }
}

let refreshCaptchaInterval = ref<number | null>(null)

function beginRefreshCaptchaInterval(expireSeconds: number) {
  // 先清除已有定时器
  if (refreshCaptchaInterval.value) {
    clearInterval(refreshCaptchaInterval.value);
    refreshCaptchaInterval.value = 0
  }
  // 设置新的定时器
  refreshCaptchaInterval.value = setInterval(getCaptcha, (expireSeconds - 5) * 1000);
}

function stopRefreshCaptchaInterval() {
  if (refreshCaptchaInterval.value) {
    clearInterval(refreshCaptchaInterval.value);
    refreshCaptchaInterval.value = 0
  }
}

onMounted(() => {
  getCaptcha();
});


// 暴露给父组件
defineExpose({onRegister})

</script>

<template>
  <div class="panel-account">
    <a-form ref="formRef" class="login-form" :model="registerForm" :rules="rules">
      <a-form-item name="identifier">
        <a-input v-model:value.trim="registerForm.identifier" placeholder="请输入用户名"/>
      </a-form-item>
      <a-form-item name="password">
        <a-input-password
            v-model:value="registerForm.password"
            autocomplete="on"
            :type="showPassword ? 'text' : 'password'"
            placeholder="请输入密码：至少三种字符，最小 8 位"
        />
      </a-form-item>

      <a-form-item name="password2">
        <a-input-password
            v-model:value="registerForm.password2"
            autocomplete="on"
            :type="showPassword ? 'text' : 'password'"
            placeholder="请输入确认密码"
        />
      </a-form-item>

      <a-form-item name="email">
        <a-input v-model:value.trim="registerForm.email" placeholder="请输入邮箱"/>
      </a-form-item>

      <a-form-item name="mobile">
        <a-input v-model:value.trim="registerForm.mobile" placeholder="请输入手机号"/>
      </a-form-item>

      <a-form-item name="code">
        <a-input class="captcha-input" v-model:value.trim="registerForm.code" placeholder="请输入验证码"/>
        <img class="captcha-img" :src="captchaBase64Image" @click="getCaptcha"/>
      </a-form-item>
      <a-form-item>
        <div class="btn" :loading="loginLoading" @click="onRegister">注册</div>
      </a-form-item>

      <!--      <a-form-item>-->
      <!--        <div class="btn" @click="resetForm">重置</div>-->
      <!--      </a-form-item>-->


      <a-form-item>
        <div class="login-form-forgot">
          <router-link to="/login">已有账号？去登录</router-link>
        </div>
      </a-form-item>
    </a-form>
  </div>
</template>

<style scoped lang="less">
@import '../register3.less';
</style>