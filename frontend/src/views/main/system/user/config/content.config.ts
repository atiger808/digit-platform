const contentConfig = {
    pageName: 'users',
    tableHeight: '520px',
    header: {
        title: '用户列表',
        btnTitle: '新增用户'
    },
    propsList: [
        {type: 'selection', label: '选择', width: '55'},
        // {type: 'index', label: '序号', width: '80px'},

        {type: 'normal', label: 'ID', prop: 'id', width: '80px'},
        {type: 'normal', label: '用户名', prop: 'username', width: '200px'},
        {type: 'normal', label: '昵称', prop: 'real_name', width: '100px'},
        {type: 'custom', label: '是否在线', prop: 'online', slotName: 'online'},
        {type: 'normal', label: '电话号', prop: 'mobile', width: '200px'},

        // 自定义插槽
        {type: 'custom', label: '部门名称', prop: 'department_info', slotName: 'department_name'},
        {type: 'custom', label: '角色', prop: 'roles', width: '200px', slotName: 'roles'},

        {type: 'status', label: '状态', prop: 'is_active', width: '100px'},

        {type: 'timer', label: '创建时间', prop: 'create_time'},
        {type: 'handler', label: '操作', width: '260'}
    ]
}

export default contentConfig