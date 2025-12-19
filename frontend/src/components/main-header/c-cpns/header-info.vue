<script setup lang="ts">
import {ref} from 'vue'
import {useLoginStore} from "@/store/login/login.ts";
import router from '@/router/index.ts'
import {useTabsStore} from '@/store/main/tabs/tabs.ts'
import type {UserProfile} from '@/types/user';
import {storeToRefs} from "pinia";
import {watch} from "vue";
import ClearCacheButton from '@/components/ClearCacheButton.vue'
import ToolPackage from "@/components/ToolPackage.vue";
// 用户信息
const userProfile = ref<UserProfile>({
  id: 0,
  username: '',
  real_name: '',
  email: '',
  profile: {}
});

// 发起action
const loginStore = useLoginStore()
const {profile} = storeToRefs(loginStore)
userProfile.value = profile.value
loginStore.loadLocalUserProfile()


const handleExitClick = () => {
  console.log('退出系统')
  loginStore.logout()
  loginStore.resetMenu()
  const tabsStore = useTabsStore()
  tabsStore.resetTabs()


  console.log("tabs", tabsStore.tabs)
  console.log("currentTab", tabsStore.currentTab)
}

const handleProfileClick = () => {
  console.log('个人中心')
  router.push('/main/analysis/profile')
}

watch(
    () => profile.value,
    (newVal) => {
      userProfile.value = newVal
    },
    {deep: true}
)


</script>

<template>

  <div class="header-info">

    <!--    1.操作小图标-->
    <div class="operation">
      <!--    工具包-->
<!--      <span>-->
<!--        <ToolPackage />-->
<!--      </span>-->
      <span>
        <clear-cache-button/>
      </span>
      <span>
        <el-icon> <Bell/></el-icon>
      </span>
      <span>
        <el-icon> <ChatDotRound/></el-icon>
      </span>
      <span>
        <el-icon> <Search/></el-icon>
      </span>

      <span>
        <span class="dot"></span>
        <el-icon> <Postcard/></el-icon>
      </span>
    </div>

    <!--    2.个人信息-->
    <div class="info">
      <el-dropdown>
        <span class="user-info">

          <el-avatar v-if="userProfile.profile.avatar" :size="30" :src="userProfile.profile.avatar" class="avatar"/>
          <el-avatar v-else :size="30" src="/src/assets/img/default-avatar.png" class="avatar"/>
          <!--          <el-avatar v-else :size="30" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" class="avatar"/>-->

          <span class="name">{{ userProfile.real_name }}</span>
        </span>

        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="handleProfileClick">
              <el-icon>
                <User/>
              </el-icon>
              <span>个人中心</span>
            </el-dropdown-item>

            <el-dropdown-item divided @click="handleProfileClick">
              <el-icon>
                <Edit/>
              </el-icon>
              <span>修改密码</span>
            </el-dropdown-item>

            <el-dropdown-item @click="handleExitClick">
              <el-icon>
                <CircleClose/>
              </el-icon>
              <span>退出系统</span>
            </el-dropdown-item>

          </el-dropdown-menu>
        </template>

      </el-dropdown>
    </div>


  </div>
</template>

<style scoped lang="scss">

.header-info {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  height: 100%;
  padding-right: 20px;
}


.operation {
  display: inline-flex;
  margin-right: 20px;

  span {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 35px;

    &:hover {
      background-color: #f2f2f2;
    }

    i {
      font-size: 20px;
    }

    .dot {
      position: absolute;
      top: 3px;
      right: 3px;
      z-index: 10;
      width: 6px;
      height: 6px;
      background: red;
      border-radius: 100%;
    }

  }
}


.info {
  .user-info {
    display: flex;
    align-items: center;
    cursor: pointer;

    .name {
      margin-left: 5px;
    }
  }
}

.info {
  :global(.el-dropdown-menu__item) {
    line-height: 36px !important;
    padding: 6px 22px;
  }
}


</style>