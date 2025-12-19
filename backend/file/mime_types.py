# -*- coding: utf-8 -*-
# @File   :mime_types.py
# @Time   :2025/7/2 18:21
# @Author :admin


# 添加一些常见的 MIME 类型映射
import mimetypes

mimetypes.add_type('application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.docx')
mimetypes.add_type('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '.xlsx')
mimetypes.add_type('application/vnd.ms-excel.sheet.macroEnabled.12', '.xlsm')
mimetypes.add_type('application/vnd.ms-powerpoint', '.ppt')
mimetypes.add_type('application/vnd.openxmlformats-officedocument.presentationml.presentation', '.pptx')
mimetypes.add_type('application/zip', '.zip')
mimetypes.add_type('application/x-rar-compressed', '.rar')
mimetypes.add_type('application/x-7z-compressed', '.7z')