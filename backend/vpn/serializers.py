# -*- coding: utf-8 -*-
# @File   :serializers.py
# @Time   :2025/5/26 17:08
# @Author :admin
import datetime
import os.path
from loguru import logger

from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from .models import DyvpnAccount, DyvpnDeviceModel, DyvpnRegionModel, DyvpnMonitor
from utils.vpn_fortigate import FgtManager


class VpnAccountSerializer(serializers.ModelSerializer):
    # --- 反序列化字段 (用于创建/更新) ---
    device_id = serializers.IntegerField(required=True)
    region_id = serializers.IntegerField(required=True)

    # --- 序列化字段 (用于展示) ---
    # 使用 source 直接从预加载的关联对象获取数据，避免 N+1 和 SerializerMethodField
    device = serializers.CharField(source='device.device_name', read_only=True)
    region = serializers.CharField(source='region.region', read_only=True)
    region_code = serializers.CharField(source='region.region_code', read_only=True)

    # 对于需要计算或处理的字段，保留 SerializerMethodField
    logo = serializers.SerializerMethodField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)  # user 也已预加载
    # 注意：gateway_address 和 gateway_port 的 source 不能直接这样写，因为需要处理字符串
    # 所以这两个仍然使用 SerializerMethodField，但因为关联对象已加载，不会产生额外查询
    gateway_address = serializers.SerializerMethodField(read_only=True)
    gateway_port = serializers.SerializerMethodField(read_only=True)

    # 可读写字段
    nickname = serializers.CharField(required=False, allow_blank=True, max_length=20)
    remark = serializers.CharField(required=False, allow_blank=True, max_length=200)
    recommender = serializers.CharField(required=False, allow_blank=True, max_length=50)
    organization_name = serializers.CharField(required=False, allow_blank=True, max_length=50)
    organization_address = serializers.CharField(required=False, allow_blank=True, max_length=50)
    contact = serializers.CharField(required=False, allow_blank=True, max_length=50)
    contact_phone = serializers.CharField(required=False, allow_blank=True, max_length=50)
    """
    关键总结：永远不要对需要写入的字段使用 SerializerMethodField，它设计为只读。改用普通字段类型（如 CharField、IntegerField）才能使前端数据传递到后端。
    """

    class Meta:
        model = DyvpnAccount
        fields = (
            'id', 'vpn_account', 'vpn_pwd', 'nickname', 'online', 'device_id', 'region_id', 'device', 'region',
            'region_code', 'logo', 'username',
            'gateway_address', 'gateway_port', 'used', 'expire_time', 'update_time', 'create_time', 'remark',
            'industry_type', 'recommender', 'organization_name', 'organization_address', 'contact', 'contact_phone')

    def get_logo(self, obj):
        return os.path.join(settings.BASE_URL, 'media', 'images',
                            f'{obj.region.region_code}.png') if obj.region else '#'

    def get_gateway_address(self, obj):
        return obj.device.vpn_server.rsplit(':', 1)[0].strip('https://').strip('http://').strip('www.')

    def get_gateway_port(self, obj):
        return obj.device.vpn_server.rsplit(':', 1)[-1]

    def validate(self, attrs):
        device_id = attrs.get('device_id')
        region_id = attrs.get('region_id')

        if device_id:
            exists_device = DyvpnDeviceModel.objects.filter(id=device_id).first()
            if not exists_device:
                raise serializers.ValidationError({'error': '设备不存在'})
            if not exists_device.used:
                raise serializers.ValidationError({'error': '设备已禁用'})

        if region_id:
            exists_region = DyvpnRegionModel.objects.filter(id=region_id).first()
            if not exists_region:
                raise serializers.ValidationError({'error': '区域不存在'})
            if not exists_region.used:
                raise serializers.ValidationError({'error': '区域已禁用'})

        if 'vpn_pwd' in attrs:
            if len(attrs['vpn_pwd']) < 4:
                raise serializers.ValidationError({'error': '密码长度不能小于4位'})
            if len(attrs['vpn_pwd']) > 20:
                raise serializers.ValidationError({'error': '密码长度不能大于20位'})

        if 'vpn_account' in attrs:
            if len(attrs['vpn_account']) < 4:
                raise serializers.ValidationError({'error': '账号长度不能小于4位'})
            if len(attrs['vpn_account']) > 20:
                raise serializers.ValidationError({'error': '账号长度不能大于20位'})

        # if 'nickname' in attrs:
        #     if len(attrs['nickname']) < 2:
        #         raise serializers.ValidationError({'error': '昵称长度不能小于2位'})
        #     if len(attrs['nickname']) > 20:
        #         raise serializers.ValidationError({'error': '昵称长度不能大于20位'})
        #
        # if 'remark' in attrs:
        #     if len(attrs['remark']) > 200:
        #         raise serializers.ValidationError({'error': '备注长度不能大于200位'})

        return attrs

    def create(self, validated_data):
        # 从请求上下文中获取当前用户
        user = self.context['request'].user
        # 确保用户已经登录
        if not user.is_authenticated:
            logger.error('用户未登录')
            raise serializers.ValidationError({'error': '用户未登录'})
        # 自动关联当前用户
        validated_data['user'] = user

        vpn_account = validated_data.get('vpn_account')
        vpn_pwd = validated_data.get('vpn_pwd')
        used = validated_data.get('used')
        if vpn_account and DyvpnAccount.objects.filter(is_delete=False).filter(vpn_account=vpn_account).exists():
            logger.error(f'Admin: {user} VPN账号已存在 {vpn_account}')
            raise serializers.ValidationError({'error': 'VPN账号已存在'})

        device_id = validated_data.pop('device_id')
        region_id = validated_data.pop('region_id')

        if region_id:
            region = DyvpnRegionModel.objects.get(id=region_id)
            validated_data['region'] = region

        if device_id:
            device = DyvpnDeviceModel.objects.get(id=device_id)
            validated_data['device'] = device

        fgtm = FgtManager(host=device.route_url, username=device.account, password=device.password)
        is_success = fgtm.add_user(vpn_account, vpn_password=vpn_pwd)
        if not is_success:
            logger.error(f'Admin: {user} VPN账号添加失败 {vpn_account}')
            raise serializers.ValidationError({'error': 'VPN账号添加失败'})
        is_success = fgtm.add_user_to_group(vpn_account, group_name=region.group_code)
        if not is_success:
            logger.error(f'Admin: {user} VPN账号添加区域失败 {vpn_account}')
            raise serializers.ValidationError({'error': 'VPN账号添加区域失败'})
        if not used:
            is_success = fgtm.disable_user(vpn_account)
            if not is_success:
                logger.error(f'Admin: {user} VPN账号禁用失败 {vpn_account}')
                raise serializers.ValidationError({'error': 'VPN账号禁用失败'})
        if region_id:
            region.online_num += 1
            region.save()
        return super().create(validated_data)

    def update(self, instance, validated_data):

        user = self.context['request'].user

        logger.info(f'Admin: {user} 修改VPN账号 {instance.vpn_account}')

        # 更新时保持用户不变
        validated_data.pop('user', None)

        vpn_account = validated_data.get('vpn_account')
        vpn_pwd = validated_data.get('vpn_pwd')
        used = validated_data.get('used')

        device_id = validated_data.pop('device_id')
        region_id = validated_data.pop('region_id')

        if vpn_account != self.instance.vpn_account:
            raise serializers.ValidationError({'error': '账号名称不能修改'})

        if device_id:
            device = DyvpnDeviceModel.objects.get(id=device_id)
            validated_data['device'] = device
        if region_id:
            region = DyvpnRegionModel.objects.get(id=region_id)
            validated_data['region'] = region

        if device_id != instance.device.id:
            logger.info(f'Admin: {user} 修改设备：{instance.device.device_name} -> {device.device_name}')
            fgtm = FgtManager(host=device.route_url, username=device.account, password=device.password)
            is_success = fgtm.delete_user(vpn_account, group_list=[instance.region.group_code])
            if not is_success:
                logger.error(f'Admin: {user} 修改设备：{instance.device.device_name} -> {device.device_name} 失败')
                raise serializers.ValidationError({'error': 'VPN账号修改设备失败'})
        else:
            fgtm = FgtManager(host=instance.device.route_url, username=instance.device.account,
                              password=device.password)

        if vpn_pwd != instance.vpn_pwd:
            logger.info(f'Admin: {user} 修改密码：{vpn_account}')
            is_success = fgtm.edit_user(vpn_account, vpn_password=vpn_pwd)
            if not is_success:
                logger.error(f'Admin: {user} 修改密码：{vpn_account} 失败')
                raise serializers.ValidationError({'error': 'VPN账号密码修改失败'})

        if region_id != instance.region.id:
            old_region = instance.region
            new_region = region
            logger.info(f'Admin: {user} 修改区域：{instance.region.region} -> {region.region}')
            is_success = fgtm.add_user_to_group(vpn_account, group_name=region.group_code)
            if not is_success:
                logger.error(f'Admin: {user} 修改区域：{instance.region.region} -> {region.region} 失败')
                raise serializers.ValidationError({'error': 'VPN账号区域修改区域失败'})

            new_region.online_num += 1
            new_region.save()

            is_success = fgtm.remove_user_from_group(vpn_account, group_name=instance.region.group_code)
            if not is_success:
                logger.error(f'Admin: {user} 移除旧区域：{instance.region.region} 失败')
                raise serializers.ValidationError({'error': 'VPN账号移除旧区域失败'})

            old_region.online_num -= 1
            old_region.save()

        if instance.used != used:
            logger.info(f'Admin: {user} 修改状态：{instance.used} -> {validated_data.get("used")}')
            if used:
                is_success = fgtm.enable_user(vpn_account)
                if not is_success:
                    logger.error(f'Admin: {user} 修改状态：{instance.used} -> {validated_data.get("used")} 启用失败')
                    raise serializers.ValidationError({'error': 'VPN账号启用失败'})
            else:
                is_success = fgtm.disable_user(vpn_account)
                if not is_success:
                    logger.error(f'Admin: {user} 修改状态：{instance.used} -> {validated_data.get("used")} 禁用失败')
                    raise serializers.ValidationError({'error': 'VPN账号禁用失败'})

        return super().update(instance, validated_data)


class ApiVPNRegionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DyvpnRegionModel
        fields = (
            'id', 'region', 'region_code', 'used'
        )


class ApiVPNAccountSerializer(serializers.ModelSerializer):
    region = serializers.CharField(source='region.region', read_only=True)
    region_code = serializers.CharField(source='region.region_code', read_only=True)

    gateway_address = serializers.SerializerMethodField()
    gateway_port = serializers.SerializerMethodField()

    class Meta:
        model = DyvpnAccount
        fields = ['vpn_account', 'vpn_pwd', 'used', 'region', 'region_code', 'gateway_address', 'gateway_port',
                  'expire_time']
        read_only_fields = fields

    def get_gateway_address(self, obj):
        return obj.device.vpn_server.rsplit(':', 1)[0].strip('https://').strip('http://').strip('www.')

    def get_gateway_port(self, obj):
        return obj.device.vpn_server.rsplit(':', 1)[-1]


class ApiCreateApiVPNAccountSerializer(serializers.Serializer):
    region_code = serializers.CharField(required=True, label='区域编码')
    expires_in = serializers.IntegerField(required=True, label='到期时间')
    user_id = serializers.CharField(required=True, label='用户')

    def validate_region_code(self, value):
        """验证地区代码是否存在且可用"""
        try:
            region = DyvpnRegionModel.objects.get(region_code=value, used=True)
            return value
        except DyvpnRegionModel.DoesNotExist:
            raise serializers.ValidationError({'error': '区域不存在或已禁用'})

    def validate(self, data):
        """验证新建数据"""
        if 'region_code' in data:
            region = DyvpnRegionModel.objects.get(region_code=data['region_code'])
            if region.device_count - region.online_num < 1:
                raise serializers.ValidationError({'error': '该区域在线数量已达上限'})
        if 'vpn_pwd' in data:
            if len(data['vpn_pwd']) < 4:
                raise serializers.ValidationError({'error': '密码长度不能小于4位'})
            if len(data['vpn_pwd']) > 20:
                raise serializers.ValidationError({'error': '密码长度不能大于20位'})
        return data

    def create(self, validated_data):
        # 获取区域和设备
        region = DyvpnRegionModel.objects.get(region_code=validated_data.get('region_code'), used=True)
        device = region.device

        # 生成VPN账号和密码
        vpn_account = DyvpnAccount.generate_vpn_account(region.region_code)
        vpn_pwd = DyvpnAccount.generate_vpn_pwd()

        # 计算过期时间
        expire_time = timezone.now() + datetime.timedelta(seconds=validated_data.get('expires_in'))

        fgtm = FgtManager(host=device.route_url, username=device.account, password=device.password)
        is_success = fgtm.add_user(vpn_account, vpn_password=vpn_pwd)
        if not is_success:
            logger.error(f'api VPN账号添加失败 {vpn_account}')
            raise serializers.ValidationError({'error': 'VPN账号添加失败'})
        is_success = fgtm.add_user_to_group(vpn_account, group_name=region.group_code)
        if not is_success:
            logger.error(f'api VPN账号添加区域失败 {vpn_account}')
            raise serializers.ValidationError({'error': 'VPN账号添加区域失败'})

        # 创建VPN账号
        vpn = DyvpnAccount.objects.create(
            region=region,
            device=device,
            vpn_account=vpn_account,
            vpn_pwd=vpn_pwd,
            nickname=validated_data.get('user_id'),
            expire_time=expire_time,
            used=True
        )

        # 更新区域在线数量
        region.online_num += 1
        region.save()

        return vpn


