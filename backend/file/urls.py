# -*- coding: utf-8 -*-
# @File   :urls.py
# @Time   :2025/4/29 14:09
# @Author :admin


from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'file'

router = DefaultRouter()

router.register('files', views.UserFilesViewSet, basename='user_files')

urlpatterns = [
    path('api/upload/init/', views.InitUploadView.as_view(), name='init_upload'),
    path('api/upload/chunk/', views.UploadChunkView.as_view(), name='upload_chunk'),
    path('api/upload/complete/', views.CompleteUploadView.as_view(), name='upload_complete'),
    path('api/multifile/upload/', views.MultiFileUploadView.as_view(), name='multifile_upload'),

    path('api/download/<int:file_id>/download/', views.ChunkedFileDownloadView.as_view(), name='file_download'),
    path('api/download/<int:file_id>/download-start/', views.FileDownloadStatusView.as_view(),
         name='file_download_start'),
    path('api/download/<int:file_id>/download-complete/', views.FileDownloadStatusView.as_view(),
         name='file_download_complete'),
    path('api/download/<int:file_id>/download-cancel/', views.FileDownloadStatusView.as_view(),
         name='file_download_cancel'),

    path('api/dashboard/user_stats_by_time/', views.UserStatsByTimeView.as_view(), name='user-stats-by-time'),
    path('api/dashboard/summary/', views.DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('api/users/online/', views.OnlineUsersView.as_view(), name='online-users'),
    path('api/user-files/user_video_stats/', views.UserFilesViewSet.as_view({'get': 'user_video_stats'}),
         name='user-video-stats'),

    path('files/summary/', views.UserFilesViewSet.as_view({'get': 'files_summary'}), name='files-summary'),

    path('api/', views.UserFilesViewSet.as_view({'patch': 'edit'}), name='edit'),
    path('api/', views.UserFilesViewSet.as_view({'get': 'custom_retrieve'}), name='custom_retrieve'),
    path('api/', include(router.urls))
]
