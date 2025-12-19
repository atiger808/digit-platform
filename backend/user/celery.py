# -*- coding: utf-8 -*-
# @File   :celery.py
# @Time   :2025/5/6 13:50
# @Author :admin

from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.utils import timezone
from .models import Profile
import os

class Command(BaseCommand):
    help = '清理未使用的头像文件'

    def handle(self, *args, **options):
        # 查找所有存储在文件系统中但未被任何Profile使用的头像
        all_files = set(default_storage.listdir('avatars')[1])
        used_files = set(
            os.path.basename(p.avatar.path)
            for p in Profile.objects.exclude(avatar='')
        )

        orphans = all_files - used_files
        for filename in orphans:
            path = os.path.join('avatars', filename)
            default_storage.delete(path)
            self.stdout.write(f'Deleted orphan avatar: {path}')

