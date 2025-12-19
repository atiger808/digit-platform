const contentConfig = {
    pageName: 'files',
    tableHeight: '520px',
    header: {
        title: '素材列表',
        btnTitle: '新增文件',
        icon: 'http://vpn.newdmy.com:10889/media/images/forticlient.ico'
    },
    propsList: [
        {type: 'selection', label: '选择', width: '48'},
        // {type: 'index', label: '序号', width: '48'},

        {type: 'normal', label: 'ID', prop: 'id', width: '48'},
        // {type: 'custom', label: '封面', prop: 'static_cover_url', width: '110', align: 'center', slotName: 'image'},

        {type: 'editable', label: '素材描述', prop: 'description', width: '140', align: 'left'},

        {type: 'custom', label: '动图', prop: 'gif_cover_url', width: '110', align: 'center', slotName: 'image'},


        {type: 'normal', label: '格式', prop: 'ext', width: '80'},
        {type: 'bytes', label: '素材大小', prop: 'file_size', width: '110', sortable:  true},
        {type: 'normal', label: '帧率', prop: 'fps', width: '80', sortable:  true},
        {type: 'normal', label: '分辨率', prop: 'resolution', width: '110'},
        {type: 'duration', label: '时长', prop: 'duration', width: '110', sortable:  true},
        // {type: 'bytes', label: '视频码率', prop: 'bitrate', width: '110', sortable:  true},
        // {type: 'bytes', label: '音频码率', prop: 'audio_bitrate', width: '110', sortable:  true},
        // {type: 'normal', label: '采样率', prop: 'ar_sample_rate', width: '110', sortable:  true},
        // {type: 'normal', label: '视频编码', prop: 'vcodec_type'},
        {type: 'link', label: '链接', prop: 'file_url'},
        // {type: 'normal', label: '音频编码', prop: 'acodec_type'},



        // 自定义插槽
        // {type: 'custom', label: '角色', prop: 'roles', width: '200px', slotName: 'roles'},

        {type: 'status', label: '状态', prop: 'status', width: '100'},
        {type: 'normal', label: '下载次数', prop: 'download_count', width: '110', sortable:  true},


        { type: 'timer', label: '创建时间', prop: 'create_time', width: '180', sortable:  true},
        {type: 'normal', label: '用户', prop: 'username', width: '160'},
        {type: 'handler', label: '操作', fixed: 'right', width: '110'}
    ]
}

export default contentConfig