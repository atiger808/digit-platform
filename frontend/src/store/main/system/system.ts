import {defineStore} from "pinia";
import {
    postUsersListData,
    deleteUserById,
    addUserData,
    editUserData,
    postPageListData,
    deletePageById,
    addPageData,
    editPageData,
} from '@/service/main/system/system.ts'
import {sessionCache} from '@/utils/cache.ts'
import {
    PROFILE,
} from "@/global/constants.ts";
import {
    getRolesList,
    getDepartmentsList,
} from "@/service/main/main.ts";


import {getDynamicMenusList} from '@/service/main/main.ts'
import useMainStore from "@/store/main/main.ts"

import type {ISystemState} from "@/types/types.ts"
import {ElMessage} from "element-plus";
import {errorParse} from "@/utils/errorParse.ts";

const useSystemStore = defineStore('system', {
    state: (): ISystemState => ({
        usersList: [],
        usersTotalCount: 0,
        pageList: [],
        pageTotalCount: 0,
        listDepartments: [],
        listRoles: []
    }),
    actions: {
        async postUsersListAction(data: any, params: any) {
            const usersListResult = await postUsersListData(data, params)
            const {total, results} = usersListResult.data.data
            this.usersList = results
            this.usersTotalCount = total
            let profile = sessionCache.getCache(PROFILE)
            let is_staff = profile.is_staff
            console.log("is_staff ",is_staff)
            if (is_staff) {
                this.getDepartmentsListAction()
                this.getRolesListAction()
            }
        },

        async deleteUserByIdAction(id: number) {
            try {
                // 1.删除数据操作
                const deleteResult = await deleteUserById(id)

                // 2. 重新请求新的数据
                this.postUsersListAction({}, {page: 1, page_size: 10})

                // 3.获取完整数据
                const mainStore = useMainStore()
                mainStore.fetchListDataAction()


            } catch (e) {
                console.log('删除失败', e)
            }
        },

        async addUserDataAction(data: any) {
            try {
                const addResult = await addUserData(data)

                // 2. 重新请求新的数据
                this.postUsersListAction({}, {page: 1, page_size: 10})

                // 3.获取完整数据
                const mainStore = useMainStore()
                mainStore.fetchListDataAction()


            } catch (e) {
                console.log('添加失败', e)
                ElMessage.error(e.message || '添加失败')
            }

        },

        async editUserDataAction(id: number, data: any) {
            try {
                const editResult = await editUserData(id, data)

                // 2. 重新请求新的数据
                this.postUsersListAction({}, {page: 1, page_size: 10})

                // 3.获取完整数据
                const mainStore = useMainStore()
                mainStore.fetchListDataAction()


            } catch (e) {
                console.log('修改失败', e)
                ElMessage.error(e.message || '修改失败')
           }

        },


        async getDepartmentsListAction() {
            const departmentsListResult = await getDepartmentsList()
            console.log('departmentsListResult ', departmentsListResult)
            this.listDepartments = departmentsListResult.data.data.results
            console.log('this.listDepartments ', this.listDepartments)
        },

        async getRolesListAction() {
            const rolesListResult = await getRolesList()
            console.log('rolesListResult ', rolesListResult)
            this.listRoles = rolesListResult.data.data.results
            console.log('this.listRoles ', this.listRoles)
        },

        /* 针对页面的数据：增删改查 */
        async postPageListAction(data: any, params: any, pageName: string) {
            if (pageName === 'menus') {
                const pageListResult = await getDynamicMenusList()
                const results = pageListResult.data.data
                const total = pageListResult.data.data.length
                this.pageList = results
                this.pageTotalCount = total

            } else {
                const pageListResult = await postPageListData(pageName, data, params)
                const {total, results} = pageListResult.data.data
                this.pageList = results
                this.pageTotalCount = total
            }
            let profile = sessionCache.getCache(PROFILE)
            let is_staff = profile.is_staff
            console.log("is_staff ",is_staff)
            if (is_staff) {
                this.getDepartmentsListAction()
                this.getRolesListAction()
            }

        },

        async deletePageByIdAction(id: number, pageName: string) {
            try {
                // 1.删除数据操作
                const deleteResult = await deletePageById(pageName, id)

                // 2. 重新请求新的数据
                this.postPageListAction({}, {page: 1, page_size: 10}, pageName)

                // 3.获取完整数据
                const mainStore = useMainStore()
                mainStore.fetchListDataAction()
                return {success: true, error: ''}

            } catch (error) {
                console.log('删除失败', error)
                const errorInfo = errorParse(error)
                console.log('errorInfo', errorInfo)
                return {success: false, error: errorInfo || '删除失败'}
            }
        },

        async addPageDataAction(data: any, pageName: string) {
            try {
                const addResult = await addPageData(pageName, data)

                // 2. 重新请求新的数据
                this.postPageListAction({}, {page: 1, page_size: 10}, pageName)

                // 3.获取完整数据
                const mainStore = useMainStore()
                mainStore.fetchListDataAction()

                return {success: true, error: ''}
            } catch (error) {
                console.log('添加失败', error)
                const errorInfo = errorParse(error)
                console.log('errorInfo', errorInfo)
                return {success: false, error: errorInfo || '添加失败'}
            }

        },

        async editPageDataAction(id: number, data: any, pageName: string) {
            try {
                console.log('id: ', id)
                const editResult = await editPageData(pageName, id, data)

                // 2. 重新请求新的数据
                this.postPageListAction({}, {page: 1, page_size: 10}, pageName)

                // 3.获取完整数据
                const mainStore = useMainStore()
                mainStore.fetchListDataAction()

                return {success: true, error: ''}

            } catch (error) {
                console.log('修改失败', error)
                const errorInfo = errorParse(error)
                console.log('errorInfo', errorInfo)
                return {success: false, error: errorInfo || '修改失败'}
            }

        },

        async patchPageDataAction(id: number, data: any, pageName: string) {
            try {
                console.log('id: ', id)
                const editResult = await editPageData(pageName, id, data)
                console.log('editResult: ', editResult)
                return {success: true, error: ''}

            } catch (error) {
                console.log('修改失败', error)
                const errorInfo = errorParse(error)
                console.log('errorInfo', errorInfo)
                return {success: false, error: errorInfo || '修改失败'}
            }

        }
    }
})


export default useSystemStore