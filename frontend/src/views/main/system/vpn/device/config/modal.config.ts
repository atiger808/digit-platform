import type { IModalConfig } from "@/components/page-modal/type.ts";

const modalConfig:IModalConfig = {
    pageName: 'vpndevices',
    header: {
        newTitle: '新增设备',
        editTitle: '编辑设备'
    },
    labelWidth: '80px',
    formItems: [
        {
            type: 'input',
            prop: 'device_name',
            label: '设备名称',
            placeholder: '请输入设备名称',
        },
        {
            type: 'input',
            prop: 'device_number',
            label: '设备编号',
            placeholder: '请输入设备编号',
        },
        {
            type: 'select',
            prop: 'device_type',
            label: '设备类型',
            options: [
                {
                    label: '路由器',
                    value: 1
                },
                {
                    label: '交换机',
                    value: 2
                },
                {
                    label: '防火墙',
                    value: 3
                },
                {
                    label: 'VPN',
                    value: 4
                },
                {
                    label: '服务器',
                    value: 5
                },
                {
                    label: 'PC',
                    value: 6
                },
                {
                    label: '移动终端',
                    value: 7
                },
                {
                    label: '其他',
                    value: 8
                }
            ]
        },
        {
            type: 'select',
            prop: 'used',
            label: '状态',
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
            type: 'input',
            prop: 'serial_number',
            label: '序列号',
            placeholder: '请输入序列号',
        },
        {
            type: 'input',
            prop: 'mac_address',
            label: 'MAC地址',
            placeholder: '请输入MAC地址',
        },
        {
            type: 'input',
            prop: 'vpn_server',
            label: '服务器',
            placeholder: '请输入服务器地址',
        },
        {
            type: 'input',
            prop: 'route_url',
            label: '路由地址',
            placeholder: '请输入路由地址',
        },
        {
            type: 'input',
            prop: 'account',
            label: '设备账号',
            placeholder: '请输入设备账号',
        },
        {
            type: 'password',
            prop: 'password',
            label: '设备密码',
            placeholder: '请输入设备密码',
        },
        {
            type: 'custom',
            slotName: 'menusList'
        }
    ],
    rules: {
        device_name: [
            { required: true, message: '请输入设备名称', trigger: 'blur' },
            { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
        ],
        device_type: [
            { required: true, message: '请选择设备类型', trigger: 'change' }
        ],
        used: [
            { required: true, message: '请选择设备状态', trigger: 'change' }
        ],
    }
}

export default modalConfig