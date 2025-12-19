# -*- coding: utf-8 -*-
# @File   :celery.py
# @Time   :2025/6/2 11:07
# @Author :admin

from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

# 设置默认的 Django 设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# 创建 Celery 应用实例
app = Celery('backend')

# 使用 Django 的设置文件配置 Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现所有 Django 应用中的 tasks.py
app.autodiscover_tasks()
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)



# # 设置定时任务
# app.conf.beat_schedule = {
#     'monitor-vpn-every-minute': {
#         'task': 'vpn.tasks.monitor_vpn_task',
#         'schedule': 5.0,  # 每5秒执行一次
#     },
# }