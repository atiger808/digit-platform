export interface IAccount {
    username?: string;
    identifier?: string;
    code?: string;
    password: string;
    password2?: string;
    mobile?: string;
    email?: string;
}

export interface IPhone {
    phone: string;
    code: string;
}

export interface IUser {
    id: number
    username: string
    real_name: string
    avatar: any
    gender: number
    email: string
    mobile: string
    department_info: DepartmentInfo
    roles: Role[]
    is_active: boolean
    create_time: string
}

export interface DepartmentInfo {
    id: number
    name: string
}

export interface Role {
    id: number
    name: string
    code: string
}


export interface ISystemState {
    usersList: IUser[]
    usersTotalCount: number
    listDepartments: any[]
    listRoles: any[]
    pageList: any[]
    pageTotalCount: number
}