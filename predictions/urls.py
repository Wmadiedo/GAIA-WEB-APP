from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'datasets', views.DatasetViewSet, basename='dataset')
router.register(r'soil-data', views.SoilDataViewSet, basename='soildata')
router.register(r'predictions', views.PredictionViewSet, basename='prediction')

urlpatterns = [
    path('', include(router.urls)),
    path('upload/', views.upload_csv, name='upload_csv'),
    path('predict/manual/', views.predict_manual, name='predict_manual'),
    path('predict/csv/<int:dataset_id>/', views.predict_csv, name='predict_csv'),
    path('dashboard/', views.dashboard_stats, name='dashboard_stats'),
    path('crop-info/<str:crop_name>/', views.crop_info, name='crop_info'),
]
