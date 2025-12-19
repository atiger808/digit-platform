// 二次封装
// 访问地址
//请求拦截器
// 响应拦截器
// import axios,  {AxiosInstance, AxiosRequestConfig, AxiosResponse} from 'axios'
import {get} from 'lodash-es'
import {useAuthStore} from "@/store/auth.ts";
import {
    getToken,
    setToken,
    removeToken,
    getRefreshToken,
    removeRefreshToken,
    removeUser,
    refreshToken
} from "@/utils/cache";

import {LOGIN_TOKEN} from '@/global/constants.ts'

import router from '@/router/index.ts'
// import { useRouter } from "vue-router"
// const router = useRouter()

import axios from 'axios'
import * as Axios from 'axios'
import {ElMessage} from "element-plus";
import {sessionCache} from "@/utils/cache";

type AxiosInstance = Axios.AxiosInstance
type AxiosRequestConfig = Axios.AxiosRequestConfig
type AxiosResponse = Axios.AxiosResponse


// 访问地址
export const api: AxiosInstance = axios.create({
    // baseURL: 'http://127.0.0.1:8000/',
    // baseURL: 'http://vpn.newdmy.com:10889/',
    baseURL: import.meta.env.VITE_API_URL,
});

// 添加isCancel方法
api.isCancel = axios.isCancel;

// 添加CancelToken
api.CancelToken = axios.CancelToken;

// 请求拦截器
api.interceptors.request.use(
    (config: AxiosRequestConfig | any) => {
        // 请求头携带token
        // config.headers.Authorization = localStorage.getItem('token')
        const token = getToken()
        if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
);

// 添加响应拦截器
api.interceptors.response.use(
    // 响应成功
    (response: AxiosResponse | any) => response,

    // 响应失败
    async (error) => {
        console.log('error ==> ',error)

        const originalRequest = error.config;

        const status = get(error, 'response.status');

        console.log('error ==> ', error)
        console.log('error.message ==> ', error.message)
        console.log('error.response ==> ', error.response)
        console.log('status ==> ', status)

        if (error.message.indexOf('timeout') != -1) {
            error.message = '网络请求超时';
        } else if (error.message == 'Network Error') {
            error.message = '网络连接错误';
        } else if (error.response && error.response.status === 401 &&
            !originalRequest.url.includes('user/api/auth/login/') &&
            !originalRequest.url.includes('user/api/auth/register/')) {
            sessionCache.removeCache(LOGIN_TOKEN)
            console.log("router", router)
            router.push("/login")
        } else {
            switch (status) {
                case 400:
                    error.message = error.response.data.detail || '请求错误';
                    break;
                case 401:
                    error.message = error.response.data.detail || '登录授权过期，请重新登录';
                    break;
                case 403:
                    error.message = error.response.data.detail || '拒绝访问';
                    break;
                case 404:
                    error.message = error.response.data.detail || `请求地址出错: ${error.response.config.url}`;
                    break;
                case 408:
                    error.message = error.response.data.detail || '请求超时';
            }
        }
        console.log('error.message ==> ', error.message)

        return Promise.reject(error);
    }
);


export default api
