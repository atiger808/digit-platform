# -*- coding: utf-8 -*-
# @File   :remove_bom.py
# @Time   :2025/6/4 14:40
# @Author :admin


import sys

input_file = 'datadump_utf8.json'
output_file = 'datadump_utf8_nobom.json'

with open(input_file, 'r', encoding='utf-8-sig') as f_in:
    content = f_in.read()

with open(output_file, 'w', encoding='utf-8') as f_out:
    f_out.write(content)