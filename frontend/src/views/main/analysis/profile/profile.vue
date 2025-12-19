<script setup lang="ts">
import {ref, reactive, onMounted, watch} from 'vue';
import {ElMessage, ElMessageBox, type FormInstance, type FormRules} from 'element-plus';
import {User} from '@element-plus/icons-vue';
import {storeToRefs} from "pinia";

import {useLoginStore} from "@/store/login/login.ts";
import type {UserProfile, ChangePasswordData} from '@/types/user';
import {formatUTC} from "@/utils/format.ts";
import {errorParse} from "@/utils/errorParse.ts";
import WatermarkWithTime from "@/components/WatermarkWithTime.vue"

// 用户信息
const userProfile = ref<UserProfile>({
  id: 0,
  username: '',
  real_name: '',
  email: '',
  mobile: '',
  profile: {}
});

// 编辑状态
const isEditing = ref(false);
const editForm = reactive({
  real_name: '',
  email: '',
  mobile: ''
});

// 密码表单
const passwordForm = reactive<ChangePasswordData>({
  old_password: '',
  new_password: '',
  confirm_password: ''
});


// 发起action
const loginStore = useLoginStore();
const {profile} = storeToRefs(loginStore)
userProfile.value = profile.value

loadUserProfile()


const passwordFormRef = ref<FormInstance>();

// 密码验证规则
const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的密码不一致'));
  } else {
    callback();
  }
};

const passwordRules: FormRules = {
  old_password: [
    {required: true, message: '请输入当前密码', trigger: 'blur'}
  ],
  new_password: [
    {required: true, message: '请输入新密码', trigger: 'blur'},
    {min: 8, message: '密码长度不能少于8位', trigger: 'blur'}
  ],
  confirm_password: [
    {required: true, message: '请确认新密码', trigger: 'blur'},
    {validator: validateConfirmPassword, trigger: 'blur'}
  ]
};

// 加载用户信息
function loadUserProfile() {
  try {
    const profile = loginStore.loadLocalUserProfile()

    console.log('loadUserProfile', profile)

    userProfile.value = profile

    if (!profile) {
      const {success, error} = loginStore.getUserProfileAction()
      console.log('getUserProfileAction', success, error)
      if (error) {
        ElMessage.error(error || "获取用户信息失败")
      }
    }


    // 如果有默认头像URL，可以在这里设置
    // if (!data.avatar) {
    //   userProfile.value.avatar = '/default-avatar.png';
    // }
  } catch (error) {
    ElMessage.error('获取用户信息失败');
  }
}

function isEmail(email: string) {
  return /^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/.test(email);
}

function isMobile(mobile: string) {
  return /^1[3-9]\d{9}$/.test(mobile);
}


// 开始编辑
const startEditing = () => {
  editForm.real_name = userProfile.value.real_name;
  editForm.email = userProfile.value.email;
  editForm.mobile = userProfile.value.mobile;
  isEditing.value = true;
};

// 取消编辑
const cancelEditing = () => {
  isEditing.value = false;
};

// 保存个人信息
const saveProfile = async () => {
  try {
    if (!editForm.real_name) {
      ElMessage.error('请输入昵称');
      return;
    } else if (!editForm.email) {
      ElMessage.error('请输入邮箱');
      return;
    } else if (!editForm.mobile) {
      ElMessage.error('请输入手机号');
      return;
    }

    if (editForm.real_name.length > 50) {
      ElMessage.error('昵称长度不能超过50个字符')
      return;
    }
    if (!isEmail(editForm.email)) {
      ElMessage.error('邮箱格式不正确');
      return;
    }
    if (!isMobile(editForm.mobile)) {
      ElMessage.error('手机号格式不正确');
      return;
    }

    const {success, error} = await loginStore.updateUserProfileAction({
      real_name: editForm.real_name,
      email: editForm.email,
      mobile: editForm.mobile
    });
    console.log('success: ', success)
    console.log('error: ', error)
    if (success) {
      isEditing.value = false;
      ElMessage.success('个人信息更新成功');
      loadUserProfile()
    } else {
      ElMessage.error(error || '个人信息更新失败');
    }

  } catch (error) {
    ElMessage.error('个人信息更新失败');
  }
};

// 处理头像变更
const handleAvatarChange = async (file: any) => {
  const isImage = file.raw.type.includes('image');
  const isLt2M = file.raw.size / 1024 / 1024 < 2;

  if (!isImage) {
    ElMessage.error('只能上传图片文件');
    return;
  }

  if (!isLt2M) {
    ElMessage.error('头像图片大小不能超过2MB');
    return;
  }

  try {
    const formData = new FormData();
    formData.append('avatar', file.raw);
    const response = await loginStore.uploadAvatarAction(formData);
    console.log('uploadAvatar response', response)
    // userProfile.value.avatar = response.avatar_url;
    ElMessage.success('头像上传成功');
    loadUserProfile()
  } catch (error) {
    console.log('uploadAvatar error', error)
    ElMessage.error('头像上传失败');
  }
};

