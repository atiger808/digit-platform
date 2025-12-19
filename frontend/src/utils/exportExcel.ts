import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';

/**
 * 导出Excel文件
 * @param data 表格数据
 * @param headers 表头配置
 * @param fileName 文件名（不含扩展名）
 */
export const exportExcel = (
  data: Record<string, any>[],
  headers: Array<{ key: string; label: string }>,
  fileName: string = 'excel-data'
) => {
  // 根据headers筛选数据
  const filteredData = data.map(item => {
    const newItem: Record<string, any> = {};
    headers.forEach(header => {
      newItem[header.label] = item[header.key];
    });
    return newItem;
  });

  // 创建工作簿
  const worksheet = XLSX.utils.json_to_sheet(filteredData);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1');

  // 生成Excel文件并保存
  const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
  const blob = new Blob([excelBuffer], { type: 'application/octet-stream' });
  saveAs(blob, `${fileName}.xlsx`);
};