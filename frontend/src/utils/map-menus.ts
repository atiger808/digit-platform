import type {RouteRecordRaw} from "vue-router";
import {sessionCache} from "./cache.ts";
import { FIRST_MENU } from "@/global/constants.ts";
const loadLocalRoutes = () => {
    const localRoutes: RouteRecordRaw[] = []
    // 1.1.读取router/main所有的ts文件
    const files: Record<string, any> = import.meta.glob('@/router/main/**/*.ts', {eager: true})

    console.log('files: ', files)

    // 1.2.将加载的对象放在localRoutes中
    for (const key in files) {
        const module = files[key].default
        localRoutes.push(module)
    }
    return localRoutes
}

export let firstMenu:any = sessionCache.getCache(FIRST_MENU)
const mapMenusToRoutes = (userMenus: any[]) => {
    // 1.加载本地路由
    const localRoutes = loadLocalRoutes()

    // 2.根据菜单去匹配正确的路由
    const routes: RouteRecordRaw[] = []
    for (const menu of userMenus) {
        for (const submenu of menu.children) {
            const route = localRoutes.find(item => item.path === submenu.path)
            if (route) {
                if (!routes.find(item => item.path === menu.path)) {
                    routes.push({path: menu.path, redirect: route.path})
                }
                routes.push(route)
            }
        }
    }

    return routes
}


/**
 * 根据路径匹配 菜单
 */

const mapPathToMenu = (path: string, userMenus: any[]) => {
    for (const menu of userMenus) {
        for (const submenu of menu.children) {
            if (submenu.path === path) {
                firstMenu = submenu
                sessionCache.setCache(FIRST_MENU, firstMenu)
                return submenu
            }
        }
    }
    return null
}

/*
 * 根据路径匹配 面包屑
 */
const mapPathToBreads = (path: string, userMenus: any[]) => {
    const breads: any[] = []
    for (const menu of userMenus) {
        for (const submenu of menu.children) {
            if (submenu.path === path) {
                breads.push({name: menu.name, path: menu.path})
                breads.push({name: submenu.name, path: submenu.path})
            }
        }
    }
    return breads
}

/**
 * 菜单映射到id的列表
 * @param menuList
 */
const mapMenuListToIds = (menuList: any[]) => {
    const ids: number[] = []
    function recursionGetId(menus: any[]) {
        for (const item of menus) {
            if (item.children && item.children.length > 0) {
                recursionGetId(item.children)
            } else if (item.type !== 0) {
                ids.push(item.id)
            }
        }
    }
    recursionGetId(menuList)

    return ids
}
/**
 * 菜单映射到select的列表
 */
const mapMenuListToLeaf = (menuList: any[]) => {
    const leafMenuList: any[] = []
    function recursionGetLeaf(menus: any[]) {
        for (const item of menus) {
            if (item.children && item.children.length > 0) {
                leafMenuList.push(item)
                recursionGetLeaf(item.children)
            } else {
                leafMenuList.push(item)
            }
        }
    }
    recursionGetLeaf(menuList)
   return leafMenuList
}


/**
 * 从菜单映射到权限的列表
 * @param menuList
 */
const mapMenusToPermissions = (menuList: any[]) => {
    const permissions: string[] = []
    function recursionGetPermission(menus: any[]) {
        for (const item of menus) {
            if (item.type === 2 && item.status === true) {
                permissions.push(item.permission)
            } else {
                recursionGetPermission(item.children ?? [])
            }
        }
    }

    console.log('menuList: ', menuList)
    recursionGetPermission(menuList)
    return permissions
}

export {
    mapMenusToRoutes, mapPathToMenu, mapPathToBreads, mapMenuListToIds,
    mapMenusToPermissions, mapMenuListToLeaf
}