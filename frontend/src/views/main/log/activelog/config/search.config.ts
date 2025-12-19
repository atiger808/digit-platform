const searchConfig = {
    pageName: 'loginlogs',
    labelWidth: '100px',
    formItems: [
        {
            type: 'input',
            prop: 'username',
            label: '登录用户名',
            placeholder: '请输入登录用户名',
            initialValue: ''
        },
        {
            type: 'input',
            prop: 'ip',
            label: '登录IP',
            placeholder: '请输入登录IP',
            initialValue: ''
        },

        {
            type: 'input',
            prop: 'province',
            label: '省份',
            placeholder: '请输入省份',
            initialValue: ''
        },

        {
            type: 'input',
            prop: 'city',
            label: '城市',
            placeholder: '请输入城市',
            initialValue: ''
        },

        {
            type: 'input',
            prop: 'os',
            label: '操作系统',
            placeholder: '请输入操作系统',
            initialValue: ''
        },

        {
            type: 'input',
            prop: 'isp',
            label: '运营商',
            placeholder: '请输入运营商',
            initialValue: ''
        },

        {
            type: 'date-picker',
            prop: 'createAt',
            label: '登录时间',
        }
    ]
}

export default searchConfig