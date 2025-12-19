import type {IModalConfig} from "@/components/page-modal/type.ts";

const modalConfig:IModalConfig = {
    pageName: 'users',
    header: {
        newTitle: '新增用户',
        editTitle: '编辑用户'
    },
    formItems: [
        {
            type: 'input',
            prop: 'username',
            label: '用户名称',
            placeholder: '请输入用户名称',
            disabled: true
        },
        {
            type: 'input',
            prop: 'real_name',
            label: '昵称',
            placeholder: '请输入昵称',
        },
        {
            type: 'password',
            prop: 'password',
            label: '密码',
            placeholder: '请输入密码',
        },
        {
            type: 'input',
            prop: 'mobile',
            label: '手机号',
            placeholder: '请输入手机号',
        },
        {
            type: 'select',
            prop: 'gender',
            label: '性别',
            placeholder: '请选择性别',
            options: [
                {value: 0, label: '未知'},
                {value: 1, label: '男'},
                {value: 2, label: '女'}
            ]
        },
        {
            type: 'select',
            prop: 'is_active',
            label: '状态',
            placeholder: '请选择状态',
            options: [
                {value: false, label: '禁用'},
                {value: true, label: '启用'}
            ]
        },
        {
            type: 'select',
            prop: 'role_id',
            label: '角色',
            placeholder: '请选择角色',
            options: []
        },
        {
            type: 'select',
            prop: 'department_id',
            label: '部门',
            placeholder: '请选择部门',
            options: []
        }
    ],
    rules: {
        username: [
            {required: true, message: '请输入用户名', trigger: 'blur'},
            {min: 4, max: 16, message: '长度在 4 到 16 个字符', trigger: 'change'},
        ],
        real_name: [
            {required: true, message: '请输入真实姓名', trigger: 'blur'},
            {min: 2, max: 10, message: '长度在 2 到 10 个字符', trigger: 'change'},
        ],
        mobile: [
            {required: true, message: '请输入手机号', trigger: 'blur'},
            {pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'change'},
        ],
        role_id: [
            {required: true, message: '请选择角色', trigger: 'blur'},
        ],
        department_id: [
            {required: true, message: '请选择部门', trigger: 'blur'},
        ],
    }
}

export default modalConfig