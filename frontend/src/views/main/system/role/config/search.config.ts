const searchConfig = {
    pageName: 'roles',
    labelWidth: '80px',
    formItems: [
        {
            type: 'input',
            prop: 'name',
            label: '角色名称',
            placeholder: '请输入角色名称',
            initialValue: ''
        },
        {
            type: 'input',
            prop: 'code',
            label: '角色代码',
            placeholder: '请输入角色代码',
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