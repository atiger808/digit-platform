const contentConfig = {
    pageName: 'vpndevices',
    tableHeight: '480px',
    header: {
        title: '设备列表',
        btnTitle: '新增设备',
        isUpdate: true
    },
    propsList: [
        { type: 'selection', label: '选择', width: '55' },
        { type: 'index', label: '序号', width: '60', align: 'center'},
        { type: 'normal', label: '设备名称', prop: 'device_name', align: 'left'},
        { type: 'normal', label: '设备类型', prop: 'device_type_name'},
        { type: 'normal', label: '设备编号', prop: 'device_number'},
        { type: 'normal', label: '序列号', prop: 'serial_number'},
        { type: 'normal', label: '服务器地址', prop: 'vpn_server'},
        // { type: 'normal', label: 'MAC地址', prop: 'mac_address'},

        // 自定义插槽
        // {type: 'custom', label: '设备权限', prop: 'menus', width: '240px', slotName: 'menus'},

        {type: 'switch', label: '状态', prop: 'used', width: '100px'},

        { type: 'timer', label: '更新时间', prop: 'update_time'},
        { type: 'timer', label: '创建时间', prop: 'create_time'},
        {type: 'handler', label: '操作', width: '260'},

    ]
}

export default contentConfig