# -*- coding: utf-8 -*-
# @File   :serializers.py
# @Time   :2025/4/29 14:15
# @Author :admin
from loguru import logger
from django.conf import settings
from rest_framework import serializers
from .models import UploadedFile, UserFileAccess, DownloadRecord, FileTag
import os
from django.contrib.auth import get_user_model
from utils.tool import save_gif_work

User = get_user_model()

class BaseDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        # 获取原始ISO 格式的时间字符串并截取前19位
        iso_str = super().to_representation(value)
        return str(iso_str)[:19] if iso_str else ''



class FileTagSerializer(serializers.ModelSerializer):
    """视频标签序列化器"""
    file_count = serializers.SerializerMethodField()

    class Meta:
        model = FileTag
        fields = '__all__'

    def get_file_count(self, obj):
        return UploadedFile.objects.filter(tags=obj, completed=True).count()

class UploadedFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    create_time = BaseDateTimeField(format=None)
    update_time = BaseDateTimeField(format=None)

    tags_info = FileTagSerializer(source='tags', many=True, read_only=True)

    class Meta:
        model = UploadedFile
        fields = '__all__'
        read_only_fields = ['completed']

    def get_file_url(self, obj):
        # 检查文件是否存在
        if not obj.file or not obj.file.name:
            logger.error(f"File does not exist for object {obj.id}")
            return None

        return os.path.join(settings.BASE_URL,obj.file.url.strip('/'))


class UserFileAccessSerializer(serializers.ModelSerializer):
    uploaded_file = UploadedFileSerializer()

    file_md5 = serializers.CharField(source='uploaded_file.file_md5', read_only=True)
    ext = serializers.CharField(source='uploaded_file.ext', read_only=True)
    file_size = serializers.CharField(source='uploaded_file.file_size', read_only=True)
    fps = serializers.CharField(source='uploaded_file.fps', read_only=True)
    width = serializers.CharField(source='uploaded_file.width', read_only=True)
    height = serializers.CharField(source='uploaded_file.height', read_only=True)
    duration = serializers.CharField(source='uploaded_file.duration', read_only=True)
    bitrate = serializers.CharField(source='uploaded_file.bitrate', read_only=True)
    audio_bitrate = serializers.CharField(source='uploaded_file.audio_bitrate', read_only=True)
    ar_sample_rate = serializers.CharField(source='uploaded_file.ar_sample_rate', read_only=True)
    vcodec_type = serializers.CharField(source='uploaded_file.vcodec_type', read_only=True)
    acodec_type = serializers.CharField(source='uploaded_file.acodec_type', read_only=True)
    download_count = serializers.CharField(source='uploaded_file.download_count', read_only=True)


    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    file_url = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    icon = serializers.SerializerMethodField(read_only=True)
    user_list = serializers.SerializerMethodField(read_only=True)

    static_cover_url = serializers.SerializerMethodField(read_only=True)
    gif_cover_url = serializers.SerializerMethodField(read_only=True)
    resolution = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserFileAccess
        fields = [
            'uploaded_file',
            'id',
            'original_filename',
            'description',
            'download_count',
            'create_time',
            'update_time',
            'username',
            'user_id',
            'file_url',
            'static_cover_url',
            'gif_cover_url',
            'status',
            'icon',
            'user_list',

            'file_md5',
            'ext',
            'file_size',
            'fps',
            'width',
            'height',
            'duration',
            'bitrate',
            'audio_bitrate',
            'ar_sample_rate',
            'vcodec_type',
            'acodec_type',
            'resolution',
        ]

    def get_status(self, obj):
        return 'completed' if obj.uploaded_file.completed else 'uploading'

    def get_file_url(self, obj):
        if obj.uploaded_file.file:
            return os.path.join(settings.BASE_URL, obj.uploaded_file.file.url.strip('/'))
            # request = self.context.get('request')
            # return request.build_absolute_uri(obj.uploaded_file.file.url) if request else obj.uploaded_file.file.url
        return None


    def get_icon(self,  obj):
        icon_name = f'{obj.os}-icon.jpg' if obj.os else 'document-icon.png'
        return os.path.join(settings.BASE_URL, 'media', 'images', icon_name)

    def get_user_list(self, obj):
        user = self.context['request'].user
        if user.is_superuser:
            return [obj.user.id for obj in UserFileAccess.objects.filter(uploaded_file=obj.uploaded_file)]
        return [obj.user.id for obj in UserFileAccess.objects.filter(uploaded_file=obj.uploaded_file, user=user)]




    def get_static_cover_url(self, obj):
        if obj.uploaded_file.completed:
            ext = obj.uploaded_file.ext
            if str(ext) in ['mp4', 'flv', 'ts', 'avi', 'mkv']:
                source_uri = obj.uploaded_file.file.url.strip('/')
                source_path = os.path.join(settings.BASE_DIR, source_uri)
                cover_uri = os.path.splitext(source_uri)[0] + '.jpg'
                cover_path = os.path.join(settings.BASE_DIR, cover_uri)
                if not os.path.exists(cover_path):
                    logger.info(f'cover_path: {cover_path} source_path: {source_path}')
                    save_gif_work(source_path, static_cover_file=cover_path, gif_cover_file=cover_path.replace('.jpg', '.gif'))
                return os.path.join(settings.BASE_URL, cover_uri)
            elif str(ext) in ['png', 'jpg', 'jpeg']:
                return os.path.join(settings.BASE_URL, obj.uploaded_file.file.url.strip('/'))

        return None

    def get_gif_cover_url(self, obj):
        if obj.uploaded_file.completed:
            ext = obj.uploaded_file.ext
            if str(ext) in ['mp4', 'flv', 'ts', 'avi', 'mkv']:
                source_uri = obj.uploaded_file.file.url.strip('/')
                source_path = os.path.join(settings.BASE_DIR, source_uri)
                cover_uri = os.path.splitext(source_uri)[0] + '.gif'
                cover_path = os.path.join(settings.BASE_DIR, cover_uri)
                if not os.path.exists(cover_path):
                    logger.info(f'cover_path: {cover_path} source_path: {source_path}')
                    save_gif_work(source_path, static_cover_file=cover_path, gif_cover_file=cover_path.replace('.gif', '.jpg'))
                return os.path.join(settings.BASE_URL, cover_uri)
            elif str(ext) in ['png', 'jpg', 'jpeg']:
                return os.path.join(settings.BASE_URL, obj.uploaded_file.file.url.strip('/'))

        return None

    def get_resolution(self, obj):
        if obj.uploaded_file.width and obj.uploaded_file.height:
            return f'{int(obj.uploaded_file.width)}x{int(obj.uploaded_file.height)}'
        return ''




class SizeRangeSerializer(serializers.Serializer):
    min = serializers.IntegerField(min_value=0, required=False)
    max = serializers.IntegerField(min_value=0, required=False)

class FileSearchSerializer(serializers.Serializer):
    keyword = serializers.CharField(required=False)
    status = serializers.ChoiceField(
        choices=[('completed', '已完成'), ('uploading', '上传中')],
        required=False
    )
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    extensions = serializers.ListField(
        child=serializers.CharField(max_length=10),
        required=False
    )
    size_range = SizeRangeSerializer(required=False)
    username = serializers.CharField(required=False)  # 新增用户名查询
    order_by = serializers.CharField(required=False)

    def validate(self, attrs):
        # 验证日期范围
        if attrs.get('start_date') and attrs.get('end_date'):
            if attrs['start_date'] > attrs['end_date']:
                raise serializers.ValidationError("结束日期不能早于开始日期")
        return attrs



