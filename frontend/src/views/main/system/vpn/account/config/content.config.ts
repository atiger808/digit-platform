const contentConfig = {
    pageName: 'vpnaccounts',
    tableHeight: '520px',
    header: {
        title: '账号列表',
        btnTitle: '新增账号',
        isUpdate: true
    },
    propsList: [
        { type: 'selection', label: '选择', width: '48' },
        { type: 'index', label: '序号', width: '48', align: 'center' },
        { type: 'normal', label: '账号名称', prop: 'vpn_account', width: '90' },
        // 自定义插槽
        {type: 'custom', label: '密码', prop: 'vpn_pwd', slotName: 'password'},
        {type: 'custom', label: '是否在线', prop: 'online', slotName: 'online', width: '90'},

        { type: 'normal', label: '昵称', prop: 'nickname'},
        { type: 'normal', label: '网关', prop: 'gateway_address', width: '140'},
        { type: 'normal', label: '端口', prop: 'gateway_port'},
        // { type: 'normal', label: '设备', prop: 'device' },
        { type: 'normal', label: '地区', prop: 'region' },

        // 自定义插槽
        {type: 'custom', label: 'logo', prop: 'logo', width: '60', slotName: 'logo'},

        { type: 'normal', label: '推荐人', prop: 'recommender' },
        { type: 'normal', label: '公司名称', prop: 'organization_name', width: '100', align: 'left' },
        { type: 'normal', label: '联系人', prop: 'contact' },
        {type: 'normal', label: '管理员', prop: 'username', width: '90'},


        { type: 'timer', label: '到期时间', prop: 'expire_time', sortable: true, width: '130'},
        {type: 'switch', label: '状态', prop: 'used', width: '70'},
        // { type: 'timer', label: '更新时间', prop: 'update_time', sortable:  true, width: '130'},
        { type: 'timer', label: '创建时间', prop: 'create_time', sortable:  true, width: '130'},
        {type: 'handler', label: '操作',width: '110', fixed: 'right',  buttons: ['info', 'edit', 'delete']},
        {type: 'tooltip', label: '备注', prop: 'remark', width: '110', align: 'left'},

    ],
    copyList: ['vpn_account', 'vpn_pwd', 'gateway_address', 'gateway_port', 'region', 'expire_time']
}

export default contentConfig