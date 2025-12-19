import type { IModalConfig } from "@/components/page-modal/type.ts";

const modalConfig:IModalConfig = {
    pageName: 'menus',
    header: {
        newTitle: '新增菜单',
        editTitle: '编辑菜单'
    },
    formItems: [
        {
            type: 'input',
            prop: 'name',
            label: '菜单名称',
            placeholder: '请输入菜单名称',
        },
        {
            type: 'input',
            prop: 'code',
            label: '菜单编码',
            placeholder: '请输入菜单编码',
        },
        {
            type: 'input',
            prop: 'permission',
            label: '权限标识',
            placeholder: '请输入权限标识',
        },
        {
            type: 'input',
            prop: 'icon',
            label: '菜单图标',
            placeholder: '请输入菜单图标',
        },
        {
            type: 'input',
            prop: 'path',
            label: '路径',
            placeholder: '请输入菜单路径',
            initialValue: ''
        },
        {
            type: 'input',
            prop: 'sort',
            label: '菜单序号',
            placeholder: '请输入菜单序号',
        },
        {
            type: 'select',
            prop: 'status',
            label: '状态',
            placeholder: '请选择菜单状态',
            options: [
                {
                    label: '启用',
                    value: true
                },
                {
                    label: '禁用',
                    value: false
                }
            ]
        },
        {
            type: 'select',
            prop: 'type',
            label: '菜单类型',
            placeholder: '请选择菜单类型',
            options: [
                {
                    label: '目录',
                    value: 0
                },
                {
                    label: '菜单',
                    value: 1
                },
                {
                    label: '按钮',
                    value: 2
                }
            ]
        },
        {
            type: 'select',
            prop: 'parent',
            label: '上级菜单',
            placeholder: '请选择上级菜单',
            options: []
        }
    ],
    rules: {
        name: [
            { required: true, message: '请输入菜单名称', trigger: 'blur' },
            { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
        ],
        code: [
            { required: true, message: '请输入菜单代码', trigger: 'blur' },
            { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
        ]
    }
}

export default modalConfig