from django.contrib import admin

from .models import DyvpnDeviceModel, DyvpnRegionModel, DyvpnAccount, DyvpnMonitor

@admin.register(DyvpnDeviceModel)
class DyvpnDeviceModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'device_name', 'device_number', 'device_type', 'mac_address', 'used', 'update_time', 'create_time')
    list_filter = ('used', 'device_type')
    list_per_page = 20

@admin.register(DyvpnRegionModel)
class DyvpnRegionModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'region', 'region_code', 'used', 'online_num', 'device_count', 'update_time', 'create_time')
    list_filter = ('used', )
    list_per_page = 20

@admin.register(DyvpnAccount)
class DyvpnAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'vpn_account', 'region', 'online', 'used', 'is_delete', 'expire_time', 'update_time', 'create_time')
    list_filter = ('is_delete', 'used', 'online')
    search_fields = ('vpn_account', 'nickname')
    list_per_page = 20



@admin.register(DyvpnMonitor)
class DyvpnMonitorAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'virtual_ip', 'duration_secs', 'online_time', 'traffic_vol_bytes', 'traffic_vol_flow', 'update_time', 'login_time', 'logout_time')
    list_filter = ('region', )
    search_fields = ('account', 'region')
    list_per_page = 20