
from moviepy.editor import *
from PIL import Image
import os
from loguru import logger
from func_timeout import func_set_timeout
from pymediainfo import MediaInfo
from django.conf import settings
import subprocess
import json

from file.models import UploadedFile


@func_set_timeout(10)
def run_get_media_info(source):
    """
    获取视频想换信息
    :param source: 视频链接或者视频路径
    :return: dict
    """
    result = {}
    try:
        media_info = MediaInfo.parse(source)
        data = media_info.to_json()
        if data:
            d = json.loads(data)
            if d.get('tracks') and isinstance(d.get('tracks'), list):
                for i in d.get('tracks'):
                    if i and isinstance(i, dict) and i.get('track_type') == 'Video':
                        result['video'] = i
                    if i and isinstance(i, dict) and i.get('track_type') == 'Audio':
                        result['audio'] = i
                    if i and isinstance(i, dict) and i.get('track_type') == 'General':
                        result['general'] = i
    except Exception as e:
        logger.info(f'get_media_info error:{e}')
    if result:
        r = result
        d = {}
        try:
            d['vcodec_type'] = r.get('general', {}).get('codecs_video', '')
            d['acodec_type'] = r.get('general', {}).get('audio_codecs', '')
            d['width'] = round(float(r.get('video', {}).get('width'))) if r.get('video', {}).get('width') else None
            d['height'] = round(float(r.get('video', {}).get('height'))) if r.get('video', {}).get(
                'height') else None
            d['fps'] = round(float(r.get('video', {}).get('frame_rate'))) if r.get('video', {}).get(
                'frame_rate') else None
            d['ar_sample_rate'] = r.get('audio', {}).get('sampling_rate')
            d['bitrate'] = float(r.get('general', {}).get('overall_bit_rate')) / 1000 if r.get('general', {}).get(
                'overall_bit_rate') else None
            d['audio_bitrate'] = float(r.get('audio', {}).get('bit_rate')) / 1000 if r.get('audio', {}).get(
                'bit_rate') else None
            d['duration'] = r.get('general', {}).get('duration')
            d['file_size'] = r.get('general', {}).get('file_size')
        except Exception as e:
            logger.info(f'get_media_info parse error:{e}')
        result['metadata'] = d
    return result


def get_media_info(source):
    """
    获取视频想换信息
    :param source: 视频链接或者视频路径
    :return: dict
    """
    result = {}
    try:
        result = run_get_media_info(source)
    except func_timeout.exceptions.FunctionTimedOut as e:
        logger.info(f'source: {source} error: {e}')
    return result




@func_set_timeout(10)
def run_ffprobe_get_media_info(source, ffprobe='ffprobe'):
    result = {}
    try:
        p = subprocess.Popen(
            [f'{ffprobe}', '-i', f'{source}', '-print_format', 'json', '-show_format', '-show_streams', '-v', 'quiet'],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
        data = json.loads(p.stdout.read())
        if data:
            metadata = {}
            streams = data.get('streams')
            if streams and isinstance(streams, list):
                for i in streams:
                    if i.get('codec_type') == 'video':
                        metadata['vcodec_type'] = i.get('codec_name')
                        metadata['width'] = i.get('width')
                        metadata['height'] = i.get('height')
                        try:
                            metadata['fps'] = eval(i.get('r_frame_rate'))
                        except Exception as e:
                            logger.info(f'error: {e}')
                    if i.get('codec_type') == 'audio':
                        metadata['acodec_type'] = i.get('codec_name')
                        metadata['ar_sample_rate'] = i.get('sample_rate')
                        metadata['audio_bitrate'] = i.get('bit_rate')
            format = data.get('format')
            if format and isinstance(format, dict):
                metadata['bitrate'] = format.get('bit_rate')
                metadata['duration'] = format.get('duration')
                metadata['file_size'] = format.get('size')
            if metadata:
                result = data
                result['metadata'] = metadata
    except Exception as e:
        logger.info(f'error: {e}')
    return result


def ffprobe_get_media_info(source, ffprobe='ffprobe'):
    result = {}
    try:
        result = run_ffprobe_get_media_info(source, ffprobe=ffprobe)
    except func_timeout.exceptions.FunctionTimedOut as e:
        logger.info(f'source: {source} error: {e}')
    return result


@func_set_timeout(10)
def run_get_pull_metadata(pull_url, ffmpeg='ffmpeg'):
    """
    FFmpeg 获取视频相关信息
    :param pull_url: 视频链接，或者视频路径
    :param ffmpeg: ffmpeg程序
    :return: metada_dic dict
    """
    cmd = f'{ffmpeg} -i "{pull_url}"'
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    error_output = [i.strip() for i in p.stderr.readlines()]
    metada_dic = {}
    if "Metadata:" in error_output:
        for i in error_output[error_output.index("Metadata:") + 1:]:
            if ':' in i:
                li = i.split(':')
                if "Stream #" in i:
                    k, v = ':'.join(li[:3]).strip(), ':'.join(li[3:]).strip()
                    if 'Audio' in k:
                        try:
                            for i in v.split(','):
                                if 'Hz' in i:
                                    ar_sample_rate = i.replace('Hz', '').strip()
                                    metada_dic['ar_sample_rate'] = ar_sample_rate
                            metada_dic['acodec_type'] = v.split()[0].strip()
                        except Exception as e:
                            logger.info(f'get_pull_metadata audio error: {e}')
                    if 'Video' in k:
                        try:
                            video_info_list = [i.strip() for i in v.split(',')]
                            i_idx = 0
                            for j in video_info_list:
                                try:
                                    size_info = j.split(' ')[0].strip()
                                    if size_info[:2].isdigit() and 'x' in size_info:
                                        width, height = size_info.split('x')
                                        metada_dic['width'] = int(width)
                                        metada_dic['height'] = int(height)

                                        bitrate = video_info_list[i_idx + 1].split(' ')[0].strip()
                                        fps = video_info_list[i_idx + 2].split(' ')[0].strip()
                                        metada_dic['bitrate'] = float(bitrate)
                                        metada_dic['fps'] = float(fps)
                                    i_idx = i_idx + 1
                                except Exception as e:
                                    logger.info(f'get_pull_metadata video error: {e}')
                            metada_dic['vcodec_type'] = v.split()[0].strip()
                        except Exception as e:
                            logger.info(f'get_pull_metadata video error: {e}')
                else:
                    k, v = li[0].strip(), ':'.join(li[1:]).strip()
                metada_dic[k] = v
    return metada_dic


def get_pull_metadata(pull_url, ffmpeg='ffmpeg'):
    """
    FFmpeg 获取视频相关信息
    :param pull_url: 视频链接，或者视频路径
    :param ffmpeg: ffmpeg程序
    :return: metada_dic dict
    """
    result = {}
    try:
        result = run_get_pull_metadata(pull_url, ffmpeg=ffmpeg)
    except func_timeout.exceptions.FunctionTimedOut as e:
        logger.info(f'source: {pull_url} error: {e}')
    return result


@func_set_timeout(10)
def run_get_metadata(pull_url, ffprobe='ffprobe'):
    """
    获取视频元数据
    :param pull_url:
    :param ffprobe:
    :return:
    """
    dic = {}
    try:
        cmd = f'{ffprobe} -v quiet -show_format -show_streams -print_format json "{pull_url}"'
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             encoding='utf-8')
        dic = json.loads(p.stdout.read())
    except Exception as e:
        logger.info(f'get_metadata error: {e}')
    return dic


