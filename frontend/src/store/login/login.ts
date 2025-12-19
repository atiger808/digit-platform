import {defineStore} from "pinia";
import {type RouteRecordRaw} from 'vue-router'
import {
    accountLoginRequest,
    phoneLoginRequest,
    getUserMenus,
    getUserInfoById,
    getUserMenusByRoleId
} from '@/service/login/login'
import {changePassword, getUserProfile, updateUserProfile, uploadAvatar} from "../../service/main/analysis/analysis.ts";
import type {IAccount, IPhone} from '@/types/types'
import {localCache, sessionCache} from '@/utils/cache.ts'
import {mapMenusToRoutes, mapMenusToPermissions} from "@/utils/map-menus.ts";
import useMainStore from '@/store/main/main.ts'
import router from '@/router/index.ts'
import {
    LOGIN_TOKEN,
    LOGIN_REFRESH_TOKEN,
    USER_INFO,
    PROFILE,
    USER_MENUS,
    PERMISSIONS,
    FIRST_MENU
} from "@/global/constants.ts";
import {errorParse} from "@/utils/errorParse.ts";


interface ILoginState {
    token: string
    userInfo: any
    profile: any
    userMenus: any[]
    permissions: string[]
    is_staff: boolean
}

export const useLoginStore = defineStore('login', {
    state: (): ILoginState => ({
        token: sessionCache.getCache(LOGIN_TOKEN) ?? '',
        userInfo: sessionCache.getCache(USER_INFO) ?? {},
        profile: sessionCache.getCache(PROFILE) ?? {},
        userMenus: sessionCache.getCache(USER_MENUS) ?? [],
        permissions: sessionCache.getCache(PERMISSIONS) ?? [],
        is_staff: false
    }),
    actions: {

        async loginAccountAction(account: IAccount) {
            try {
                // 1.账号登录获取token等信息
                const loginResult = await accountLoginRequest(account)
                const id = loginResult.data.user.id
                this.is_staff = loginResult.data.user.is_staff
                this.token = loginResult.data.access
                this.refresh = loginResult.data.refresh


                // 2.进行本地缓存
                sessionCache.setCache(LOGIN_TOKEN, this.token)
                sessionCache.setCache(LOGIN_REFRESH_TOKEN, this.refresh)


                // 3.根据角色请求用户的权限（菜单menus）
                this.getUserMenusAction()

                // 4.请求所有roles,departments数据
                const mainStore = useMainStore()
                mainStore.fetchListDataAction(this.is_staff)


                // 请求个人信息
                this.getUserProfileAction()


                // 5.页面跳转（main页面）
                router.push('/main')
                return {success: true, error: '', attempts: ''}
            } catch (error) {
                console.error('登录失败:', error)
                let errorInfo = errorParse(error)
                console.log('errorInfo', errorInfo)
                let attempts= ''
                if (error.response.data.hasOwnProperty('attempts')) {
                    attempts = error.response.data.attempts
                }
                return { success: false, error: errorInfo || '登录失败，请检查用户名和密码', attempts: attempts}
            }

        },

        async loginPhoneAction(phone: IPhone) {
            try {
                // 1.手机登录获取token等信息
                const loginResult = await phoneLoginRequest(phone)
                const id = loginResult.data.user.id
                this.token = loginResult.data.access
                this.refresh = loginResult.data.refresh
                console.log('this.token', this.token)
                console.log('this.refresh', this.refresh)
                console.log('user.id', id)
                // 2.进行本地缓存
                sessionCache.setCache(LOGIN_TOKEN, this.token)
                sessionCache.setCache(LOGIN_REFRESH_TOKEN, this.refresh)

                this.userMenus = [
                    {
                        path: '/main/analysis/overview',
                        name: 'Overview',
                        component: () => import('@/views/main/analysis/overview/overview.vue'),
                        meta: {title: '系统总览'}
                    },
                    {
                        path: '/main/analysis/dashboard',
                        name: 'Dashboard',
                        component: () => import('@/views/main/analysis/dashboard/dashboard.vue'),
                    }
                ]

                // // 2.获取登录用户的详细信息（role信息）
                // const userInfoResult = await getUserInfoById(id)
                // const userInfo = userInfoResult.data
                // this.userInfo = userInfo
                //
                // // 3.根据角色请求用户的权限（菜单menus）
                // const userMenusResult = await getUserMenusByRoleId(this.userInfo.role.id)
                // const userMenus = userMenusResult.data
                // this.userMenus = userMenus

                sessionCache.setCache(USER_MENUS, this.userMenus)

                // 重要: 动态添加路由
                const routes = mapMenusToRoutes(this.userMenus)
                console.log('routes', routes)
                routes.forEach(route => router.addRoute('Main', route))
                router.push('/main')
                return {success: true, error: ''}

            } catch (error) {
                console.error('登录失败:', error)
                return {
                    success: false,
                    error: error.response?.data?.detail || '登录失败，请检查用户名和密码'
                }
            }
        },


        async getUserMenusAction() {
            try {
                // 获取用户菜单
                const userMenusResult = await getUserMenus();
                console.log('userMenusResult', userMenusResult)
                const userMenus = userMenusResult.data.data
                this.userMenus = userMenus
                sessionCache.setCache(USER_MENUS, this.userMenus)

                // 重要：获取用户所有按钮的权限
                const permissions = mapMenusToPermissions(this.userMenus)
                this.permissions = permissions
                sessionCache.setCache(PERMISSIONS, this.permissions)

                // 重要: 动态添加路由
                const routes = mapMenusToRoutes(this.userMenus)
                console.log('routes', routes)
                routes.forEach(route => router.addRoute('Main', route))

                return {success: true, error: ''}
            } catch (error) {
                console.error('获取用户菜单失败:', error)
                return {
                    success: false,
                    error: error.response?.data?.detail|| '获取用户菜单失败'
                }
            }
        },

        async getUserProfileAction() {
            try {
                const userProfileResult = await getUserProfile();
                const profile = userProfileResult.data
                this.profile = profile
                sessionCache.setCache(PROFILE, profile)
                console.log('获取profile success')
                return {success: true, error: ''}
            } catch (error) {
                console.error('获取用户信息失败:', error)
                return {
                    success: false,
                    error: error.response?.data?.detail || '获取用户信息失败'
                }
            }
        },

        async updateUserProfileAction(data: any) {
            try {
                const userProfileResult = await updateUserProfile(data);
                this.getUserProfileAction()
                return {success: true, error: ''}
            } catch (error) {
                console.error('更新用户信息失败:', error)
                let errorInfo = errorParse(error)
                return {
                    success: false,
                    error: errorInfo || '更新用户信息失败'
                }
            }
        },


        async uploadAvatarAction(formData: any) {
            try {
                const userProfileResult = await uploadAvatar(formData);
                const profile = userProfileResult.data
                this.getUserProfileAction()
                return {success: true, error: ''}
            } catch (error) {
                console.error('上传头像失败:', error)
                return {
                    success: false,
                    error: error || '上传头像失败'
                }
            }
        },


        async changePasswordAction(data: any) {
            const userProfileResult = await changePassword(data);
            userInfo = this.getUserInfo()
            delete userInfo.password
            sessionCache.setCache(USER_INFO, userInfo)

            this.getUserProfileAction()
        },


        logout() {
            sessionCache.removeCache(LOGIN_TOKEN)
            sessionCache.removeCache(LOGIN_REFRESH_TOKEN)
            sessionCache.removeCache(USER_MENUS)
            sessionCache.removeCache(PROFILE)
            sessionCache.removeCache(PERMISSIONS)
            sessionCache.removeCache(FIRST_MENU)
            console.log('logout success')
            router.push('/login')
        },

        resetMenu() {
            this.userMenus = []
        },

        saveUserInfo(account: IAccount) {
            sessionCache.setCache(USER_INFO, account)
        },

        clearUserInfo() {
            sessionCache.removeCache(USER_INFO)
        },

        getUserInfo() {
            const userInfo = sessionCache.getCache(USER_INFO)
            self.userInfo = userInfo
            return userInfo
        },

        loadLocalUserProfile() {
            const profile = sessionCache.getCache(PROFILE)
            self.profile = profile
            return profile
        },

        async loadLocalCacheAction() {
            const token = sessionCache.getCache(LOGIN_TOKEN)
            const userMenus = sessionCache.getCache(USER_MENUS)

            if (token && userMenus) {
                this.token = token
                this.userMenus = userMenus

                // 1.请求所有roles,departments数据
                const mainStore = useMainStore()
                mainStore.fetchListDataAction()

                const {listMenus} = mainStore

                console.log('listMenus', listMenus)
                console.log('userMenus', userMenus)


                // 2.获取用户所有按钮的权限
                const permissions = mapMenusToPermissions(userMenus)
                this.permissions = permissions

                sessionCache.setCache(USER_MENUS, this.userMenus)
                sessionCache.setCache(PERMISSIONS, this.permissions)

                // 重要: 动态添加路由
                const routes = mapMenusToRoutes(this.userMenus)
                console.log('routes', routes)
                routes.forEach(route => router.addRoute('Main', route))
            }
        }

    }
})