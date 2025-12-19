# -*- coding: utf-8 -*-
# @File   :test_login.py
# @Time   :2025/6/4 10:52
# @Author :admin


import requests
# from django.test import Client
# client = Client()
# response = client.login(username='root', password='qweasdzxc8899')
# print("Login success:", response)  # 应输出 True


import json

# 读取原始文件
with open('datadump.json', 'rb') as f:
    data = f.read().decode('utf-8', errors='replace')  # 自动替换非法字符

# 重新写入
with open('datadump_fixed.json', 'w', encoding='utf-8') as f:
    json.dump(json.loads(data), f, ensure_ascii=False, indent=2)