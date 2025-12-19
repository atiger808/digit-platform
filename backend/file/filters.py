# -*- coding: utf-8 -*-
# @File   :filters.py
# @Time   :2025/4/29 14:29
# @Author :admin

import django_filters
from django_filters import rest_framework as filters
from .models import UserFileAccess


class FileFilter(filters.FilterSet):
    original_filename = django_filters.CharFilter(field_name='original_filename', lookup_expr='icontains')
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
        model = UserFileAccess
        fields = ['original_filename', 'create_time']


class UserFileAccessFilter(django_filters.FilterSet):
    original_filename = django_filters.CharFilter(field_name='original_filename', lookup_expr='icontains')
    description = django_filters.CharFilter(field_name='description', lookup_expr='icontains')
    os = django_filters.CharFilter(field_name='os', lookup_expr='icontains')
    real_name = django_filters.CharFilter(field_name='user__real_name', lookup_expr='icontains')
    username = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    ext = django_filters.CharFilter(field_name='uploaded_file__ext', lookup_expr='icontains')
    status = django_filters.BooleanFilter(field_name='uploaded_file__completed')

    create_time_start = django_filters.DateFilter(
        field_name='create_time',
        lookup_expr='gte',
        input_formats=['%Y-%m-%d', '%Y-%m-%d %H:%M:%S'],
        label='开始日期 (YYYY-MM-DD)'
    )
    create_time_end = django_filters.DateFilter(
        field_name='create_time',
        lookup_expr='lte',
        input_formats=['%Y-%m-%d', '%Y-%m-%d %H:%M:%S'],
        label='结束日期 (YYYY-MM-DD)'
    )
    min_size = django_filters.NumberFilter(
        field_name='uploaded_file__file_size',
        lookup_expr='gte',
        label='最小文件大小 (bytes)'
    )
    max_size = django_filters.NumberFilter(
        field_name='uploaded_file__file_size',
        lookup_expr='lte',
        label='最大文件大小 (bytes)'
    )

    class Meta:
        model = UserFileAccess
        fields = ['original_filename', 'description', 'os', 'real_name', 'username', 'ext', 'status']

