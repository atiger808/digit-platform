import {defineStore} from "pinia";
import {
    registerAccount,
} from '@/service/register/register.ts'
import type {IAccount, IPhone} from '@/types/types'
import {localCache, sessionCache} from '@/utils/cache.ts'
import useMainStore from '@/store/main/main.ts'
import router from '@/router/index.ts'
import {
    LOGIN_TOKEN,
    LOGIN_REFRESH_TOKEN,
    USER_INFO,
    PROFILE,
    USER_MENUS,
    PERMISSIONS
} from "@/global/constants.ts";
import {errorParse} from "@/utils/errorParse.ts";


interface IRegisterState {
    token: string
    userInfo: any
    profile: any
    userMenus: any
    permissions: string[],
    is_staff: boolean
}

export const useRegisterStore = defineStore('register', {
    state: (): IRegisterState => ({
        token: sessionCache.getCache(LOGIN_TOKEN) ?? '',
        userInfo: sessionCache.getCache(USER_INFO) ?? {},
        profile: sessionCache.getCache(PROFILE) ?? {},
        userMenus: sessionCache.getCache(USER_MENUS) ?? [],
        permissions: sessionCache.getCache(PERMISSIONS) ?? [],
        is_staff: false
    }),
    actions: {

        async registerAccountAction(account: IAccount) {
            try {
                const registerResult = await registerAccount(account)
                console.log('registerResult', registerResult)
                sessionCache.setCache(USER_INFO, account)
                router.push('/login')
                // 1.注册成功
                return {success: true, error: ''}
            } catch (error) {
                console.error('注册失败:', error)
                const errorInfo = errorParse(error)
                console.log('errorInfo', errorInfo)

                return {success: false, error: errorInfo || '注册失败'}
            }
        }

    }
})