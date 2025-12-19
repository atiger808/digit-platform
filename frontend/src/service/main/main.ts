import {api} from '@/service/request.ts'

/**
 * 获取所有角色
 */
export const getRolesList = () => api.get('user/api/roles/', {params: {_t: Date.now()}})

/**
 * 获取所有用户
 */

export const getUsersList = (params: any) => api.get('user/api/users/', {params: params})

/**
 * 获取所有部门
 */
export const getDepartmentsList = () => api.get('user/api/departments/', {params: {_t: Date.now()}})


/**
 * 获取所有菜单
 */
export const getMenusList = () => api.get('user/api/menus/', {params: {_t: Date.now()}})


/**
 * 获取动态菜单
 */
export const getDynamicMenusList = () => api.get('user/api/menus/dynamic/', {params: {_t: Date.now()}})
