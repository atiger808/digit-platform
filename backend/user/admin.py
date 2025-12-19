from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Department, Role, Menu, Product, Profile, LoginLog, OperationLog

class CustomUserAdmin(UserAdmin):
    list_display = (
    'id', 'username', 'real_name', 'email', 'mobile', 'department', 'is_active', 'is_staff', 'last_login_time', 'last_login', 'create_time')
    list_filter = ('is_active', 'is_staff', 'department')
    search_fields = ('username', 'real_name', 'email', 'mobile')
    filter_horizontal = ('roles', 'groups', 'user_permissions')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('real_name', 'avatar', 'gender', 'email', 'mobile', 'department')}),
        ('权限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'roles', 'groups', 'user_permissions')}),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
    )
    list_per_page = 20


class CustomMenuAdmin(admin.ModelAdmin):
    list_display = (
    'id', 'name', 'parent', 'type', 'sort', 'status', 'permission', 'icon', 'path', 'create_time')
    list_filter = ['type', 'status']
    search_fields = ('name', 'code')
    list_per_page = 20

class CustomRoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'status', 'create_time')
    list_filter = ['status']
    search_fields = ('name', 'code')
    list_per_page = 20

class CustomDepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'status', 'create_time')
    list_filter = ['status']
    search_fields = ('name', 'code')
    list_per_page = 20

class CustomLoginLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'ip', 'agent', 'browser', 'os', 'login_type', 'create_time')
    list_filter = ['login_type', 'os', 'browser']
    search_fields = ('username', 'ip')
    list_per_page = 20

class CustomOperationLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'request_modular', 'creator', 'request_path', 'request_method', 'request_ip', 'request_browser', 'response_code', 'request_os', 'status', 'create_time')
    list_filter = ['request_os', 'request_method', 'status', 'response_code', 'request_browser']
    search_fields = ('request_path', 'request_ip', 'request_modular')
    list_per_page = 20

admin.site.register(User, CustomUserAdmin)
admin.site.register(Menu, CustomMenuAdmin)
admin.site.register(Department, CustomDepartmentAdmin)
admin.site.register(Role, CustomRoleAdmin)

admin.site.register(Product)
admin.site.register(Profile)

admin.site.register(LoginLog, CustomLoginLogAdmin)
admin.site.register(OperationLog, CustomOperationLogAdmin)