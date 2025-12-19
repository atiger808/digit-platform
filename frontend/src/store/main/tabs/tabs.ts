import {defineStore} from 'pinia'
import {type RouteLocationNormalized} from 'vue-router'

export interface TabItem {
    path: string
    title?: string
    affix?: boolean // 是否固定页签
}

export const useTabsStore = defineStore('tabs', {
    state: () => ({
        tabs: [] as TabItem[],
        currentTab: '' as string
    }),
    actions: {
        addTab(route: RouteLocationNormalized) {
            const exists = this.tabs.some(tab => tab.path === route.path)
            if (!exists) {
                console.log('addTab', route.path.includes('/login'), route)
                if (!route.path.includes('/login')) {
                    this.tabs.push({
                        path: route.path,
                        title: route.meta.title,
                        affix: route.meta.affix,
                    })
                }

            }
            this.currentTab = route.path
        },
        removeTab(path: string) {
            this.tabs = this.tabs.filter(tab => tab.path !== path)
        },

        setCurrentTab(path: string) {
            this.currentTab = path
        },

        resetTabs() {
            // // 保留固定页签
            const affixTabs = this.tabs.filter(tab => tab.affix)
            this.tabs = affixTabs || []
            this.currentTab = affixTabs.length > 0 ? affixTabs[0].path : ''

            // this.tabs = []
            // this.currentTab = ''

        },

    }
})