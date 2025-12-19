import {api} from '@/service/request.ts'
/**
 * 用户的网络请求
 */
export const postUsersListData = (data: any, params: any) => api.post('user/api/users/query/', data, {params: params})


/**
 * 删除用户
 */
export const deleteUserById = (id: number) => api.delete(`user/api/users/${id}/`)


/**
 * 新增用户
 */
export const addUserData = (data: any) => api.post('user/api/users/', data)


/**
 * 编辑用户
 */
export const editUserData = (id:number, data: any) => api.patch(`user/api/users/${id}/`, data)


/**
 * 针对页面的数据：增删改查
 * @param pageName
 * @param data
 * @param params
 */

export const postPageListData = (pageName: string, data: any, params: any) => api.post(`user/api/${pageName}/query/`, data, {params: params})


export const deletePageById = (pageName: string, id: number) => api.delete(`user/api/${pageName}/${id}/`)

export const addPageData = (pageName: string, data: any) => api.post(`user/api/${pageName}/`, data)

export const editPageData = (pageName: string, id: number, data: any) => api.patch(`user/api/${pageName}/${id}/`, data)