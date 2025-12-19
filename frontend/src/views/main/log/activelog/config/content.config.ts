const contentConfig = {
    pageName: 'loginlogs',
    tableHeight: '520px',
    header: {
        title: '登录日志列表',
        btnTitle: '新增日志',
        isUpdate: true
    },
    propsList: [
        { type: 'selection', label: '选择', width: '48' },
        { type: 'index', label: '序号', width: '48', align: 'center' },
        { type: 'normal', label: '登录用户', prop: 'username', align:'left', width: '90' },
        // 自定义插槽
        // {type: 'custom', label: '是否在线', prop: 'online', slotName: 'online'},

        { type: 'normal', label: '登录IP', prop: 'ip', width: '140'},
        { type: 'normal', label: '浏览器名', prop: 'browser'},
        { type: 'normal', label: '操作系统', prop: 'os'},
        { type: 'normal', label: '大洲', prop: 'continent' },
        { type: 'normal', label: '国家', prop: 'country' },
        { type: 'normal', label: '省份', prop: 'province' },
        { type: 'normal', label: '城市', prop: 'city' },
        { type: 'normal', label: '县区', prop: 'district' },
        { type: 'normal', label: '区域代码', prop: 'area_code' },
        { type: 'normal', label: '英文全称', prop: 'country_english' },
        { type: 'normal', label: '简称', prop: 'country_code', width: '60' },
        { type: 'normal', label: '运营商', prop: 'isp' },
        { type: 'normal', label: '经度', prop: 'longitude' },
        { type: 'normal', label: '纬度', prop: 'latitude' },


        // 自定义插槽
        // {type: 'custom', label: 'logo', prop: 'logo', width: '60', slotName: 'logo'},


        // { type: 'timer', label: '更新时间', prop: 'update_time'},
        { type: 'timer', label: '登录时间', prop: 'create_time', sortable:  true, width: '130'},
        {type: 'handler', label: '操作',width: '110', fixed: 'right'},

    ],
    copyList: ['vpn_account', 'vpn_pwd', 'gateway_address', 'gateway_port', 'region', 'expire_time']
}

export default contentConfig