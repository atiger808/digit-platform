const contentConfig = {
    pageName: 'vpnregions',
    tableHeight: '520px',
    header: {
        title: '区域列表',
        btnTitle: '新增区域',
        isUpdate: true
    },
    propsList: [
        { type: 'selection', label: '选择', width: '55' },
        { type: 'index', label: '序号', width: '60', align: 'center' },
        { type: 'normal', label: '区域名称', prop: 'region', width: '150' },
        { type: 'normal', label: '区域代码', prop: 'region_code', width: '150' },


        // 自定义插槽
        {type: 'custom', label: 'logo', prop: 'logo', width: '80px', slotName: 'logo'},

        { type: 'normal', label: '设备编号', prop: 'vpn_device_number'},

        {type: 'switch', label: '状态', prop: 'used', width: '100px'},

        { type: 'timer', label: '更新时间', prop: 'update_time'},
        { type: 'timer', label: '创建时间', prop: 'create_time'},
        {type: 'handler', label: '操作', width: '260'},

    ]
}

export default contentConfig