import type { IModalConfig } from "@/components/page-modal/type.ts";

const modalConfig:IModalConfig = {
    pageName: 'vpnmonitors',
    header: {
        newTitle: '新增监控',
        editTitle: '编辑监控'
    },
    labelWidth: '80px',
    formItems: [
        {
            type: 'input',
            prop: 'vpn_account',
            label: '账号名称',
            placeholder: '请输入监控名称',
        },
        {
            type: 'select',
            prop: 'online',
            label: '状态',
            options: [
                {
                    value: true,
                    label: '在线'
                },
                {
                    value: false,
                    label: '离线'
                }
            ]
        },

        {
            type: 'custom',
            slotName: 'menusList'
        }
    ],
    rules: {
        vpn_account: [
            { required: true, message: '请输入监控名称', trigger: 'blur' },
            { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
        ],
        status: [
            { required: true, message: '请选择状态', trigger: 'change' }
        ],
    }
}

export default modalConfig