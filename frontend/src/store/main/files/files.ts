import {defineStore} from "pinia";
import {
    postFileListData,
    deleteFileById,
    editFileById,
    renameFileById,
    downloadFileById
} from '@/service/main/files/files'
import {errorParse} from "@/utils/errorParse.ts";


interface IFileState {
    fileList: any[]
    totalCount: number
}

const useFileStore = defineStore('files', {
    state: (): IFileState => ({
        fileList: [],
        totalCount: 0
    }),
    actions: {
        async postFileListAction(data: any, params: any, pageName: string) {
            const fileResult = await postFileListData(pageName, data, params)
            const {total, results} = fileResult.data.data
            this.fileList = results
            this.totalCount = total
        },
        async deleteFileAction(id: number, pageName: string) {
            await deleteFileById(pageName, id)
            this.postFileListAction({}, {page: 1, page_size: 10}, pageName)
        },

        async editFileAction(id: number, data: any, pageName: string) {
            try {
                console.log('id: ', id)
                const editResult = await editFileById(pageName, id, data)

                // 2. 重新请求新的数据
                this.postFileListAction({}, {page: 1, page_size: 10}, pageName)


            } catch (e) {
                console.log('修改失败', e)
                ElMessage.error(e.message || '修改失败')
            }

        },

        async addFileAction(data: any, pageName: string) {
            // 2. 重新请求新的数据
            await this.postFileListAction({}, {page: 1, page_size: 10}, pageName)
        },

        async renameFileAction(id: any, params: any, pageName: string) {
            await renameFileById(pageName, id, params)
            // 2. 重新请求新的数据
            this.postFileListAction({}, {page: 1, page_size: 10}, pageName)
        },

        async downloadFileAction(id: number, params: any, pageName: string) {
            try {
                const downloadResult = await downloadFileById(pageName, id, params)
                console.log('下载成功 downloadResult', downloadResult)
                return downloadResult
            } catch (error) {
                let errorInfo = errorParse(error)
                console.log('下载失败', error, ' errorInfo', errorInfo)
                return null
            }
        }


    }
})

export default useFileStore