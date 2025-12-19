from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save

class Department(models.Model):
    name = models.CharField(max_length=50, verbose_name="部门名称")
    code = models.CharField(max_length=50, unique=True, verbose_name="部门编码")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, verbose_name="上级部门")
    status = models.BooleanField(default=True, verbose_name="状态")
    sort = models.IntegerField(default=0, verbose_name="排序")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "部门"
        verbose_name_plural = verbose_name
        # permissions = [
        #     ('add_department', 'Can add department'),
        #     ('change_department', 'Can change department'),
        #     ('delete_department', 'Can delete department'),
        # ]

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=50, verbose_name="角色名称")
    code = models.CharField(max_length=50, unique=True, verbose_name="角色编码")
    status = models.BooleanField(default=True, verbose_name="状态")
    sort = models.IntegerField(default=0, verbose_name="排序")
    menus = models.ManyToManyField(
        'Menu',
        blank=True,
        verbose_name="菜单权限",
        related_name="roles",
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "角色"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name



class Menu(models.Model):
    MENU_TYPE_CHOICES = (
        (0, '目录'),
        (1, '菜单'),
        (2, '按钮'),
    )

    name = models.CharField(max_length=50, verbose_name="菜单名称")
    code = models.CharField(max_length=50, verbose_name="菜单编码")
    type = models.IntegerField(choices=MENU_TYPE_CHOICES, default=0, verbose_name="菜单类型")
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',  # 关键点：定义反向关系名称
        verbose_name="上级菜单"
    )
    path = models.CharField(max_length=200, null=True, blank=True, verbose_name="路由地址")
    component = models.CharField(max_length=200, null=True, blank=True, verbose_name="组件路径")
    permission = models.CharField(max_length=200, null=True, blank=True, verbose_name="权限标识")
    icon = models.CharField(max_length=50, null=True, blank=True, verbose_name="图标")
    status = models.BooleanField(default=True, verbose_name="状态")
    sort = models.IntegerField(default=0, verbose_name="排序")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "菜单"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class User(AbstractUser):
    GENDER_CHOICES = (
        (0, '未知'),
        (1, '男'),
        (2, '女'),
    )

    username = models.CharField(max_length=50, unique=True, verbose_name="用户名", db_index=True)
    real_name = models.CharField(max_length=50, null=True, blank=True, verbose_name="真实姓名", db_index=True)
    avatar = models.CharField(max_length=255, null=True, blank=True, verbose_name="头像")
    # avatar = models.ImageField(upload_to='avatars/', null=True, blank=True,verbose_name="头像")
    gender = models.IntegerField(choices=GENDER_CHOICES, default=0, verbose_name="性别")
    email = models.EmailField(null=True, blank=True, verbose_name="邮箱")
    mobile = models.CharField(max_length=11,  null=True, blank=True, verbose_name="手机号", db_index=True)
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="部门")
    roles = models.ManyToManyField(Role, blank=True, verbose_name="角色")
    is_active = models.BooleanField(default=True, verbose_name="状态") # 是否激活

    is_superuser = models.BooleanField(default=False, verbose_name="是否是超级管理员")
    is_staff = models.BooleanField(default=False, verbose_name="是否是员工")

    require_captcha = models.BooleanField(default=False, verbose_name="是否需要验证码")
    last_login_time = models.DateTimeField(null=True, blank=True, verbose_name="上次登录时间")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name
        ordering = ['-create_time']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['real_name']),
            models.Index(fields=['mobile']),
            models.Index(fields=['is_active']),
            models.Index(fields=['department']),
            # 复合索引
            models.Index(fields=['username', 'is_active']),
        ]

        permissions = [
            ("add_user", "可以添加用户"),
            ("view_user", "可以查看用户"),
            ("change_user", "可以修改用户"),
            ("delete_user", "可以删除用户"),
            ("assign_role", "可以分配角色"),
            ("assign_department", "可以分配部门"),
        ]
        default_permissions = []

        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['username'],
        #         name='unique_username'
        #     ),
        #     models.UniqueConstraint(
        #         fields=['email'],
        #         name='unique_email'
        #     ),
        #     models.UniqueConstraint(
        #         fields=['mobile'],
        #         name='unique_mobile'
        #     )
        # ]

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.real_name or self.username

    def get_short_name(self):
        return self.real_name or self.username

    @property
    def profile(self):
        return self



