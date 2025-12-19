const searchConfig = {
    pageName: 'files',
    formItems: [
        {
            type: 'input',
            prop: 'description',
            label: '素材描述',
            placeholder: '输入素材描述',
            initialValue: ''
        },
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
            label: '用户昵称',
            placeholder: '请输入用户昵称',
            initialValue: ''
        },
        {
            type: 'select',
            prop: 'ext',
            label: '格式',
            options: [
                { value: 'mp4', label: 'MP4' },
                { value: 'ts', label: 'TS' },
                { value: 'flv', label: 'FLV' },
                { value: 'mkv', label: 'MKV' },
                { value: 'avi', label: 'AVI' },
                { value: 'jpg', label: 'JPG' },
                { value: 'png', label: 'PNG' },
                { value: 'zip', label: 'ZIP' },
                { value: 'rar', label: 'RAR' },
                { value: 'exe', label: 'EXE' },
                { value: 'pdf', label: 'PDF' },
                { value: 'docx', label: 'DOCX' },
                { value: 'xlsx', label: 'XLSX' },
                { value: 'pptx', label: 'PPTX' },
                { value: '', label: '全部' }
            ]
        },
        {
            type: 'date-picker',
            prop: 'createAt',
            label: '创建时间',
        },
        // {
        //     type: 'input-number',
        //     label: '最小范围',
        //     prop: 'min_size',
        //     min: 1024,
        //     placeholder: '最小(KB)'
        // },
        // {
        //     type: 'input-number',
        //     prop: 'max_size',
        //     label: '最大范围',
        //     max: 5000,
        //     placeholder: '最大(KB)'
        // }
    ]
}

export default searchConfig