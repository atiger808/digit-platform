import type { IModalConfig } from "@/components/page-modal/type.ts";

const modalConfig:IModalConfig = {
    pageName: 'vpnregions',
    header: {
        newTitle: '新增区域',
        editTitle: '编辑区域'
    },
    labelWidth: '100px',
    formItems: [
        {
            type: 'input',
            prop: 'region',
            label: '区域名称',
            placeholder: '请输入区域名称',
        },
        {
            type: 'input',
            prop: 'region_code',
            label: '区域代码',
            placeholder: '请输入区域代码',
        },
        {
            type: 'input',
            prop: 'device_count',
            label: '终端数量',
            placeholder: '请输入终端数量',
        },
        {
            type: 'select',
            prop: 'used',
            label: '状态',
            options: [
                {
                    value: true,
                    label: '启用'
                },
                {
                    value: false,
                    label: '禁用'
                }
            ]
        },

        {
            type: 'select',
            prop: 'device_id',
            label: '防火墙设备',
            placeholder: '请选择防火墙设备',
            options: []
        },

        {
            type: 'select',
            prop: 'vpn_device_id',
            label: 'VPN设备',
            placeholder: '请选择VPN设备',
            options: []
        },

        {
            type: 'custom',
            slotName: 'menusList'
        }
    ],
    rules: {
        name: [
            { required: true, message: '请输入区域名称', trigger: 'blur' },
            { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
        ],
        code: [
            { required: true, message: '请输入区域代码', trigger: 'blur' },
            { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
        ]
    }
}

export default modalConfig