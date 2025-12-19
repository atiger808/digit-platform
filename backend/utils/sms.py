# -*- coding: utf-8 -*-
# @File   :utils.py
# @Time   :2025/5/8 14:27
# @Author :admin
# utils/sms.py

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import random
from django.conf import settings

def send_sms(phone, code):
    client = AcsClient(
        settings.SMS_CONFIG['ACCESS_KEY_ID'],
        settings.SMS_CONFIG['ACCESS_KEY_SECRET'],
        settings.SMS_CONFIG['REGION']
    )

    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')

    request.add_query_param('PhoneNumbers', phone)
    request.add_query_param('SignName', settings.SMS_CONFIG['SIGN_NAME'])
    request.add_query_param('TemplateCode', settings.SMS_CONFIG['TEMPLATE_CODE'])
    request.add_query_param('TemplateParam', f'{{"code":"{code}"}}')

    response = client.do_action_with_exception(request)
    return response