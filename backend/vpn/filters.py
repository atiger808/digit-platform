# -*- coding: utf-8 -*-
# @File   :filters.py
# @Time   :2025/4/29 14:29
# @Author :admin

import django_filters
from django_filters import rest_framework as filters
from .models import DyvpnAccount, DyvpnDeviceModel, DyvpnRegionModel, DyvpnMonitor




class DyvpnAccountFilter(django_filters.FilterSet):
    vpn_account = django_filters.CharFilter(field_name='vpn_account')
    nickname = django_filters.CharFilter(field_name='nickname', lookup_expr='icontains')
    remark = django_filters.CharFilter(field_name='remark', lookup_expr='icontains')
    used = django_filters.BooleanFilter(field_name='used')
    online = django_filters.BooleanFilter(field_name='online')
    device_name = django_filters.CharFilter(field_name='device__device_name', lookup_expr='icontains')
    region = django_filters.CharFilter(field_name='region__region', lookup_expr='icontains')
    username = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')

    industry_type = django_filters.CharFilter(field_name='industry_type')
    recommender = django_filters.CharFilter(field_name='recommender', lookup_expr='icontains')
    organization_name = django_filters.CharFilter(field_name='organization_name', lookup_expr='icontains')
    contact = django_filters.CharFilter(field_name='contact', lookup_expr='icontains')


    create_time_start = django_filters.DateTimeFilter(
        field_name='create_time',
        lookup_expr='gte',
        input_formats=['%Y-%m-%d', '%Y-%m-%d %H:%M:%S'],
        label='开始日期 (YYYY-MM-DD)'
    )
    create_time_end = django_filters.DateTimeFilter(
        field_name='create_time',
        lookup_expr='lte',
        input_formats=['%Y-%m-%d', '%Y-%m-%d %H:%M:%S'],
        label='结束日期 (YYYY-MM-DD)'
    )

    class Meta:
        model = DyvpnAccount
        fields = ['vpn_account', 'used', 'device_name', 'region', 'username', 'nickname', 'remark', 'industry_type', 'recommender', 'organization_name', 'contact', 'create_time']


class DyvpnMonitorFilter(django_filters.FilterSet):
    vpn_account = django_filters.CharFilter(field_name='account__vpn_account')
    nickname = django_filters.CharFilter(field_name='account__nickname', lookup_expr='icontains')
    remark = django_filters.CharFilter(field_name='account__remark', lookup_expr='icontains')
    region = django_filters.CharFilter(field_name='region__region', lookup_expr='icontains')
    device_name = django_filters.CharFilter(field_name='account__device__device_name', lookup_expr='icontains')
    online =  django_filters.BooleanFilter(field_name='account__online')
    username = django_filters.CharFilter(field_name='account__user__username', lookup_expr='icontains')

    # 在线状态优化
    online = django_filters.BooleanFilter(method='filter_online')

    create_time_start = django_filters.DateTimeFilter(
        field_name='login_time',
        lookup_expr='gte',
        input_formats=['%Y-%m-%d', '%Y-%m-%d %H:%M:%S'],
        label='开始日期 (YYYY-MM-DD)'
    )
    create_time_end = django_filters.DateTimeFilter(
        field_name='login_time',
        lookup_expr='lte',
        input_formats=['%Y-%m-%d', '%Y-%m-%d %H:%M:%S'],
        label='结束日期 (YYYY-MM-DD)'
    )

    # 添加排序参数
    ordering = django_filters.OrderingFilter(
        fields=(
            ('login_time', 'login_time'),
            ('logout_time', 'logout_time'),
            ('traffic_vol_bytes', 'traffic_vol_bytes'),
        )
    )

    class Meta:
        model = DyvpnMonitor
        fields = ['vpn_account', 'region', 'device_name', 'username', 'nickname', 'remark', 'online', 'login_time']

    def filter_online(self, queryset, name, value):
        if value:  # 在线
            return queryset.filter(logout_time__isnull=True)
        else:  # 离线
            return queryset.filter(logout_time__isnull=False)
        return queryset



class DyvpnDeviceFilter(django_filters.FilterSet):
    device_name = django_filters.CharFilter(field_name='device_name', lookup_expr='icontains')
    device_number = django_filters.CharFilter(field_name='device_number')
    device_type = django_filters.NumberFilter(field_name='device_type')
    serial_number = django_filters.CharFilter(field_name='serial_number', lookup_expr='icontains')
    mac_address = django_filters.CharFilter(field_name='mac_address', lookup_expr='icontains')
    used = django_filters.BooleanFilter(field_name='used')

    create_time_start = django_filters.DateTimeFilter(
        field_name='create_time',
        lookup_expr='gte',
        input_formats=['%Y-%m-%d', '%Y-%m-%d %H:%M:%S'],
        label='开始日期 (YYYY-MM-DD)'
    )
    create_time_end = django_filters.DateTimeFilter(
        field_name='create_time',
        lookup_expr='lte',
        input_formats=['%Y-%m-%d', '%Y-%m-%d %H:%M:%S'],
        label='结束日期 (YYYY-MM-DD)'
    )

    class Meta:
        model = DyvpnDeviceModel
        fields = ['device_name', 'device_number', 'device_type', 'serial_number', 'mac_address', 'used', 'create_time']


class DyvpnRegionFilter(django_filters.FilterSet):
    region = django_filters.CharFilter(field_name='region', lookup_expr='icontains')
    region_code = django_filters.CharFilter(field_name='region_code', lookup_expr='icontains')
    used = django_filters.BooleanFilter(field_name='used')
    # 防火墙设备编号
    device_number = django_filters.CharFilter(field_name='device__device_number', lookup_expr='icontains')
    # VPN设备编号
    vpn_device_number = django_filters.CharFilter(field_name='vpn_device__device_number', lookup_expr='icontains')

    create_time_start = django_filters.DateTimeFilter(
        field_name='create_time',
        lookup_expr='gte',
        input_formats=['%Y-%m-%d', '%Y-%m-%d %H:%M:%S'],
        label='开始日期 (YYYY-MM-DD)'
    )
    create_time_end = django_filters.DateTimeFilter(
        field_name='create_time',
        lookup_expr='lte',
        input_formats=['%Y-%m-%d', '%Y-%m-%d %H:%M:%S'],
        label='结束日期 (YYYY-MM-DD)'
    )

    class Meta:
        model = DyvpnRegionModel
        fields = ['region', 'region_code', 'device_number', 'vpn_device_number', 'used', 'create_time']