def get_metadata(pull_url, ffprobe='ffprobe'):
    """
    获取视频元数据
    :param pull_url:
    :param ffprobe:
    :return:
    """
    result = {}
    try:
        result = run_get_metadata(pull_url, ffprobe=ffprobe)
    except func_timeout.exceptions.FunctionTimedOut as e:
        logger.info(f'source: {pull_url} error: {e}')
    return result



def save_gif_work(source_video_file, gif_cover_file=None, static_cover_file=None):
    try:
        video = VideoFileClip(source_video_file)
        width, height = video.size
        fps = video.fps
        duration = video.duration
        gif_cover = video.subclip(0, 2).resize(height=120)
        gif_cover.write_gif(gif_cover_file)
        video.save_frame(static_cover_file, t=0, withmask=False)
        video.close()
        item = dict()
        item['width'] = width
        item['height'] = height
        item['fps'] = fps
        item['duration'] = duration
        return item
    except Exception as e:
        logger.info(f'封面动图生成失败！source_video_file: {source_video_file} error: {e}')
        return {}



def update_video_attrs(video_id):
    try:
        video_obj = UploadedFile.objects.filter(id=video_id).first()
        if not video_obj:
            logger.info(f'video_id: {video_id} is not exists')
            return

        if not video_obj.fps or not video_obj.width or not video_obj.vcodec_type:
            source_uri = video_obj.file.url.strip('/')
            cover_uri_static = os.path.splitext(source_uri)[0] + '.jpg'
            cover_uri_gif = os.path.splitext(source_uri)[0] + '.gif'

            source_path = os.path.join(settings.BASE_DIR, source_uri)
            cover_path_static = os.path.join(settings.BASE_DIR, cover_uri_static)
            cover_path_gif = os.path.join(settings.BASE_DIR, cover_uri_gif)

            item = save_gif_work(source_path, static_cover_file=cover_path_static, gif_cover_file=cover_path_gif)
            metadata = ffprobe_get_media_info(source_path).get('metadata', {})
            if metadata:
                logger.info(f'metadata: {metadata}')
                video_obj.fps = metadata.get('fps')
                video_obj.width = metadata.get('width')
                video_obj.height = metadata.get('height')
                video_obj.duration = metadata.get('duration')
                video_obj.bitrate = metadata.get('bitrate')
                video_obj.audio_bitrate = metadata.get('audio_bitrate')
                video_obj.ar_sample_rate = metadata.get('ar_sample_rate')
                video_obj.vcodec_type = metadata.get('vcodec_type')
                video_obj.acodec_type = metadata.get('acodec_type')
                video_obj.save()
                logger.info(f'metadata update success')
            elif item:
                logger.info(f'item: {item}')
                video_obj.fps = metadata.get('fps')
                video_obj.width = metadata.get('width')
                video_obj.height = metadata.get('height')
                video_obj.duration = metadata.get('duration')
                video_obj.save()
                logger.info(f'item update success')
            else:
                logger.info(f'metadata is empty: {video_id}')

    except Exception as e:
        logger.info(f'error: {e}')