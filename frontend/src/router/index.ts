import {createRouter, createWebHashHistory, type RouteRecordRaw} from 'vue-router'
import {localCache, sessionCache} from "../utils/cache.ts";
import {LOGIN_TOKEN} from "../global/constants.ts";
import {firstMenu} from "../utils/map-menus.ts";
import {useTabsStore} from '@/store/main/tabs/tabs.ts'

declare module 'vue-router' {
    interface RouteMeta {
        title: string
        breadcrumb?: boolean
    }
}

export const routes: RouteRecordRaw[] = [
    {
        path: '/',
        redirect: '/main'
    },
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/login/login3.vue')
    },
    {
        path: '/register',
        name: 'Register',
        component: () => import('@/views/register/register.vue')
    },
    {
        path: '/main',
        name: 'Main',
        component: () => import('@/views/main/main.vue'),
        children: [
            {
                path: '404',
                component: () => import('@/views/error-page/404.vue'),
                meta: {hidden: true, title: '404'}
            }
        ]
    },
    {
        path: '/:pathMatch(.*)*',
        redirect: '/main/404',
        meta: {hidden: true}
    },
]

const router = createRouter({
    history: createWebHashHistory(),
    routes
})


// 导航守卫
// 参数：to(跳转到的位置)/from(从那里跳转过来)
// 返回值：返回值决定导航的路径（不返回或者返回undefined,默认跳转）
// 举个例子：/ => /main
// to: /main from: /返回值：/abc
router.beforeEach((to, from) => {
    const token = sessionCache.getCache(LOGIN_TOKEN)
    if (to.path.startsWith('/main') && !token) {
        return '/login'
    }

    if (to.path.startsWith('/404') && !token) {
        return '/login'
    }

    if (to.path === '/login' && token) {
        return '/main'
    }

    if (to.path === '/login' && !token) {
        const tabStore = useTabsStore()
        tabStore.resetTabs()
    }

    if (to.path === '/main') {
        console.log('firstMenu', firstMenu)

        return '/main/analysis/overview'

        // if (firstMenu) {
        //     return firstMenu?.path
        // } else {
        //     return '/main/analysis/overview'
        // }

    }


})


export default router