class ApiUpdateVPNAccountSerializer(serializers.ModelSerializer):
    region_code = serializers.CharField(required=True, label='区域编码', write_only=True)
    expires_in = serializers.IntegerField(required=True, label='到期时间', write_only=True)
    vpn_pwd = serializers.CharField(required=True, label='密码', write_only=True)

    class Meta:
        model = DyvpnAccount
        fields = ['vpn_account', 'vpn_pwd', 'region_code', 'expires_in']

    def validate_region_code(self, value):
        """验证地区代码是否存在且可用"""
        try:
            region = DyvpnRegionModel.objects.get(region_code=value, used=True)
            return value
        except DyvpnRegionModel.DoesNotExist:
            raise serializers.ValidationError({'error': '区域不存在或已禁用'})

    def validate(self, data):
        """验证更新数据"""
        if 'region_code' in data:
            region = DyvpnRegionModel.objects.get(region_code=data['region_code'])
            if region.device_count - region.online_num < 1:
                raise serializers.ValidationError({'error': '该区域在线数量已达上限'})
        if 'vpn_pwd' in data:
            if len(data['vpn_pwd']) < 6:
                raise serializers.ValidationError({'error': '密码长度不能小于6位'})
            if len(data['vpn_pwd']) > 20:
                raise serializers.ValidationError({'error': '密码长度不能大于20位'})
        return data

    def update(self, instance, validated_data):
        """处理区域变更"""
        if 'region_code' in validated_data:
            old_region = instance.region
            new_region = DyvpnRegionModel.objects.get(region_code=validated_data['region_code'])

            if old_region != new_region:
                fgtm = FgtManager(host=old_region.device.route_url, username=old_region.device.account,
                                  password=old_region.device.password)
                is_success = fgtm.remove_user_from_group(instance.vpn_account, group_name=old_region.group_code)
                if not is_success:
                    logger.error(f'API 移除旧区域：{old_region.region} 失败')
                    raise serializers.ValidationError({'error': 'VPN账号移除旧区域失败'})
                # 更新区域计数
                old_region.online_num -= 1
                old_region.save()

                if old_region.device != new_region.device:
                    fgtm = FgtManager(host=new_region.device.route_url, username=new_region.device.account,
                                      password=new_region.device.password)

                is_success = fgtm.add_user_to_group(instance.vpn_account, group_name=new_region.group_code)
                if not is_success:
                    logger.error(f'API 添加新区域：{new_region.region} 失败')
                    raise serializers.ValidationError({'error': 'VPN账号添加新区域失败'})
                # 更新区域计数
                new_region.online_num += 1
                new_region.save()

                # 更新账号区域和设备
                instance.region = new_region
                instance.device = new_region.device
                instance.save()

        # """处理密码变更"""
        if 'vpn_pwd' in validated_data:
            if validated_data.get('region_code') and instance.region.region_code != validated_data.get('region_code'):
                device = DyvpnRegionModel.objects.get(region_code=validated_data.get('region_code'))
            else:
                device = instance.device
            old_vpn_pwd = instance.vpn_pwd
            new_vpn_pwd = validated_data.get('vpn_pwd')

            if old_vpn_pwd != new_vpn_pwd:
                fgtm = FgtManager(host=device.route_url, username=device.account,
                                  password=device.password)
                is_success = fgtm.edit_user(instance.vpn_account, vpn_password=new_vpn_pwd)
                if not is_success:
                    logger.error(f'API 修改密码失败')
                    raise serializers.ValidationError({'error': 'VPN账号密码修改失败'})
                instance.vpn_pwd = new_vpn_pwd
                instance.save()

        # 处理过期时间变更
        if 'expires_in' in validated_data:
            instance.expire_time = timezone.now() + datetime.timedelta(seconds=validated_data['expires_in'])
            instance.save()

        return instance


