import {api} from '@/service/request.ts'


/**
 * 针对页面的数据：增删改查
 * @param pageName
 * @param data
 * @param params
 */

export const postPageListData = (pageName: string, data: any, params: any) => api.post(`vpn/${pageName}/query/`, data, {params: params})


export const deletePageById = (pageName: string, id: number) => api.delete(`vpn/${pageName}/${id}/`)

export const addPageData = (pageName: string, data: any) => api.post(`vpn/${pageName}/`, data)

export const editPageData = (pageName: string, id: number, data: any) => api.patch(`vpn/${pageName}/${id}/`, data)



/**
 * 获取所有设备
 */
export const getDeviceList = (params?: any) => api.get('vpn/vpndevices/', {params: params})

/**
 * 获取所有区域
 */
export const getRegionList = (params?: any) => api.get('vpn/vpnregions/', {params: params})



export const getVpnLogList = (params: any) => api.get('vpn/vpnmonitors/', {params: params})


// export const getVpnTrafficTimeseries =  (params: any) => api.get('vpn/vpnmonitors/timeseries/', {params: params})
export const getVpnTrafficTimeseries =  (data: any, params: any) => api.post(`vpn/vpnmonitors/query/`, data, {params: params})

export const getVpnRegionSummary = (params: any) => api.get('vpn/vpnaccounts/region/summary/', {params: params})
export const getVpnmonitorsRegionSummary = (params: any) => api.get('vpn/vpnmonitors/region/summary/', {params: params})