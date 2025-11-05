from django.contrib import admin
from .models import Dataset, SoilData, Prediction

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'rows_count', 'file_size', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'user__username', 'user__email']
    readonly_fields = ['file_size', 'rows_count', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

@admin.register(SoilData)
class SoilDataAdmin(admin.ModelAdmin):
    list_display = ['user', 'nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall', 'created_at']
    list_filter = ['created_at', 'user', 'dataset']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['user', 'predicted_crop', 'confidence_score', 'model_version', 'created_at']
    list_filter = ['predicted_crop', 'created_at', 'user', 'model_version']
    search_fields = ['user__username', 'user__email', 'predicted_crop']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'