import type { IModalConfig } from "@/components/page-modal/type.ts";

const modalConfig:IModalConfig = {
    pageName: 'vpnaccounts',
    header: {
        newTitle: '新增日志',
        editTitle: '查看'
    },
    labelWidth: '100px',
    tableWidth: '50%',
    disabled: true,
    isView: true,
    formItems: [
        {
            type: 'input',
            prop: 'username',
            label: '登录用户',
            placeholder: '请输入登录用户',
        },
        {
            type: 'input',
            prop: 'ip',
            label: '登录ip',
            placeholder: '请输入登录ip',
        },

        {
            type: 'input',
            prop: 'browser',
            label: '浏览器名',
            placeholder: '请输入浏览器名',
        },


        {
            type: 'input',
            prop: 'os',
            label: '操作系统',
            placeholder: '请输入操作系统',
        },

        {
            type: 'input',
            prop: 'agent',
            label: 'agent信息',
            placeholder: '请输入agent信息',
        },


        {
            type: 'input',
            prop: 'continent',
            label: '大洲',
            placeholder: '请输入大洲',
        },


        {
            type: 'input',
            prop: 'country',
            label: '国家',
            placeholder: '请输入国家',
        },

        {
            type: 'input',
            prop: 'province',
            label: '省份',
            placeholder: '请输入省份',
        },

        {
            type: 'input',
            prop: 'city',
            label: '城市',
            placeholder: '请输入城市',
        },

        {
            type: 'input',
            prop: 'district',
            label: '县区',
            placeholder: '请输入县区',
        },

         {
            type: 'input',
            prop: 'area_code',
            label: '区域代码',
            placeholder: '请输入区域代码',
        },

         {
            type: 'input',
            prop: 'country_english',
            label: '英文全称',
            placeholder: '请输入英文全称',
        },

        {
            type: 'input',
            prop: 'country_code',
            label: '简称',
            placeholder: '请输入简称',
        },


        {
            type: 'input',
            prop: 'isp',
            label: '运营商',
            placeholder: '请输入运营商',
        },


        {
            type: 'input',
            prop: 'longitude',
            label: '经度',
            placeholder: '请输入经度',
        },


        {
            type: 'input',
            prop: 'latitude',
            label: '纬度',
            placeholder: '请输入纬度',
        },

        { type: 'date-select', label: '登录时间', prop: 'create_time'},

        {
            type: 'custom',
            slotName: 'menusList'
        }
    ]
}

export default modalConfig