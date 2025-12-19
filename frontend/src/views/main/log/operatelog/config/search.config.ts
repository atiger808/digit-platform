const searchConfig = {
    pageName: 'operationlogs',
    labelWidth: '80px',
    formItems: [
        {
            type: 'input',
            prop: 'real_name',
            label: '操作人',
            placeholder: '请输入操作人',
            initialValue: ''
        },
        {
            type: 'input',
            prop: 'request_modular',
            label: '请求模块',
            placeholder: '请输入请求模块',
            initialValue: ''
        },
        {
            type: 'input',
            prop: 'request_ip',
            label: 'IP地址',
            placeholder: '请输入IP地址',
            initialValue: ''
        },
        {
            type: 'select',
            prop: 'request_method',
            label: '请求方式',
            placeholder: '请选择',
            options: [
                {
                    value: 'POST',
                    label: 'POST'
                },
                {
                    value: 'PATCH',
                    label: 'PATCH'
                },
                {
                    value: 'DELETE',
                    label: 'DELETE'
                },
            ]
        },
        {
            type: 'input',
            prop: 'response_code',
            label: '响应码',
            placeholder: '请输入响应码',
            initialValue: ''
        },
        {
            type: 'input',
            prop: 'request_os',
            label: '操作系统',
            placeholder: '请输入操作系统',
            initialValue: ''
        },

        {
            type: 'select',
            prop: 'status',
            label: '响应状态',
            options: [
                {
                    value: true,
                    label: '成功'
                },
                {
                    value: false,
                    label: '失败'
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