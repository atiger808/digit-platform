# -*- coding: utf-8 -*-
# @File   :serializers.py
# @Time   :2025/4/17 16:35
# @Author :admin

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate
from django.core.cache import cache
from django.conf import settings
from django.db.models import Q
from datetime import datetime, timedelta

from .models import EmailCode, User, Department, Role, Menu, Product, Profile, LoginLog, OperationLog
from utils.captcha import CaptchaService
from loguru import logger
import re
import os


class EmailCodeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, label='邮箱')

    class Meta:
        model = EmailCode
        fields = ['email']

    def validate_email(self, value):
        if value:
            if not re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', value):
                raise serializers.ValidationError('邮箱格式不正确')
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError('邮箱已注册过')
        return value


class CaptchaSerializer(serializers.Serializer):
    """验证码序列化器"""

    code = serializers.CharField(
        max_length=4,
        min_length=4,
        label='验证码',
        write_only=True,
    )
    key = serializers.CharField(
        max_length=100,
        min_length=10,
        label='验证码key',
        write_only=True,
    )

    def validate(self, attrs):
        logger.info(f'验证码验证: {attrs}')
        key = attrs.get('key')
        code = attrs.get('code').lower()

        cache_key = f'captcha:{key}'
        actual_code = cache.get(cache_key)

        if not actual_code:
            raise serializers.ValidationError('验证码已过期')
        if code != actual_code:
            raise serializers.ValidationError('验证码错误')
        cache.delete(cache_key)

        return super().validate(attrs)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # 添加自定义声明
        token['username'] = user.username
        token['real_name'] = user.real_name if user.real_name else user.username
        # token['avatar'] = user.avatar if user.avatar else ''
        token['avatar'] = user.profile.avatar.url if user.profile.avatar else ''
        token['department'] = user.department.name if user.department else ''
        token['roles'] = [role.name for role in user.roles.all()]

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # 添加自定义响应数据
        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        # 添加用户信息
        user = self.user
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'real_name': user.real_name if user.real_name else user.username,
            # 'avatar': user.avatar if user.avatar else None,
            'avatar': user.profile.avatar.url if user.profile.avatar else None,
            'email': user.email,
            'mobile': user.mobile,
            'department': user.department.name if user.department else None,
            'roles': [role.name for role in user.roles.all()],
            'is_staff': user.is_staff,
        }

        logger.info(f'user: {user}')
        if user.is_active == False:
            logger.info('该用户已被禁用')
            raise serializers.ValidationError({'is_active': '该用户已被禁用'})

        user.last_login_time = user.last_login  # 上次登录时间
        user.last_login = timezone.now()   # 这次登录时间
        user.save()

        return data


