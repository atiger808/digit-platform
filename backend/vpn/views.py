from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Sum, Max, F
from django.db import transaction
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.exceptions import Throttled

from loguru import logger
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.core.cache import cache
from django.http import HttpResponse
import os
import json
import hashlib
import datetime

from .models import DyvpnAccount, DyvpnDeviceModel, DyvpnRegionModel, DyvpnMonitor
from .serializers import VpnAccountSerializer, ApiVPNRegionsSerializer, ApiVPNAccountSerializer, ApiCreateApiVPNAccountSerializer, \
    ApiUpdateVPNAccountSerializer, ApiVPNAccountDetailSerializer, VpnDeviceSerializer, VpnRegionSerializer, \
    VpnMonitorSerializer
from .filters import DyvpnAccountFilter, DyvpnDeviceFilter, DyvpnRegionFilter, DyvpnMonitorFilter
from .permissions import IsAdminUser, IsSuperAdmin, IsOwnerOrAdmin, IPWhitelistSignturePermission
from utils.vpn_fortigate import FgtManager
from utils.mixins import CustomResponseMixin, EncryptionResponseMixin
from utils.encrypt_aes import encrypt_data, decrypt_data


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 20000

    def get_paginated_response(self, data):
        return Response({
            'total': self.page.paginator.count,
            'page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'has_next': self.page.has_next(),
            'has_previous': self.page.has_previous(),
            'results': data,
        })


