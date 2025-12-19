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
import {errorParse} from "@/utils/errorParse.ts";


//--------------------- 登录表单 ---------------------------------

const registerStore = useRegisterStore()

const registerForm = reactive({
  identifier: '',
  password: '',
  password2: '',
  email: '',
  code: '',
  emailCode: '',
  key: '',
  identifier_type: 'email',
  loginDevice: LOGIN_DEVICE_ENUM.PC.value
});

const rules = {
  password: [{required: true, message: '密码不能为空'}, {
    min: 6,
    max: 20,
    message: '长度在 6 到 20 个字符',
    trigger: 'change'
  }],
  password2: [{required: true, message: '确认密码不能为空'}],
  email: [{required: true, message: '邮箱不能为空'}, {
    pattern: /^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/,
    message: '请输入正确的邮箱',
    trigger: 'change',
  }],
  emailCode: [{required: true, message: '验证码不能为空'}],
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

  formRef.value?.validate?.()?.then(async () => {
    try {
      // SmartLoading.show();
      console.log('registerForm: ', registerForm)
      registerForm.identifier = registerForm.email
      registerForm.code = registerForm.emailCode
      registerForm.key = registerForm.email
      if (!registerForm.email) {
        message.error('邮箱不能为空');
        return;
      }
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
      message.success('注册成功');
    } catch (e) {
      registerForm.code = '';
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
  });
}

// 重置
const resetForm = () => {
  formRef.value?.resetFields();
};

//--------------------- 邮箱验证码 ---------------------------------

const emailCodeShowFlag = ref(true);
let emailCodeTips = ref('获取邮箱验证码');
let emailCodeButtonDisabled = ref(false);
// 定时器
let countDownTimer = ref<number | null>(null)

// 开始倒计时
function runCountDown() {
  emailCodeButtonDisabled.value = true;
  let countDown = 60;
  emailCodeTips.value = `${countDown}秒后重新获取`;
  countDownTimer.value = setInterval(() => {
    if (countDown > 1) {
      countDown--;
      emailCodeTips.value = `${countDown}秒后重新获取`;
    } else {
      clearInterval(countDownTimer.value);
      countDownTimer.value = 0;
      emailCodeButtonDisabled.value = false;
      emailCodeTips.value = '获取验证码';
    }
  }, 1000);
}


// 发送邮箱验证码
async function sendEmailCode() {
  try {
    // SmartLoading.show();
    if (!registerForm.email) {
      message.error('邮箱不能为空');
      return;
    }
    let result = await api.post('user/api/email-code/', {email: registerForm.email})
    console.log("result: ", result)
    message.success(result.data.detail || '验证码发送成功!请登录邮箱查看验证码~');
    runCountDown();
  } catch (error) {
    console.log("error: ", error)
    let errorInfo = errorParse(error)
    console.log('errorInfo', errorInfo)
    message.error(errorInfo || '发送验证码失败');
  } finally {
    // SmartLoading.hide();
  }
}

// 暴露给父组件
defineExpose({onRegister})

</script>

<template>
  <div class="panel-email">
    <a-form ref="formRef" class="login-form" :model="registerForm" :rules="rules">

      <a-form-item name="email">
        <a-input v-model:value.trim="registerForm.email" placeholder="请输入邮箱"/>
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

      <a-form-item name="emailCode" v-if="emailCodeShowFlag">
        <a-input-group compact>
          <a-input style="width: calc(100% - 110px)" v-model:value="registerForm.emailCode" autocomplete="on"
                   placeholder="请输入邮箱验证码"/>
          <a-button @click="sendEmailCode" class="code-btn" type="primary" :disabled="emailCodeButtonDisabled">
            {{ emailCodeTips }}
          </a-button>
        </a-input-group>
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