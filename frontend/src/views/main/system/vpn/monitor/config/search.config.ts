const searchConfig = {
    pageName: 'vpnmonitors',
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
            type: 'select',
            prop: 'device_name',
            label: '设备名称',
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
            type: 'date-picker',
            prop: 'createAt',
            label: '创建时间',
        }
    ]
}

export default searchConfig