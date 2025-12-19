# -*- coding: utf-8 -*-
# @File   :filters.py
# @Time   :2025/4/22 11:47
# @Author :admin

import django_filters
from django_filters import rest_framework as filters
from .models import User, Department, Role, Menu, LoginLog, OperationLog


class UserFilter(filters.FilterSet):
    username = django_filters.CharFilter(field_name='username')
    real_name = django_filters.CharFilter(field_name='real_name', lookup_expr='icontains')
    mobile = django_filters.CharFilter(field_name='mobile', lookup_expr='icontains')
    is_active = django_filters.BooleanFilter(field_name='is_active')
    create_time_start = django_filters.DateTimeFilter(
        field_name='create_time',
        lookup_expr='gte',
        input_formats=['%Y-%m-%d', '%Y-%m-%d %H:%M:%S'],
    )
    create_time_end = django_filters.DateTimeFilter(
        field_name='create_time',
        lookup_expr='lte',
        input_formats=['%Y-%m-%d', '%Y-%m-%d %H:%M:%S'],
    )

    class Meta:
        model = User
        fields = ['username', 'real_name', 'mobile', 'is_active', 'create_time']


class BaseFilter(filters.FilterSet):
    """基础过滤器"""
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    code = django_filters.CharFilter(field_name='code', lookup_expr='icontains')
    status = django_filters.BooleanFilter(field_name='status')
    create_time_start = django_filters.DateTimeFilter(
        field_name='create_time',
        lookup_expr='gte',
        input_formats=['%Y-%m-%d', '%Y-%m-%d %H:%M:%S']
    )
    create_time_end = django_filters.DateTimeFilter(
        field_name='create_time',
        lookup_expr='lte',
        input_formats=['%Y-%m-%d', '%Y-%m-%d %H:%M:%S']
    )


class DepartmentFilter(BaseFilter):
    parent = django_filters.NumberFilter(field_name='parent__id')

    class Meta:
        model = Department
        fields = ['name', 'code', 'status', 'parent', 'create_time']


class RoleFilter(BaseFilter):
    class Meta:
        model = Role
        fields = ['name', 'code', 'status', 'create_time']


class MenuFilter(BaseFilter):
    type = django_filters.NumberFilter(field_name='type')
    parent = django_filters.NumberFilter(field_name='parent__id')

    class Meta:
        model = Menu
        fields = ['name', 'code', 'status', 'type', 'parent', 'create_time']


class LoginlogFilter(BaseFilter):
    username = django_filters.CharFilter(field_name='username', lookup_expr='icontains')
    continent = django_filters.CharFilter(field_name='continent', lookup_expr='icontains')
    country = django_filters.CharFilter(field_name='country', lookup_expr='icontains')
    province = django_filters.CharFilter(field_name='province', lookup_expr='icontains')
    city = django_filters.CharFilter(field_name='city', lookup_expr='icontains')
    district = django_filters.CharFilter(field_name='district', lookup_expr='icontains')
    os = django_filters.CharFilter(field_name='os', lookup_expr='icontains')
    isp = django_filters.CharFilter(field_name='isp', lookup_expr='icontains')
    area_code = django_filters.CharFilter(field_name='area_code', lookup_expr='icontains')
    country_english = django_filters.CharFilter(field_name='country_english', lookup_expr='icontains')
    country_code = django_filters.CharFilter(field_name='country_code', lookup_expr='icontains')
    ip = django_filters.CharFilter(field_name='ip', lookup_expr='icontains')

    class Meta:
        model = LoginLog
        fields = ['username', 'continent', 'country', 'province', 'city', 'district', 'os', 'isp', 'area_code',
                  'country_english', 'country_code', 'ip', 'create_time']


class OperationlogFilter(BaseFilter):
    creator_name = django_filters.CharFilter(field_name='creator__username')
    real_name = django_filters.CharFilter(field_name='creator__real_name', lookup_expr='icontains')
    request_modular = django_filters.CharFilter(field_name='request_modular', lookup_expr='icontains')
    response_code = django_filters.CharFilter(field_name='response_code')
    request_method = django_filters.CharFilter(field_name='request_method')
    status = django_filters.BooleanFilter(field_name='status')
    request_ip = django_filters.CharFilter(field_name='request_ip', lookup_expr='icontains')
    request_browser = django_filters.CharFilter(field_name='request_browser', lookup_expr='icontains')
    request_os = django_filters.CharFilter(field_name='request_os', lookup_expr='icontains')

    class Meta:
        model = OperationLog
        fields = ['creator_name', 'real_name', 'response_code', 'request_method', 'status', 'request_ip', 'request_browser',
                  'request_os', 'create_time']
