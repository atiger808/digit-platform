import type { IModalConfig } from "@/components/page-modal/type.ts";

const modalConfig:IModalConfig = {
    pageName: 'departments',
    header: {
        newTitle: '新增部门',
        editTitle: '编辑部门'
    },
    formItems: [
        {
            type: 'input',
            prop: 'name',
            label: '部门名称',
            placeholder: '请输入部门名称',
        },
        {
            type: 'input',
            prop: 'code',
            label: '部门代码',
            placeholder: '请输入部门代码',
        },
        {
            type: 'select',
            prop: 'status',
            label: '状态',
            placeholder: '请选择状态',
            options: [
                {
                    value: true,
                    label: '启用'
                },
                {
                    value: false,
                    label: '禁用'
                }
            ]
        },
        {
            type: 'select',
            prop: 'parent',
            label: '上级部门',
            placeholder: '请选择上级部门',
            options: []
        }
    ],
    rules: {
        name: [
            { required: true, message: '请输入部门名称', trigger: 'blur' },
            { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
        ],
        code: [
            { required: true, message: '请输入部门代码', trigger: 'blur' },
            { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
        ]
    }
}

export default modalConfig