class RegisterSerializer(serializers.ModelSerializer):
    identifier = serializers.CharField(required=True, label='身份标识')
    identifier_type = serializers.ChoiceField(
        choices=['username', 'email', 'mobile'],
        label='标识类型',
        write_only=True
    )
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    code = serializers.CharField(write_only=True, label='验证码')
    key = serializers.CharField(required=False)

    mobile = serializers.CharField(required=False, label='手机号')
    email = serializers.CharField(required=False, label='邮箱')

    class Meta:
        model = User
        fields = ('identifier_type', 'identifier', 'password', 'password2', 'code', 'key', 'mobile', 'email')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            }
        }

    def validate(self, attrs):
        logger.info(f'注册验证: {attrs}')
        identifier = attrs.get('identifier')
        code = attrs.get('code')
        key = attrs.get('key')

        # 验证码校验
        if not code:
            raise serializers.ValidationError({'code': '验证码不能为空'})

        # 检查标识唯一性
        if attrs['identifier_type'] == 'email':
            success, msg = CaptchaService.verify_email_code(key, code)
            if not success:
                raise serializers.ValidationError({'code': msg})
            if User.objects.filter(email=identifier).exists():
                raise serializers.ValidationError({'email': '邮箱已注册'})
        elif attrs['identifier_type'] == 'mobile':
            success, msg = CaptchaService.verify_sms_code(key, code)
            if not success:
                raise serializers.ValidationError({'code': msg})
            if User.objects.filter(mobile=identifier).exists():
                raise serializers.ValidationError({'mobile': '手机号已注册'})
        else:
            success, msg = CaptchaService.verify_image_captcha(key, code)
            if not success:
                raise serializers.ValidationError({'code': msg})

            if User.objects.filter(username=identifier).exists():
                raise serializers.ValidationError({'username': '用户已注册'})

            if attrs['password'] != attrs['password2']:
                raise serializers.ValidationError({'password': '两次密码不一致'})

        return attrs

        # # 至少提供一个身份标识
        # identifiers = ['username', 'email', 'mobile']
        # if not any(attrs.get(key) for key in identifiers):
        #     raise serializers.ValidationError('必须提供用户名、邮箱或手机号')
        #
        # # 检查邮箱唯一性
        # if attrs.get('email') and User.objects.filter(email=attrs['email']).exists():
        #     raise serializers.ValidationError('邮箱已存在')
        #
        # # 检查手机号唯一性
        # if attrs.get('mobile') and User.objects.filter(mobile=attrs['mobile']).exists():
        #     raise serializers.ValidationError('手机号已存在')
        #
        # if attrs.get('username') and attrs['password'] != attrs['password2']:
        #     raise serializers.ValidationError({"password": "两次密码不一致"})
        # return attrs

    def validate_mobile(self, value):
        if value:
            if not re.match(r'^1[3-9]\d{9}$', value):
                raise serializers.ValidationError('手机号格式不正确')
            if User.objects.filter(mobile=value).exists():
                raise serializers.ValidationError('手机号已存在')
        return value

    def validate_email(self, value):
        if value:
            if not re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', value):
                raise serializers.ValidationError('邮箱格式不正确')
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError('邮箱已存在')
        return value

    def create(self, validated_data):
        logger.info(f'register: {validated_data}')
        # 生成用户名
        username = validated_data.get('identifier') or validated_data.get('mobile') or validated_data.get('email')
        # 移除字段
        validated_data.pop('identifier')
        validated_data.pop('identifier_type')
        validated_data.pop('code')
        validated_data.pop('key')
        validated_data.pop('password2')

        # 创建用户
        user = User.objects.create(
            username=username,
            email=validated_data.get('email', ''),
            mobile=validated_data.get('mobile', ''),
            password=make_password(validated_data['password'])
        )
        role_id = validated_data.get('role_id')
        if not role_id:
            role_id = Role.objects.filter(code='user').first().id
        # 分配默认角色
        if role_id:
            user.roles.set([role_id])
            role_obj = Role.objects.filter(id=role_id).first()
            if role_obj:
                if role_obj.code == 'system':
                    user.is_superuser = True
                    user.is_staff = True
                elif role_obj.code == 'admin':
                    user.is_staff = True
                    user.is_superuser = False
                elif role_obj.code == 'user':
                    user.is_superuser = False
                    user.is_staff = False
            user.save()

        return user


