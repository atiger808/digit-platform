from django.apps import AppConfig


class FileConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'file'

    # def ready(self):
    #     # 导入并初始化 MIME 类型
    #     import backend.file.mime_types  # noqa
