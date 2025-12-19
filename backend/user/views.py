from rest_framework import viewsets, status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from .filters import UserFilter, DepartmentFilter, RoleFilter, MenuFilter, LoginlogFilter, OperationlogFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate
from django.db.models import Prefetch
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser
from django.core.files.storage import default_storage
from django.core.cache import cache
from django.core.mail import send_mail
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.http import HttpResponse

from rest_framework.decorators import throttle_classes
from rest_framework.throttling import AnonRateThrottle

from utils.mixins import CustomResponseMixin
from utils.sms import send_sms
from utils.captcha import CaptchaService
from utils.request_util import get_browser, get_request_ip, get_os, get_ip_analysis, get_request_path, save_login_log
from utils.json_response import SuccessResponse, DetailResponse, ErrorResponse
from utils.encrypt_aes import encrypt_data, decrypt_data

import os
import random
from loguru import logger
from django.conf import settings
from .models import User, Department, Role, Menu, Product, Profile, LoginLog, OperationLog
from .serializers import (
    EmailCodeSerializer,
    MyTokenObtainPairSerializer,
    SendCaptchaSerializer,
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    UserListSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserRoleUpdateSerializer,
    UserDepartmentUpdateSerializer,
    DepartmentSerializer,
    DepartmentCreateSerializer,
    RoleSerializer,
    RoleCreateUpdateSerializer,
    RoleWithMenuTreeSerializer,
    MenuSerializer,
    MenuAssignmentSerializer,
    ProductSerializer,
    DynamicMenuSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    AvatarSerializer,
    LoginLogSerializer,
    OperationLogSerializer
)
from .permissions import (
    IsSuperAdmin,
    IsAdminUser,
    IsManagerUser,
    HasMenuPermission,
    UserQueryPermission,
    UserCreatePermission,
    IsOwnerOrAdmin,
    UserPermission,
    UserDeletePermission,
    MenusPermission,

)


class CustomPagination(PageNumberPagination):
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


class CaptchaView(APIView):
    permission_classes = [AllowAny]
    """生成图片验证码"""

    def get(self, request, *args, **kwargs):
        # new_key = CaptchaStore.generate_key()
        # captcha = CaptchaStore.objects.get(hashkey=new_key)
        # # 获取实际验证码内容（转换为小写）
        # actual_code = captcha.response.lower()
        #
        # logger.info(f'Generated captcha with key: {new_key}')
        # logger.info(f'actual_code: {actual_code}')
        #
        # # 存储图片验证码到redis
        # cache.set(f'captcha:{new_key}', actual_code) #5分种过期

        # return Response({
        #     'key': new_key,
        #     'image_url': captcha_image_url(new_key)
        # }, status=status.HTTP_200_OK)

        key, image_data = CaptchaService.generate_image_captcha()
        response = HttpResponse(image_data, content_type='image/png')

        # 添加 CORS 相关头
        response['Access-Control-Expose-Headers'] = 'Captcha-Key'
        response['Captcha-Key'] = key  # 保持原命名
        response['Cache-Control'] = 'no-store, no-cache'

        return response