class ApiVPNAccountDetailSerializer(ApiVPNAccountSerializer):
    class Meta(ApiVPNAccountSerializer.Meta):
        # 可以添加更多字段或覆盖父类配置
        fields = ApiVPNAccountSerializer.Meta.fields + ['nickname', 'create_time', 'online']


class VpnMonitorSerializer(serializers.ModelSerializer):
    # 直接使用关联字段，避免SerializerMethodField
    vpn_account = serializers.CharField(source='account.vpn_account', read_only=True)
    nickname = serializers.CharField(source='account.nickname', read_only=True)
    region = serializers.CharField(source='region.region', read_only=True)
    device = serializers.CharField(source='account.device.device_name', read_only=True)
    username = serializers.CharField(source='account.user.username', read_only=True)
    online = serializers.SerializerMethodField()
    online_time = serializers.SerializerMethodField()

    class Meta:
        model = DyvpnMonitor
        fields = (
            'id', 'vpn_account', 'nickname', 'region', 'device', 'username',
            'duration_secs', 'expiry_secs', 'traffic_vol_bytes', 'online_time',
            'virtual_ip', 'online', 'logout_time', 'login_time')

    def get_online(self, obj):
        return obj.logout_time is None

    def get_online_time(self, obj):
        return str(datetime.timedelta(seconds=obj.duration_secs)) if obj.duration_secs else ''


