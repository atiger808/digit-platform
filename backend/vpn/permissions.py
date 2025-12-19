# -*- coding: utf-8 -*-
# @File   :permissions.py
# @Time   :2025/5/29 16:35
# @Author :admin
import ipaddress
from loguru import logger
import json

from rest_framework.permissions import BasePermission
from django.conf import settings
import hashlib
import time
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status

class IsSuperAdmin(BasePermission):
    """仅超级管理员有权限"""

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsAdminUser(BasePermission):
    """仅管理员有权限"""

    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsOwnerOrAdmin(BasePermission):
    """对象所有者或者管理员有权限"""

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user or obj.user == request.user



class SignaturePermission(BasePermission):
    """
    自定义签名验证权限
    要求请求头中包含：
    X-Timestamp: 请求时间戳
    X-Signature: 签名
    """

    def has_permission(self, request, view):
        # 获取请求中的时间戳和签名
        timestamp = request.META.get('HTTP_X_TIMESTAMP')
        signature = request.META.get('HTTP_X_SIGNATURE')
        client_ip = request.META.get('REMOTE_ADDR')
        logger.info(f'client_ip: {client_ip} timestamp:{timestamp}, signature:{signature}')
        if not timestamp or not signature:
            logger.error(f'client_ip: {client_ip} 缺少参数X-Timestamp或X-Signature')
            raise PermissionDenied({'error': '缺少参数X-Timestamp或X-Signature'})

        # 验证时间戳有效性
        try:
            timestamp = int(timestamp)
            current_time = int(time.time())
            if abs(current_time - timestamp) > 300: # 5分钟有效期
                logger.error(f'client_ip: {client_ip} 时间戳无效，已经过期')
                raise PermissionDenied('时间戳无效，已经过期')
        except  ValueError:
            logger.error(f'client_ip: {client_ip} 时间戳无效，请检查格式')
            raise PermissionDenied({'error': '时间戳无效，请检查格式'})

        # 获取API密钥（应该从安全的地方获取，如数据库或环境变量）
        api_key = getattr(settings, 'API_SECRET_KEY', 'your-secret-key')

        # 生成预期签名1
        # path = request.get_full_path()
        # method = request.method.upper()
        # data = request.body.decode('utf-8') if request.body else '{}'
        # sign_str = f'{method}{path}{timestamp}{data}{api_key}'
        # expected_signature = hashlib.sha256(sign_str.encode('utf-8')).hexdigest()

        # 生成预期签名2
        try:
            user_id = request.query_params.get('user_id') or json.loads(request.body)['user_id']
        except  Exception as e:
            logger.error(f'client_ip: {client_ip} 缺少参数user_id error:{e}')
            raise PermissionDenied({'error': '缺少参数user_id'})
        sign_str = f'{timestamp}{user_id}{api_key}'
        expected_signature = hashlib.md5(sign_str.encode('utf-8')).hexdigest()

        # 比较签名
        if not self.compare_signatures(signature, expected_signature):
            logger.error(f'client_ip: {client_ip} 签名无效 expected_signature:{expected_signature}')
            raise PermissionDenied({'error': '签名无效'})
        return True

    def compare_signatures(self, signature1, signature2):
        """安全地比较两个签名，防止时序攻击"""
        return hashlib.sha256(signature1.encode()).hexdigest() == hashlib.sha256(signature2.encode()).hexdigest()


    def permission_denied(self, request, message=None):
        """权限被拒绝时返回的响应"""
        if message is None:
            message = "签名验证失败"
        return Response({
            'message': message,
            'status': status.HTTP_403_FORBIDDEN,
            'code': 40003,
            "timestamp": int(time.time())
        }, status=status.HTTP_403_FORBIDDEN)


class IPWhitelistSignturePermission(SignaturePermission):
    """带IP白名单的签名验证"""
    whitelist = ['127.0.0.1', '192.168.1.0/24', '122.226.65.250', '122.226.220.154'] # 实际应该从设置或数据库获取

    def has_permission(self, request, view):
        client_ip = request.META.get('REMOTE_ADDR')

        # 检查IP是否在白名单中
        if not any(ipaddress.ip_address(client_ip) in ipaddress.ip_network(net) for net in self.whitelist):
            raise PermissionDenied('IP地址不在白名单中')

        return super().has_permission(request, view)
