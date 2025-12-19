from django.contrib import admin

from .models import UploadedFile, UserFileAccess, DownloadRecord, FileTag

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'upload_id', 'filename', 'ext', 'download_count', 'file_size', 'uploaded_chunks', 'total_chunks', 'file', 'completed', 'update_time', 'create_time')
    list_per_page = 20

@admin.register(UserFileAccess)
class UserFileAccessAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'original_filename', 'os', 'update_time', 'create_time')
    list_per_page = 20

@admin.register(DownloadRecord)
class DownloadRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'original_filename', 'ip_address', 'user_agent', 'status', 'create_time')
    list_per_page = 20


@admin.register(FileTag)
class FileTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'created_at')
    list_per_page = 20