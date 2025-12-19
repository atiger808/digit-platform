from django.db import models
from django.utils import timezone
from user.models import User
import datetime
import uuid
import random
import string

class DyvpnDeviceModel(models.Model):

    DEVICE_TYPE_CHOICES = (
        (1, '路由器'),
        (2, '交换机'),
        (3, '防火墙'),
        (4, 'VPN'),
        (5, '服务器'),
        (6, 'PC'),
        (7, '移动终端'),
        (8, '其他'),
    )

    id = models.AutoField(primary_key=True)
    device_name = models.CharField(default='', max_length=50, null=True, verbose_name='设备名称')

    # 设备编号
    device_number = models.CharField(default='', max_length=50, null=True, verbose_name='设备编号')
    # 设备类型
    device_type = models.IntegerField(default=3, choices=DEVICE_TYPE_CHOICES, null=True, verbose_name='设备类型', db_index=True)
    # 设备描述
    device_desc = models.TextField(default='', null=True, verbose_name='设备描述')

    serial_number = models.CharField(default='', max_length=50, null=True, verbose_name='设备序列号')
    mac_address = models.CharField(default='', max_length=50, null=True, verbose_name='MAC地址')
    vpn_server = models.CharField(default='', max_length=200, null=True, verbose_name='VPN服务器地址')
    route_url = models.CharField(default='', max_length=200, null=True, verbose_name='路由地址')
    account = models.CharField(default='', max_length=50, null=True, verbose_name='管理员账号')
    password = models.CharField(default='', max_length=50, null=True, verbose_name='管理员密码')
    cookie = models.TextField(default='', null=True)
    used = models.BooleanField(default=False, null=True, verbose_name='设备状态')  # 设备是否启用
    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '设备'
        verbose_name_plural = verbose_name
        # 排序
        ordering = ['-create_time']
        indexes = [
            models.Index(fields=['device_name']),
            models.Index(fields=['account']),
            models.Index(fields=['used']),
            models.Index(fields=['device_type']),
        ]

    def __str__(self):
        return self.device_name


class DyvpnRegionModel(models.Model):
    """
    sslvpn 区域表
    区域代码：
        1：日本JP，2：新加坡SG，3：台湾TWN，4：韩国KOR，5：印尼IDN，
        6：马来西亚MAS，7：泰国THA，8：英国UK，9：德国GER，10：美国US
    """
    id = models.AutoField(primary_key=True)
    device = models.ForeignKey(DyvpnDeviceModel, on_delete=models.CASCADE, null=True, verbose_name='防火墙设备', related_name='device')
    # VPN设备
    vpn_device = models.ForeignKey (DyvpnDeviceModel, on_delete=models.CASCADE, null=True, verbose_name='VPN设备', related_name='vpn_device')
    region = models.CharField(default='', max_length=50, null=True, verbose_name='区域')
    region_code = models.CharField(default='', max_length=50, null=True, verbose_name='区域代码')
    device_count = models.IntegerField(default=1000, null=True, verbose_name='终端数量上限')  # 终端数量
    online_num = models.IntegerField(default=0, null=True, verbose_name='当前数量')  # 在线数量
    used = models.BooleanField(default=False, null=True, verbose_name='是否可用')   # 是否可用
    group_code = models.CharField(default='', max_length=50, null=True, verbose_name='分组代码')

    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')
    create_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '区域'
        verbose_name_plural = verbose_name
        # 排序
        ordering = ['-create_time']
        indexes = [
            models.Index(fields=['region']),
            models.Index(fields=['region_code']),
            models.Index(fields=['device']),
        ]

    def save(self, *args, **kwargs):
        if self.region_code and not self.group_code:
            self.group_code = self.region_code
        super().save(*args, **kwargs)

    def __str__(self):
        return self.region