class LoginSerializer(serializers.Serializer):
    """登录序列化"""
    identifier = serializers.CharField()
    password = serializers.CharField(required=True, label='密码', style={'input_type': 'password'}, write_only=True)
    code = serializers.CharField(required=False, label='验证码', allow_blank=True, max_length=6)
    key = serializers.CharField(required=False, allow_blank=True, max_length=32)

    def get_tokens_for_user(self, user):
        """
        获取用户token
        :param user:
        :return:
        """
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')
        key = attrs.get('key')
        code = attrs.get('code')

        # 如果需要验证码则验证
        user = authenticate(
            request=self.context.get('request'),
            identifier=identifier,
            password=password
        )

        if not user:
            attempts = cache.get(f'login_attempts:{identifier}', 0)
            logger.info(f'identifier: {identifier} attempts: {attempts}次登录')
            if attempts >= settings.MAX_LOGIN_ATTEMPTS:
                if not code:
                    logger.info(f'identifier: {identifier} 尝试次数已超过最大限制, 需要验证码')
                    raise serializers.ValidationError({'code': '请输入验证码', 'attempts': attempts})
                success, msg = CaptchaService.verify_image_captcha(key, code)
                if not success:
                    raise serializers.ValidationError({'code': msg})
            raise serializers.ValidationError(
                {'error': '用户名或密码错误', 'remaining_attempts': settings.MAX_LOGIN_ATTEMPTS - attempts})

        if not user.is_active:
            logger.info('该用户已被禁用')
            raise serializers.ValidationError({'error': '该用户已被禁用'})

        data = self.get_tokens_for_user(user)
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'real_name': user.real_name if user.real_name else user.username,
            'avatar': user.profile.avatar.url if user.profile.avatar else None,
            'email': user.email,
            'mobile': user.mobile,
            'department': user.department.name if user.department else None,
            'roles': [role.name for role in user.roles.all()],
            'is_staff': user.is_staff,
        }
        user.last_login_time = user.last_login  # 上次登录时间
        user.last_login = timezone.now()  # 这次登录时间
        user.save()

        return data


class SendCaptchaSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    code_type = serializers.ChoiceField(choices=['register', 'login'])

    def validate_identifier(self, value):
        # 根据类型校验格式
        code_type = self.initial_data.get('code_type')
        if code_type == 'register':
            if '@' in value:
                if not re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', value):
                    raise serializers.ValidationError('邮箱格式错误')
                if User.objects.filter(email=value).exists():
                    raise serializers.ValidationError('邮箱已注册')
            elif value.isdigit() and len(value) == 11:
                if not re.match(r'^1[3-9]\d{8}$', value):
                    raise serializers.ValidationError('手机号格式错误')
                if User.objects.filter(mobile=value).exists():
                    raise serializers.ValidationError('手机号已注册')
        return value


class UserSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField(read_only=True)
    roles_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'real_name', 'avatar', 'gender', 'email', 'mobile',
                  'department', 'department_name', 'roles_name', 'is_active',
                  'last_login_time', 'create_time']
        extra_kwargs = {
            'password': {'write_only': True},
            'department': {'write_only': True},
            'roles': {'write_only': True},
        }

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

    def get_roles_name(self, obj):
        return [role.name for role in obj.roles.all()]

    def create(self, validated_data):
        logger.info(validated_data)
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)


