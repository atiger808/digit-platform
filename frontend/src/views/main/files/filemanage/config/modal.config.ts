import type {IModalConfig} from "@/components/page-modal/type.ts";

const modalConfig:IModalConfig = {
    pageName: 'files',
    header: {
        newTitle: '新增素材',
        editTitle: '编辑素材'
    },
    labelWidth: '100px',
    tableWidth: '60%',
    disabled: true,
    isView: true,
    formItems: [
        {
            type: 'input',
            prop: 'id',
            label: 'ID',
            placeholder: '',
        },
        {
            type: 'input',
            prop: 'file_md5',
            label: 'MD5',
            placeholder: '',
        },
        {
            type: 'input',
            prop: 'ext',
            label: '格式',
            placeholder: '',
        },
        {
            type: 'input',
            prop: 'file_size',
            label: '素材大小',
            placeholder: '',
        },
        {
            type: 'input',
            prop: 'fps',
            label: '帧率',
            placeholder: '',
        },
        {
            type: 'input',
            prop: 'resolution',
            label: '分辨率',
            placeholder: '',
        },
        {
            type: 'input',
            prop: 'duration',
            label: '时长(秒)',
            placeholder: '',
        },
        {
            type: 'input',
            prop: 'bitrate',
            label: '视频码率',
            placeholder: '',
        },
        {
            type: 'input',
            prop: 'audio_bitrate',
            label: '音频码率',
            placeholder: '',
        },
        {
            type: 'input',
            prop: 'ar_sample_rate',
            label: '采样率',
            placeholder: '',
        },{
            type: 'input',
            prop: 'vcodec_type',
            label: '视频编码',
            placeholder: '',
        },{
            type: 'input',
            prop: 'acodec_type',
            label: '音频编码',
            placeholder: '',
        },
        {
            type: 'textarea',
            prop: 'description',
            label: '素材描述',
            placeholder: '请输入文件描述',
        },
        {
            type: 'checkbox',
            prop: 'user_list',
            label: '授权用户',
            placeholder: '选择用户',
            options: []
        },
    ],
    rules: {
        original_filename: [
            {required: true, message: '请输入文件名', trigger: 'blur'},
            {min: 3, max: 100, message: '长度在 3 到 100 个字符', trigger: 'blur'},
        ],
        user: [
            {required: true, message: '请输入上传者', trigger: 'blur'},
            {min: 2, max: 20, message: '长度在 2 到 10 个字符', trigger: 'blur'},
        ]
    }
}

export default modalConfig