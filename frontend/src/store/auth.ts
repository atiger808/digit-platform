import {defineStore} from 'pinia'
import {ref, computed} from 'vue'
import {useRouter} from "vue-router"
import router from '@/router'
import api from '@/service/request.ts'
import {
    getToken,
    setToken,
    getRefreshToken,
    setRefreshToken,
    removeToken,
    removeRefreshToken,
    getUser,
    setUser,
    removeUser,


} from "@/utils/cache.ts"


export const useAuthStore = defineStore('auth', () => {
    // 状态
    const token = ref(getToken())
    const refreshToken = ref(getRefreshToken())
    const user = ref(getUser())
    const returnUrl = ref(null)
    // const router = useRouter()

    // Getter
    const isAuthenticated = computed(() => !!token.value)
    const currentUser = computed(() => user.value ? JSON.parse(user.value) : null)

    // Actions
    const login = async (username, password) => {
        try {
            const response = await api.post('user/login/', {
                username: username,
                password: password
            })

            // 存储 token 和用户信息
            token.value = response.data.access
            refreshToken.value = response.data.refresh
            user.value = JSON.stringify(response.data.user)

            setToken(response.data.access)
            setRefreshToken(response.data.refresh)
            setUser(response.data.user)

            // 重定向到之前的路由或首页
            router.push(returnUrl.value || '/')
            return {success: true}
        } catch (error) {
            console.error('登录失败:', error)
            return {
                success: false,
                error: error.response?.data?.detail || '登录失败，请检查用户名和密码'
            }
        }
    }

    const logout = () => {
        token.value = null
        refreshToken.value = null
        user.value = null
        removeToken()
        removeRefreshToken()
        removeUser()
        // 重定向到登录页
        router.push('/login')
    }

    const fetchUser = async () => {
        if (!token.value) return

        try {
            const response = await api.get('/profile/')
            user.value = JSON.stringify(response.data)
            setUser(response.data)
        } catch (error) {
            if (error.response?.status === 401) {
                logout()
            }
            console.error('获取用户信息失败:', error)
        }
    }

    const setReturnUrl = (url) => {
        returnUrl.value = url
    }

    return {
        token,
        refreshToken,
        user,
        returnUrl,
        isAuthenticated,
        currentUser,
        login,
        logout,
        fetchUser,
        setReturnUrl
    }
})