const searchConfig = {
    pageName: 'vpndevices',
    labelWidth: '80px',
    formItems: [
        {
            type: 'input',
            prop: 'device_name',
            label: '设备名称',
            placeholder: '请输入设备名称',
            initialValue: ''
        },
        {
            type: 'input',
            prop: 'device_number',
            label: '设备编号',
            placeholder: '请输入设备编号',
            initialValue: ''
        },
        {
            type: 'input',
            prop: 'serial_number',
            label: '序列号',
            placeholder: '请输入序列号',
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
            type: 'select',
            prop: 'device_type',
            label: '设备类型',
            options: [
                {
                    label: '路由器',
                    value: 1
                },
                {
                    label: '交换机',
                    value: 2
                },
                {
                    label: '防火墙',
                    value: 3
                },
                {
                    label: 'VPN',
                    value: 4
                },
                {
                    label: '服务器',
                    value: 5
                },
                {
                    label: 'PC',
                    value: 6
                },
                {
                    label: '移动终端',
                    value: 7
                },
                {
                    label: '其他',
                    value: 8
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