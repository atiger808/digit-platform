const searchConfig = {
    pageName: 'menus',
    labelWidth: '80px',
    formItems: [
        {
            type: 'input',
            prop: 'name',
            label: '菜单名称',
            placeholder: '请输入菜单名称',
            initialValue: ''
        },
        {
            type: 'input',
            prop: 'code',
            label: '菜单编码',
            placeholder: '请输入菜单编码',
            initialValue: ''
        },
        {
            type: 'select',
            prop: 'status',
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