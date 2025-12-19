const contentConfig = {
    pageName: 'roles',
    tableHeight: '520px',
    header: {
        title: '角色列表',
        btnTitle: '新增角色'
    },
    propsList: [
        { type: 'selection', label: '选择', width: '55' },
        { type: 'index', label: '序号', width: '60', align: 'center' },
        { type: 'normal', label: '角色名称', prop: 'name', width: '100' },
        { type: 'normal', label: '角色代码', prop: 'code', width: '100' },

        // 自定义插槽
        {type: 'custom', label: '角色权限', prop: 'menus', slotName: 'menus'},

        {type: 'status', label: '状态', prop: 'status', width: '100px'},

        { type: 'timer', label: '创建时间', prop: 'create_time', width: '200'},
        {type: 'handler', label: '操作', width: '260'},

    ]
}

export default contentConfig