class UserListSerializer(serializers.ModelSerializer):
    """用于列表查询的简化序列器（带分页 ）"""
    department_info = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()

    department_id = serializers.SerializerMethodField()
    role_id = serializers.SerializerMethodField()
    online = serializers.SerializerMethodField()

    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'real_name', 'avatar', 'gender', 'email', 'mobile', 'department_info', 'roles',
                  'role_id', 'department_id', 'online', 'last_login_time', 'is_superuser', 'is_staff',
                  'is_active', 'create_time']

    def get_department_info(self, obj):
        return {
            'id': obj.department.id if obj.department else None,
            'name': obj.department.name if obj.department else None
        }

    def get_roles(self, obj):
        return [{
            'id': role.id,
            'name': role.name,
            'code': role.code
        } for role in obj.roles.all()]

    def get_role_id(self, obj):
        return obj.roles.first().id if obj.roles.exists() else None



    def get_department_id(self, obj):
        return obj.department.id if obj.department else None

    def get_online(self, obj):
        if obj.last_login is None:
            return False
        return timezone.now().astimezone() < (obj.last_login.astimezone() + settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME'))

    def get_fields(self):
        fields = super().get_fields()
        user = self.context['request'].user

        if not user.is_superuser:
            fields.pop('last_login_time', None)
            fields.pop('is_superuser', None)
            fields.pop('is_staff', None)

        return fields


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    role_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text='角色ID列表'
    )
    department_id = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text='部门ID'
    )
    role_id = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text='角色ID'
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'real_name', 'avatar', 'gender', 'email', 'mobile',
                  'department_id', 'role_ids', 'role_id', 'is_staff', 'is_superuser', 'is_active', 'create_time']
        extra_kwargs = {
            'mobile': {'required': True}
        }

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username:
            raise serializers.ValidationError({'username': '用户名不能为空'})

        if len(username) > 50:
            raise serializers.ValidationError({'username': '用户名长度不能超过50个字符'})

        if not password:
            raise serializers.ValidationError({'password': '密码不能为空'})

        if len(password) > 50:
            raise serializers.ValidationError({'password': '密码长度不能超过50个字符'})

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': '用户名已存在'})





        # 验证部门是否存在
        department_id = attrs.get('department_id')
        if department_id:
            try:
                Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                raise serializers.ValidationError({'department_id': '部门不存在'})

        # 验证角色是否存在
        role_ids = attrs.get('role_ids', [])
        logger.info(role_ids)
        role_id = attrs.get('role_id')
        logger.info(role_id)
        if role_id:
            role_ids.append(role_id)
            role_ids = list(set(role_ids))
            attrs['role_ids'] = role_ids
        if role_ids:
            existing_roles = Role.objects.filter(id__in=role_ids).count()
            if existing_roles != len(role_ids):
                raise serializers.ValidationError({'role_ids': '包含无效的角色ID'})

        # 验证手机号邮箱是否存在
        mobile = attrs.get('mobile')
        email = attrs.get('email')

        if mobile:
            if not re.match(r'^1[3-9]\d{9}$', mobile):
                raise serializers.ValidationError({'mobile': '手机号格式不正确'})

            if User.objects.filter(mobile=mobile).exists():
                raise serializers.ValidationError({'mobile': '手机号已存在'})

        if email:
            if not re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
                raise serializers.ValidationError({'email': '邮箱格式不正确'})
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError({'email': '邮箱已存在'})



        return attrs

    def create(self, validated_data):
        """提取角色和部门数据"""
        role_id = validated_data.pop('role_id', None)
        role_ids = validated_data.pop('role_ids', [])
        department_id = validated_data.pop('department_id', None)
        logger.info(role_id)
        logger.info(role_ids)
        logger.info(department_id)

        if not role_id and not role_ids:
            role_id = Role.objects.filter(code='user').first().id

        # 加密密码
        validated_data['password'] = make_password(validated_data['password'])

        # 创建用户
        user = User.objects.create(**validated_data)

        # 设置部门和角色
        if department_id:
            user.department_id = department_id
            user.save()
        if role_ids:
            user.roles.set(role_ids)
        # 分配默认角色
        if role_id:
            role_obj = Role.objects.filter(id=role_id).first()
            if role_obj:
                if role_obj.code == 'system':
                    user.is_superuser = True
                    user.is_staff = True
                elif role_obj.code == 'admin':
                    user.is_staff = True
                    user.is_superuser = False
                elif role_obj.code == 'user':
                    user.is_superuser = False
                    user.is_staff = False

        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    department_id = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text='部门ID'
    )
    role_id = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text='角色ID'
    )

    class Meta:
        model = User
        fields = ['real_name', 'avatar', 'password', 'gender', 'email', 'mobile', 'department', 'roles',
                  'department_id', 'role_id', 'is_staff', 'is_superuser', 'is_active']

    def validate(self, attrs):
        # 验证部门是否存在
        department_id = attrs.get('department_id')
        if department_id:
            try:
                Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                raise serializers.ValidationError({'department_id': '部门不存在'})

        # 验证角色是否存在
        role_ids = attrs.get('role_ids', [])
        role_id = attrs.get('role_id')
        if role_id:
            role_ids.append(role_id)
        if role_ids:
            existing_roles = Role.objects.filter(id__in=role_ids).count()
            if existing_roles != len(role_ids):
                raise serializers.ValidationError({'role_ids': '包含无效的角色ID'})

        return attrs

    def update(self, instance, validated_data):
        user = self.context['request'].user
        logger.info(f'user: {user} validated_data: {validated_data}')
        department_id = validated_data.pop('department_id', None)
        role_id = validated_data.pop('role_id', None)
        role_ids = validated_data.pop('role_ids', [])

        real_name = validated_data.get('real_name')
        email = validated_data.get('email')
        mobile = validated_data.get('mobile')
        password = validated_data.get('password')

        if real_name and instance.real_name != real_name:
            if len(real_name) > 50:
                raise serializers.ValidationError({'real_name': '昵称长度不能超过50个字符'})
            existing_user = User.objects.filter(real_name=real_name).exclude(id=instance.id).first()
            if existing_user:
                raise serializers.ValidationError({'real_name': '昵称已存在'})

        if email and instance.email != email:
            if not re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
                raise serializers.ValidationError({'email': '邮箱格式不正确'})
            existing_user = User.objects.filter(email=email).exclude(id=instance.id).first()
            if existing_user:
                raise serializers.ValidationError({'email': '邮箱已存在'})

        if mobile and instance.mobile != mobile:
            if not re.match(r'^1[3-9]\d{9}$', mobile):
                raise serializers.ValidationError({'mobile': '手机号格式不正确'})
            existing_user = User.objects.filter(mobile=mobile).exclude(id=instance.id).first()
            if existing_user:
                raise serializers.ValidationError({'mobile': '手机号已存在'})

        if department_id:
            instance.department_id = department_id
            instance.save()
        if role_id:
            instance.roles.set([role_id])
        if role_ids:
            instance.roles.set(role_ids)

        for key, value in validated_data.items():
            setattr(instance, key, value)
        role_obj = Role.objects.filter(id=role_id).first()
        if role_obj:
            logger.info(f'user: {user} is_superuser: {user.is_superuser} instance: {instance} role_obj: {role_obj}')
            if role_obj.code == 'system':
                if not user.is_superuser:
                    logger.info(f'user: {user} instance: {instance} 没有操作权限')
                    raise serializers.ValidationError({'error': '没有操作权限'})
                instance.is_superuser = True
                instance.is_staff = True
            elif role_obj.code == 'admin':
                if not user.is_superuser:
                    logger.info(f'user: {user} instance: {instance} 没有操作权限')
                    raise serializers.ValidationError({'error': '没有操作权限'})
                instance.is_staff = True
                instance.is_superuser = False
            elif role_obj.code == 'user':
                instance.is_superuser = False
                instance.is_staff = False
        if password:
            instance.password = make_password(password)
        instance.save()
        return instance


