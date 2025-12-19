# -*- coding: utf-8 -*-
# @File   :convert_encoding.py
# @Time   :2025/6/4 14:19
# @Author :admin

# convert_encoding.py
import sys

input_file = 'datadump.json'
output_file = 'datadump_utf8.json'

with open(input_file, 'r', encoding='iso-8859-1') as f_in:
    content = f_in.read()

with open(output_file, 'w', encoding='utf-8') as f_out:
    f_out.write(content)

print("✅ 文件已成功转换为 UTF-8 编码")