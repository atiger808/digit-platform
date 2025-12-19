# -*- coding: utf-8 -*-
# @File   :vpn_monitor.py
# @Time   :2025/6/2 09:04
# @Author :admin

from django.utils import timezone
from django.db import transaction
from django.db import close_old_connections
import datetime
from loguru import logger
from rest_framework.status import is_success

from utils.vpn_fortigate import FgtManager
from .models import DyvpnAccount, DyvpnRegionModel, DyvpnDeviceModel, DyvpnMonitor


def process_device(device):
    fgtm = FgtManager(host=device.route_url, username=device.account, password=device.password)
    info = fgtm.online_user()
    return info


def fech_online_vpns(device):
    """获取在线vpn账号接口数据"""
    info = process_device(device)
    if info.get('is_success') is True:
        online_vpns = info.get('online_user_list') or []
    else:
        online_vpns = None
        logger.error(f'获取设备{device}在线用户失败')
    return online_vpns


def update_vpn_connections(online_vpns, device):
    """监控VPN连接状态并更新日志"""
    online_account_names = {vpn['vpn_user'] for vpn in online_vpns}
    now = timezone.now()
    # 获取device下的所有账号的初始状态
    close_old_connections()
    all_accounts = DyvpnAccount.objects.filter(used=True, is_delete=False).filter(device=device)

    # 创建在线账号字典，用于快速查找
    online_accounts = {}
    for account in all_accounts:
        online_accounts[account.vpn_account] = account
    if online_vpns:
        logger.info(f'online_account_names: {online_account_names} 发现 {len(online_vpns)} 个在线VPN账号')

    new_monitor_objs = []
    updated_accounts = []
    updated_monitors = []

    # 处理新上线的账户
    for vpn_data in online_vpns:
        vpn_user = vpn_data.get('vpn_user')

        # 获取对应的DyvpnAccount实例
        account_instance = online_accounts.get(vpn_user)

        if not account_instance:
            logger.warning(f'未找到对应账号: {vpn_user}')
            continue
        # 更新账号在线状态（如果之前不在线）
        if not account_instance.online:
            account_instance.online = True
            account_instance.update_time = now
            updated_accounts.append(account_instance)

        in_bytes = vpn_data.get('in_bytes') or 0
        out_bytes = vpn_data.get('out_bytes') or 0
        duration_secs = vpn_data.get('duration_secs') or 0
        traffic_vol_bytes = vpn_data.get('traffic_vol_bytes') or 0
        # logger.info(f'vpn_user：{vpn_user} traffic_vol_bytes: {traffic_vol_bytes} duration_secs: {duration_secs}')
        # 检查是否已有未结束的会话
        active_session = DyvpnMonitor.objects.filter(account=account_instance, logout_time__isnull=True).first()
        if active_session:
            # 更新会话信息
            active_session.duration_secs = duration_secs
            active_session.expiry_secs = vpn_data.get('expiry_secs')
            active_session.virtual_ip = vpn_data.get('virtual_ip', '')
            active_session.login_terminal = vpn_data.get('login_terminal', '')
            active_session.login_ip = vpn_data.get('login_ip', '')
            active_session.login_time = active_session.login_time if active_session.login_time else now - datetime.timedelta(
                seconds=duration_secs)
            active_session.traffic_vol_bytes = vpn_data.get('traffic_vol_bytes')
            active_session.traffic_vol_flow = str(round(vpn_data.get('traffic_vol_bytes') / 1024 / 1024, 2)) + 'MB'
            active_session.in_bytes = vpn_data.get('in_bytes')
            active_session.out_bytes = vpn_data.get('out_bytes')
            active_session.online_time = str(datetime.timedelta(seconds=int(duration_secs)))
            active_session.update_time = now
            updated_monitors.append(active_session)
        else:
            region_instance = DyvpnRegionModel.objects.filter(device=device).filter(
                region=account_instance.region).first()
            # 创建新的会话
            new_monitor_objs.append(DyvpnMonitor(
                account=account_instance,
                region=region_instance,
                duration_secs=vpn_data.get('duration_secs'),
                expiry_secs=vpn_data.get('expiry_secs'),
                virtual_ip=vpn_data.get('virtual_ip', ''),
                login_terminal=vpn_data.get('login_terminal', ''),
                login_ip=vpn_data.get('login_ip', ''),
                login_time=now - datetime.timedelta(seconds=duration_secs),
                traffic_vol_bytes=vpn_data.get('traffic_vol_bytes'),
                traffic_vol_flow=str(round(traffic_vol_bytes / 1024 / 1024, 2)) + 'MB',
                in_bytes=vpn_data.get('in_bytes'),
                out_bytes=vpn_data.get('out_bytes'),
                down_flow=str(round(in_bytes / 1024 / 1024, 2)) + 'MB',
                up_flow=str(round(out_bytes / 1024 / 1024, 2)) + 'MB',
                online_time=str(datetime.timedelta(seconds=int(duration_secs))),
            ))

    if updated_accounts:
        logger.info(f'online updated_accounts: {updated_accounts}')
        with transaction.atomic():
            DyvpnAccount.objects.bulk_update(updated_accounts, ['online', 'update_time'])

    if updated_monitors:
        logger.info(f'online updated_monitors: {updated_monitors}')
        with transaction.atomic():
            DyvpnMonitor.objects.bulk_update(updated_monitors,
                                             ['duration_secs', 'expiry_secs', 'virtual_ip', 'login_terminal',
                                              'login_ip', 'login_time', 'traffic_vol_bytes', 'traffic_vol_flow',
                                              'in_bytes', 'out_bytes', 'down_flow', 'up_flow',
                                              'online_time', 'update_time'])

    if new_monitor_objs:
        logger.info(f'online new_monitor_objs: {new_monitor_objs} 新增 {len(new_monitor_objs)} 个VPN会话')
        with transaction.atomic():
            DyvpnMonitor.objects.bulk_create(new_monitor_objs)

    # 批量处理已下线的VPN账号
    offline_accounts = []
    updated_monitors = []

    expired_sessions = DyvpnMonitor.objects.filter(logout_time__isnull=True).exclude(
        account__vpn_account__in=online_account_names)

    for session in expired_sessions:
        session.logout_time = now

        account = session.account
        account.online = False
        account.update_time = now

        offline_accounts.append(account)
        updated_monitors.append(session)

    if offline_accounts:
        logger.info(f'offline offline_accounts: {offline_accounts}')
        DyvpnAccount.objects.bulk_update(offline_accounts, ['online', 'update_time'])

        # 更新缓存中的状态
        for account_name in offline_accounts:
            if account_name in online_accounts:
                online_accounts[account_name].online = False

    if updated_monitors:
        logger.info(f'offline updated_monitors: {updated_monitors}  退出 {len(expired_sessions)} 个VPN会话')
        with transaction.atomic():
            DyvpnMonitor.objects.bulk_update(updated_monitors, ['logout_time'])

    # 处理其他可能下线的账号（没有活动会话但状态为在线）
    # 这包括那些从未创建过会话但状态为在线的账号
    offline_accounts_from_status = set()
    for account_name, account in online_accounts.items():
        if account_name not in online_account_names and account.online:
            account.online = False
            account.update_time = now
            offline_accounts_from_status.add(account)

    if offline_accounts_from_status:
        logger.info(f"更新 {len(offline_accounts_from_status)} 个状态不一致账号为下线")
        DyvpnAccount.objects.bulk_update(list(offline_accounts_from_status), ['online', 'update_time'])

    if online_account_names or offline_accounts or offline_accounts_from_status:
        logger.info(
            f"VPN监控任务完成. 在线账号: {len(online_account_names)}, 下线账号: {len(offline_accounts or offline_accounts_from_status)}")


