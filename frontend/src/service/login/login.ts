import {api} from '@/service/request.ts'
import type { IAccount, IPhone } from "@/types/types.ts"


export const getCaptcha = () => api.get('user/api/captcha/', {params: {_t: Date.now()}})
export const generateCaptcha = () => api.get('user/api/captcha/', {params: {_t: Date.now()}})

export const verifyCaptcha = (data) => api.post('user/api/verify-captcha/', data)

export const postEmailCode = (data) => api.post('user/api/email-code/', data)

export const verifyEmailCode = (data) => api.post('user/api/verify-email-code/', data)

export const postSMSCode = (data) => api.post('user/api/sms-code/', data)

export const verifySMSCode = (data: {phone: string, code: string}) => api.post('user/api/verify-sms-code/', data)


export const accountLoginRequest = (account: IAccount) => api.post('user/api/auth/login/', account)


export const phoneLoginRequest = (phone: IAccount) => api.post('user/api/auth/login/', phone)

export const getUserInfoById = (id: number) => api.get(`user/${id}/`, {params: {_t: Date.now()}})

export const getUserMenusByRoleId = (id: number) => api.get(`user/${id}/menu/`, {params: {_t: Date.now()}})

export const getUserMenus = () => api.get('user/api/menus/dynamic/', {params: {_t: Date.now()}})