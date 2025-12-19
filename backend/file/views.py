from celery.utils.imports import module_file
from django.shortcuts import render
from django.db.models import Q
from rest_framework.decorators import action
from django.db.models import Count, Sum
from django.db.models.functions import TruncDay, TruncHour  # ✅ 关键导入
from django.utils import timezone
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from django.http import FileResponse, StreamingHttpResponse, HttpResponse
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch
from django.db import models
from rest_framework.filters import SearchFilter, OrderingFilter
from dateutil import parser
from loguru import logger
from django.conf import settings
import os
import re
from urllib.parse import quote
import requests
from django.utils.encoding import escape_uri_path
import threading
import multiprocessing
from utils.tool import update_video_attrs
from utils.mixins import CustomResponseMixin, EncryptionResponseMixin
# 添加一些常见的 MIME 类型映射
import mimetypes


mimetypes.add_type('application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.docx')
mimetypes.add_type('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '.xlsx')
mimetypes.add_type('application/vnd.ms-excel.sheet.macroEnabled.12', '.xlsm')
mimetypes.add_type('application/vnd.ms-powerpoint', '.ppt')
mimetypes.add_type('application/vnd.openxmlformats-officedocument.presentationml.presentation', '.pptx')
mimetypes.add_type('application/zip', '.zip')
mimetypes.add_type('application/x-rar-compressed', '.rar')
mimetypes.add_type('application/x-7z-compressed', '.7z')

from .serializers import (
    UploadedFileSerializer,
    UserFileAccessSerializer,
    FileSearchSerializer
)
from .filters import UserFileAccessFilter
from .models import UploadedFile, UserFileAccess, DownloadRecord
from utils.mixins import CustomResponseMixin

User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'total': self.page.paginator.count,
            'page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'has_next': self.page.has_next(),
            'has_previous': self.page.has_previous(),
            'results': data,
        })


class UserFilesViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    queryset = UserFileAccess.objects.select_related(
        'user', 'uploaded_file'
    ).order_by('-create_time')
    serializer_class = UserFileAccessSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]

    filterset_class = UserFileAccessFilter

    # 可搜索字段
    search_fields = [
        'original_filename',
        'description',
        'uploaded_file__filename',
        'uploaded_file__file_md5',
        'uploaded_file__ext'
    ]

    def get_queryset(self):
        queryset = self.get_user_file_access_queryset(self.request.user)

        # 状态过滤（示例：completed=true/false）
        status = self.request.query_params.get('status')
        if status in ['completed', 'uploading']:
            queryset = queryset.filter(
                uploaded_file__completed=(status == 'completed')
            )

        return queryset

    def get_user_file_access_queryset(self, user):
        """根据用户权限获取对应的 UserFileAccess 查询集"""
        if user.is_superuser:
            # 超级用户可以访问所有记录，并优化查询性能
            return UserFileAccess.objects.select_related('uploaded_file').order_by('-create_time')
        else:
            # 普通用户只能访问自己的记录
            return UserFileAccess.objects.filter(user=user).select_related('uploaded_file').order_by('-create_time')

    @action(detail=False, methods=['post'])
    def query(self, request):

        queryset = self.filter_queryset(self.get_queryset())

        # 2. 应用过滤器
        filterset = UserFileAccessFilter(data=request.data, queryset=queryset)
        if not filterset.is_valid():
            return Response({
                'code': 400,
                'msg': '参数错误',
                'errors': filterset.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        queryset = filterset.qs
        logger.info(f'queryset: {len(queryset)}')

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': serializer.data,
        }, status=status.HTTP_200_OK)


    @action(detail=False, methods=['get'])
    def files_summary(self, request):
        """
        统计每个用户的视频素材数量、总时长、总字节数。
        - 普通用户：仅返回自己
        - 超级用户/管理员：返回所有用户（可选分页或限制）
        """
        user = request.user

        # 1. 构建基础查询集（仅 completed 的视频文件）
        base_access_qs = UserFileAccess.objects.select_related('uploaded_file').filter(
            uploaded_file__completed=True,
            uploaded_file__duration__isnull=False,  # 仅统计有 duration 的（即视频）
            uploaded_file__file_size__gt=0
        )

        # 2. 根据权限过滤用户范围
        if user.is_superuser or user.is_staff:
            # 管理员：统计所有用户
            user_ids = base_access_qs.values_list('user_id', flat=True).distinct()
        else:
            # 普通用户：只统计自己
            user_ids = [user.id]

        # 3. 聚合统计：按 user_id 分组
        stats_qs = base_access_qs.filter(
            user_id__in=user_ids
        ).values(
            'user_id',
            'user__username',
            'user__real_name'
        ).annotate(
            file_count=Count('uploaded_file_id', distinct=True),
            total_duration=Sum('uploaded_file__duration'),
            total_size=Sum('uploaded_file__file_size')
        ).order_by('user_id')

        # 4. 构造返回数据
        result = []
        for stat in stats_qs:
            result.append({
                'user_id': stat['user_id'],
                'username': stat['user__username'],
                'real_name': stat['user__real_name'] or stat['user__username'],
                'file_count': stat['file_count'] or 0,
                'total_duration': float(stat['total_duration'] or 0),
                'total_size': stat['total_size'] or 0,
            })

        logger.info(f'result: {result}')

        return Response({
            'code': 200,
            'msg': 'success',
            'data': result
        })

    @action(detail=False, methods=['get'], url_path='user_video_stats')
    def user_video_stats(self, request):
        """
        获取用户视频素材统计（数量、总时长、总大小）
        - 普通用户：仅自己
        - 管理员：所有用户
        仅统计 completed=True 且 duration 不为 null 的视频文件
        """
        user = request.user

        # Step 1: 获取用户可见的 UserFileAccess 查询集（带权限）
        if user.is_superuser or user.is_staff:
            # 管理员：所有用户
            access_queryset = UserFileAccess.objects.select_related('uploaded_file').filter(
                uploaded_file__completed=True,
                uploaded_file__duration__isnull=False,
                uploaded_file__file_size__gt=0
            )
        else:
            # 普通用户：仅自己
            access_queryset = UserFileAccess.objects.select_related('uploaded_file').filter(
                user=user,
                uploaded_file__completed=True,
                uploaded_file__duration__isnull=False,
                uploaded_file__file_size__gt=0
            )

        # Step 2: 按用户聚合统计
        stats = access_queryset.values(
            'user_id',
            'user__username',
            'user__real_name'
        ).annotate(
            file_count=Count('uploaded_file_id', distinct=True),
            total_duration=Sum('uploaded_file__duration'),
            total_size=Sum('uploaded_file__file_size')
        ).order_by('user_id')

        # Step 3: 构造响应数据
        result = []
        for item in stats:
            result.append({
                'user_id': item['user_id'],
                'username': item['user__username'],
                'real_name': item['user__real_name'] or item['user__username'],
                'file_count': item['file_count'] or 0,
                'total_duration': float(item['total_duration'] or 0),
                'total_size': item['total_size'] or 0,
            })

        return Response({
            'code': 200,
            'msg': 'success',
            'data': result
        })

    @action(detail=True, methods=['delete'])
    def delete(self, request, pk=None):
        """删除文件记录和物理文件"""
        request_user = request.user
        file_access = None
        try:
            file_access = self.get_object()
            uploaded_file = file_access.uploaded_file

            # 检查是否还有其他关联记录
            other_accesses_count = UserFileAccess.objects.filter(uploaded_file=uploaded_file).exclude(
                pk=file_access.pk).count()
            logger.info(f'other_accesses_count: {other_accesses_count}')
            other_accesses_count = UserFileAccess.objects.filter(uploaded_file=uploaded_file).exclude(
                user=request.user).count()
            logger.info(f'other_accesses_count: {other_accesses_count}')

            # 管理员或没有其他关联时允许删除物理文件
            can_delete_physical = (
                    # request.user.is_superuser or
                    other_accesses_count == 0
            )

            with transaction.atomic():
                if can_delete_physical:
                    if uploaded_file.file:
                        try:
                            source_uri = uploaded_file.file.url.strip('/')
                            cover_uri_static = os.path.splitext(source_uri)[0] + '.jpg'
                            cover_uri_gif = os.path.splitext(source_uri)[0] + '.gif'
                            cover_path_static = os.path.join(settings.BASE_DIR, cover_uri_static)
                            cover_path_gif = os.path.join(settings.BASE_DIR, cover_uri_gif)
                            if os.path.exists(cover_path_static):
                                os.remove(cover_path_static)
                            if os.path.exists(cover_path_gif):
                                os.remove(cover_path_gif)
                        except Exception as e:
                            logger.info(f'error: {e}')
                        uploaded_file.file.delete()  # 删除物理文件
                    uploaded_file.delete()  # 删除数据库记录
                    message = '文件及记录已彻底删除'
                else:
                    file_access.delete()  # 只删除关联记录
                    message = '"已从您的文件列表中移除"'

                logger.info(
                    f'request_user: {request_user} pk: {pk} can_delete_physical: {can_delete_physical} {message}')

                return Response({
                    'code': 200,
                    'msg': message
                }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f'Error deleting file: {str(e)}')
            return Response({
                'code': 500,
                'msg': '文件删除失败',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'])
    def rename(self, request, pk=None):
        """重命名"""
        file_access = self.get_object()
        new_description = request.data.get('new_description')

        logger.info(f'new_description: {new_description} pk: {pk}')

        if not new_description:
            return Response({
                'code': 400,
                'msg': '请输入新的文件名'
            }, status=status.HTTP_400_BAD_REQUEST)

        file_access.description = new_description
        file_access.save()

        logger.info(f'file_access: {file_access} 重命名成功')

        return Response({
            'code': 200,
            'msg': '重命名成功',
            'data': self.get_serializer(file_access).data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def edit(self, request, pk=None):
        request_user = request.user

        if not request_user.is_superuser or not request_user.is_staff:
            logger.info(f'{request_user} 无权限')
            return Response({
                'code':403,
                'msg': '无操作权限'
            }, status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()
        user_id = request.data.get('user_id')
        user_list = request.data.get('user_list') or []
        

        if not isinstance(user_list, list):
            return Response({
                'code': 400,
                'msg': '参数错误',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        if user_id:
            user_list.append(user_id)

        description = request.data.get('description')
        logger.info(f'instance: {instance} user_id: {user_id}')
        if not instance:
            return Response({
                'code': 400,
                'msg': '文件不存在'
            }, status=status.HTTP_400_BAD_REQUEST)

        has_exists_user_list = [obj.user for obj in self.get_queryset().filter(uploaded_file=instance.uploaded_file)]

        logger.info(f'has_exists_user_list: {has_exists_user_list} user_list: {user_list}')

        for old_user in has_exists_user_list:
            if old_user.id not in user_list:
                UserFileAccess.objects.filter(uploaded_file=instance.uploaded_file, user=old_user).delete()
                logger.info(f"request_user: {request_user} 删除用户关联: {old_user.username} instance: {instance}")

        for user_id in user_list:

            existing_user = User.objects.filter(id=user_id).first()
            if existing_user:

                # 安全创建用户关联
                user_access, created = UserFileAccess.objects.get_or_create(
                    user=existing_user,
                    uploaded_file=instance.uploaded_file,
                    defaults={
                        'description': description or instance.description,
                    }
                )

                if instance.user == existing_user:
                    if (description and user_access.description != description):
                        user_access.description = description or user_access.description
                        user_access.save()
                        logger.info(
                            f'request_user: {request_user} 文件描述更新成功 -> {existing_user} user_access: {user_access}')

                if created:
                    logger.info(
                        f'request_user: {request_user} 安全创建用户关联成功 -> {existing_user} user_access: {user_access}')

            else:
                logger.info(f'request_user: {request_user} user_id: {user_id}, 用户不存在')

        return Response({
            'code': 200,
            'msg': '更新成功',
        }, status=status.HTTP_200_OK)


@action(detail=True, methods=['get'])
def custom_retrieve(self, request, pk=None):
    return super().retrieve(request, pk)


class InitUploadView(CustomResponseMixin, APIView):
    permission_classes = [IsAuthenticated]  # 需要登录

    def post(self, request):
        file_md5 = request.data.get('file_md5')
        filename = request.data.get('filename')
        total_chunks = request.data.get('total_chunks')

        description = os.path.splitext(filename)[0] if filename else ''

        logger.info(f'request.user: {request.user}')

        # 检查是否已存在相同MD5的完整文件
        existing_file = UploadedFile.objects.filter(
            file_md5=file_md5,
            completed=True
        ).first()
        logger.info(f'existing_file: {existing_file}')
        if existing_file:
            try:
                # 安全创建用户关联
                user_access, created = UserFileAccess.objects.get_or_create(
                    user=request.user,
                    uploaded_file=existing_file,
                    defaults={
                        'original_filename': filename,
                        'description': description,
                    }
                )
                logger.info(f'user_access: {user_access} created: {created}')
                return Response({
                    'code': 200,
                    'msg': '文件已存在' + (
                        f'(新建关联) | {user_access.user}' if created else f'(已有关联) | {user_access.user}'),
                    'id': existing_file.id,
                    'file_md5': existing_file.file_md5,
                    'filename': existing_file.filename,
                    'ext': existing_file.ext,
                    'create_time': existing_file.create_time,
                    'user': f'{user_access.user}',
                    'is_existing': True,

                })
            except Exception as e:
                logger.error(f'Error: {e}')
                return Response({
                    'code': 500,
                    'msg': f'创建文件关联失败: {str(e)}',
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 创建新的上传记录
        upload_id = file_md5
        uploaded_file, created = UploadedFile.objects.get_or_create(
            upload_id=upload_id,
            defaults={
                'file_md5': file_md5,
                'filename': filename,
                'description': description,
                'total_chunks': total_chunks,
            }
        )

        # 创建用户文件访问记录
        UserFileAccess.objects.get_or_create(
            user=request.user,
            uploaded_file=uploaded_file,
            defaults={
                'original_filename': filename,
                'description': description,
            }
        )

        if not created:
            return Response({
                'code': 200,
                'msg': '继续上传',
                'upload_id': upload_id,
                'uploaded_chunks': uploaded_file.uploaded_chunks,

            })
        chunk_dir = os.path.join(settings.MEDIA_ROOT, 'chunks', upload_id)
        os.makedirs(chunk_dir, exist_ok=True)

        return Response({
            'code': 200,
            'msg': '初始化成功',
            'upload_id': upload_id,

        })


class UploadChunkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        upload_id = request.data.get('upload_id')
        chunk_number = request.data.get('chunk_number')
        chunk = request.data.get('chunk')

        try:
            # 检查用户是否有权限操作这个上传ID
            UserFileAccess.objects.get(
                user=request.user,
                uploaded_file__upload_id=upload_id
            )
            uploaded_file = UploadedFile.objects.get(upload_id=upload_id)
        except (UserFileAccess.DoesNotExist, UploadedFile.DoesNotExist):
            return Response({
                'code': 403,
                'msg': '无效的上传ID或没有权限',
            }, status=status.HTTP_403_FORBIDDEN)

        # 保存分片
        chunk_dir = os.path.join(settings.MEDIA_ROOT, 'chunks', upload_id)
        chunk_path = os.path.join(chunk_dir, f'chunk_{chunk_number}')

        with open(chunk_path, 'wb') as f:
            for chunk_data in chunk.chunks():
                f.write(chunk_data)

        # 更新已上传分片数
        uploaded_file.uploaded_chunks += 1
        uploaded_file.save()

        return Response({
            'code': 200,
            'msg': '分片上传成功',
            'uploaded_chunks': uploaded_file.uploaded_chunks,

        })


class CompleteUploadView(CustomResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        upload_id = request.data.get('upload_id')
        file_md5 = request.data.get('file_md5')
        filename = request.data.get('filename')

        try:
            # 检查用户是否有权限操作这个上传ID
            user_access = UserFileAccess.objects.get(
                user=request.user,
                uploaded_file__upload_id=upload_id
            )
            uploaded_file = UploadedFile.objects.get(upload_id=upload_id)
        except (UserFileAccess.DoesNotExist, UploadedFile.DoesNotExist):
            return Response({
                'code': 403,
                'msg': '无效的上传ID或没有权限'}, status=status.HTTP_403_FORBIDDEN)

        # 检查分片是否全部上传
        if uploaded_file.uploaded_chunks != uploaded_file.total_chunks:
            return Response({
                'code': 400,
                'msg': '分片未全部上传'}, status=status.HTTP_400_BAD_REQUEST)

        # 如果文件已经完成(可能其他用户已经上传完成)
        if uploaded_file.completed:
            return Response({
                'code': 200,
                'msg': '文件上传已完成',
                'file_id': uploaded_file.id,
                'file_url': uploaded_file.file.url,
                'file_md5': uploaded_file.file_md5,
                'filename': uploaded_file.filename,
                'ext': uploaded_file.ext,
                'total_chunks': uploaded_file.total_chunks,
                'create_time': uploaded_file.create_time,

            })
        # 合并保存
        chunk_dir = os.path.join(settings.MEDIA_ROOT, 'chunks', upload_id)
        output_path = os.path.join(settings.MEDIA_ROOT, 'uploads',
                                   f'{file_md5}.{user_access.original_filename.split(".")[-1]}')

        # 确保上传目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'wb') as output_file:
            for i in range(1, uploaded_file.total_chunks + 1):
                chunk_path = os.path.join(chunk_dir, f'chunk_{i}')
                with open(chunk_path, 'rb') as chunk_file:
                    output_file.write(chunk_file.read())
                os.remove(chunk_path)
        # 更新文件记录
        uploaded_file.file.name = f'uploads/{file_md5}.{user_access.original_filename.split(".")[-1]}'
        uploaded_file.filename = user_access.original_filename
        uploaded_file.description = user_access.description
        uploaded_file.completed = True
        uploaded_file.save()

        # p = threading.Thread(target=update_video_attrs, args=(uploaded_file.id,))
        # p.start()
        update_video_attrs(uploaded_file.id)

        # 删除分片目录
        os.rmdir(chunk_dir)


        return Response({
            'code': 200,
            'msg': '文件上传完成',
            'file_id': uploaded_file.id,
            'file_url': uploaded_file.file.url,
            'file_md5': uploaded_file.file_md5,
            'ext': uploaded_file.ext,

        })


class MultiFileUploadView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info(f'request.user: {request.user}')
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        file_raw = request.FILES['file']
        filename = request.data.get('filename')
        file_md5 = request.data.get('file_md5')
        description = os.path.splitext(filename)[0]

        logger.info(f'filename: {filename} description: {description} file_md5: {file_md5}')



        try:
            if not file_md5:
                return Response({
                    'code':400,
                    'msg': '请提供文件MD5'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 1. 检查是否已存在相同MD5的完整文件
            existing_file = UploadedFile.objects.filter(
                file_md5=file_md5,
                completed=True
            ).first()

            logger.info(f'existing_file: {existing_file}')

            if existing_file:
                try:
                    # 安全创建用户关联
                    user_access, created = UserFileAccess.objects.get_or_create(
                        user=request.user,
                        uploaded_file=existing_file,
                        defaults={
                            'original_filename': filename,
                            'description': description,
                        }
                    )
                    logger.info(f'user_access: {user_access} created: {created}')

                    return Response({
                        'code': 200,
                        'msg': '文件已存在' + (
                            f'(新建关联) | {user_access.user}' if created else f'(已有关联) | {user_access.user}'),
                        'id': existing_file.id,
                        'file_md5': existing_file.file_md5,
                        'filename': existing_file.filename,
                        'ext': existing_file.ext,
                        'create_time': existing_file.create_time,
                        'user': f'{user_access.user}',
                        'is_existing': True,

                    })
                except Exception as e:
                    logger.error(f'Error: {e}')
                    return Response({
                        'code': 500,
                        'msg': f'创建文件关联失败: {str(e)}',
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 2. 创建新的上传记录
            logger.info('创建新的上传记录')
            upload_id = file_md5
            uploaded_file, created = UploadedFile.objects.get_or_create(
                upload_id=upload_id,
                defaults={
                    'file_md5': file_md5,
                    'filename': filename,
                    'description': description,
                }
            )

            logger.info(f'uploaded_file: {uploaded_file} created: {created}')

            # 3. 创建用户文件访问记录
            logger.info('创建用户文件访问记录')
            user_access, created = UserFileAccess.objects.get_or_create(
                user=request.user,
                original_filename=filename,
                uploaded_file=uploaded_file,
                defaults={
                    'original_filename': filename,
                    'description': description,
                }
            )

            logger.info(f'user_access: {user_access} created: {created}')

            output_path = os.path.join(settings.MEDIA_ROOT, 'uploads',
                                       f'{file_md5}.{user_access.original_filename.split(".")[-1]}')
            logger.info(f'output_path: {output_path}')

            # 确保上传目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, 'wb') as output_file:
                for chunk_data in file_raw.chunks():
                    output_file.write(chunk_data)

            # 更新文件记录
            uploaded_file.file.name = f'uploads/{file_md5}.{user_access.original_filename.split(".")[-1]}'
            uploaded_file.filename = user_access.original_filename
            uploaded_file.description = user_access.description
            uploaded_file.completed = True
            uploaded_file.save()

            # p = threading.Thread(target=update_video_attrs, args=(uploaded_file.id,))
            # p.start()
            update_video_attrs(uploaded_file.id)

            return Response({
                'code': 200,
                'msg': '文件上传完成',
                'file_id': uploaded_file.id,
                'filename': uploaded_file.filename,
                'file_md5': uploaded_file.file_md5,
                'create_time': uploaded_file.create_time,
            })

        except Exception as e:
            logger.error(f'Error uploading file: {str(e)}')
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FileDownloadView(CustomResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        try:
            logger.info(f'file_id: {file_id}')
            file_obj = UserFileAccess.objects.get(id=file_id)
            file_path = file_obj.uploaded_file.file.path
        except DownloadRecord.DoesNotExist:
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)

        # 确保文件存在
        if not os.path.exists(file_path):
            return Response({'error': 'File does not exist'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # 跟新下载计数
            uploaded_file = file_obj.uploaded_file
            uploaded_file.download_count += 1
            uploaded_file.save()

            # 记录下载日志
            DownloadRecord.objects.create(
                user=request.user if request.user.is_authenticated else None,
                uploaded_file=uploaded_file,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                original_filename=file_obj.original_filename,
            )

            safe_name = self.safe_filename(file_obj.original_filename)
            logger.info(f'file_obj: {file_obj} filename: {safe_name}')

            # 获取文件大小
            file_size = os.path.getsize(file_path)

            # 改进的流式响应生成器
            def file_iterator():
                try:
                    with open(file_path, 'rb') as f:
                        remaining = file_size
                        chunk_size = 64 * 1024  # 64KB chunks

                        while remaining > 0:
                            chunk = f.read(min(chunk_size, remaining))
                            if not chunk:
                                break
                            remaining -= len(chunk)
                            yield chunk
                except ConnectionResetError:
                    logger.warning("Client disconnected during download")
                except Exception as e:
                    logger.error(f"File streaming error: {str(e)}")

            # 创建响应
            response = StreamingHttpResponse(
                file_iterator(),
                content_type='application/octet-stream'
            )

            # 设置响应头（兼容所有浏览器）
            response['Content-Length'] = str(file_size)
            response['Content-Disposition'] = self.get_content_disposition(safe_name)
            # 允许前端访问 Content-Disposition 头
            response['Access-Control-Expose-Headers'] = 'Content-Disposition, Content-Length'

            response['Accept-Ranges'] = 'bytes'
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate'
            response['X-Accel-Buffering'] = 'no'  # 禁用Nginx缓冲
            # response['Pragma'] = 'no-cache'
            # response['Expires'] = '0'

            return response


        except Exception as e:
            logger.error(f'Error downloading file: {str(e)}')
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def safe_filename(self, filename):
        """移除文件名中的非法字符"""
        return re.sub(r'[\\/*?:"<>|]', "", filename)

    def get_content_disposition(self, filename):
        """
        生成兼容所有浏览器的Content-Disposition头
        """
        try:
            from urllib.parse import quote
            quoted = quote(filename.encode('utf-8'))
            return f"attachment; filename*=UTF-8''{quoted}"
        except:
            return f'attachment; filename="{filename}"'


class ChunkedFileDownloadView(CustomResponseMixin, APIView):
    CHUNK_SIZE = 2 * 1024 * 1024  # 2MB分块

    def get(self, request, file_id):
        try:
            # 获取文件对象并锁定记录（防止并发修改）
            with transaction.atomic():
                file_obj = UserFileAccess.objects.get(id=file_id)
                file_path = file_obj.uploaded_file.file.path

                if not os.path.exists(file_path):
                    return HttpResponse("File not found", status=404)

                file_size = os.path.getsize(file_path)
                file_name = self.safe_filename(file_obj.original_filename)

                # 创建下载记录（标记开始）

                download_record = DownloadRecord.objects.filter(
                    uploaded_file=file_obj.uploaded_file,
                    user=request.user
                ).first()
                if not download_record:
                    download_record = DownloadRecord.objects.create(
                        user=request.user if request.user.is_authenticated else None,
                        ip_address=self.get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT'),
                        uploaded_file=file_obj.uploaded_file,
                        original_filename=file_obj.original_filename,
                        status='started'
                    )

            # 处理Range请求头
            range_header = request.META.get('HTTP_RANGE', '').strip()
            range_match = re.match(r'bytes=(\d+)-(\d+)?', range_header) if range_header else None

            # 分块下载逻辑
            def file_iterator():
                download_completed = False
                try:
                    with open(file_path, 'rb') as f:
                        if range_match:  # 部分下载
                            first_byte = int(range_match.group(1))
                            last_byte = int(range_match.group(2)) if range_match.group(2) else file_size - 1
                            f.seek(first_byte)
                            remaining = last_byte - first_byte + 1
                        else:  # 完整下载
                            remaining = file_size

                        while remaining > 0:
                            chunk = f.read(min(self.CHUNK_SIZE, remaining))
                            if not chunk:
                                break
                            remaining -= len(chunk)
                            yield chunk

                    # 只有完整下载才标记完成
                    download_completed = not range_match
                except ConnectionResetError:
                    logger.warning("Client disconnected during download")
                except Exception as e:
                    logger.error(f"File streaming error: {str(e)}")
                finally:
                    # 确保无论如何都尝试更新状态

                    self.update_download_status(file_obj, download_record, download_completed)

            # 创建响应
            if range_match:
                first_byte = int(range_match.group(1))
                last_byte = int(range_match.group(2)) if range_match.group(2) else file_size - 1
                length = last_byte - first_byte + 1

                if first_byte >= file_size:
                    return HttpResponse(
                        status=416,
                        headers={
                            'Content-Range': f'bytes */{file_size}',
                            'Accept-Ranges': 'bytes'
                        }
                    )

                # 流式响应
                response = StreamingHttpResponse(
                    file_iterator(),
                    status=status.HTTP_206_PARTIAL_CONTENT,
                    content_type='application/octet-stream'
                )

                response['Content-Range'] = f'bytes {first_byte}-{last_byte}/{file_size}'
                response['Content-Length'] = str(length)
            else:
                # 完整文件下载
                response = StreamingHttpResponse(
                    file_iterator(),
                    content_type='application/octet-stream'
                )
                response['Content-Length'] = str(file_size)

            # 设置响应头
            response['Accept-Ranges'] = 'bytes'
            response['Content-Disposition'] = self.get_content_disposition(file_name)
            response['Access-Control-Expose-Headers'] = 'Content-Range, Content-Disposition'
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'

            return response

        except Exception as e:
            logger.error(f"Download failed: {str(e)}")
            return HttpResponse(f"Server Error: {str(e)}", status=500)

    def update_download_status(self, file_obj, download_record, completed):
        """更新下载状态和计数"""
        try:
            with transaction.atomic():
                if completed:
                    # 原子操作更新计数
                    file_obj.uploaded_file.download_count = models.F('download_count') + 1
                    file_obj.uploaded_file.save(update_fields=['download_count'])
                    download_record.status = 'completed'
                else:
                    download_record.status = 'interrupted'
                download_record.save()

        except Exception as e:
            logger.error(f"Failed to update download status: {str(e)}")
            raise

    def file_chunk_generator(self, file_path, start, end):
        """生成文件分块"""
        with open(file_path, 'rb') as f:
            f.seek(start)
            remaining = end - start + 1

            while remaining > 0:
                chunk_size = min(self.CHUNK_SIZE, remaining)
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk

    def get_content_disposition(self, filename):
        """生成兼容的Content-Disposition头"""
        try:
            quoted = quote(filename.encode('utf-8'))
            return f"attachment; filename*=UTF-8''{quoted}"
        except:
            return f'attachment; filename="{filename}"'

    def safe_filename(self, filename):
        """清理文件名"""
        return re.sub(r'[\\/*?:"<>|]', "", filename)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# views.py
class FileDownloadStatusView(CustomResponseMixin, APIView):

    def post(self, request, file_id):
        try:
            download_record_id = request.data.get('download_record_id')
            # 从路径中提取操作类型
            action = request.path.split('/')[-2]
            with transaction.atomic():
                file_obj = UserFileAccess.objects.select_for_update().get(id=file_id)
                logger.info(
                    f'user: {request.user} file_obj: {file_obj} action: {action} download_record_id: {download_record_id}')
                # 根据请求类型更新状态
                if action == 'download-start':
                    download_record = DownloadRecord.objects.create(
                        user=request.user if request.user.is_authenticated else None,
                        ip_address=self.get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT'),
                        uploaded_file=file_obj.uploaded_file,
                        original_filename=file_obj.original_filename
                    )
                    return Response({'success': True, 'id': download_record.id, 'status': f'{action.split("-")[-1]}'})
                elif action == 'download-complete':
                    file_obj.uploaded_file.download_count += 1
                    file_obj.uploaded_file.save()
                    DownloadRecord.objects.filter(
                        uploaded_file=file_obj.uploaded_file,
                        user=request.user,
                        id=download_record_id
                    ).update(status='completed')
                elif action == 'download-cancel':
                    DownloadRecord.objects.filter(
                        uploaded_file=file_obj.uploaded_file,
                        user=request.user,
                        id=download_record_id
                    ).update(status='cancelled')
                else:
                    return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'success': True, 'status': f'{action.split("-")[-1]}'})
        except UserFileAccess.DoesNotExist:
            logger.error(f'File {file_id} not found for user {request.user}')
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f'Error file {file_id} for user {request.user}: {str(e)}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip






class UserStatsByTimeView(EncryptionResponseMixin, APIView):
    """
    按时间范围统计用户素材数量、时长、大小
    权限：认证用户
    参数：
        start_time: ISO 格式时间字符串
        end_time: ISO 格式时间字符串
        granularity: 'hour' 或 'day' （可选，默认根据时间跨度自动判断）
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        start_str = request.query_params.get('start_time')
        end_str = request.query_params.get('end_time')
        granularity = request.query_params.get('granularity', 'auto')

        if not start_str or not end_str:
            return Response({'code': 400, 'msg': '缺少 start_time 或 end_time 参数'}, status=400)

        try:
            # start_time = parser.isoparse(start_str)
            # end_time = parser.isoparse(end_str)
            start_time = timezone.datetime.fromisoformat(start_str)
            end_time = timezone.datetime.fromisoformat(end_str)

        except (ValueError, TypeError):
            return Response({'code': 400, 'msg': '时间格式错误'}, status=400)

        # 自动判断粒度
        delta = end_time - start_time
        if granularity == 'auto':
            granularity = 'hour' if delta <= timedelta(days=1) else 'day'

        # 权限过滤
        base_filter = {
            'uploaded_file__completed': True,
            'uploaded_file__duration__isnull': False,
            'uploaded_file__file_size__gt': 0,
            'uploaded_file__create_time__gte': start_time,
            'uploaded_file__create_time__lt': end_time,
        }

        if user.is_superuser or user.is_staff:
            access_queryset = UserFileAccess.objects.select_related('uploaded_file').filter(**base_filter)
        else:
            access_queryset = UserFileAccess.objects.select_related('uploaded_file').filter(user=user, **base_filter)

        # ✅ 修复：去掉 ...，写完整 annotate
        if granularity == 'hour':
            stats = access_queryset.annotate(
                time_bucket=TruncHour('uploaded_file__create_time')
            ).values('time_bucket').annotate(
                file_count=Count('uploaded_file_id'),
                total_duration=Sum('uploaded_file__duration'),
                total_size=Sum('uploaded_file__file_size')
            ).order_by('time_bucket')
        else:  # day
            stats = access_queryset.annotate(
                time_bucket=TruncDay('uploaded_file__create_time')
            ).values('time_bucket').annotate(
                file_count=Count('uploaded_file_id'),
                total_duration=Sum('uploaded_file__duration'),
                total_size=Sum('uploaded_file__file_size')
            ).order_by('time_bucket')

        # 格式化结果
        result = []
        for item in stats:
            time_str = (
                item['time_bucket'].strftime('%Y-%m-%d %H:%M:%S')
                if granularity == 'hour'
                else item['time_bucket'].strftime('%Y-%m-%d %H:%M:%S')
            )
            result.append({
                'create_time': time_str,
                'file_count': item['file_count'] or 0,
                'total_duration': float(item['total_duration'] or 0),
                'total_size': item['total_size'] or 0,
            })

        return Response({
            'code': 200,
            'msg': 'success',
            'data': {
                'granularity': granularity,
                'total': len(result),
                'results': result
            }
        })

class DashboardSummaryView(APIView):
    """
    获取仪表盘汇总数据：
    - 今日新增素材数量
    - 今日新增素材总时长
    - 全部素材数量
    - 全部素材总时长
    权限：仅认证用户可访问
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # 获取当前用户可见的 UploadedFile ID 列表（考虑权限）
        if request.user.is_superuser or request.user.is_staff:
            # 管理员：所有 completed 的视频文件
            file_queryset = UploadedFile.objects.filter(
                completed=True,
                duration__isnull=False,
                file_size__gt=0
            )
        else:
            # 普通用户：只能看到自己有权限的文件
            accessible_file_ids = UserFileAccess.objects.filter(
                user=request.user
            ).values_list('uploaded_file_id', flat=True)
            file_queryset = UploadedFile.objects.filter(
                id__in=accessible_file_ids,
                completed=True,
                duration__isnull=False,
                file_size__gt=0
            )

        # 今日新增
        today_files = file_queryset.filter(create_time__gte=today_start)
        today_file_count = today_files.count()
        today_duration = today_files.aggregate(
            total=Sum('duration')
        )['total'] or 0

        # 全部
        total_file_count = file_queryset.count()
        total_duration = file_queryset.aggregate(
            total=Sum('duration')
        )['total'] or 0

        return Response({
            'code': 200,
            'msg': 'success',
            'data': {
                'today_file_count': today_file_count,
                'today_duration': float(today_duration),
                'total_file_count': total_file_count,
                'total_duration': float(total_duration),
            }
        })


class OnlineUsersView(APIView):
    """
    获取当前在线用户（last_login_time 在过去 15 分钟内）
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (request.user.is_superuser or request.user.is_staff):
            return Response({
                'code': 200,
                'msg': 'success',
                'data': []
            })
            # return Response({
            #     'code': 403,
            #     'msg': '仅管理员可查看在线用户'
            # }, status=403)

        now = timezone.now().astimezone()
        threshold = now - settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME')


        online_users = User.objects.filter(
            is_active=True,
            last_login_time__gte=threshold
        ).values('id', 'username', 'real_name', 'last_login_time')

        logger.info(f'online_users: {online_users}')

        data = [
            {
                'user_id': u['id'],
                'username': u['username'],
                'real_name': u['real_name'] or u['username'],
                'last_login_time': u['last_login_time'].isoformat() if u['last_login_time'] else None
            }
            for u in online_users
        ]

        return Response({
            'code': 200,
            'msg': 'success',
            'data': data
        })
