# -*- coding: utf-8 -*-
# @File   :authentication.py
# @Time   :2025/5/10 11:59
# @Author :admin
from venv import logger

from django.contrib.auth.backends import ModelBackend
from django.core.cache import cache
from django.conf import settings
from django.db.models import Q
from .models import User


class EnhancedAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, identifier=None, captcha=None, **kwargs):
        logger.info(f"Authenticating user with identifier: {identifier or username}")

        # 确定使用的标识符
        identifier = identifier or username
        if not identifier:
            return None

        if hasattr(request, 'path') and isinstance(request.path, str) and '/admin/login/' in request.path:
            try:
                user = User.objects.get(username=identifier)
                if user.check_password(password) and user.is_staff:
                    return user
            except User.DoesNotExist:
                return None

        # 获取用户
        try:
            user = User.objects.get(
                Q(username=identifier) |
                Q(mobile=identifier) |
                Q(email=identifier)
            )
        except User.DoesNotExist:
            return None

        # 检查账户是否被锁定
        if self._is_account_locked(identifier):
            logger.warning(f"Account locked: {identifier}")
            return None

        # 验证密码
        if not user.check_password(password):
            self._handle_failed_login(identifier)
            return None

        # 登录成功，清除失败计数
        self._clear_login_attempts(identifier)

        return user

    def get_user(self, identifier):
        try:
            return User.objects.get(
                Q(username=identifier) |
                Q(mobile=identifier) |
                Q(email=identifier)
            )
        except User.DoesNotExist:
            return None

    def _handle_failed_login(self, identifier):
        count = cache.get(f'login_attempts:{identifier}', 0) + 1
        cache.set(f'login_attempts:{identifier}', count, settings.LOGIN_ATTEMPT_TIMEOUT)

        if count >= settings.MAX_LOGIN_ATTEMPTS:
            User.objects.filter(
                Q(username=identifier) |
                Q(mobile=identifier) |
                Q(email=identifier)
            ).update(require_captcha=True)

    def _is_account_locked(self, identifier):
        return bool(cache.get(f'account_lock:{identifier}'))

    def _clear_login_attempts(self, identifier):
        cache.delete(f'login_attempts:{identifier}')
        cache.delete(f'account_lock:{identifier}')
        User.objects.filter(
            Q(username=identifier) |
            Q(mobile=identifier) |
            Q(email=identifier)
        ).update(require_captcha=False)

    def has_perm(self, user_obj, perm, obj=None):
        if user_obj.is_superuser:
            return True
        return super().has_perm(user_obj, perm, obj)

    def get_user_permissions(self, user_obj, obj=None):
        return user_obj.user_permissions.all()

    def get_group_permissions(self, user_obj, obj=None):
        return set()

    def get_all_permissions(self, user_obj, obj=None):
        if user_obj.is_anonymous:
            return set()
        return super().get_all_permissions(user_obj, obj)

    def has_module_perms(self, user_obj, app_label):
        return True
