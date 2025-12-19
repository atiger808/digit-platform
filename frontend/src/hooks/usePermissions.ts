import {useLoginStore} from "@/store/login/login.ts";


// export function usePermissions(permissionID:string) {  // 确保使用 export
//   const store = useLoginStore()
//
//   const hasPermission = (permission: string) => {
//     return computed(() => store.getters.hasPermission(permission))
//   }
//
//   return {
//     hasPermission
//   }
// }


export function usePermissions(permissionID: string) {  // 确保使用 export
    const store = useLoginStore()
    const { permissions } = store
    return !!permissions.find(item => item.includes(permissionID))
}


