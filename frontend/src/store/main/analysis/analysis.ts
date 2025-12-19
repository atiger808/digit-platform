import {defineStore} from "pinia";
import {
    getAmountListData,
    getGoodsCategoryCount,
    getGoodsCategorySale,
    getGoodsCategoryFavor,
    getGoodsAddressSale,
} from "@/service/main/analysis/analysis";

import {getVpnRegionSummary} from "@/service/main/vpns/vpns.ts";
import {getFileSummary} from "@/service/main/files/files.ts";
import {decryptData} from "@/utils/encrypts.ts";


interface IAnalysisState {
    amountList: any[],
    goodsCategoryCount: any[],
    goodsCategorySale: any[],
    goodsCategoryFavor: any[],
    goodsAddressSale: any[],
    vpnRegionSummary: any[],
    fileSummary: any[]
}

const useAnalysisStore = defineStore('analysis', {
    state: (): IAnalysisState => ({
        amountList: [],
        goodsCategoryCount: [],
        goodsCategorySale: [],
        goodsCategoryFavor: [],
        goodsAddressSale: [],
        vpnRegionSummary: [],
        fileSummary: []
    }),
    actions: {
        async fetchVPNRegionSummary() {
            let res = await getVpnRegionSummary({_t: Date.now()})
            let result = decryptData(res.data.result)
            result = JSON.parse(result)
            this.vpnRegionSummary = result.data.data
        },

        async fetchAmountListData() {
            let result = await getAmountListData()
            this.amountList = result.data.data
        },
        async fetchGoodsCategoryCount() {
            let result = await getGoodsCategoryCount()
            this.goodsCategoryCount = result.data.data
        },
        async fetchGoodsCategorySale() {
            let result = await getGoodsCategorySale()
            this.goodsCategorySale = result.data.data
        },
        async fetchGoodsCategoryFavor() {
            let result = await getGoodsCategoryFavor()
            this.goodsCategoryFavor = result.data.data
        },
        async fetchGoodsAddressSale() {
            let result = await getGoodsAddressSale()
            this.goodsAddressSale = result.data.data
        },

        async fetchFileSummary() {
            let result = await getFileSummary()
            this.fileSummary = result.data.data
        },

    


        fetchAnalysisDataAction() {
            getAmountListData().then(res => {
                this.amountList = res.data.data
            })
            getGoodsCategoryCount().then(res => {
                this.goodsCategoryCount = res.data.data
            })
            getGoodsCategorySale().then(res => {
                this.goodsCategorySale = res.data.data
            })
            getGoodsCategoryFavor().then(res => {
                this.goodsCategoryFavor = res.data.data
            })
            getGoodsAddressSale().then(res => {
                this.goodsAddressSale = res.data.data
            })
            getVpnRegionSummary({_t: Date.now()}).then(res => {
                let result = decryptData(res.data.result)
                result = JSON.parse(result)
                this.vpnRegionSummary = result.data.data
            })
            getFileSummary({_t: Date.now()}).then(res => {
                console.log("res: ", res)
                let result = res.data.data
                this.fileSummary = result.data
                console.log("this.fileSummary: ", this.fileSummary)
            })
        }
    }
})

export default useAnalysisStore