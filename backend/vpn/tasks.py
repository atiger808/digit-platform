# -*- coding: utf-8 -*-
# @File   :tasks.py
# @Time   :2025/6/2 11:07
# @Author :admin

from backend.celery_app import app
import time
import gc
from .vpn_monitor import monitor_vpn_connections, monitor_vpn_expire

# 添加一个简单的测试任务
@app.task
def vpn_expire_task():
    print("Starting VPN expiration task...")
    try:
        monitor_vpn_expire()
        return "Success"
    except Exception as e:
        print(f"VPN expiration task failed: {str(e)}")
        raise
    finally:
        gc.collect() # 手动触发垃圾回收

@app.task
def monitor_vpn_task():
    print("Starting VPN monitoring task...")
    try:
        monitor_vpn_connections()
        return "Success"
    except Exception as e:
        print(f"VPN monitoring failed: {str(e)}")
        raise
    finally:
        gc.collect() # 手动触发垃圾回收