class VerifyCaptchaView(APIView):
    permission_classes = [AllowAny]
    """验证图片验证码"""

    def post(self, request, *args, **kwargs):
        # key = request.data.get('key')
        # code = request.data.get('code').lower()
        #
        # cache_key = f'captcha:{key}'
        # actual_code = cache.get(cache_key)
        #
        # logger.info(f'actual_code: {actual_code}')
        #
        # if not actual_code:
        #     return Response({'detail': '验证码已过期'}, status=status.HTTP_400_BAD_REQUEST)
        #
        # if code != actual_code:
        #     return Response({'detail': '验证码错误'}, status=status.HTTP_400_BAD_REQUEST)
        #
        # cache.delete(cache_key)
        # return Response({'message': '验证码验证成功'}, status=status.HTTP_200_OK)

        key = request.data.get('key')
        code = request.data.get('code').lower()
        if CaptchaService.verify_image_captcha(key, code):
            return Response({'message': '验证码验证成功'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': '验证码错误'}, status=status.HTTP_400_BAD_REQUEST)


class EmailCodeView(APIView):
    permission_classes = [AllowAny]
    serializer_class = EmailCodeSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({'error': '邮箱不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = ''.join(random.choices('0123456789', k=6))

            # 存储到缓存（5分钟过期）
            cache_key = f'email_code:{email}'
            cache.set(cache_key, code, settings.CAPTCHA_TIMEOUT)

            try:
                logger.info(f'发送邮件到：{email} from_email:{settings.EMAIL_HOST_USER}')
                # 发送邮箱
                send_mail(
                    subject=settings.EMAIL_SUBJECT_PREFIX,
                    message=f'您的验证码是：{code}，5分钟内有效',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                )
            except Exception as e:
                logger.error(f'发送邮件失败：{e}')
                return Response({'error': '发送邮件失败,请检查邮件地址是否存在'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'detail': '验证码发送成功'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({'detail': '邮箱或验证码不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f'email_code:{email}'
        cache_code = cache.get(cache_key)

        if not cache_code or cache_code != code:
            return Response({'detail': '验证码错误或已过期'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证成功后删除缓存
        cache.delete(cache_key)
        return Response({'detail': '验证成功'}, status=status.HTTP_200_OK)


class SMSCodeView(APIView):
    permission_classes = [AllowAny]

    @throttle_classes([AnonRateThrottle])
    def post(self, request):
        """发送短信验证码"""
        phone = request.data.get('mobile')
        if not phone:
            return Response({'error': '手机号不能为空'}, status=400)

        # 生成6位随机验证码
        code = ''.join(random.choices('0123456789', k=6))

        # 存储到Redis（5分钟有效期）
        cache.set(f'sms_code:{phone}', code, settings.CAPTCHA_TIMEOUT)

        # 发送短信
        try:
            send_sms(phone, code)
            Response({'detail': '验证码发送成功'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.info(f'Failed to send SMS: {e}')
            return Response({'error': '发送短信失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifySMSCodeView(APIView):
    def post(self, request):
        """验证短信验证码"""
        phone = request.data.get('phone')
        code = request.data.get('code')

        stored_code = cache.get(f'sms:{phone}')
        if not stored_code:
            return Response({'error': '验证码已过期'}, status=400)

        if code != stored_code:
            return Response({'error': '验证码错误'}, status=400)

        cache.delete(f'sms:{phone}')
        return Response({'message': '验证成功'}, status=200)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class SendCaptchaView(APIView):
    permission_classes = [AllowAny]
    serializer_class = SendCaptchaSerializer
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data['identifier']
        code_type = serializer.validated_data['code_type']

        # 生成验证码
        code = CaptchaService.generate_code(identifier, code_type)

        # 发送逻辑（示例为邮件）
        if '@' in identifier:
            send_mail(
                subject='注册验证码',
                message=f'您的验证码是：{code}，5分钟内有效',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[identifier],
                fail_silently=False,
            )
        else:
            # 调用短信接口
            send_sms(identifier, code)

        return Response({
            'message': '验证码已发送'
        })


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        return Response({
            'message': '注册成功',
            'data': UserSerializer(user).data
        })

    # def create(self, request, *args, **kwargs):
    #
    #     key = request.data.get('key')
    #     code = request.data.get('code').lower()
    #
    #     cache_key = f'captcha:{key}'
    #     actual_code = cache.get(cache_key)
    #
    #     if not actual_code:
    #         return Response({'detail': '验证码已过期'}, status=status.HTTP_400_BAD_REQUEST)
    #     if code != actual_code:
    #         return Response({'detail': '验证码错误'}, status=status.HTTP_400_BAD_REQUEST)
    #     cache.delete(cache_key)
    #
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     user = serializer.save()
    #
    #     # 生成token
    #     token_serializer = MyTokenObtainPairSerializer(data={
    #         'username': user.username,
    #         'password': request.data['password']
    #     })
    #     token_serializer.is_valid(raise_exception=True)
    #     tokens = token_serializer.validated_data
    #
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(tokens, status=status.HTTP_201_CREATED, headers=headers)


class LoginAttemptsView(APIView):
    def get(self, request):
        identifier = request.query_params.get('identifier')

        if not identifier:
            return Response(
                {"error": "缺少 identifier 参数"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(identifier) > 255:
            return Response(
                {"error": "标识符过长"},
                status=400
            )

        # 构造缓存键
        cache_key = f'login_attempts:{identifier}'
        attempts = cache.get(cache_key, 0)

        # 计算剩余尝试次数
        remaining_attempts = settings.MAX_LOGIN_ATTEMPTS - attempts

        return Response({
            "identifier": identifier,
            "attempts": attempts,
            "remaining_attempts": max(remaining_attempts, 0),
            "require_captcha": attempts >= settings.CAPTCHA_THRESHOLD
        })


class LoginView(TokenObtainPairView):
    """登录视图"""

    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        # key = request.data.get('key')
        # code = request.data.get('code').lower()
        #
        # cache_key = f'captcha:{key}'
        # actual_code = cache.get(cache_key)
        #
        # if not actual_code:
        #     return Response({'detail': '验证码已过期'}, status=status.HTTP_400_BAD_REQUEST)
        # if code != actual_code:
        #     return Response({'detail': '验证码错误'}, status=status.HTTP_400_BAD_REQUEST)
        # cache.delete(cache_key)

        identifier = request.data.get('identifier')
        password = request.data.get('password')
        decryprPassword = decrypt_data(password)
        password = decryprPassword
        request.data['password'] = password

        # 获取user-agent和登录ip
        browser = get_browser(request)
        user_ip = get_request_ip(request)
        os_version = get_os(request)

        # 关键：传递 request 对象和命名参数
        user = authenticate(
            request=request,
            identifier=identifier,
            password=password
        )

        logger.info(f'Login attempt with identifier: {identifier} Authentication result: {user} user_ip: {user_ip} browser: {browser} os_version: {os_version}')

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        request.user = user
        # 记录登录日志
        save_login_log(request=request)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    """
    用户管理接口
    - 列表查询：GET /api/users/
    - 创建用户：POST /api/users/
    - 用户详情：GET /api/users/{id}/
    - 更新用户：PUT /api/users/{id}/
    - 部分更新：PATCH /api/users/{id}/
    - 删除用户：DELETE /api/users/{id}/
    - 修改密码：POST /api/users/{id}/change_password/
    - 禁用/启用：POST /api/users/{id}/toggle_active/
    """
    queryset = User.objects.order_by('-create_time')
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser, UserQueryPermission, UserPermission]
    # filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, UserDeletePermission]
        return super().get_permissions()

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance == request.user:
                return Response(
                    {'code': 400, 'msg': '您不能删除自己的账户'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            self.perform_destroy(instance)
            return Response({'code': 200, 'msg': '删除账户成功'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return Response(
                {'code': 400, 'detail': f'删除账户失败'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer

        elif self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer

        elif self.action == 'list' or self.action == 'query':
            return UserListSerializer

        return UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # 超级管理员获取全部数据
        if user.is_superuser:
            return queryset.select_related('department').prefetch_related('roles')

        # 部门管理员获取部门及子部门下的用户列表
        if user.roles.filter(code='dept_admin').exists():
            if user.department:
                dept_ids = self._get_department_tree_ids(user.department)
                return queryset.filter(department__in=dept_ids).select_related('department').prefetch_related('roles')
            return queryset.none()

        # 普通用户获取自己
        return queryset.filter(id=user.id).select_related('department').prefetch_related('roles')

    def _get_department_tree_ids(self, department):
        ids = [department.id]
        children = Department.objects.filter(parent=department)
        for child in children:
            ids.extend(self._get_department_tree_ids(child))
        return ids

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
        queryset = self.get_queryset()

        # 2. 应用过滤器
        filterset = UserFilter(data=request.data, queryset=queryset)
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
        return Response({
            'code': 200,
            'msg': 'success',
            'data': serialzer.data
        })

    @action(detail=False, methods=['get'])
    def current_user(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def change_status(self, request, pk=None):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        return Response({'code': 200, 'msg': 'success', 'is_active': user.is_active})

    # 在视图中
    def perform_create(self, serializer):
        # 只有超级管理员可以创建管理员用户
        if not self.request.user.is_superuser:
            serializer.validated_data.pop('is_staff', None)
            serializer.validated_data.pop('is_superuser', None)
        serializer.save()

    @action(detail=True, methods=['patch'])
    def update_roles(self, request, pk=None):
        """更新用户角色"""
        user = self.get_object()
        serializer = UserRoleUpdateSerializer(
            data=request.data,
            context={'user': user}
        )
        serializer.is_valid(raise_exception=True)
        user.roles.set(serializer.validated_data['role_ids'])
        return Response({'code': 200, 'msg': '角色更新成功'})

    @action(detail=True, methods=['patch'])
    def update_department(self, request, pk=None):
        """更新用户部门"""
        user = self.get_object()
        serializer = UserDepartmentUpdateSerializer(
            data=request.data,
            context={'user': user}
        )
        serializer.is_valid(raise_exception=True)
        user.department_id = serializer.validated_data['department_id']
        user.save()
        return Response({'code': 200, 'msg': '部门更新成功'})


class DepartmentViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    """
    部门管理接口
    - 列表查询：GET /api/departments/
    - 创建部门：POST /api/departments/
    - 部门详情：GET /api/departments/{id}/
    - 更新部门：PUT /api/departments/{id}/
    - 部分更新：PATCH /api/departments/{id}/
    - 删除部门：DELETE /api/departments/{id}/
    - 部门树：GET /api/departments/tree/
    """
    queryset = Department.objects.order_by('-create_time')
    serializer_class = DepartmentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DepartmentFilter
    search_fields = ['name', 'code']
    ordering_fields = ['sort', 'create_time']
    permission_classes = [IsAuthenticated, IsAdminUser]

    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return DepartmentCreateSerializer
        elif self.action == 'list' or self.action == 'query':
            return DepartmentSerializer
        return DepartmentSerializer

    @action(detail=False, methods=['post'])
    def query(self, request):
        """
        POST方式查询部门（支持分页和复杂查询）
        请求示例：
        {
            "name": "技术",
            "status": true,
            "parent": 1,
            "create_time_start": "2023-01-01"
        }
        """
        queryset = self.filter_queryset(self.get_queryset())
        # 2. 应用过滤器
        filterset = DepartmentFilter(data=request.data, queryset=queryset)
        if not filterset.is_valid():
            return Response({
                'code': 400,
                'msg': '参数错误',
                'errors': filterset.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        filtered_queryset = filterset.qs

        page = self.paginate_queryset(filtered_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'msg': 'success',
            'data': serializer.data
        })

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """获取部门树形结构"""
        departments = Department.objects.filter(parent__isnull=True)
        tree_data = self._build_tree(departments)
        return Response(tree_data)

    def _build_tree(self, departments, parent=None):
        """递归构建部门树形结构"""
        tree = []
        for dept in departments:
            if (dept.parent == parent) or (dept.parent is None and parent is None):
                node = {
                    'id': dept.id,
                    'name': dept.name,
                    'code': dept.code,
                    'children': self._build_tree(departments, dept)
                }
                tree.append(node)
        return tree

    def destroy(self, request, *args, **kwargs):
        """删除部门前检查是否有子部门"""
        instance = self.get_object()
        if instance.department_set.exists():
            return Response(
                {'code': 400, 'msg': '删除失败，该部门下存在子部门'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class RoleViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    """
    角色管理接口
    - 列表查询：GET /api/roles/
    - 创建角色：POST /api/roles/
    - 角色详情：GET /api/roles/{id}/
    - 更新角色：PUT /api/roles/{id}/
    - 部分更新：PATCH /api/roles/{id}/
    - 删除角色：DELETE //apiroles/{id}/
    - 分配菜单：POST /api/roles/{id}/assign_menus/
    """
    queryset = Role.objects.order_by('-create_time').prefetch_related(
        Prefetch('menus', queryset=Menu.objects.filter(status=True))
    )
    serializer_class = RoleWithMenuTreeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = RoleFilter
    search_fields = ['name', 'code']
    pagination_class = CustomPagination

    # def get_serializer_class(self):
    #     if self.action in ['create', 'update', 'partial_update']:
    #         return RoleCreateUpdateSerializer
    #     if self.action in ['list', 'retrieve', 'query']:
    #         return RoleWithMenuTreeSerializer
    #     return RoleSerializer  # 使用展示用的序列化器

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'query']:
            return RoleWithMenuTreeSerializer
        return RoleCreateUpdateSerializer

    def perform_create(self, serializer):
        """创建后的额外操作"""
        role = serializer.save()
        logger.info(f"角色创建成功：{role.name} (ID: {role.id})")

    def perform_update(self, serializer):
        """更新后的额外操作"""
        role = serializer.save()
        logger.info(f"角色更新成功：{role.name} (ID: {role.id})")

    @action(detail=False, methods=['post'])
    def query(self, request):
        """
        POST方式查询角色（支持分页和复杂查询）
        请求示例：
        {
            "name": "管理",
            "status": true,
            "page": 1,
            "page_size": 10
        }
        """
        queryset = self.filter_queryset(self.get_queryset())

        # 2. 应用过滤器
        filterset = RoleFilter(data=request.data, queryset=queryset)
        if not filterset.is_valid():
            return Response({
                'code': 400,
                'msg': '参数错误',
                'errors': filterset.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        filtered_queryset = filterset.qs

        page = self.paginate_queryset(filtered_queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'msg': 'success',
            'data': serializer.data
        })

    @action(detail=True, methods=['get'])
    def menu_tree(self, request, pk=None):
        """
        获取单个角色的完整菜单树
        GET /api/roles/{id}/menu_tree/
        """
        role = self.get_object()
        serializer = RoleWithMenuTreeSerializer(role)
        return Response(serializer.data['menus'])

    @action(detail=True, methods=['post'])
    def assign_menus(self, request, pk=None):
        """为角色分配权限"""
        role = self.get_object()
        serializer = MenuAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role.menus.set(serializer.validated_data['menu_ids'])
        return Response({'code': 200, 'msg': '菜单分配成功'})

    def destroy(self, request, *args, **kwargs):
        """删除角色前检查是否有用户关联"""
        instance = self.get_object()
        if instance.user_set.exists():
            return Response(
                {'code': 400, 'msg': '删除失败，该角色下存在用户关联'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.data['old_password']):
            return Response({'code': 400, "msg": "当前密码不正确"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.data['new_password'])
        user.save()

        return Response({'code': 200, "msg": "密码修改成功"}, status=status.HTTP_200_OK)


class AvatarUploadView(generics.GenericAPIView):
    serializer_class = AvatarSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]  # 允许多媒体文件上传

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        avatar = serializer.validated_data['avatar']
        user = request.user

        logger.info(user)
        logger.info(f"用户 {user.username} 上传了头像")

        # 确保用户有 Profile 记录
        profile, created = Profile.objects.get_or_create(user=user)

        try:
            # 删除旧头像
            if profile.avatar:
                self._delete_old_avatar(profile.avatar.path)

            # 保存新头像
            filename = f'avatars/user_{user.id}/{avatar.name}'
            saved_path = default_storage.save(filename, avatar)

            # 更新Profile
            profile.avatar = saved_path
            profile.save()

            return Response({
                'code': 200,
                'msg': '更新成功',
                'avatar_url': profile.avatar.url
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # 清理可能部分上传的文件
            if 'saved_path' in locals():
                self._delete_old_avatar(saved_path)
            return Response({
                'code': 500,
                'msg': '头像上传失败',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _delete_old_avatar(self, old_avatar_path):
        """删除旧头像"""
        try:
            if default_storage.exists(old_avatar_path):
                default_storage.delete(old_avatar_path)
        except Exception as e:
            logger.error(f"删除旧头像失败：{e}")


class MenuViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    """
    菜单管理接口
    - 动态菜单：GET /api/menus/dynamic/ (所有认证用户)
    - 其他操作仅限管理员：
      - 列表：GET /api/menus/
      - 创建：POST /api/menus/
      - 详情：GET /api/menus/{id}/
      - 更新：PUT /api/menus/{id}/
      - 删除：DELETE /api/menus/{id}/
    """
    queryset = Menu.objects.order_by('sort')
    serializer_class = MenuSerializer
    permission_classes = [IsAuthenticated, MenusPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MenuFilter
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'dynamic':
            return DynamicMenuSerializer
        return MenuSerializer

    @action(detail=False, methods=['post'])
    def query(self, request):
        """
        POST方式查询菜单（管理员专用）
        请求示例：
        {
            "name": "用户",
            "type": 1,
            "parent": 2
        }
        """
        if not request.user.is_staff:
            return Response(
                {'code': 403, 'msg': '权限不足'},
                status=status.HTTP_403_FORBIDDEN
            )

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def dynamic(self, request):
        """
        获取当前用户的动态菜单
        普通用户只能看到呗授权的菜单
        """
        user = request.user

        # 如果是超级管理员，则返回所有菜单
        if user.is_superuser:
            menus = Menu.objects.filter(
                parent__isnull=True,
                status=True,
                type__in=[0, 1]  # 0:目录, 1:菜单
            ).order_by('sort')
        else:
            menus = Menu.objects.filter(
                parent__isnull=True,
                status=True,
                type__in=[0, 1],
                roles__in=user.roles.all()  # 使用related_name
            ).distinct().order_by('sort')

        serializer = self.get_serializer(menus, many=True)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """菜单列表 （仅管理员）"""
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """创建菜单（管理员用）"""
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """获取菜单详情（管理员用）"""
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """更新菜单（管理员用）"""
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """删除菜单（管理员用）"""
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """获取菜单树（管理员用）"""
        menus = Menu.objects.filter(type__in=[0, 1], status=True).order_by('sort')
        tree_data = self.build_tree(menus)
        return Response(tree_data)

    def build_tree(self, menus, parent=None):
        tree = []
        for menu in menus:
            if (menu.parent == parent) or (menu.parent is None and parent is None):
                node = {
                    'id': menu.id,
                    'name': menu.name,
                    'code': menu.code,
                    'type': menu.type,
                    'path': menu.path,
                    'component': menu.component,
                    'permission': menu.permission,
                    'icon': menu.icon,
                    'sort': menu.sort,
                    'children': self.build_tree(menus, menu)
                }
                tree.append(node)
        return tree


class ProductViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    queryset = Product.objects.order_by('-create_time')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'code', 'status']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsManagerUser]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def amount(self, request):
        data = [
            {
                'title': '商品总销量',
                'tips': '商品总销量',
                'subtitle': '商品总销量',
                'amount': 'count',
                'number1': 509998,
                'number2': 509998,
            },
            {
                'title': '商品总收藏',
                'tips': '商品总收藏',
                'amount': 'count',
                'number1': 96880,
                'number2': 96880,
            },
            {
                'title': '商品总库存',
                'tips': '商品总库存',
                'amount': 'count',
                'number1': 865990,
                'number2': 865990,
            },
            {
                'title': '商品总销售额',
                'tips': '商品总销售额',
                'subtitle': '商品总销售额',
                'amount': 'saleroom',
                'number1': 6506900,
                'number2': 6506900,
            }
        ]
        return Response(data)

    @action(detail=False, methods=['get'])
    def category_count(self, request):
        data = [
            {
                'name': '上衣',
                'goodsCount': 1000
            },
            {
                'name': '裤子',
                'goodsCount': 1200
            },
            {
                'name': '鞋子',
                'goodsCount': 1100
            },
            {
                'name': '厨具',
                'goodsCount': 1050
            },
            {
                'name': '家具',
                'goodsCount': 800
            },
            {
                'name': '床上用品',
                'goodsCount': 700
            },
            {
                'name': '女装',
                'goodsCount': 1190
            }
        ]

        return Response(data)

    @action(detail=False, methods=['get'])
    def category_sale(self, request):
        data = [
            {
                'name': '家用电器',
                'saleCount': 300
            },
            {
                'name': '食用酒水',
                'saleCount': 800
            },
            {
                'name': '个护健康',
                'saleCount': 600
            },
            {
                'name': '服饰箱包',
                'saleCount': 900
            },
            {
                'name': '母婴产品',
                'saleCount': 1000
            }
        ]
        return Response(data)

    @action(detail=False, methods=['get'])
    def category_favor(self, request):
        data = [
            {
                'name': '上衣',
                'favorCount': 6091
            },
            {
                'name': '裤子',
                'favorCount': 4939
            },
            {
                'name': '鞋子',
                'favorCount': 19647
            },
            {
                'name': '厨具',
                'favorCount': 15426
            },
            {
                'name': '家具',
                'favorCount': 16526
            }
        ]

        return Response(data)

    @action(detail=False, methods=['get'])
    def address_sale(self, request):
        data = [
            {
                'name': '上海',
                'saleCount': 256333
            },
            {
                'name': '北京',
                'saleCount': 69363
            },
            {
                'name': '广州',
                'saleCount': 125682
            },
            {
                'name': '深圳',
                'saleCount': 5600
            },
            {
                'name': '杭州',
                'saleCount': 25333
            },
            {
                'name': '南京',
                'saleCount': 6000
            },
            {
                'name': '西安',
                'saleCount': 7988
            },
            {
                'name': '成都',
                'saleCount': 25630
            },
            {
                'name': '武汉',
                'saleCount': 4506
            },
            {
                'name': '长沙',
                'saleCount': 69056
            },
            {
                'name': '天津',
                'saleCount': 9863
            },
            {
                'name': '重庆',
                'saleCount': 45440
            },
            {
                'name': '苏州',
                'saleCount': 7966
            },
            {
                'name': '无锡',
                'saleCount': 2563
            },
            {
                'name': '青岛',
                'saleCount': 2563
            },
            {
                'name': '济南',
                'saleCount': 84693
            },
            {
                'name': '郑州',
                'saleCount': 125639
            },
            {
                'name': '合肥',
                'saleCount': 2563
            },
            {
                'name': '福州',
                'saleCount': 4622
            },
            {
                'name': '厦门',
                'saleCount': 2563
            },
            {
                'name': '南昌',
                'saleCount': 6323
            },
            {
                'name': '南宁',
                'saleCount': 1256
            },
            {
                'name': '乌鲁木齐',
                'saleCount': 2563
            },
            {
                'name': '哈尔滨',
                'saleCount': 4566
            },
        ]

        return Response(data)


class LoginlogViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    queryset = LoginLog.objects.all()
    pagination_class = CustomPagination
    serializer_class = LoginLogSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filterset_class = LoginlogFilter

    def get_queryset(self):
        """
        获取基础查询集（包含权限过滤）
        """

        # user = self.request.user
        # # 生成缓存key
        # filter_params = self.request.data
        # cache_key = f"login_log_{user.id}_{hash(str(sorted(filter_params.items())))}"
        #
        # # 尝试从缓存获取
        # cached_queryset = cache.get(cache_key)
        # if cached_queryset:
        #     return cached_queryset

        queryset = self.get_user_access_queryset(self.request.user)
        # optimized_queryset = queryset.select_related('creator').only(
        #     'id',
        #     'username',
        #     'ip',
        #     'browser',
        #     'os',
        #     'continent',
        #     'country',
        #     'province',
        #     'city',
        #     'district',
        #     'isp',
        #     'area_code',
        #     'country_english',
        #     'country_code',
        #     'longitude',
        #     'latitude',
        #     'login_type',
        #     'create_time',
        #     'creator_id',
        #     'creator__username',
        #     'creator__real_name'
        # )
        #
        # # 缓存3分钟（登录日志变化较频繁）
        # cache.set(cache_key, optimized_queryset, 180)
        return queryset.select_related('creator').only(
            'id',
            'username',
            'ip',
            'browser',
            'os',
            'continent',
            'country',
            'province',
            'city',
            'district',
            'isp',
            'area_code',
            'country_english',
            'country_code',
            'longitude',
            'latitude',
            'login_type',
            'create_time',
            'creator_id',
            'creator__username',
            'creator__real_name'
        )

    def get_user_access_queryset(self, user):
        """
        获取用户访问权限的查询集
        """
        if user.is_superuser:
            # 超级用户可以查看所有数据
            return self.queryset
        else:
            # 其他用户只能查看自己的数据
            return self.queryset.filter(creator=user)

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
        filterset = LoginlogFilter(data=request.data, queryset=queryset)
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
        return Response({
            'code': 200,
            'msg': 'success',
            'data': serialzer.data
        })


class OperationlogViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    queryset = OperationLog.objects.all()
    pagination_class = CustomPagination
    serializer_class = OperationLogSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filterset_class = OperationlogFilter

    def get_queryset(self):
        """
        获取优化后的基础查询集（包含权限过滤）
        """
        # user = self.request.user
        # # 生成缓存key
        # filter_params = self.request.data
        # cache_key = f"operation_log_{user.id}_{hash(str(sorted(filter_params.items())))}"
        #
        # # 尝试从缓存获取
        # cached_queryset = cache.get(cache_key)
        # if cached_queryset:
        #     return cached_queryset

        queryset = self.get_user_access_queryset(self.request.user)
        # 预加载关联对象，只选择需要的字段
        # optimized_queryset = queryset.select_related('creator').only(
        #     'id',
        #     'request_modular',
        #     'request_path',
        #     'request_body',
        #     'request_method',
        #     'request_msg',
        #     'request_ip',
        #     'request_browser',
        #     'response_code',
        #     'request_os',
        #     'json_result',
        #     'status',
        #     'create_time',
        #     'creator_id',
        #     'creator__username',
        #     'creator__real_name'
        # )

        # 缓存5分钟
        # cache.set(cache_key, optimized_queryset, 300)
        return queryset.select_related('creator').only(
            'id',
            'request_modular',
            'request_path',
            'request_body',
            'request_method',
            'request_msg',
            'request_ip',
            'request_browser',
            'response_code',
            'request_os',
            'json_result',
            'status',
            'create_time',
            'creator_id',
            'creator__username',
            'creator__real_name'
        )

    def get_user_access_queryset(self, user):
        """
        获取用户访问权限的查询集
        """
        if user.is_superuser:
            # 超级用户可以查看所有数据
            return self.queryset
        else:
            # 其他用户只能查看自己的数据
            return self.queryset.filter(creator=user)

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
        filterset = OperationlogFilter(data=request.data, queryset=queryset)
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
        return Response({
            'code': 200,
            'msg': 'success',
            'data': serialzer.data
        })
