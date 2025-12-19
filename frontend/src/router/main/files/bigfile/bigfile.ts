export default {
    path: '/main/files/bigfile',
    name: 'BigFile',
    component: () => import('@/views/main/files/bigfile/bigfile.vue'),
    meta: {title: '大文件上传'}
}