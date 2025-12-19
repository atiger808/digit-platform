const contentConfig = {
    pageName: 'departments',
    tableHeight: '520px',
    header: {
        title: '部门列表',
        btnTitle: '新增部门'
    },
    propsList: [
        {type: 'selection', label: '选择', width: '55'},
        {type: 'index', label: '序号', width: '80px'},

        {type: 'normal', label: '部门名称', prop: 'name'},
        {type: 'normal', label: '部门代码', prop: 'code'},
        {type: 'normal', label: '上级部门', prop: 'parent_name', width: '100px'},

        // 自定义插槽
        // {type: 'custom', label: '部门名称', prop: 'name', width: '210px', slotName: 'name'},
        // {type: 'custom', label: '上级部门', prop: 'parent_name', width: '200px', slotName: 'parent_name'},

        {type: 'status', label: '状态', prop: 'status', width: '100px'},

        {type: 'timer', label: '创建时间', prop: 'create_time'},
        {type: 'handler', label: '操作'},
    ]
}

export default contentConfig