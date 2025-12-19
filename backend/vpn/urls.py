# -*- coding: utf-8 -*-
# @File   :urls.py
# @Time   :2025/5/26 17:04
# @Author :admin

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'vpn'

router = DefaultRouter()
router.register(r'vpnaccounts', views.VpnAccountViewSet, basename='vpnaccount')
router.register(r'vpnmonitors', views.VpnMonitorViewSet, basename='vpnmonitor')
router.register(r'vpndevices', views.VpnDeviceViewSet, basename='vpndevice')
router.register(r'vpnregions', views.VpnRegionViewSet, basename='vpnregion')

urlpatterns = [
    path('api/vpn-regions/', views.ApiVPNRegionView.as_view(), name='vpn-region'),
    path('api/vpn-accounts/', views.ApiCreateVPNAccountView.as_view(), name='create-vpn-account'),
    path('api/vpn-accounts/<str:vpn_account>/', views.ApiUpdateVPNAccountView.as_view(), name='update-vpn-account'),
    path('api/vpn-accounts/<str:vpn_account>/detail/', views.ApiVPNAccountDetailView.as_view(), name='vpn-account-detail'),
    path('vpnaccounts/region/summary/', views.VpnAccountViewSet.as_view({'get': 'region_summary'}), name='vpnaccounts-region-summary'),
    path('vpnmonitors/region/summary/', views.VpnMonitorViewSet.as_view({'get': 'region_summary'}), name='vpnmonitors-region-summary'),
    path('', include(router.urls))
]