class DyvpnAccount(models.Model):
    """
    sslvpn 账号表
    """
    # 行业类型
    INDUSTRY_TYPE_CHOICES = [
        (1, '个人'),
        (2, '企业'),
        (3, '政府'),
        (4, '教育'),
        (5, '金融'),
        (6, '医疗'),
        (7, '保险'),
        (8, '科技'),
        (9, '游戏'),
        (10, '旅游'),
        (11, '互联网'),
        (12, '其他')
    ]

    id = models.AutoField(primary_key=True)
    region = models.ForeignKey(DyvpnRegionModel, on_delete=models.CASCADE, null=True, verbose_name='区域')
    device = models.ForeignKey(DyvpnDeviceModel, on_delete=models.CASCADE, null=True, verbose_name='设备')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name='用户')

    vpn_account = models.CharField(default='', unique=True, max_length=50, null=True)
    vpn_pwd = models.CharField(default='', max_length=50, null=True)

    nickname = models.CharField(default='', max_length=50, null=True)

    used = models.BooleanField(default=True, null=True, verbose_name='使用状态')
    is_delete = models.BooleanField(default=False, null=True, verbose_name='删除状态')
    online = models.BooleanField(default=False, null=True, verbose_name='在线状态')
    count = models.IntegerField(default=1, null=True)  # 可用设备数量

    # 行业类型
    industry_type = models.IntegerField(default=1, choices=INDUSTRY_TYPE_CHOICES, null=True, verbose_name='行业类型', db_index=True)
    # 推荐人
    recommender = models.CharField(default='', max_length=50, null=True, verbose_name='推荐人')
    # 机构名称
    organization_name = models.CharField(default='', max_length=50, null=True, verbose_name='机构名称')
    # 机构地址
    organization_address = models.CharField(default='', max_length=50, null=True, verbose_name='机构地址')
    # 联系人
    contact = models.CharField(default='', max_length=50, null=True, verbose_name='联系人')
    # 联系方式
    contact_phone = models.CharField(default='', max_length=50, null=True, verbose_name='联系方式')


    expire_time = models.DateTimeField(null=True, verbose_name='到期时间')  # 到期时间
    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')
    create_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')

    remark = models.TextField(default='', null=True, verbose_name='备注')

    class Meta:
        verbose_name = '账号'
        # 排序
        ordering = ['-create_time']
        indexes = [
            models.Index(fields=['vpn_account']),
            models.Index(fields=['nickname']),
            models.Index(fields=['online']),
            models.Index(fields=['user']),
            models.Index(fields=['region']),
        ]

    def __str__(self):
        return self.vpn_account

    def get_online_status(self):
        """获取账号在线状态"""
        if not self.online:
            return "离线"

        # 检查是否有未结束的会话
        active_session = DyvpnMonitor.objects.filter(
            account=self,
            logout_time__isnull=True
        ).exists()

        # 如果数据库状态与实际会话不一致，修正状态
        if self.online != active_session:
            self.online = active_session
            self.save()

        return "在线" if active_session else "离线"

    @classmethod
    def generate_vpn_account(cls, region_code):
        """生成账号"""
        return f'{region_code.lower()}-{uuid.uuid4().hex[:8]}'

    @classmethod
    def generate_vpn_pwd(cls, length=12):
        """生成密码"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


class DyvpnMonitor(models.Model):
    id = models.AutoField(primary_key=True)
    account = models.ForeignKey(DyvpnAccount, on_delete=models.CASCADE, null=True, verbose_name='账号')
    region = models.ForeignKey(DyvpnRegionModel, on_delete=models.CASCADE, null=True, verbose_name='区域')
    duration_secs = models.BigIntegerField(default=0, null=True, verbose_name='在线时长(秒)')
    expiry_secs = models.BigIntegerField(default=0, null=True, verbose_name='到期时间')
    online_time = models.CharField(default='', max_length=50, null=True, verbose_name='在线时长')
    virtual_ip = models.CharField(default='', max_length=50, null=True, verbose_name='虚拟IP')

    login_terminal = models.CharField(default='', max_length=50, null=True, verbose_name='登录终端')
    login_ip = models.CharField(default='', max_length=50, null=True, verbose_name='登录IP')

    in_bytes = models.BigIntegerField(default=0, null=True, verbose_name='下行字节')
    out_bytes = models.BigIntegerField(default=0, null=True, verbose_name='上行字节')
    traffic_vol_bytes = models.BigIntegerField(default=0, null=True, verbose_name='流量字节数')

    down_flow = models.CharField(default='', max_length=100, null=True, verbose_name='下行流量')
    up_flow = models.CharField(default='', max_length=100, null=True, verbose_name='上行流量')
    traffic_vol_flow = models.CharField(default='', max_length=100, null=True, verbose_name='上下行流量')

    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')

    logout_time = models.DateTimeField(null=True, blank=True, verbose_name="退出时间")
    login_time = models.DateTimeField(verbose_name="登录时间")

    class Meta:
        verbose_name = 'VPN监控日志'
        verbose_name_plural = verbose_name
        ordering = ['-login_time']
        indexes = [
            # 现有索引
            models.Index(fields=['account']),
            models.Index(fields=['login_time']),
            models.Index(fields=['logout_time']),

            # 新增复合索引（关键优化）
            models.Index(fields=['login_time', 'account']),
            models.Index(fields=['logout_time', 'account']),
            models.Index(fields=['account', 'login_time']),

            # 在线状态专用部分索引（PostgreSQL特有）
            models.Index(
                fields=['logout_time'],
                name='dyvpn_monitor_online_idx',
                condition=models.Q(logout_time__isnull=True)
            ),

            # 大流量查询索引
            models.Index(fields=['traffic_vol_bytes', 'login_time']),
        ]

    def  __str__(self):
        return f'{self.account.vpn_account}@{self.virtual_ip} {self.account.region.region} ({self.login_time})'

    def save(self, *args, **kwargs):
        # 只保留必要的计算逻辑
        if not self.region and self.account:
            self.region = self.account.region
        super().save(*args, **kwargs)

    def get_duration(self):
        """获取格式化后的在线时长"""
        if self.duration_secs:
            return str(datetime.timedelta(seconds=self.duration_secs))
        else:
            return "未知"
    def is_active(self):
        """检查会话是否活跃"""
        return self.logout_time is None
