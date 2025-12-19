import axios from "axios";


class HYRequest {
    constructor(baseURL, timeout = 10000) {
        this.instance = axios.create({
            baseURL,
            timeout
        })

        // 2. 添加实例请求拦截器
        this.instance.interceptors.request.use(config => {
            // 拦截后需要将拦截下来的请求数据返回
            return config
        }, err => {
            return err
        })

        // 2. 添加实例响应拦截器
        this.instance.interceptors.response.use(res => {
            // 拦截后需要将拦截下来处理成的结果返回
        })
    }
}

export default HYRequest;


