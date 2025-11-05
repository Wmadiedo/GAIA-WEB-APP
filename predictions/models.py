from django.db import models
from django.conf import settings
import os

def upload_to(instance, filename):
    return f'datasets/{instance.user.id}/{filename}'

class Dataset(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='datasets')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=upload_to)
    file_size = models.PositiveIntegerField()
    rows_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Dataset'
        verbose_name_plural = 'Datasets'
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    def delete(self, *args, **kwargs):
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)

class SoilData(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='soil_data')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, null=True, blank=True, related_name='soil_records')
    
    nitrogen = models.FloatField(verbose_name='Nitrógeno (N)')
    phosphorus = models.FloatField(verbose_name='Fósforo (P)')
    potassium = models.FloatField(verbose_name='Potasio (K)')
    temperature = models.FloatField(verbose_name='Temperatura (°C)')
    humidity = models.FloatField(verbose_name='Humedad (%)')
    ph = models.FloatField(verbose_name='pH del Suelo')
    rainfall = models.FloatField(verbose_name='Precipitación (mm)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Dato de Suelo'
        verbose_name_plural = 'Datos de Suelo'
    
    def __str__(self):
        return f"Soil Data - {self.user.username} ({self.created_at.strftime('%Y-%m-%d')})"

class Prediction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='predictions')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, null=True, blank=True, related_name='predictions')
    soil_data = models.ForeignKey(SoilData, on_delete=models.CASCADE, related_name='predictions')
    
    predicted_crop = models.CharField(max_length=100, verbose_name='Cultivo Predicho')
    confidence_score = models.FloatField(verbose_name='Confianza (%)')
    model_version = models.CharField(max_length=50, default='1.0', verbose_name='Versión del Modelo')
    
    second_crop = models.CharField(max_length=100, null=True, blank=True, verbose_name='Segunda Opción')
    second_confidence = models.FloatField(null=True, blank=True, verbose_name='Confianza 2da Opción')
    third_crop = models.CharField(max_length=100, null=True, blank=True, verbose_name='Tercera Opción')
    third_confidence = models.FloatField(null=True, blank=True, verbose_name='Confianza 3ra Opción')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Predicción'
        verbose_name_plural = 'Predicciones'
    
    def __str__(self):
        return f"{self.predicted_crop} - {self.confidence_score}% ({self.user.username})"
