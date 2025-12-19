const searchConfig = {
    pageName: 'vpnaccounts',
    labelWidth: '80px',
    formItems: [
        {
            type: 'input',
            prop: 'vpn_account',
            label: '账号名称',
            placeholder: '请输入账号名称',
            initialValue: ''
        },
        {
            type: 'input',
            prop: 'username',
            label: '管理员',
            placeholder: '请输入管理员',
            initialValue: ''
        },
        {
            type: 'input',
            prop: 'nickname',
            label: '昵称',
            placeholder: '请输入昵称',
            initialValue: ''
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
            placeholder: '请选择行业',
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
            label: '公司',
            placeholder: '请输入公司名称',
        },
        {
            type: 'input',
            prop: 'contact',
            label: '联系人',
            placeholder: '请输入联系人名字',
        },
        {
            type: 'input',
            prop: 'remark',
            label: '备注',
            placeholder: '请输入备注',
            initialValue: ''
        },
        {
            type: 'select',
            prop: 'region',
            label: '地区',
            placeholder: '请选择地区',
            initialValue: ''
        },

        {
            type: 'select',
            prop: 'online',
            label: '在线状态',
            options: [
                {
                    value: 1,
                    label: '在线'
                },
                {
                    value: 0,
                    label: '离线'
                }
            ]
        },

        {
            type: 'select',
            prop: 'used',
            label: '状态',
            options: [
                {
                    value: 1,
                    label: '启用'
                },
                {
                    value: 0,
                    label: '禁用'
                }
            ]
        },
        {
            type: 'date-picker',
            prop: 'createAt',
            label: '创建时间',
        }
    ]
}

export default searchConfig