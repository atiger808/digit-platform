const searchConfig = {
    pageName: 'users',
    formItems: [
        {
            type: 'input',
            prop: 'username',
            label: '用户名',
            placeholder: '请输入用户名',
            initialValue: ''
        },
        {
            type: 'input',
            prop: 'real_name',
            label: '昵称',
            placeholder: '请输入昵称',
            initialValue: ''
        },
        {
            type: 'input',
            prop: 'mobile',
            label: '电话号',
            placeholder: '请输入电话号',
            initialValue: ''
        },
        {
            type: 'select',
            prop: 'is_active',
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