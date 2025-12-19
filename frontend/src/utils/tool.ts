import {ElMessage} from 'element-plus';

// 复制功能函数
export const copyToClipboard = async (content: string) => {
    try {
        if (typeof content != "string") {
            content = JSON.stringify(content);
        }
        await navigator.clipboard.writeText(content);
        ElMessage.success('复制成功!');
    } catch (err) {
        console.error('复制失败:', err);
        useFallbackCopy(content);
    }
};

// 兼容方案（旧版浏览器）
const useFallbackCopy = (content: string) => {
    const textarea = document.createElement('textarea');
    textarea.value = content;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();

    try {
        const successful = document.execCommand('copy');
        successful
            ? ElMessage.success('复制成功!')
            : ElMessage.error('复制失败，请手动复制');
    } catch (err) {
        ElMessage.error(`复制失败: ${err}`);
    } finally {
        document.body.removeChild(textarea);
    }
};

export const parseContentDisposition = (contentDisposition: string | null): string => {
    if (!contentDisposition) return 'download';


    try {
        if (contentDisposition.startsWith('=?') && contentDisposition.endsWith('?=')) {
            // 1. 提取Base64部分
            const base64Part = contentDisposition.split('?b?')[1].split('?=')[0];

            // 2. Base64解码
            const decoded = atob(base64Part);
            console.log("decoded: ", decoded)
            contentDisposition = decoded;
        }
    } catch (e) {
        // 忽略错误
        console.log('解码失败:', e)
    }


    // 尝试 RFC 5987 编码 (filename*=utf-8'')
    const utf8FilenameMatch = contentDisposition.match(/filename\*=utf-8''([^;]+)/i);
    if (utf8FilenameMatch && utf8FilenameMatch[1]) {
        console.log("utf8FilenameMatch: ", utf8FilenameMatch)
        return decodeURIComponent(utf8FilenameMatch[1]);
    }


    // 尝试标准文件名 (filename="...")
    const filenameMatch = contentDisposition.match(/filename="?([^;"]+)/i);
    if (filenameMatch && filenameMatch[1]) {
        // 移除可能的引号
        return filenameMatch[1].replace(/['"]/g, '');
    }

    // 尝试 URL 编码的文件名
    const urlEncodedMatch = contentDisposition.match(/filename=([^;]+)/i);
    if (urlEncodedMatch && urlEncodedMatch[1]) {
        try {
            return decodeURIComponent(urlEncodedMatch[1]);
        } catch {
            return urlEncodedMatch[1];
        }
    }

    return 'download';
};


