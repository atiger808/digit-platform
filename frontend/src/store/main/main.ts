import {defineStore} from "pinia";
import {
    getRolesList,
    getDepartmentsList,
    getMenusList,
    getUsersList,
    getDynamicMenusList
} from "@/service/main/main.ts";
import {sessionCache} from '@/utils/cache.ts'
import { PROFILE } from "@/global/constants.ts";

interface IMainState {
    listRoles: any[],
    listDepartments: any[],
    listUsers: any[],
    listMenus: any[]
}

const useMainStore = defineStore('main', {
    state: (): IMainState => ({
        listRoles: [],
        listDepartments: [],
        listUsers: [],
        listMenus: []
    }),
    actions: {
        async fetchListDataAction(is_staff: boolean) {
            // 获取菜单列表
            // const resultMenus = await getMenusList()
            // console.log('resultMenus ', resultMenus)
            // this.listMenus = resultMenus.data.data.results
            // console.log('this.listMenus ', this.listMenus)

            const resultMenus = await getDynamicMenusList()

            this.listMenus = resultMenus.data.data


            // 获取用户列表
            const resultUsers = await getUsersList({"page": 1, "page_size": 100, '_t': Date.now()})

            this.listUsers = resultUsers.data.data.results


            let profile = sessionCache.getCache(PROFILE)
            is_staff = is_staff || profile.is_staff
            console.log("is_staff ",is_staff)
            if (is_staff) {
                this.getDepartmentsListAction()
                this.getRolesListAction()
            }

        },
        async getDepartmentsListAction() {
            const departmentsListResult = await getDepartmentsList()
            this.listDepartments = departmentsListResult.data.data.results
        },

        async getRolesListAction() {
            const rolesListResult = await getRolesList()
            this.listRoles = rolesListResult.data.data.results
        },
    },
})

export default useMainStore