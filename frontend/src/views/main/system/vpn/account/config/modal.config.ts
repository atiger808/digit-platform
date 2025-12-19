import type { IModalConfig } from "@/components/page-modal/type.ts";

const modalConfig:IModalConfig = {
    pageName: 'vpnaccounts',
    header: {
        newTitle: '新增账号',
        editTitle: '编辑账号'
    },
    labelWidth: '80px',
    tableWidth: '50%',
    formItems: [
        {
            type: 'input',
            prop: 'vpn_account',
            label: '账号名称',
            placeholder: '请输入账号名称',
            disabled: true
        },
        {
            type: 'password',
            prop: 'vpn_pwd',
            label: '账号密码',
            placeholder: '请输入账号密码',
        },
        {
            type: 'select',
            prop: 'region_id',
            label: '区域',
            placeholder: '请选择区域',
            options: []
        },
         {
            type: 'select',
            prop: 'device_id',
            label: '设备',
            placeholder: '请选择设备',
            options: []
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
            type: 'date-select',
            prop: 'expire_time',
            label: '有效期',
        },
        {
            type: 'input',
            prop: 'nickname',
            label: '昵称',
            placeholder: '请输入昵称',
        },
        {
            type: 'input',
            prop: 'recommender',
            label: '推荐人',
            placeholder: '请输入推荐人名字',
        },
        {
            type: 'select',
            prop: 'industry_type',
            label: '行业类型',
            placeholder: '请选择行业类型',
            options: [
                {
                    label: '个人',
                    value: 1
                },
                {
                    label: '企业',
                    value: 2
                },
                {
                    label: '政府',
                    value: 3
                },
                {
                    label: '教育',
                    value: 4
                },
                {
                    label: '金融',
                    value: 5
                },
                {
                    label: '医疗',
                    value: 6
                },
                {
                    label: '保险',
                    value: 7
                },
                {
                    label: '科技',
                    value: 8
                },{
                    label: '游戏',
                    value: 9
                },
                {
                    label: '旅游',
                    value: 10
                },
                {
                    label: '互联网',
                    value: 11
                },
                {
                    label: '其他',
                    value: 12
                },

            ]
        },
        {
            type: 'input',
            prop: 'organization_name',
            label: '公司名称',
            placeholder: '请输入公司/机构名称',
        },
        {
            type: 'input',
            prop: 'organization_address',
            label: '公司地址',
            placeholder: '请输入公司/机构地址',
        },
        {
            type: 'input',
            prop: 'contact',
            label: '联系人',
            placeholder: '请输入联系人',
        },
        {
            type: 'input',
            prop: 'contact_phone',
            label: '联系方式',
            placeholder: '请输入联系方式',
        },

        {
            type: 'textarea',
            prop: 'remark',
            label: '备注',
            placeholder: '请输入备注'
        },

        {
            type: 'custom',
            slotName: 'menusList'
        }
    ],
    rules: {
        vpn_account: [
            { required: true, message: '请输入账号名称', trigger: 'blur' },
            { min: 4, max: 16, message: '长度在 4 到 16 个字符', trigger: 'change' },
            { pattern: /^[a-zA-Z0-9_]+$/, message: '只能输入字母、数字和下划线', trigger: 'change' }
        ],
        vpn_pwd: [
            { required: true, message: '请输入账号密码', trigger: 'blur' },
            { min: 4, max: 20, message: '长度在 4 到 20 个字符', trigger: 'change' },
            { pattern: /^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?`~ ]+$/, message: '不能含有非法字符', trigger: 'change' }
        ],
        used: [
            { required: true, message: '请选择状态', trigger: 'change' }
        ],
        expire_time: [
            { required: true, message: '请选择有效期', trigger: 'change' }
        ],
        device_id: [
            { required: true, message: '请选择设备', trigger: 'change' }
        ],
        region_id: [
            { required: true, message: '请选择区域', trigger: 'change' }
        ]
    }
}

export default modalConfig