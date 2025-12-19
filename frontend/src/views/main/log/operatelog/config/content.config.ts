const contentConfig = {
    pageName: 'operationlogs',
    tableHeight: '520px',
    header: {
        title: '操作日志列表',
        btnTitle: '新增日志',
        isUpdate: true
    },
    propsList: [
        { type: 'selection', label: '选择', width: '48' },
        { type: 'index', label: '序号', width: '48', align: 'center' },
        { type: 'normal', label: '请求模块', prop: 'request_modular', align: 'left',  width: '120'},
        // // 自定义插槽
        // {type: 'custom', label: '密码', prop: 'vpn_pwd', slotName: 'password'},
        // {type: 'custom', label: '是否在线', prop: 'online', slotName: 'online'},

        { type: 'normal', label: '请求地址', prop: 'request_path', width: '240', align: 'left'},
        { type: 'tooltip', label: '请求参数', prop: 'request_body'},
        { type: 'normal', label: '请求方式', prop: 'request_method'},
        { type: 'normal', label: 'IP地址', prop: 'request_ip', width: '140'},

        // 自定义插槽
        // {type: 'custom', label: 'logo', prop: 'logo', width: '60', slotName: 'logo'},

        {type: 'normal', label: '浏览器', prop: 'request_browser'},
        {type: 'normal', label: '操作系统', prop: 'request_os'},
        {type: 'normal', label: '响应码', prop: 'response_code'},
        {type: 'result', label: '响应状态', prop: 'status'},
        {type: 'tooltip', label: '返回信息', prop: 'json_result'},
        {type: 'normal', label: '操作人', prop: 'real_name'},


        // { type: 'timer', label: '更新时间', prop: 'update_time'},
        { type: 'timer', label: '创建时间', prop: 'create_time', sortable:  true, width: '130'},
        {type: 'handler', label: '操作',width: '110'},

    ],
    copyList: ['vpn_account', 'vpn_pwd', 'gateway_address', 'gateway_port', 'region', 'expire_time']
}

export default contentConfig