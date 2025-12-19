# -*- coding: utf-8 -*-
# @File   :captcha.py
# @Time   :2025/5/10 12:07
# @Author :admin
import os.path
import random
import string
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.cache import cache
from django.conf import settings

from loguru import logger
from django.core.cache import cache
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore

class CaptchaService:
    @staticmethod
    def generate_code(identifier, code_type, length=6, expire=5):
        """生成验证码并存入缓存"""
        code = ''.join(random.choice('0123456789') for _ in range(length))
        cache_key = f'captcha:{code_type}:{identifier}'
        cache.set(cache_key, code, expire)
        return code

    @staticmethod
    def verify_code(identifier, code_type, code):
        """验证验证码"""
        cache_key = f'captcha:{code_type}:{identifier}'
        stored_code = cache.get(cache_key)
        if not stored_code:
            return False, '验证码已过期'
        if stored_code != code:
            return False, '验证码错误'
        cache.delete(cache_key)
        return True, '验证成功'

    @staticmethod
    def generate_image_captcha_1():
        key = CaptchaStore.generate_key()
        captcha = CaptchaStore.objects.get(hashkey=key)
        # 获取实际验证码内容（转换为小写）
        actual_code = captcha.response.lower()

        logger.info(f'Generated captcha with key: {key}')
        logger.info(f'actual_code: {actual_code}')

        # 存储图片验证码到redis
        cache.set(f'captcha:{key}', actual_code, settings.CAPTCHA_TIMEOUT) #5分种过期

        return key, captcha_image_url(key)

    @staticmethod
    def generate_image_captcha(width=160, height=43, length=4):
        """生成图形验证码"""
        # 生成随机字符（排除易混淆字符）
        # chars = string.ascii_uppercase.replace('O', '').replace('I', '') + \
        #         string.digits.replace('0', '').replace('1', '')
        code = ''.join(random.choices(string.digits, k=length))

        # 创建图片对象
        image = Image.new('RGB', (width, height), (166, 225, 230))
        draw = ImageDraw.Draw(image)

        # 使用随机字体
        try:
            font = ImageFont.truetype(settings.CAPTCHA_FONT_PATH, settings.CAPTCHA_FONT_SIZE)
        except Exception as e:
            logger.error(f'Failed to load font: {e}')
            font = ImageFont.load_default()

        # 绘制验证码字符
        x = 10
        for char in code:
            # 随机字符颜色
            fill = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
            # 随机旋转角度
            angle = random.randint(-30, 30)
            # 创建字符图片
            char_image = Image.new('RGBA', (30, 40), (255, 255, 255, 0))
            char_draw = ImageDraw.Draw(char_image)
            char_draw.text((0, 0), char, font=font, fill=fill)
            char_image = char_image.rotate(angle, expand=1)
            # 将字符贴到主图
            image.paste(char_image, (x, 5), char_image)
            x += 30 + random.randint(-5, 5)

        # 添加干扰线
        for _ in range(3):
            start = (random.randint(0, width), random.randint(0, height))
            end = (random.randint(0, width), random.randint(0, height))
            draw.line([start, end], fill=(random.randint(0, 255), 0, 0), width=2)

        # 添加噪点
        for _ in range(100):
            xy = (random.randint(0, width), random.randint(0, height))
            draw.point(xy, fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

        # 生成缓存key
        key = f"{random.getrandbits(64):016x}"

        # 存储到Redis（5分钟有效期）
        cache.set(f'captcha:{key}', code.lower(), settings.CAPTCHA_TIMEOUT)

        # 转换为字节流
        buffer = BytesIO()
        image.save(buffer, 'PNG')
        image_data = buffer.getvalue()

        return key, image_data

    @staticmethod
    def verify_image_captcha(key, code):
        actual_code = cache.get(f'captcha:{key}')
        if not actual_code:
            return False, '验证码已过期'
        if actual_code.lower() != code.lower():
            return False, '验证码错误'
        cache.delete(f'captcha:{key}')
        return True, '验证成功'

    @staticmethod
    def verify_email_code(key, code):
        actual_code = cache.get(f'email_code:{key}')
        if not actual_code:
            return False, '验证码已过期'
        if actual_code.lower() != code.lower():
            return False, '验证码错误'
        cache.delete(f'email_code:{key}')
        return True, '验证成功'

    @staticmethod
    def verify_sms_code(key, code):
        actual_code = cache.get(f'sms_code:{key}')
        if not actual_code:
            return False, '验证码已过期'
        if actual_code.lower() != code.lower():
            return False, '验证码错误'
        cache.delete(f'sms_code:{key}')
        return True, '验证成功'