class UserRoleUpdateSerializer(serializers.Serializer):
    role_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )

    def validate_role_ids(self, value):
        logger.info(f'value: {value}')
        # 验证角色是否存在
        existing_roles = Role.objects.filter(id__in=value).count()
        if existing_roles != len(value):
            raise serializers.ValidationError('包含无效的角色ID')
        return value


class UserDepartmentUpdateSerializer(serializers.Serializer):
    department_id = serializers.IntegerField(
        required=True
    )

    def validate_department_id(self, value):
        # 验证部门是否存在
        try:
            Department.objects.get(id=value)
        except Department.DoesNotExist:
            raise serializers.ValidationError('部门不存在')
        return value


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("旧密码不正确")
        return value


class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField(required=False)
    class Meta:
        model = Profile
        fields = ['id', 'avatar', 'bio', 'location', 'birth_date']

    def get_avatar(self, obj):
        if obj.avatar:
            avatar_url = os.path.join(settings.BASE_URL, obj.avatar.url.strip('/'))
            return avatar_url 
        return None


class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    role_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'real_name', 'email', 'mobile', 'profile', 'role_name', 'department_name',
                  'is_staff', 'is_superuser', 'is_active', 'last_login', 'last_login_time', 'date_joined']
        read_only_fields = ['id', 'username']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        profile = instance.profile

        logger.info(f'profile_data: {profile_data}')
        logger.info(f'profile: {profile}')
        logger.info(f'validated_data: {validated_data}')
        logger.info(f'instance: {instance}')

        real_name = validated_data.get('real_name')
        email = validated_data.get('email')
        mobile = validated_data.get('mobile')

        if real_name and instance.real_name != real_name:
            existing_user = User.objects.filter(real_name=real_name).exclude(id=instance.id).first()
            if existing_user:
                raise serializers.ValidationError({'real_name': '昵称已存在'})

        if email and instance.email != email:
            existing_user = User.objects.filter(email=email).exclude(id=instance.id).first()
            if existing_user:
                raise serializers.ValidationError({'email': '邮箱已存在'})
        if mobile and instance.mobile != mobile:
            existing_user = User.objects.filter(mobile=mobile).exclude(id=instance.id).first()
            if existing_user:
                raise serializers.ValidationError({'mobile': '手机号已存在'})

        if len(real_name)>50:
            raise serializers.ValidationError('昵称长度不能超过50个字符')
        if not re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
            raise serializers.ValidationError('邮箱格式不正确')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            raise serializers.ValidationError('手机号格式不正确')


        # 更新用户字段
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        # 更新profile字段
        for key, value in profile_data.items():
            setattr(profile, key, value)
        profile.save()
        return instance

    def get_role_name(self, obj):
        role = obj.roles.first()
        if role:
            return role.name
        return None

    def get_department_name(self, obj):
        department = obj.department
        if department:
            return department.name
        return None


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("新密码和确认密码不匹配")

        password_validation.validate_password(data['new_password'])

        return data


