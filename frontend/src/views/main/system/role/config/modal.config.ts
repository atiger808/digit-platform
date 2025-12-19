import type { IModalConfig } from "@/components/page-modal/type.ts";

const modalConfig:IModalConfig = {
    pageName: 'roles',
    header: {
        newTitle: '新增角色',
        editTitle: '编辑角色'
    },
    formItems: [
        {
            type: 'input',
            prop: 'name',
            label: '角色名称',
            placeholder: '请输入角色名称',
        },
        {
            type: 'input',
            prop: 'code',
            label: '角色代码',
            placeholder: '请输入角色代码',
        },
        {
            type: 'custom',
            slotName: 'menusList'
        }
    ],
    rules: {
        name: [
            { required: true, message: '请输入角色名称', trigger: 'blur' },
            { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
        ],
        code: [
            { required: true, message: '请输入角色代码', trigger: 'blur' },
            { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
        ]
    }
}

export default modalConfig