# -*- coding: utf-8 -*-
# @File   :urls.py
# @Time   :2025/4/17 16:36
# @Author :admin


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from .views import (
    MyTokenObtainPairView,
    RegisterView,
    LoginView,
    UserViewSet,
    DepartmentViewSet,
    RoleViewSet,
    LoginlogViewSet,
    OperationlogViewSet,

    UserProfileView,
    ChangePasswordView,
    AvatarUploadView,

    MenuViewSet,
    ProductViewSet
)

from . import views

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'menus', MenuViewSet, basename='menu')
router.register(r'goods', ProductViewSet, basename='product')
router.register(r'loginlogs', LoginlogViewSet, basename='loginlog')
router.register(r'operationlogs', OperationlogViewSet, basename='operationlog')

app_name = 'user'

urlpatterns = [

    path('api/captcha/', views.CaptchaView.as_view(), name='captcha'),
    path('api/verify-captcha/', views.VerifyCaptchaView.as_view(), name='verify-captcha'),

    path('api/email-code/', views.EmailCodeView.as_view(), name='email-code'),
    path('api/verify-email-code/', views.VerifyEmailCodeView.as_view(), name='verify-email-code'),

    path('api/sms-code/', views.SMSCodeView.as_view(), name='sms-code'),
    path('api/verify-sms-code/', views.VerifySMSCodeView.as_view(), name='verify-sms-code'),

    path('api/send-captcha/', views.SendCaptchaView.as_view(), name='send-captcha'),
    path('api/auth/register/', RegisterView.as_view(), name='auth_register'),
    path('api/login-attempts/', views.LoginAttemptsView.as_view(), name='login-attempts'),
    path('api/auth/login/', LoginView.as_view(), name='auth_login'),
    path('api/auth/obtain/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('api/profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/change/password/', ChangePasswordView.as_view(), name='change-password'),
    path('api/upload/avatar/', AvatarUploadView.as_view(), name='upload-avatar'),

    path('api/menus/dynamic/', MenuViewSet.as_view({'get': 'dynamic'}), name='menus-dynamic'),
    path('api/goods/amount/list/', ProductViewSet.as_view({'get': 'amount'}), name='goods-amount'),
    path('api/goods/category/count/', ProductViewSet.as_view({'get': 'category_count'}), name='goods-category-count'),
    path('api/goods/category/sale/', ProductViewSet.as_view({'get': 'category_sale'}), name='goods-category-sale'),
    path('api/goods/category/favor/', ProductViewSet.as_view({'get': 'category_favor'}), name='goods-category-favor'),
    path('api/goods/address/sale/', ProductViewSet.as_view({'get': 'address_sale'}), name='goods-address-sale'),
    path('api/', include(router.urls)),
]
