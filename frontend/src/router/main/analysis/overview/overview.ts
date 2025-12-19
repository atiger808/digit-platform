export default {
    path: '/main/analysis/overview',
    name: 'Overview',
    component: () => import('@/views/main/analysis/overview/overview.vue'),
    meta: {title: '首页', affix: true} // 添加固定标记，表示不可关闭
}