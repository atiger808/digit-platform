from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class FileTag(models.Model):
    """文件标签"""
    name = models.CharField('标签名称', max_length=50, unique=True)
    color = models.CharField('标签颜色', max_length=7, default='#1890ff')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '文件标签'
        verbose_name_plural = '文件标签'
        ordering = ['id']

    def __str__(self):
        return self.name


class UploadedFile(models.Model):
    upload_id = models.CharField(max_length=100, unique=True, verbose_name='上传ID')
    # 添加索引提高查询效率
    file_md5 = models.CharField(max_length=32, db_index=True, verbose_name='文件MD5')
    filename = models.CharField(max_length=255, verbose_name='文件名')

    total_chunks = models.IntegerField(default=0)
    uploaded_chunks = models.IntegerField(default=0)
    file = models.FileField(upload_to='uploads/', null=True, blank=True, verbose_name='文件')

    completed = models.BooleanField(default=False, verbose_name='是否完成')

    ext = models.CharField(max_length=10, verbose_name='文件扩展名')
    file_size = models.BigIntegerField(default=0, verbose_name='文件大小(字节)', db_index=True)  # 新增字段

    fps = models.FloatField(max_length=5, default=0, null=True, verbose_name='帧率')
    width = models.FloatField(max_length=5, default=0, null=True, verbose_name='宽度')
    height = models.FloatField(max_length=5, default=0, null=True, verbose_name='高度')
    duration = models.FloatField(max_length=20, default=0, null=True, verbose_name='时长')
    bitrate = models.BigIntegerField(default=0, null=True, verbose_name='视频码率')
    audio_bitrate = models.BigIntegerField(default=0, null=True, verbose_name='音频码率')
    ar_sample_rate = models.BigIntegerField(default=0, null=True, verbose_name='音频采样率')
    vcodec_type = models.CharField(max_length=10, default='', null=True, verbose_name='视频编码')
    acodec_type = models.CharField(max_length=10, default='', null=True, verbose_name='音频编码')

    description = models.TextField(verbose_name='描述', default='', null=True, blank=True)
    download_count = models.IntegerField(default=0, null=True, verbose_name='下载次数')

    tags = models.ManyToManyField(FileTag, blank=True, verbose_name='标签')

    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')



    class Meta:
        verbose_name = '文件资料'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.file_md5

    def save(self, *args, **kwargs):
        # 自动提取文件扩展名·
        if self.filename and not self.ext:
            self.ext = self.filename.split('.')[-1].lower()

        # 自动计算文件大小
        if self.file and not self.file_size:
            self.file_size = self.file.size

        super().save(*args, **kwargs)


class UserFileAccess(models.Model):
    """记录用户对文件的访问权限"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, verbose_name='上传文件')
    original_filename = models.CharField(max_length=255, verbose_name='原始文件名')
    description = models.TextField('素材描述', default='', blank=True, null=True)

    os = models.CharField(default='', max_length=50, verbose_name='操作系统', null=True, blank=True)



    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        unique_together = ('user', 'uploaded_file')
        verbose_name = '用户可访问文件'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.original_filename


class DownloadRecord(models.Model):
    """记录用户下载记录"""

    STATUS_CHOICES = [
        ('started', 'Started'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('interrupted', 'Interrupted'),
        ('failed', 'Failed')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, verbose_name='上传文件')
    ip_address = models.GenericIPAddressField(verbose_name='IP地址', null=True, blank=True)
    user_agent = models.CharField(max_length=255, verbose_name='用户agent信息', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    original_filename = models.CharField(max_length=255, verbose_name='原始文件名')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '用户下载记录'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.original_filename
