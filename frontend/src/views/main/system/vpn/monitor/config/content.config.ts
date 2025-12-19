const contentConfig = {
    pageName: 'vpnmonitors',
    tableHeight: '520px',
    header: {
        title: '实时监控日志',
        btnTitle: '新增监控',
        isRefresh: true,
        isExport: true
    },
    propsList: [
        { type: 'selection', label: '选择', width: '55' },
        { type: 'index', label: '序号', width: '60', align: 'center' },
        { type: 'normal', label: '账号名称', prop: 'vpn_account' },
        // 自定义插槽
        {type: 'custom', label: '是否在线', prop: 'online', slotName: 'online'},

        { type: 'normal', label: '昵称', prop: 'nickname' },
        { type: 'normal', label: '设备', prop: 'device' },
        { type: 'normal', label: '地区', prop: 'region' },
        { type: 'normal', label: '虚拟IP', prop: 'virtual_ip' },

        { type: 'bytes', label: '上下行流量', prop: 'traffic_vol_bytes', sortable: true },
        { type: 'normal', label: '在线时长', prop: 'online_time', sortable: true },


        // 自定义插槽
        // {type: 'custom', label: 'logo', prop: 'logo', width: '80px', slotName: 'logo'},

        {type: 'normal', label: '管理员', prop: 'username'},
        // {type: 'status', label: '状态', prop: 'status', width: '80px'},

        // { type: 'timer', label: '更新时间', prop: 'update_time'},
        { type: 'timer', label: '上线时间', prop: 'login_time', sortable:  true},
        { type: 'timer', label: '离线时间', prop: 'logout_time', sortable:  true},


        {type: 'handler', label: '操作',width: '260'},

    ]
}

export default contentConfig