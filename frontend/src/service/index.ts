import {BASE_URL, TIME_OUT} from "@/service/config";
import {sessionCache} from "@/utils/cache.ts";
import {LOGIN_TOKEN} from "@/global/constants.ts";
import HYRequest from '@/service/request'

const hyRequest = new HYRequest({
    baseURL: BASE_URL,
    timeout: TIME_OUT,
    withCredentials: true,
    interceptors: {
        requestSuccessFn: (config) => {
            // 拦截到请求，携带token
            const token = sessionCache.getCache(LOGIN_TOKEN)
            if (token) {
                if (config.headers) {
                    config.headers.Authorization = `Bearer ${token}`
                }
            }
            return config
        },
        requestFailureFn: (err) => {}
    }
})

export default hyRequest