class AvatarSerializer(serializers.Serializer):
    avatar = serializers.ImageField(
        required=True,
        max_length=100,
        allow_empty_file=False,
        use_url=True
    )

    def validate_avatar(self, value):
        # 验证文件类型
        valid_types = ['image/png', 'image/jpeg', 'image/jpg']
        if value.content_type not in valid_types:
            raise serializers.ValidationError("文件类型不正确，请上传PNG、JPG或JPEG格式的图片")

        # 验证文件大小
        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("文件大小不能超过2MB")

        return value


class DepartmentSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = Department
        fields = '__all__'


class DepartmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['name', 'code', 'parent', 'status', 'sort']


class DynamicMenuSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = (
            'id', 'name', 'code', 'type', 'status', 'path', 'component', 'permission', 'icon', 'sort', 'parent', 'parent_name',
            'children', 'create_time')

    def get_children(self, obj):
        user = self.context['request'].user
        queryset = Menu.objects.filter(parent=obj, status=True)

        if not user.is_superuser:
            queryset = queryset.filter(roles__in=user.roles.all())

        return DynamicMenuSerializer(
            queryset.order_by('sort'),
            many=True,
            context=self.context
        ).data

    def get_parent_name(self, obj):
        if obj.parent:
            return obj.parent.name
        return None


class MenuTreeSerializer(serializers.ModelSerializer):
    """菜单树形结构序列化器"""
    children = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ['id', 'name', 'code', 'type', 'path', 'component', 'icon', 'children']

    def get_children(self, obj):
        """递归获取子菜单"""
        children = Menu.objects.filter(parent=obj, status=True).order_by('sort')
        serializer = MenuTreeSerializer(children, many=True, context=self.context)
        return serializer.data


class RoleSerializer(serializers.ModelSerializer):
    menus = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = '__all__'

    def get_menus(self, obj):
        """获取角色关联的菜单树"""
        # 获取一级菜单（parent为null的菜单）
        root_menus = obj.menus.filter(parent__isnull=True, status=True).order_by('sort')
        return MenuNodeSerializer(root_menus, many=True, context=self.context).data


class MenuNodeSerializer(serializers.ModelSerializer):
    """菜单节点序列化器"""
    children = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ['id', 'name', 'code', 'type', 'path', 'component', 'icon', 'children']

    def get_children(self, obj):
        """通过 parent 的反向关系 children 获取子菜单"""
        owned_menu_ids = self.context.get('owned_menu_ids', set())

        # 使用 obj.children 访问子菜单（通过反向关系）
        children = obj.children.filter(
            id__in=owned_menu_ids,
            status=True
        ).order_by('sort')

        return MenuNodeSerializer(
            children,
            many=True,
            context=self.context
        ).data


