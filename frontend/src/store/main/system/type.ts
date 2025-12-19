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
}