class Product(models.Model):
    STATUS_CHOICES = (
        (0, '下架'),
        (1, '上架'),
    )

    name = models.CharField(max_length=100, verbose_name="商品名称")
    code = models.CharField(max_length=50, unique=True, verbose_name="商品编码")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="成本")
    stock = models.IntegerField(default=0, verbose_name="库存")
    description = models.TextField(null=True, blank=True, verbose_name="描述")
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="状态")
    sort = models.IntegerField(default=0, verbose_name="排序")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "商品"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/%Y%m%d/', blank=True, verbose_name="头像")
    # 可以添加其他字段，如性别、年龄、地址等
    bio = models.TextField(max_length=500, blank=True, verbose_name="简介")
    location = models.CharField(max_length=30, blank=True, verbose_name="地址")
    birth_date = models.DateField(null=True, blank=True, verbose_name="生日")

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name


# 信号：当创建User时自动创建Profile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# 信号：当保存User时自动保存Profile
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        Profile.objects.create(user=instance)



class EmailCode(models.Model):
    email = models.EmailField(max_length=50, verbose_name="邮箱")
    code = models.CharField(max_length=6, verbose_name="验证码")
    send_time = models.DateTimeField(auto_now_add=True, verbose_name="发送时间")
    expire_time = models.DateTimeField(verbose_name="过期时间")

    class Meta:
        verbose_name = "邮箱验证码"
        verbose_name_plural = verbose_name



class CoreModel(models.Model):
    """
    核心标准抽象模型模型,可直接继承使用
    增加审计字段, 覆盖字段时, 字段名称请勿修改, 必须统一审计字段名称
    """
    id = models.BigAutoField(primary_key=True, help_text="Id", verbose_name="Id")
    description = models.CharField(max_length=255, verbose_name="描述", null=True, blank=True, help_text="描述")
    creator = models.ForeignKey(to=User, related_query_name='creator_query', null=True,
                                verbose_name='创建人', help_text="创建人", on_delete=models.SET_NULL,
                                db_constraint=False, db_index=True)
    modifier = models.CharField(max_length=255, null=True, blank=True, help_text="修改人", verbose_name="修改人")
    dept_belong_id = models.CharField(max_length=255, help_text="数据归属部门", null=True, blank=True,
                                      verbose_name="数据归属部门")
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True, help_text="修改时间",
                                           verbose_name="修改时间", db_index=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="创建时间",
                                           verbose_name="创建时间", db_index=True)

    class Meta:
        abstract = True
        verbose_name = '核心模型'
        verbose_name_plural = verbose_name




