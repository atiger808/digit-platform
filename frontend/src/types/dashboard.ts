export interface DashboardSummary {
  today_file_count: number;
  today_duration: number;
  total_file_count: number;
  total_duration: number;
}

export interface UserVideoStat {
  user_id: number;
  username: string;
  real_name: string;
  file_count: number;
  total_duration: number;
  total_size: number;
}

export interface OnlineUser {
  user_id: number;
  username: string;
  real_name: string;
  last_login_time: string;
}