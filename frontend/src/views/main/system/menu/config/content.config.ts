const contentConfig = {
    pageName: 'menus',
    tableHeight: '520px',
    header: {
        title: '菜单列表',
        btnTitle: '新增菜单'
    },
    propsList: [
        // { type: 'selection', label: '选择', width: '55' },
        // { type: 'index', label: '序号', width: '60', align: 'center' },

        { label: '菜单名称', prop: 'name', width: '200', align: 'left'},
        { type: 'normal', label: '级别', prop: 'type', width: '60' },

        { type: 'normal', label: '父菜单', prop: 'parent_name' },
        { type: 'normal', label: '菜单代码', prop: 'code'},
        { type: 'normal', label: '路由', prop: 'path', align: 'left'},
        { type: 'normal', label: '排序', prop: 'sort'},
        { type: 'normal', label: '权限', prop: 'permission'},

        // 自定义插槽
        // {type: 'custom', label: '父菜ID', prop: 'parent', width: '100px', slotName: 'parent'},
        {type: 'custom', label: '图标', prop: 'icon', slotName: 'icon'},

        {type: 'status', label: '状态', prop: 'status', width: '100px'},
        { type: 'timer', label: '创建时间', prop: 'create_time'},
        {type: 'handler', label: '操作', width: '260'},

    ],
    childrenTree: {
        rowKey: 'id',
        treeProps: {
            children: 'children',
            hasChildren: 'hasChildren'
        }
    }
}

export default contentConfig