class RoleWithMenuTreeSerializer(serializers.ModelSerializer):
    """角色详情带完整菜单树"""
    menus = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ['id', 'name', 'code', 'status', 'menus', 'create_time']

    def get_menus(self, obj):
        # 获取角色拥有的菜单ID
        owned_menu_ids = set(obj.menus.values_list('id', flat=True))

        # 获取需要显示的菜单（角色拥有的菜单+它们的直接父菜单）
        all_menus = Menu.objects.filter(
            Q(id__in=owned_menu_ids) |
            Q(children__id__in=owned_menu_ids)  # 使用反向关系
        ).distinct().prefetch_related('children')

        # 构建树形结构
        menu_dict = {menu.id: menu for menu in all_menus}
        root_menus = [m for m in all_menus if not m.parent_id or m.parent_id not in menu_dict]

        return MenuNodeSerializer(
            root_menus,
            many=True,
            context={'owned_menu_ids': owned_menu_ids}
        ).data


class RoleCreateUpdateSerializer(serializers.ModelSerializer):
    """用于创建/更新的角色序列化器"""
    menu_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text='菜单ID列表'
    )

    class Meta:
        model = Role
        fields = ['name', 'code', 'status', 'sort', 'menu_ids']

    def validate_menu_ids(self, value):
        """
        验证菜单ID是否存在
        """
        if value:
            existing_menus = Menu.objects.filter(id__in=value).count()
            if existing_menus != len(value):
                raise serializers.ValidationError('包含无效的菜单ID')
        return value

    def create(self, validated_data):
        """创建角色并关联菜单"""
        menu_ids = validated_data.pop('menu_ids', [])
        role = Role.objects.create(**validated_data)
        if menu_ids:
            role.menus.set(menu_ids)
        return role

    def update(self, instance, validated_data):
        """更新菜单及菜单关联"""
        menu_ids = validated_data.pop('menu_ids', [])
        role = super().update(instance, validated_data)
        if menu_ids is not None:  # 明确区分传空数组和不传的情况
            role.menus.set(menu_ids)
        return role


class MenuSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = Menu
        fields = '__all__'


class MenuAssignmentSerializer(serializers.Serializer):
    """
        菜单分配序列化器
        用于角色分配菜单权限的专用序列化器
    """
    menu_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text='菜单ID列表'
    )

    class Meta:
        # 虽然这是Serializer而不是ModelSerializer，
        # 但定义Meta类可以方便文档生成
        ref_name = "MenuAssignmentSerializer"
        fields = ['menu_ids']

    def validate_menu_ids(self, value):
        """
        验证菜单ID是否存在
        """
        if not value:
            raise serializers.ValidationError('至少需要分配一个菜单')

        # 检查所有菜单ID是否存在
        existing_menus = Menu.objects.filter(id__in=value).count()
        if existing_menus != len(value):
            raise serializers.ValidationError('包含无效的菜单ID')

        return value


class ProductSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class LoginLogSerializer(serializers.ModelSerializer):
    # 如果需要显示创建者信息
    creator_username = serializers.CharField(source='creator.username', read_only=True, allow_null=True)
    creator_real_name = serializers.CharField(source='creator.real_name', read_only=True, allow_null=True)
    class Meta:
        model = LoginLog
        # fields = '__all__'
        fields = [
            'id',
            'username',
            'ip',
            'browser',
            'agent',
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
            'creator_username',
            'creator_real_name'
        ]

class OperationLogSerializer(serializers.ModelSerializer):
    creator_username = serializers.CharField(source='creator.username', read_only=True)
    real_name = serializers.CharField(source='creator.real_name', read_only=True)
    class Meta:
        model = OperationLog
        # fields = '__all__'
        fields = [
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
            'creator_username',
            'real_name'
        ]