class LoginLog(CoreModel):
    LOGIN_TYPE_CHOICES = ((1, "普通登录"), (2, "扫码登录"),)

    id = models.BigAutoField(primary_key=True, help_text="Id", verbose_name="Id")
    description = models.CharField(max_length=255, verbose_name="描述", null=True, blank=True, help_text="描述")
    creator = models.ForeignKey(to=User, related_query_name='creator_query', null=True,
                                verbose_name='创建人', help_text="创建人", on_delete=models.SET_NULL,
                                db_constraint=False, db_index=True)

    username = models.CharField(max_length=32, verbose_name="登录用户名", null=True, blank=True, help_text="登录用户名", db_index=True)
    ip = models.CharField(max_length=50, verbose_name="登录ip", null=True, blank=True, help_text="登录ip", db_index=True)
    agent = models.TextField(verbose_name="agent信息", null=True, blank=True, help_text="agent信息")
    browser = models.CharField(max_length=200, verbose_name="浏览器名", null=True, blank=True, help_text="浏览器名", db_index=True)
    os = models.CharField(max_length=200, verbose_name="操作系统", null=True, blank=True, help_text="操作系统", db_index=True)
    continent = models.CharField(max_length=50, verbose_name="州", null=True, blank=True, help_text="洲", db_index=True)
    country = models.CharField(max_length=50, verbose_name="国家", null=True, blank=True, help_text="国家", db_index=True)
    province = models.CharField(max_length=50, verbose_name="省份", null=True, blank=True, help_text="省份", db_index=True)
    city = models.CharField(max_length=50, verbose_name="城市", null=True, blank=True, help_text="城市", db_index=True)
    district = models.CharField(max_length=50, verbose_name="县区", null=True, blank=True, help_text="县区", db_index=True)
    isp = models.CharField(max_length=50, verbose_name="运营商", null=True, blank=True, help_text="运营商", db_index=True)
    area_code = models.CharField(max_length=50, verbose_name="区域代码", null=True, blank=True, help_text="区域代码", db_index=True)
    country_english = models.CharField(max_length=50, verbose_name="英文全称", null=True, blank=True,
                                       help_text="英文全称", db_index=True)
    country_code = models.CharField(max_length=50, verbose_name="简称", null=True, blank=True, help_text="简称", db_index=True)
    longitude = models.CharField(max_length=50, verbose_name="经度", null=True, blank=True, help_text="经度")
    latitude = models.CharField(max_length=50, verbose_name="纬度", null=True, blank=True, help_text="纬度")
    login_type = models.IntegerField(default=1, choices=LOGIN_TYPE_CHOICES, verbose_name="登录类型",
                                     help_text="登录类型", db_index=True)

    class Meta:
        db_table = "login_log"
        verbose_name = "登录日志"
        verbose_name_plural = verbose_name
        ordering = ("-create_time",)
        indexes = [
            models.Index(fields=['create_time']),
            models.Index(fields=['creator', 'create_time']),
            models.Index(fields=['username', 'create_time']),
            models.Index(fields=['ip', 'create_time']),
            models.Index(fields=['os', 'create_time']),
            models.Index(fields=['country', 'province', 'city']),
            models.Index(fields=['login_type', 'create_time']),
            # 复合索引优化常见查询
            models.Index(fields=['creator', 'create_time', 'username']),
            models.Index(fields=['ip', 'create_time', 'username']),
        ]


class OperationLog(CoreModel):
    request_modular = models.CharField(max_length=64, verbose_name="请求模块", null=True, blank=True,
                                       help_text="请求模块", db_index=True)
    request_path = models.CharField(max_length=400, verbose_name="请求地址", null=True, blank=True,
                                    help_text="请求地址")
    request_body = models.TextField(verbose_name="请求参数", null=True, blank=True, help_text="请求参数")
    request_method = models.CharField(max_length=8, verbose_name="请求方式", null=True, blank=True,
                                      help_text="请求方式", db_index=True)
    request_msg = models.TextField(verbose_name="操作说明", null=True, blank=True, help_text="操作说明")
    request_ip = models.CharField(max_length=50, verbose_name="请求ip地址", null=True, blank=True,
                                  help_text="请求ip地址", db_index=True)
    request_browser = models.CharField(max_length=64, verbose_name="请求浏览器", null=True, blank=True,
                                       help_text="请求浏览器", db_index=True)
    response_code = models.CharField(max_length=64, verbose_name="响应状态码", null=True, blank=True,
                                     help_text="响应状态码", db_index=True)
    request_os = models.CharField(max_length=64, verbose_name="操作系统", null=True, blank=True, help_text="操作系统", db_index=True)
    json_result = models.TextField(verbose_name="返回信息", null=True, blank=True, help_text="返回信息")
    status = models.BooleanField(default=False, verbose_name="响应状态", help_text="响应状态", db_index=True)

    class Meta:
        db_table = "operation_log"
        verbose_name = "操作日志"
        verbose_name_plural = verbose_name
        ordering = ("-create_time",)
        indexes = [
            models.Index(fields=['create_time']),
            models.Index(fields=['creator', 'create_time']),
            models.Index(fields=['status', 'create_time']),
            models.Index(fields=['request_modular', 'create_time']),
            models.Index(fields=['creator', 'status']),
            # 复合索引优化常见查询
            models.Index(fields=['creator', 'create_time', 'status']),
        ]


