import { api } from '@/service/request.ts'


export const getAmountListData = (params: any) => api.get('user/api/goods/amount/list/', {params: params})

export const getGoodsCategoryCount = () => api.get('user/api/goods/category/count/')

export const getGoodsCategorySale = () => api.get('user/api/goods/category/sale/')

export const getGoodsCategoryFavor = () => api.get('user/api/goods/category/favor/')

export const getGoodsAddressSale = () => api.get('user/api/goods/address/sale/')

export const getUserProfile  = () => api.get('user/api/profile/', {params: {_t: Date.now()}})

export const updateUserProfile = (data: any) => api.patch('user/api/profile/', data)

export const changePassword = (data: any) => api.patch('user/api/change/password/', data)

export const uploadAvatar = (formData: any) => api.post('user/api/upload/avatar/', formData, {headers: {'Content-Type': 'multipart/form-data'}})