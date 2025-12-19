import type {IModalConfig} from "@/components/page-modal/type.ts";

const modalConfig: IModalConfig = {
    pageName: 'vpnaccounts',
    header: {
        newTitle: '新增日志',
        editTitle: '查看',
    },
    labelWidth: '100px',
    tableWidth: '50%',
    disabled: true,
    isView: true,
    formItems: [
        {
            type: 'input',
            prop: 'request_modular',
            label: '请求模块',
            placeholder: '请输入请求模块',
        },
        {
            type: 'input',
            prop: 'request_path',
            label: '请求地址',
            placeholder: '请输入请求地址',
        },

        {
            type: 'textarea',
            prop: 'request_body',
            label: '请求参数',
            placeholder: '请输入请求参数'
        },

        {
            type: 'textarea',
            prop: 'json_result',
            label: '返回信息',
            placeholder: '请输入返回信息'
        },


        {
            type: 'input',
            prop: 'request_method',
            label: '请求方式',
            placeholder: '请输入请求方式',
        },


        {
            type: 'input',
            prop: 'request_ip',
            label: 'IP地址',
            placeholder: '请输入IP地址',
        },
        {
            type: 'input',
            prop: 'request_browser',
            label: '请求浏览器',
            placeholder: '请输入请求浏览器',
        },
        {
            type: 'input',
            prop: 'response_code',
            label: '响应码',
            placeholder: '请输入响应码',
        },
        {
            type: 'input',
            prop: 'request_os',
            label: '操作系统',
            placeholder: '请输入操作系统',
        },

        {
            type: 'input',
            prop: 'real_name',
            label: '操作人',
            placeholder: '请输入操作人',
        },

        // {type: 'date-select', label: '更新时间', prop: 'update_time'},
        {type: 'date-select', label: '创建时间', prop: 'create_time'},


        {
            type: 'custom',
            slotName: 'menusList'
        }
    ]
}

export default modalConfig