// 提交密码修改
const submitPassword = async () => {
  try {
    await passwordFormRef.value?.validate();

    await ElMessageBox.confirm('确定要修改密码吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });

    await loginStore.changePasswordAction(passwordForm);

    ElMessage.success('密码修改成功');
    resetPasswordForm();


  } catch (error) {
    console.log('submitPassword error', error)

    const errorInfo = errorParse(error)

    console.log('errorInfo', errorInfo)

    if (error !== 'cancel') {
      ElMessage.error(errorInfo || '密码修改失败');
    }
  }
};

// 重置密码表单
const resetPasswordForm = () => {
  passwordFormRef.value?.resetFields();
};


watch(
    () => profile.value,
    (newValue) => {
      console.log('profile changed', newValue)
      userProfile.value = newValue
      // 如果有默认头像URL，可以在这里设置
      // if (!newValue.avatar) {
      //   userProfile.value.avatar = '/default-avatar.png';
      // }
    },
    {deep: true}
)

</script>


<template>
  <WatermarkWithTime>
    <div class="profile-container">
      <el-card class="profile-card">
        <template #header>
          <div class="card-header">
            <h2>个人信息</h2>
          </div>
        </template>

        <!-- 个人信息展示与编辑区域 -->
        <div class="profile-content">
          <!-- 头像区域 -->
          <div class="avatar-section">
            <el-upload
                class="avatar-uploader"
                :show-file-list="false"
                :auto-upload="false"
                :on-change="handleAvatarChange"
                accept="image/*"
            >
              <img v-if="userProfile.profile?.avatar" :src="userProfile.profile.avatar" class="avatar"/>
              <el-icon v-else class="avatar-uploader-icon">
                <User/>
              </el-icon>
              <div class="avatar-hover-text">点击更换头像</div>
            </el-upload>
          </div>

          <!-- 基本信息区域 -->
          <div class="info-section">
            <el-descriptions :column="1" border>

              <el-descriptions-item label="账号">
                <el-tag>{{ userProfile.username }}</el-tag>
              </el-descriptions-item>

              <el-descriptions-item label="角色">
                <el-tag>{{ userProfile.role_name }}</el-tag>
              </el-descriptions-item>

              <el-descriptions-item label="部门">
                <el-tag>{{ userProfile.department_name }}</el-tag>
              </el-descriptions-item>

              <el-descriptions-item label="上次登录日期">
                <el-tag>{{ formatUTC(userProfile.last_login_time) }}</el-tag>
              </el-descriptions-item>

              <el-descriptions-item label="加入日期">
                <el-tag>{{ formatUTC(userProfile.date_joined) }}</el-tag>
              </el-descriptions-item>

              <el-descriptions-item label="昵称">
                <el-input
                    v-if="isEditing"
                    v-model="editForm.real_name"
                    placeholder="请输入昵称"
                />
                <span v-else>{{ userProfile.real_name || '未设置' }}</span>
              </el-descriptions-item>

              <el-descriptions-item label="邮箱">
                <el-input
                    v-if="isEditing"
                    v-model="editForm.email"
                    placeholder="请输入邮箱"
                    type="email"
                />
                <span v-else>{{ userProfile.email || '未设置' }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="手机号">
                <el-input
                    v-if="isEditing"
                    v-model="editForm.mobile"
                    placeholder="请输入手机号"
                    type="tel"
                />
                <span v-else>{{ userProfile.mobile || '未设置' }}</span>
              </el-descriptions-item>
            </el-descriptions>

            <!-- 操作按钮 -->
            <div class="action-buttons">
              <el-button
                  v-if="!isEditing"
                  type="primary"
                  @click="startEditing"
              >
                编辑信息
              </el-button>

              <template v-else>
                <el-button type="success" @click="saveProfile">保存</el-button>
                <el-button @click="cancelEditing">取消</el-button>
              </template>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 修改密码卡片 -->
      <el-card class="password-card">
        <template #header>
          <div class="card-header">
            <h2>修改密码</h2>
          </div>
        </template>

        <el-form
            :model="passwordForm"
            :rules="passwordRules"
            ref="passwordFormRef"
            label-width="120px"
        >
          <el-form-item label="当前密码" prop="old_password">
            <el-input
                v-model="passwordForm.old_password"
                type="password"
                show-password
                placeholder="请输入当前密码"
            />
          </el-form-item>

          <el-form-item label="新密码" prop="new_password">
            <el-input
                v-model="passwordForm.new_password"
                type="password"
                show-password
                placeholder="请输入新密码"
            />
          </el-form-item>

          <el-form-item label="确认密码" prop="confirm_password">
            <el-input
                v-model="passwordForm.confirm_password"
                type="password"
                show-password
                placeholder="请再次输入新密码"
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="submitPassword">提交修改</el-button>
            <el-button @click="resetPasswordForm">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </WatermarkWithTime>
  >
</template>

<style scoped>
.profile-container {
  //max-width: 1000px;
  margin: 0 auto;
  padding: 0px;
}

.profile-card, .password-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profile-content {
  display: flex;
  gap: 30px;
}

.avatar-section {
  flex: 0 0 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.info-section {
  flex: 1;
}

.avatar-uploader {
  width: 150px;
  height: 150px;
  border: 1px dashed var(--el-border-color);
  border-radius: 50%;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
  margin-bottom: 15px;
}

.avatar-uploader:hover {
  border-color: var(--el-color-primary);
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 150px;
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-hover-text {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  text-align: center;
  padding: 5px;
  transform: translateY(100%);
  transition: transform 0.3s;
}

.avatar-uploader:hover .avatar-hover-text {
  transform: translateY(0);
}

.action-buttons {
  margin-top: 20px;
  text-align: right;
}

@media (max-width: 768px) {
  .profile-content {
    flex-direction: column;
  }

  .avatar-section {
    margin-bottom: 20px;
  }
}
</style>