import dayjs from 'dayjs';

interface VPNLog {
  create_time: string;
  file_count: number,
  total_duration: number,
  total_size: number,
}

/**
 * 补全虚拟数据
 * @param data 原始数据列表
 * @param startDate 开始日期 (YYYY-MM-DD)
 * @param endDate 结束日期 (YYYY-MM-DD)
 * @returns 补全后的数据列表
 */
export function completeVirtualData(
  data: VPNLog[],
  startDate: string,
  endDate: string
): VPNLog[] {
  if (data.length === 0) {
    return generateFullRangeVirtualData(startDate, endDate);
  }

  // 1. 找出最小和最大login_time
  const sortedData = [...data].sort((a, b) =>
    dayjs(a.create_time).diff(dayjs(b.create_time))
  );
  const minLoginTime = sortedData[0].create_time;
  const maxLoginTime = sortedData[sortedData.length - 1].create_time;

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
  ].sort((a, b) => dayjs(a.create_time).diff(dayjs(b.create_time)));

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
    create_time: time.format('YYYY-MM-DD HH:mm:ss'),
    file_count: 0,
    total_duration: 0,
    total_size: 0,
  };
}

/**
 * 创建基础模板数据
 */
function createBaseTemplate(): VPNLog {
  const now = dayjs().format('YYYY-MM-DD HH:mm:ss');
  return {
    create_time: now,
    file_count: 0,
    total_duration: 0,
    total_size: 0,
    
  };
}




export default completeVirtualData