class VpnAccountViewSet(EncryptionResponseMixin, CustomResponseMixin, viewsets.ModelViewSet):
    queryset = DyvpnAccount.objects.filter(is_delete=False).select_related(
        'device', 'region', 'user'
    ).order_by('-create_time')
    pagination_class = CustomPagination
    serializer_class = VpnAccountSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filterset_class = DyvpnAccountFilter
    online_user_list = []

    def check_throttles(self, request):
        """检查用户创建频率"""
        if self.action == 'create' and not request.user.is_superuser:
            user = request.user
            recent_creates = DyvpnAccount.objects.filter(user=user, create_time__gt=timezone.now() - datetime.timedelta(
                hours=1)).count()
            logger.info(f'User {user} create account count: {recent_creates}')
            # 每小时最多创建5个账户
            if recent_creates >= 5:
                logger.error(f'User {user} 您创建的账户过于频繁，请稍后再试 recent_creates：{recent_creates} >= 5')
                raise Throttled(detail='您创建的账户过于频繁，请稍后再试')

        return super().check_throttles(request)

    def get_queryset(self):
        """
        获取基础查询集（包含权限过滤）
        """
        queryset = self.get_user_access_queryset(self.request.user)
        return queryset

    def get_user_access_queryset(self, user):
        """
        获取用户访问权限的查询集
        """
        if user.is_superuser:
            # 超级用户可以查看所有数据
            return self.queryset
        else:
            # 其他用户只能查看自己的数据
            return self.queryset.filter(user=user)

    @action(detail=False, methods=['post'])
    def query(self, request):
        """
        POST方式查询用户列表（带权限控制+分页）
        请求参数:
        {
            "username": "",       # 用户名模糊查询
            "real_name": "",      # 真实姓名模糊查询
            "mobile": "",         # 手机号模糊查询
            "is_active": true,    # 激活状态
            "department": 1,      # 部门ID
            "create_time_start": "2023-01-01",  # 创建时间范围
            "create_time_end": "2023-12-31",
            // 分页参数通过URL传递
        }
        """

        # 1. 获取基础查询集（包含权限过滤）
        queryset = self.filter_queryset(self.get_queryset())

        # 2. 应用过滤器
        filterset = DyvpnAccountFilter(data=request.data, queryset=queryset)
        if not filterset.is_valid():
            return Response({
                'code': 400,
                'msg': '参数错误',
                'errors': filterset.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        filtered_queryset = filterset.qs

        # 3. 应用分页
        page = self.paginate_queryset(filtered_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # 4. 无分页返回
        serialzer = self.get_serializer(queryset, many=True)
        return Response(serialzer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance == request.user:
                logger.error(f'User {request.user} 您不能删除自己的账户')
                return Response(
                    {'code': 400, 'msg': '您不能删除自己的账户'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            is_owner = instance.user == request.user
            is_superuser = request.user.is_superuser

            can_delete = is_owner or is_superuser

            # 判断删除账户是否为当前用户关联的账号，如果不是，则不能删除
            if not can_delete:
                logger.error(f"User {request.user} 您无权限删除此账户 {instance}")
                return Response(
                    {'code': 400, 'msg': '您无权限删除此账户'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            logger.info(f"Admin {request.user} 删除VPN账号: {instance}")
            fgtm = FgtManager(host=instance.device.route_url, username=instance.device.account,
                              password=instance.device.password)

            is_success = fgtm.delete_user(instance.vpn_account)
            if not is_success:
                logger.error(f"Admin {request.user} 删除VPN账号失败: {instance}")
                return Response(
                    {'code': 400, 'msg': '删除账户失败'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            instance.is_delete = True
            instance.save()
            region_instance = DyvpnRegionModel.objects.filter(region_code=instance.region.region_code).first()
            if region_instance:
                region_instance.online_num -= 1
                region_instance.save()
            # self.perform_destroy(instance)
            logger.info(f"Admin {request.user} 删除VPN账号成功: {instance}")
            return Response({'code': 200, 'msg': '删除账户成功'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"User {request.user} 删除账户失败: {e}")
            return Response(
                {'code': 400, 'msg': '删除账户失败'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])  # 或者 ['post'] 如果需要过滤条件
    def region_summary(self, request):
        """统计各区域用户总数和在线总数"""
        # 获取所有监控记录的查询集 (应用权限过滤)
        base_queryset = self.filter_queryset(self.get_queryset())

        # 1. 统计每个区域的总用户数 (distinct account)
        total_users_per_region = base_queryset.values('region__region_code', 'region__region').annotate(
            total_users=Count('vpn_account', distinct=True),
        ).order_by('region__region_code')

        # 2. 统计每个区域的在线用户数 (distinct account where logout_time is null)
        online_users_per_region = base_queryset.filter(
            online=True
        ).values('region__region_code').annotate(
            online_users=Count('vpn_account', distinct=True)
        ).order_by('region__region_code')

        # 将在线数据转换为字典方便查找
        online_dict = {item['region__region_code']: item['online_users'] for item in online_users_per_region}

        # 统计到期用户数
        expire_users_per_region = base_queryset.filter(
            is_delete=False,
            expire_time__lte=timezone.now()
        ).values('region__region_code').annotate(
            expire_users=Count('vpn_account', distinct=True)
        ).order_by('region__region_code')
        expire_dict = {item['region__region_code']: item['expire_users'] for item in expire_users_per_region}


        # 3. 合并数据
        summary_data = []
        for item in total_users_per_region:
            region_code = item['region__region_code']
            region_name = item['region__region'] or settings.REGION_CODE_TO_NAME.get(region_code, region_code)
            region_english = settings.REGION_CODE_TO_ENGLISH.get(region_code, region_code)
            total = item['total_users']
            online = online_dict.get(region_code, 0)
            expire = expire_dict.get(region_code, 0)

            summary_data.append({
                'name': region_name,  # 地图上显示的名称
                'region_english': region_english,  # 地图上显示的英文名称
                'region_code': region_code,  # 区域代码，用于地图匹配
                'value': [total, online, expire]  # ECharts 接受的值格式，可以是数组[总用户数，在线用户数, 到期用户数]
            })

        return Response({
            'code': 200,
            'msg': 'success',
            'data': summary_data
        })



class ApiVPNRegionView(generics.ListAPIView):
    queryset = DyvpnRegionModel.objects.all()
    permission_classes = (IPWhitelistSignturePermission,) # IPWhitelistSignturePermission
    serializer_class = ApiVPNRegionsSerializer





class ApiCreateVPNAccountView(generics.CreateAPIView):
    permission_classes = [IPWhitelistSignturePermission]
    serializer_class = ApiCreateApiVPNAccountSerializer

    def check_throttles(self, request):
        """检查用户创建频率"""
        recent_creates = DyvpnAccount.objects.filter(user__isnull=True,
                                                     create_time__gt=timezone.now() - datetime.timedelta(
                                                         hours=1)).count()
        logger.info(f'create account count: {recent_creates}')
        # 每小时最多创建50个账户
        if recent_creates >= 50:
            logger.error(f'您创建的账户过于频繁，请稍后再试 recent_creates: {recent_creates} > 50')
            raise Throttled(detail='您创建的账户过于频繁，请稍后再试')

        return super().check_throttles(request)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vpn_account = serializer.save()

        # 使用ApiVPNAccountSerializer返回响应数据
        responser_serializer = ApiVPNAccountSerializer(vpn_account)
        return Response({
            'code': 200,
            'msg': 'success',
            'data': responser_serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        logger.info(f"Admin {request.user} 删除VPN账号: {instance} 没有操作权限")
        # 没有操作权限
        return Response(
            {'code': 400, 'msg': '没有操作权限'},
            status=status.HTTP_400_BAD_REQUEST
        )

class ApiUpdateVPNAccountView(generics.UpdateAPIView):
    queryset = DyvpnAccount.objects.filter(is_delete=False)
    serializer_class = ApiUpdateVPNAccountSerializer
    permission_classes = [IPWhitelistSignturePermission]
    lookup_field = 'vpn_account'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_account = serializer.save()

        response_serializer = ApiVPNAccountSerializer(updated_account)
        return Response({
            'code': 200,
            'msg': 'success',
            'data': response_serializer.data
        })
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        logger.info(f"Admin {request.user} 删除VPN账号: {instance} 没有操作权限")
        # 没有操作权限
        return Response(
            {'code': 400, 'msg': '没有操作权限'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ApiVPNAccountDetailView(generics.RetrieveAPIView):
    queryset = DyvpnAccount.objects.filter(is_delete=False)
    serializer_class = ApiVPNAccountDetailSerializer
    permission_classes = [IPWhitelistSignturePermission]
    lookup_field = 'vpn_account'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # 更新在线状态
        instance.get_online_status()

        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'msg': 'success',
            'data': serializer.data
        })
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        logger.info(f"Admin {request.user} 删除VPN账号: {instance} 没有操作权限")
        # 没有操作权限
        return Response(
            {'code': 400, 'msg': '没有操作权限'},
            status=status.HTTP_400_BAD_REQUEST
        )


class VpnMonitorViewSet(EncryptionResponseMixin, CustomResponseMixin, viewsets.ModelViewSet):
    queryset = DyvpnMonitor.objects.order_by('-login_time')
    pagination_class = CustomPagination
    serializer_class = VpnMonitorSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filterset_class = DyvpnMonitorFilter
    online_user_list = []
    online_info_list = []

    def get_queryset(self):
        """
        获取基础查询集（包含权限过滤）
        """
        # cache_key = self.get_cache_key(self.request, view_name='vpn_monitor_queryset_0')
        # cached = cache.get(cache_key)
        # if cached:
        #     return cached
        queryset = self.get_user_access_queryset(self.request.user)
        # cache.set(cache_key, queryset, timeout=60)  # 缓存1分钟
        return queryset.select_related(
            'account',
            'account__user',
            'account__device',
            'region'
        ).only(
            'id',
            'duration_secs',
            'expiry_secs',
            'traffic_vol_bytes',
            'virtual_ip',
            'logout_time',
            'login_time',
            'account__vpn_account',
            'account__nickname',
            'account__device__device_name',
            'account__user__username',
            'region__region'
        )

    def get_user_access_queryset(self, user):
        """
        获取用户访问权限的查询集
        """
        if user.is_superuser:
            # 超级用户可以查看所有数据
            return self.queryset
        else:
            account = DyvpnAccount.objects.filter(user=user).first()
            # 其他用户只能查看自己的数据
            return self.queryset.filter(account=account)

    def get_cache_key(self, request, view_name='vpn_monitor_queryset_'):
        """生成基于请求参数的唯一缓存键"""
        # 使用请求参数和用户信息创建唯一键
        params = {
            'user_id': request.user.id,
            # 'query_params': request.query_params.dict(),
            'data': request.data if request.method == 'POST' else None
        }
        # 创建可哈希的字符串表示
        key_str = json.dumps(params, sort_keys=True, default=str)
        key_md5 = f'{view_name}:{hashlib.md5(key_str.encode()).hexdigest()}'
        logger.info(f'cache key: {key_md5} key_str: {key_str}')
        return key_md5

    @action(detail=False, methods=['post'])
    def query(self, request):
        """
        POST方式查询用户列表（带权限控制+分页）
        请求参数:
        {
            "username": "",       # 用户名模糊查询
            "real_name": "",      # 真实姓名模糊查询
            "mobile": "",         # 手机号模糊查询
            "is_active": true,    # 激活状态
            "department": 1,      # 部门ID
            "create_time_start": "2023-01-01",  # 创建时间范围
            "create_time_end": "2023-12-31",
            // 分页参数通过URL传递
        }
        """
        # 1. 获取基础查询集（包含权限过滤）
        queryset = self.filter_queryset(self.get_queryset())

        # 2. 应用过滤器
        filterset = DyvpnMonitorFilter(data=request.data, queryset=queryset)
        if not filterset.is_valid():
            return Response({
                'code': 400,
                'msg': '参数错误',
                'errors': filterset.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # 过滤在线状态的查询集
        online = request.data.get('online')
        if online == 1:
            filtered_queryset = filterset.qs.filter(Q(account__online=True)).filter(Q(logout_time__isnull=True))
        else:
            filtered_queryset = filterset.qs

        # 3. 应用分页
        page = self.paginate_queryset(filtered_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(filtered_queryset, many=True)
            response = Response(serializer.data)

        return response

    @action(detail=False, methods=['get'])
    def region_summary(self, request):
        """
        获取按区域统计的用户数、流量、时长和在线用户数
        """
        # 获取经过权限过滤的基础查询集
        base_queryset = self.filter_queryset(self.get_queryset())

        # 1. 统计每个区域的基础数据
        # 使用 annotate 聚合计算每个区域的总用户数、总流量、总时长
        region_stats = base_queryset.values(
            'region__region',  # 中文区域名 (例如 "日本")
            'region__region_code',  # 区域代码 (例如 "JP")
            'region__id'  # 区域ID，用于关联
        ).annotate(
            total_users=Count('account', distinct=True),  # 总用户数 (去重)
            total_traffic_bytes=Sum('traffic_vol_bytes'),  # 总流量 (字节)
            total_duration_secs=Sum('duration_secs'),  # 总时长 (秒)
            # 注意：在线用户数需要特殊处理，见下一步
        ).order_by('region__region_code')

        # 2. 统计每个区域的在线用户数
        # 在线定义为：logout_time 为 NULL 或 logout_time 在未来 (容错)
        # 或者更简单地，只查找 logout_time__isnull=True 的记录
        online_users_per_region = base_queryset.filter(
            logout_time__isnull=True
        ).values('region__id').annotate(
            online_users=Count('account', distinct=True)
        ).order_by('region__id')

        # 将在线用户数统计结果转换为字典，方便查找
        # 键是 region__id, 值是 online_users 数量
        online_users_dict = {item['region__id']: item['online_users'] for item in online_users_per_region}

        # 统计到期用户数
        expire_users_per_region = base_queryset.filter(
            account__expire_time__lte=timezone.now()
        ).values('region__id').annotate(
            expire_users=Count('account', distinct=True)
        ).order_by('region__id')
        expire_users_dict = {item['region__id']: item['expire_users'] for item in expire_users_per_region}

        # 3. 合并数据并准备响应
        summary_data = []
        for stats in region_stats:
            region_id = stats['region__id']
            region_name = stats['region__region']
            region_code = stats['region__region_code']

            region_english = settings.REGION_CODE_TO_ENGLISH.get(region_code, region_code)

            # 从聚合结果中获取基础数据
            total_users = stats['total_users'] or 0
            total_traffic_bytes = stats['total_traffic_bytes'] or 0
            total_duration_secs = stats['total_duration_secs'] or 0

            # 从字典中查找对应的在线用户数
            online_users = online_users_dict.get(region_id, 0)
            expire_users = expire_users_dict.get(region_id, 0)

            summary_data.append({
                'name': region_name,  # 区域中文名
                'region_english': region_english,  # 这里暂时用中文名，如果 DyvpnRegionModel 有英文名字段，请替换
                'region_code': region_code,  # 区域代码
                'total_users': total_users,
                'total_traffic_bytes': total_traffic_bytes,
                'total_duration_secs': total_duration_secs,
                'online_users': online_users,
                'expire_users': expire_users
            })

        return Response({
            'code': 200,
            'msg': 'success',
            'data': summary_data
        })


class VpnDeviceViewSet(EncryptionResponseMixin, CustomResponseMixin, viewsets.ModelViewSet):
    queryset = DyvpnDeviceModel.objects.order_by('-create_time')
    pagination_class = CustomPagination
    serializer_class = VpnDeviceSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_class = DyvpnDeviceFilter

    @action(detail=False, methods=['post'])
    def query(self, request):
        """
        POST方式查询用户列表（带权限控制+分页）
        请求参数:
        {
            "create_time_start": "2023-01-01",  # 创建时间范围
            "create_time_end": "2023-12-31",
            // 分页参数通过URL传递
        }
        """
        # 1. 获取基础查询集（包含权限过滤）
        queryset = self.get_queryset()

        # 2. 应用过滤器
        filterset = DyvpnDeviceFilter(data=request.data, queryset=queryset)
        if not filterset.is_valid():
            return Response({
                'code': 400,
                'msg': '参数错误',
                'errors': filterset.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        filtered_queryset = filterset.qs

        # 3. 应用分页
        page = self.paginate_queryset(filtered_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # 4. 无分页返回
        serialzer = self.get_serializer(queryset, many=True)
        return Response(serialzer.data)


class VpnRegionViewSet(EncryptionResponseMixin, CustomResponseMixin, viewsets.ModelViewSet):
    queryset = DyvpnRegionModel.objects.select_related('device').order_by('-create_time')
    pagination_class = CustomPagination
    serializer_class = VpnRegionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_class = DyvpnRegionFilter

    def get_queryset(self):
        """
        可以在这里添加额外的查询集逻辑，如果需要的话。
        例如，如果未来需要基于用户权限进行过滤（尽管当前是 IsAdminUser）。
        当前实现可以直接返回基础查询集，因为 select_related 已在 queryset 定义中。
        """
        # 确保返回的查询集是优化过的
        # self.queryset 已经包含了 select_related('device')
        return super().get_queryset()  # 这会返回 self.queryset

    @action(detail=False, methods=['post'])
    def query(self, request):
        """
        POST方式查询用户列表（带权限控制+分页）
        请求参数:
        {
            "create_time_start": "2023-01-01",  # 创建时间范围
            "create_time_end": "2023-12-31",
            // 分页参数通过URL传递
        }
        """

        # 1. 获取基础查询集（包含权限过滤）
        queryset = self.get_queryset()

        # 2. 应用过滤器
        filterset = DyvpnRegionFilter(data=request.data, queryset=queryset)
        if not filterset.is_valid():
            return Response({
                'code': 400,
                'msg': '参数错误',
                'errors': filterset.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        filtered_queryset = filterset.qs

        # 3. 应用分页
        page = self.paginate_queryset(filtered_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # 4. 无分页返回
        serialzer = self.get_serializer(queryset, many=True)
        return Response(serialzer.data)
