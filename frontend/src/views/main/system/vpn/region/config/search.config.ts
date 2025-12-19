const searchConfig = {
    pageName: 'vpnregions',
    labelWidth: '80px',
    formItems: [
        {
            type: 'input',
            prop: 'region',
            label: '区域名称',
            placeholder: '请输入区域名称',
            initialValue: ''
        },
        {
            type: 'input',
            prop: 'region_code',
            label: '区域代码',
            placeholder: '请输入区域代码',
            initialValue: ''
        },
        {
            type: 'input',
            prop: 'vpn_device_number',
            label: '设备编号',
            placeholder: '请输入设备编号',
            initialValue: ''
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