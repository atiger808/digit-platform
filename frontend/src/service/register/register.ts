import {api} from '@/service/request.ts'
import type { IAccount, IPhone } from "@/types/types.ts"

export const registerAccount = (account: IAccount) => api.post('user/api/auth/register/', account)