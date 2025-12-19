import dayjs from 'dayjs';

interface Account {
  id: number;
  vpn_account: string;
  vpn_pwd: string;
  online: boolean;
  device_id: number;
  region_id: number;
  device: string;
  region: string;
  region_code: string;
  logo: string;
  username: string;
  vpn_server: string;
  used: boolean;
  expire_time: string;
  update_time: string;
  create_time: string;
}

interface VPNLog {
  id: number;
  account: Account;
  vpn_account: string;
  region: string;
  device: string;
  username: string;
  duration_secs: number;
  expiry_secs: number;
  traffic_vol_bytes: number;
  traffic_vol_flow: string;
  in_bytes: number;
  out_bytes: number;
  down_flow: string;
  up_flow: string;
  online_time: string;
  virtual_ip: string;
  login_ip: string;
  login_terminal: string;
  online: boolean;
  update_time: string;
  logout_time: string;
  login_time: string;
}

/**
 * 补全虚拟数据
 * @param data 原始数据列表
 * @param startDate 开始日期 (YYYY-MM-DD)
 * @param endDate 结束日期 (YYYY-MM-DD)
 * @returns 补全后的数据列表
 */
export function completeVPNData(
  data: VPNLog[],
  startDate: string,
  endDate: string
): VPNLog[] {
  if (data.length === 0) {
    return generateFullRangeVirtualData(startDate, endDate);
  }

  // 1. 找出最小和最大login_time
  const sortedData = [...data].sort((a, b) =>
    dayjs(a.login_time).diff(dayjs(b.login_time))
  );
  const minLoginTime = sortedData[0].login_time;
  const maxLoginTime = sortedData[sortedData.length - 1].login_time;

  // 2. 生成startDate到minLoginTime的虚拟数据
  const startVirtualData = generateVirtualData(
    startDate,
    minLoginTime,
    sortedData[0] // 使用第一条数据作为模板
  );

  // 3. 生成maxLoginTime到endDate的虚拟数据
  const endVirtualData = generateVirtualData(
    maxLoginTime,
    endDate,
    sortedData[0] // 使用第一条数据作为模板
  );

  // 4. 合并所有数据并重新排序
  const completedData = [
    ...startVirtualData,
    ...sortedData,
    ...endVirtualData
  ].sort((a, b) => dayjs(a.login_time).diff(dayjs(b.login_time)));

  return completedData;
}

/**
 * 生成两个时间点之间的虚拟数据
 */
function generateVirtualData(
  startTime: string,
  endTime: string,
  template: VPNLog,
  includeStart: boolean = true,
  includeEnd: boolean = true
): VPNLog[] {
  const virtualData: VPNLog[] = [];
  const start = dayjs(startTime);
  const end = dayjs(endTime);


  // 处理起始时间点（非整点时）
  if (includeStart && start.minute() !== 0 || start.second() !== 0) {
    virtualData.push(createVirtualDataPoint(start, template));
  }


  // 生成每小时数据点（包含起始整点）
  let current = dayjs(startTime).startOf('hour');
  if (current.isBefore(start)) {
    current = current.add(1, 'hour');
  }



  while (current.isBefore(end)) {
    // 跳过已经包含的起始点
    if (!current.isSame(start) || includeStart) {
      virtualData.push(createVirtualDataPoint(current, template));
    }
    current = current.add(1, 'hour');
  }


  // 处理结束时间点（非整点时）
  if (includeEnd && (end.minute() !== 0 || end.second() !== 0)) {
    // 避免重复添加（当结束点刚好是整点时）
    if (!end.startOf('hour').isSame(end)) {
      virtualData.push(createVirtualDataPoint(end, template));
    }
  }

  return virtualData;
}

/**
 * 生成完整时间范围的虚拟数据（当原始数据为空时）
 */
function generateFullRangeVirtualData(
  startDate: string,
  endDate: string
): VPNLog[] {
  const template = createBaseTemplate();
  return generateVirtualData(startDate, endDate, template);
}

/**
 * 创建虚拟数据点
 */
function createVirtualDataPoint(
  time: dayjs.Dayjs,
  template: VPNLog
): VPNLog {
  return {
    ...template,
    id: -Math.floor(Math.random() * 10000), // 虚拟数据ID设为-1
    login_time: time.format('YYYY-MM-DD HH:mm:ss'),
    logout_time: time.add(1, 'hour').format('YYYY-MM-DD HH:mm:ss'),
    duration_secs: 0,
    traffic_vol_bytes: 0,
    traffic_vol_flow: '0.0MB',
    in_bytes: 0,
    out_bytes: 0,
    down_flow: '0.0MB',
    up_flow: '0.0MB',
    online_time: '0:00:00',
    online: false,
    update_time: time.format('YYYY-MM-DD HH:mm:ss')
  };
}

/**
 * 创建基础模板数据
 */
function createBaseTemplate(): VPNLog {
  const now = dayjs().format('YYYY-MM-DD HH:mm:ss');
  return {
    id: -1,
    account: {
      id: -1,
      vpn_account: 'virtual',
      vpn_pwd: '',
      online: false,
      device_id: -1,
      region_id: -1,
      device: 'Virtual',
      region: 'Virtual',
      region_code: 'VIR',
      logo: '',
      username: 'virtual',
      vpn_server: '',
      used: false,
      expire_time: now,
      update_time: now,
      create_time: now
    },
    vpn_account: 'virtual',
    region: 'Virtual',
    device: 'Virtual',
    username: 'virtual',
    duration_secs: 0,
    expiry_secs: 0,
    traffic_vol_bytes: 0,
    traffic_vol_flow: '0.0MB',
    in_bytes: 0,
    out_bytes: 0,
    down_flow: '0.0MB',
    up_flow: '0.0MB',
    online_time: '0:00:00',
    virtual_ip: '0.0.0.0',
    login_ip: '',
    login_terminal: '',
    online: false,
    update_time: now,
    logout_time: now,
    login_time: now
  };
}




export default completeVPNData