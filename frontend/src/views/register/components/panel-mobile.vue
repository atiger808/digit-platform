<script setup lang="ts">
import {message, notification, Button} from 'ant-design-vue';
import {onMounted, onUnmounted, reactive, ref, watch} from 'vue';
import {ElLoading, ElMessage} from "element-plus";
import type {FormInstance} from 'element-plus'
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
  mobile: '',
  code: '',
  mobileCode: '',
  key: '',
  identifier_type: 'mobile',
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
  mobile: [{required: true, message: '手机号不能为空'}, {
    pattern: /^1[3-9]\d{9}$/,
    message: '请输入正确的手机号',
    trigger: 'change'
  }],
  mobileCode: [{required: true, message: '验证码不能为空'}],
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

  formRef.value?.validate()?.then(async () => {
    try {
      // SmartLoading.show();
      console.log('registerForm: ', registerForm)
      registerForm.identifier = registerForm.mobile
      registerForm.code = registerForm.mobileCode;
      registerForm.key = registerForm.mobile
      if (!registerForm.mobile) {
        message.error('手机号不能为空');
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

//--------------------- 手机验证码 ---------------------------------

const mobileCodeShowFlag = ref(true);
let mobileCodeTips = ref('获取手机验证码');
let mobileCodeButtonDisabled = ref(false);
// 定时器
let countDownTimerSms = ref<number | null>(null)

// 开始倒计时
function runCountDownSms() {
  mobileCodeButtonDisabled.value = true;
  let countDown = 60;
  mobileCodeTips.value = `${countDown}秒后重新获取`;
  countDownTimerSms.value = setInterval(() => {
    if (countDown > 1) {
      countDown--;
      mobileCodeTips.value = `${countDown}秒后重新获取`;
    } else {
      clearInterval(countDownTimerSms.value);
      countDownTimerSms.value = 0;
      mobileCodeButtonDisabled.value = false;
      mobileCodeTips.value = '获取验证码';
    }
  }, 1000);
}


// 发送手机验证码
async function sendSmsCode() {
  try {
    // SmartLoading.show();
    if (!registerForm.mobile) {
      message.error('手机号不能为空');
      return;
    }
    let result = await api.post('user/api/sms-code/', {mobile: registerForm.mobile})
    console.log("result: ", result)
    message.success(result.data.detail || '验证码发送成功!请查看手机验证码~');
    runCountDownSms();
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
  <div class="panel-mobile">
    <a-form ref="formRef" class="login-form" :model="registerForm" :rules="rules">
      <a-form-item name="mobile">
        <a-input v-model:value.trim="registerForm.mobile" placeholder="请输入手机号"/>
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

      <a-form-item name="mobileCode" v-if="mobileCodeShowFlag">
        <a-input-group compact>
          <a-input style="width: calc(100% - 110px)" v-model:value="registerForm.mobileCode" autocomplete="on"
                   placeholder="请输入手机验证码"/>
          <a-button @click="sendSmsCode" class="code-btn" type="primary" :disabled="mobileCodeButtonDisabled">
            {{ mobileCodeTips }}
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