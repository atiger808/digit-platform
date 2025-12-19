// utils/chunkedDownload.ts
import {api} from '@/service/request.ts'
import type {CancelTokenSource} from 'axios';

import {
    downloadFileStart,
    downloadFileCancel,
    downloadFileComplete
} from "@/service/main/files/files.ts";

interface ChunkedDownloadOptions {
    url: string;
    fileSize: number;
    fileId: number;
    chunkSize?: number;
    onProgress?: (progress: number) => void;
    onChunk?: (chunk: ArrayBuffer, loaded: number) => void;
    cancelToken?: CancelTokenSource;
}

export const chunkedDownload = async (options: ChunkedDownloadOptions) => {
    const {
        url,
        fileSize,
        fileId,
        chunkSize = 2 * 1024 * 1024, // 默认2MB分块
        onProgress,
        onChunk,
        cancelToken
    } = options;

    // 2. 标记开始下载
    const startResult = await downloadFileStart(fileId);
    console.log('开始下载结果:', startResult)
    const download_record_id = startResult.data.data.id;
    console.log('download_record_id:', download_record_id)
    try {
        const chunks: ArrayBuffer[] = [];
        let downloaded = 0;
        // 3. 分块下载
        while (downloaded < fileSize) {
            const end = Math.min(downloaded + chunkSize - 1, fileSize - 1);
            const range = `bytes=${downloaded}-${end}`;

            const response = await api.get(url, {
                responseType: 'arraybuffer',
                headers: {Range: range},
                cancelToken: cancelToken?.token,
                timeout: 30000
            });

            if (response.status !== 206 && response.status !== 200) {
                throw new Error(`Unexpected status code: ${response.status}`);
            }

            const chunk = response.data;
            chunks.push(chunk);
            downloaded += chunk.byteLength;

            onChunk?.(chunk, downloaded);

            const progress = Math.round((downloaded / fileSize) * 100);
            onProgress?.(progress);
        }

        // 4. 标记下载完成
        await downloadFileComplete(fileId, {download_record_id: download_record_id})

        // 合并分块
        return mergeChunks(chunks)

    } catch (error) {
        if (api.isCancel(error)) {
            await downloadFileCancel(fileId, {download_record_id: download_record_id});
            throw new Error('下载取消')
        }
        throw error
    }
};


const mergeChunks = (chunks: ArrayBuffer[]): ArrayBuffer => {
    const totalLength = chunks.reduce((acc, chunk) => acc + chunk.byteLength, 0);
    const merged = new Uint8Array(totalLength);
    let offset = 0;

    chunks.forEach(chunk => {
        merged.set(new Uint8Array(chunk), offset);
        offset += chunk.byteLength;
    });

    return merged.buffer;
};