import {defineStore} from "pinia";
import {
    postPageListData,
    deletePageById,
    addPageData,
    editPageData,
    getDeviceList,
    getRegionList,
} from '@/service/main/vpns/vpns'

import {errorParse} from "@/utils/errorParse.ts";
import {decryptData} from "@/utils/encrypts.ts";


const useVpnStore = defineStore('vpns', {
    state: () => ({
        pageList: [],
        pageTotalCount: 0,
        listDevices: [],
        listVpnDevices: [],
        listRegions: [],
    }),
    actions: {
        async postPageListAction(pageName: string, data: any, params: any) {
            const pageListData = await postPageListData(pageName, data, params)
            console.log('pageListData ', pageListData)

            let result = decryptData(pageListData.data.result)
            result = JSON.parse(result)

            const {total, results} = result.data
            this.pageList = results
            this.pageTotalCount = total

            this.getDeviceListAction()
            this.getRegionListAction()

        },
        async deletePageByIdAction(pageName: string, id: number) {
            try {
                await deletePageById(pageName, id)
                this.postPageListAction(pageName, {}, {page: 1, page_size: 10})
                return {success: true, error: ''}
            } catch (error) {
                const errorInfo = errorParse(error)
                console.log('errorInfo', errorInfo)
                return {success: false, error: errorInfo || '删除失败'}
            }
        },
        async addPageDataAction(pageName: string, data: any) {
            try {
                await addPageData(pageName, data)
                this.postPageListAction(pageName, {}, {page: 1, page_size: 10})
                return {success: true, error: ''}
            } catch (error) {
                const errorInfo = errorParse(error)
                console.log('errorInfo', errorInfo)
                return {success: false, error: errorInfo || '添加失败'}
            }
        },
        async editPageDataAction(pageName: string, id: number, data: any) {
            try {
                await editPageData(pageName, id, data)
                this.postPageListAction(pageName, {}, {page: 1, page_size: 10})
                return {success: true, error: ''}
            } catch (error) {
                console.log('修改失败', error)
                const errorInfo = errorParse(error)
                console.log('errorInfo', errorInfo)
                return {success: false, error: errorInfo || '修改失败'}
            }
        },

        async patchPageDataAction(pageName: string, id: number, data: any){
            try {
                await editPageData(pageName, id, data)
                return {success: true, error: ''}
            } catch (error) {
                console.log('修改失败', error)
                const errorInfo = errorParse(error)
                console.log('errorInfo', errorInfo)
                return {success: false, error: errorInfo || '修改失败'}
            }
        },


        async getDeviceListAction(params: any) {
            const deviceListData = await getDeviceList(params ||  {page:1, page_size:100, _t: Date.now()})
            console.log('deviceListData ', deviceListData)
            let result = decryptData(deviceListData.data.result)
            result = JSON.parse(result)
            const {total, results} = result.data
            console.log('total', total, 'results', results)
            // 获取device_type值为3的防火墙设备
            this.listDevices = results.filter(item => item.device_type === 3)
            // 获取device_type值为4的VPN设备
            this.listVpnDevices = results.filter(item => item.device_type === 4)
            console.log('this.listDevices', this.listDevices)
            console.log('this.listVpnDevices', this.listVpnDevices)
        },

        async getRegionListAction() {
            const regionListData = await getRegionList()
            console.log('regionListData ', regionListData)
            let result = decryptData(regionListData.data.result)
            result = JSON.parse(result)
            const {total, results} = result.data
            this.listRegions = results
        },

    }
})


export default useVpnStore