class VpnDeviceSerializer(serializers.ModelSerializer):
    device_number = serializers.CharField(required=False, allow_blank=True, max_length=50)
    device_type_name = serializers.SerializerMethodField(read_only=True)

    serial_number = serializers.CharField(required=False, allow_blank=True, max_length=50)
    mac_address = serializers.CharField(required=False, allow_blank=True, max_length=50)
    vpn_server = serializers.CharField(required=False, allow_blank=True, max_length=200)
    route_url = serializers.CharField(required=False, allow_blank=True, max_length=200)
    account = serializers.CharField(required=False, allow_blank=True, max_length=50)
    password = serializers.CharField(required=False, allow_blank=True, max_length=50)


    class Meta:
        model = DyvpnDeviceModel
        fields = (
        'id', 'device_name', 'device_number', 'device_type', 'device_type_name', 'device_desc', 'serial_number',
        'mac_address', 'vpn_server', 'route_url', 'account', 'password', 'used', 'update_time', 'create_time')

    def get_device_type_name(self, obj):
        return obj.DEVICE_TYPE_CHOICES[obj.device_type - 1][1]


class VpnRegionSerializer(serializers.ModelSerializer):
    # --- 反序列化字段 (用于创建/更新) ---
    device_id = serializers.IntegerField(required=True)
    vpn_device_id = serializers.IntegerField(required=True)

    # --- 序列化字段 (用于展示) ---
    # 使用 source 直接从预加载的关联对象获取数据，避免 SerializerMethodField
    # 这利用了 ViewSet 中 queryset 的 select_related('device')
    # 防火墙设备名称
    device = serializers.CharField(source='device.device_name', read_only=True, allow_null=True)
    # 防火墙设备编号
    device_number = serializers.CharField(source='device.device_number', read_only=True, allow_null=True)

    # VPN设备名称
    vpn_device = serializers.CharField(source='vpn_device.device_name', read_only=True, allow_null=True)
    # VPN设备编号
    vpn_device_number = serializers.CharField(source='vpn_device.device_number', read_only=True, allow_null=True)

    # 对于 logo，因为它基于模型字段计算，SerializerMethodField 是合适的
    logo = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DyvpnRegionModel
        fields = (
            'id', 'region', 'region_code', 'logo',
            'device_id', 'device', 'device_number',
            'vpn_device_id', 'vpn_device', 'vpn_device_number',
            'device_count', 'online_num', 'used',
            'update_time', 'create_time'
        )

    def get_logo(self, obj):
        return os.path.join(settings.BASE_URL, 'media', 'images', f'{obj.region_code}.png') if obj.region_code else '#'

    def validate(self, attrs):
        device_id = attrs.get('device_id')
        if device_id:
            exists_device = DyvpnDeviceModel.objects.filter(id=device_id).exists()
            if not exists_device:
                raise serializers.ValidationError('防火墙设备不存在')

        vpn_device_id = attrs.get('vpn_device_id')
        if vpn_device_id:
            exists_device = DyvpnDeviceModel.objects.filter(id=vpn_device_id).exists()
            if not exists_device:
                raise serializers.ValidationError('VPN设备不存在')

        return attrs

    def create(self, validated_data):
        device_id = validated_data.pop('device_id')
        if device_id:
            device = DyvpnDeviceModel.objects.get(id=device_id)
            validated_data['device'] = device

        vpn_device_id = validated_data.pop('vpn_device_id')
        if vpn_device_id:
            vpn_device = DyvpnDeviceModel.objects.get(id=vpn_device_id)
            validated_data['vpn_device'] = vpn_device

        return super().create(validated_data)

    def update(self, instance, validated_data):
        device_id = validated_data.pop('device_id')
        if device_id:
            device = DyvpnDeviceModel.objects.get(id=device_id)
            validated_data['device'] = device

        vpn_device_id = validated_data.pop('vpn_device_id')
        if vpn_device_id:
            vpn_device = DyvpnDeviceModel.objects.get(id=vpn_device_id)
            validated_data['vpn_device'] = vpn_device

        return super().update(instance, validated_data)