def monitor_vpn_connections():
    """检测vpn登录登出日志"""
    close_old_connections()
    device_list = DyvpnDeviceModel.objects.filter(used=True).filter(device_type=3)
    for device in device_list:
        online_vpns = fech_online_vpns(device)
        if online_vpns is not None:
            update_vpn_connections(online_vpns, device)
        else:
            logger.warning(f'获取设备{device.device_name}的在线VPN连接失败')


def fech_expire_vpns(device):
    now = timezone.now()
    close_old_connections()
    expire_accounts = DyvpnAccount.objects.filter(used=True, is_delete=False, expire_time__lte=now).filter(
        device=device)
    if expire_accounts.count() > 0:
        logger.info(f'设备{device.device_name} 发现 {expire_accounts.count()} 个到期VPN')
    return expire_accounts


def update_vpn_expire(expire_vpns, device):
    fgtm = FgtManager(host=device.route_url, username=device.account, password=device.password)
    for account in expire_vpns:
        is_success = fgtm.disable_user(account.vpn_account)
        if is_success:
            logger.info(
                f'设备{device.device_name}的到期VPN: {account.vpn_account} 到期时间: {account.expire_time.astimezone()} 已更新为禁用')
            account.used = False
            account.save()
        else:
            logger.warning(f'设备{device.device_name}的到期VPN: {account.vpn_account} 更新为禁用失败')


def monitor_vpn_expire():
    """检测vpn是否到期"""
    close_old_connections()
    device_list = DyvpnDeviceModel.objects.filter(used=True).filter(device_type=3)
    for device in device_list:
        expire_vpns = fech_expire_vpns(device)
        if expire_vpns is not None:
            update_vpn_expire(expire_vpns, device)
