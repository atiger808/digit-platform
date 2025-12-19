import {api} from '@/service/request.ts'

export const postFileListData = (pageName: string, data: any, params: any) => api.post('file/api/files/query/', data, {params: params})

export const deleteFileById = (pageName: string,id: any) => api.delete(`file/api/files/${id}/delete/`)

export const editFileById = (pageName: string, id: any, data: any) => api.patch(`file/api/files/${id}/edit/`, data)

export const renameFileById = (pageName: string, id: any, params: any) => api.patch(`file/api/files/${id}/rename/`, params)

export const retrieveFileById = (pageName: string, id: any, params: any) => api.get(`file/api/files/${id}/custom_retrieve/`, params)

export const downloadFileById = (pageName: string, id: any, params: any) => api.get(`file/api/download/${id}/download/`, params)

export const downloadFileStart = (id: any, data: any) => api.post(`file/api/download/${id}/download-start/`,  data)

export const downloadFileCancel = (id: any, data: any) => api.post(`file/api/download/${id}/download-cancel/`,  data)

export const downloadFileComplete = (id: any, data: any) => api.post(`file/api/download/${id}/download-complete/`,  data)


export const getSummary = (params: any) => api.get('file/api/dashboard/summary/', {params: params})

export const getUserVideoStats = (params: any) => api.get('file/api/user-files/user_video_stats/', {params: params})

export const getOnlineUsers = (params: any) => api.get('file/api/users/online/', {params: params})


export const getFileSummary = (params: any) => api.get('file/files/summary/', {params: params})

export const getUserStatsByTime = (params: any) => api.get('file/api/dashboard/user_stats_by_time/', {params: params})
