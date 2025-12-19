// 处理token 获取token 设置token 移除token

import axios from "@/service/request.ts";
import {LOGIN_TOKEN, LOGIN_REFRESH_TOKEN} from "../global/constants.ts";
import { encryptData, decryptData } from "./encrypts.ts";


enum CacheType {
    Local,
    Session
}

class Cache {
    storage: Storage

    constructor(type: CacheType) {
        this.storage = type === CacheType.Local ? localStorage : sessionStorage
    }

    setCache(key: string, value: any) {
        if (value) {
            if (key === LOGIN_TOKEN || key === LOGIN_REFRESH_TOKEN) {
                this.storage.setItem(key, JSON.stringify(value))
            } else {
                this.storage.setItem(key, encryptData(value))
            }


        }
    }

    getCache(key: string) {
        const value = this.storage.getItem(key)
        if (value) {
            if (key === LOGIN_TOKEN || key === LOGIN_REFRESH_TOKEN){
                return JSON.parse(value)
            } else {
                return JSON.parse(decryptData(value))
            }
        }
    }

    removeCache(key: string) {
        this.storage.removeItem(key)
    }

    clear() {
        this.storage.clear()
    }

}

const localCache = new Cache(CacheType.Session)
const sessionCache = new Cache(CacheType.Local)



export const setToken = token => sessionCache.setCache(LOGIN_TOKEN, token)

export const getToken = () => sessionCache.getCache(LOGIN_TOKEN)

export const removeToken = () => sessionCache.removeCache(LOGIN_TOKEN)

export const setRefreshToken = token => sessionCache.setCache(LOGIN_REFRESH_TOKEN, token)
export const getRefreshToken = () => sessionCache.getCache(LOGIN_REFRESH_TOKEN)

export const removeRefreshToken = () => sessionCache.removeCache(LOGIN_REFRESH_TOKEN)

export const getUser = () => sessionCache.getCache('user')
export const setUser = (user) => sessionCache.setCache('user', typeof user === 'string' ? user : JSON.stringify(user))
export const removeUser = () => sessionCache.removeCache('user')

export const refreshToken = async () => {
    const refresh = sessionCache.getCache(LOGIN_REFRESH_TOKEN)
    console.log('refreshToken =>')
    console.log('refresh: ' + refresh)
    if (!refresh) {
        return
    }
    let res = await axios.post('user/token/refresh/', {refresh: refresh})
    console.log("refreshToken res ==>")
    console.log(res)
    if (res.code === 200) {
        sessionCache.setCache(LOGIN_TOKEN, res.data.access)
        sessionCache.setCache(LOGIN_REFRESH_TOKEN, res.data.refresh)
    } else {
        sessionCache.removeCache(LOGIN_TOKEN)
        sessionCache.removeCache(LOGIN_REFRESH_TOKEN)
    }
}


// 检查 Token 是否有效
export function isTokenValid() {
    const token = getToken()
    if (!token) return false

    try {
        const payload = JSON.parse(atob(token.split('.')[1]))
        return payload.exp * 1000 > Date.now()
    } catch (e) {
        return false
    }
}



export { localCache, sessionCache }

