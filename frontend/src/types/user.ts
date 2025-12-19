export interface UserProfile {
  id: number;
  username: string;  // 账号
  real_name: string; // 昵称
  email: string;
  profile?: object;
}

export interface ChangePasswordData {
  old_password: string;
  new_password: string;
  confirm_password: string;
}