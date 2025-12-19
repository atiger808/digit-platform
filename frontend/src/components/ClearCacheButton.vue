<!-- components/ClearCacheButton.vue -->
<template>
  <el-tooltip content="清除浏览器缓存" placement="top">
    <el-button
      type="danger"
      :icon="Delete"
      circle
      :loading="loading"
      @click="handleClearCache"
    />
  </el-tooltip>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {localCache, sessionCache} from '@/utils/cache.ts'
import {
    LOGIN_TOKEN,
    LOGIN_REFRESH_TOKEN,
    USER_INFO,
    IS_REMEMBER,
    PROFILE,
    USER_MENUS,
    PERMISSIONS,
    FIRST_MENU
} from "@/global/constants.ts";
export default defineComponent({
  name: 'ClearCacheButton',
  setup() {
    const loading = ref(false)

    const clearBrowserCache = async () => {
      try {
        const user_info = sessionCache.getCache(USER_INFO)
        const is_remember = sessionCache.getCache(IS_REMEMBER)
        // 清除 localStorage
        localStorage.clear()

        // 清除 sessionStorage
        sessionStorage.clear()

        // 清除 cookies (需要遍历所有cookie)
        const cookies = document.cookie.split(';')
        for (const cookie of cookies) {
          const eqPos = cookie.indexOf('=')
          const name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie
          document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`
        }
        sessionCache.setCache(USER_INFO, user_info)
        sessionCache.setCache(IS_REMEMBER, is_remember)
        // 强制刷新页面
        window.location.reload()
      } catch (error) {
        console.error('清除缓存失败:', error)
        throw error
      }
    }

    const handleClearCache = async () => {
      try {
        await ElMessageBox.confirm(
          '确定要清除所有浏览器缓存吗？这将包括本地存储、会话存储和Cookies。',
          '警告',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        loading.value = true
        await clearBrowserCache()
        ElMessage.success('缓存清除成功！')
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('清除缓存失败')
        }
      } finally {
        loading.value = false
      }
    }

    return {
      Delete,
      loading,
      handleClearCache
    }
  }
})
</script>