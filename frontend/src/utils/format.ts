import dayjs from "dayjs";
import utc from 'dayjs/plugin/utc'

// dayjs.extend(utc)

export const formatUTC = (utcString: string, format:string="YYYY-MM-DD HH:mm:ss") => {
  // return dayjs.utc(utcString).utcOffset(8).format(format);
  if (!utcString) return ''
  return dayjs(utcString).format(format)
};


export const formatBytes = (bytes: number, decimals = 2) => {
  if (bytes === 0 || !Number.isFinite(bytes)) return '0 Bytes';
  const k = 1024,
    dm = decimals < 0 ? 0 : decimals,
    sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'],
    i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

export const formatDuration = (seconds: number): string => {
  const days = Math.floor(seconds / (24 * 3600));
  const hours = Math.floor((seconds % (24 * 3600)) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  let result = '';
  if (days > 0) result += days + '天';
  if (hours > 0) result += hours + '小时';
  if (minutes > 0) result += minutes + '分钟';
  if (secs > 0 || result === '') result += secs + '秒'; // 如果都是0，显示0秒
  return result;
};

export function formatAxis(param: Date): string {
	let hour: number = new Date(param).getHours();
	if (hour < 6) return '凌晨好';
	else if (hour < 9) return '早上好';
	else if (hour < 12) return '上午好';
	else if (hour < 14) return '中午好';
	else if (hour < 17) return '下午好';
	else if (hour < 19) return '傍晚好';
	else if (hour < 22) return '晚上好';
	else return '夜里好';
}

// 首字母大写
export function capitalize(str: string): string {
	return str.charAt(0).toUpperCase() + str.slice(1);
}


export function toLocalISOString(date: Date): string {
  const pad = (n: number) => n.toString().padStart(2, '0');
  
  const year = date.getFullYear();
  const month = pad(date.getMonth() + 1);
  const day = pad(date.getDate());
  const hours = pad(date.getHours());
  const minutes = pad(date.getMinutes());
  const seconds = pad(date.getSeconds());
  
  // 固定为 +08:00（根据你所在时区调整）
  return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}+08:00`;
}