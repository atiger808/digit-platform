<template>
  <div class="login">

    <LoginPanel/>

<!--    <div class="login-panel">-->
<!--    <el-card class="login-card">-->
<!--      <h2>登录</h2>-->
<!--      <el-form-->
<!--          label-position="top"-->
<!--          ref="ruleFormRef"-->
<!--          label-width="200px"-->
<!--          class="demo-ruleForm"-->
<!--          :model="loginForm"-->
<!--          :rules="loginRules"-->  `
<!--          @keyup.enter="handleLogin"-->
<!--      >-->
<!--        <el-form-item label="用户名" :label-width="formLabelWidth" prop="username">-->
<!--          <el-input v-model="loginForm.username" autocomplete="off"></el-input>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="密码" :label-width="formLabelWidth" prop="password">-->
<!--          <el-input type="password" v-model="loginForm.password" autocomplete="off"></el-input>-->
<!--        </el-form-item>-->

<!--        <el-form-item>-->
<!--          <el-button-->
<!--              type="primary"-->
<!--              class="login-button"-->
<!--              :loading="loading"-->
<!--              @click="handleLogin"-->
<!--          >-->
<!--            登录-->
<!--          </el-button>-->
<!--        </el-form-item>-->
<!--      </el-form>-->
<!--      <div v-if="errorMessage" class="error">{{ errorMessage }}</div>-->
<!--    </el-card>-->

<!--  </div>-->


  </div>
</template>

<script setup lang="ts">
import {ref, reactive } from 'vue'
import {useRouter} from "vue-router";
import { useLoginStore } from '@/store/login/login.ts'
import LoginPanel from "@/views/login/c-cpns/login-panel.vue";
const authStore = useLoginStore()

const router = useRouter()

const loading = ref(false)
const ruleFormRef = ref(null)
const loginForm = reactive({
  username: 'root',
  password: 'qweasd123456',
})

const loginRules = reactive({
  username: [
    {required: true, message: '请输入用户名', trigger: 'blur'},
    {min: 4, max: 16, message: '要求4-16个字符', trigger: 'blur'},
  ],
  password: [
    {required: true, message: '请输入密码', trigger: 'blur'},
    {min: 4, max: 16, message: '密码要求4-16个字符', trigger: 'blur'},
  ],
})

const errorMessage = ref('')

const handleLogin = () => {
  ruleFormRef.value.validate(async (valid: any) => {
    if (valid) {
      loading.value = true;


      let { success, error } = await authStore.loginAccountAction(loginForm)

      console.log('res ==> ')
      console.log('success: ', success)
      console.log('error: ', error)
      if (!success) {
        errorMessage.value = error
      }
      loading.value = false;
    }
  });
}

</script>

<style scoped lang="scss">

.login {
  display: flex;
  align-items: center;
  justify-content: center;

  width: 100%;
  height: 100%;

  //background: url("../../assets/img/bg.png");
}


//.login-panel {
//  width: 400px;
//  margin-bottom: 150px;
//  align-items: center;
//  justify-content: center;
//
//  .title {
//    text-align: center;
//    margin-bottom: 15px;
//  }
//
//  .icon {
//    display: flex;
//    align-items: center;
//    justify-content: center;
//
//    .text {
//      margin-left: 5px;
//    }
//  }
//
//  .controls {
//    margin-top: 12px;
//    display: flex;
//    justify-content: space-between;
//  }
//
//  .login-btn {
//    margin-top: 10px;
//    width: 100%;
//  }
//
//}

</style>