from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import os
def upload_to(instance,filename):
    return f'datasets/user_{instance.user.id}/{filename}'

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
    # Rangos normales para alertas
    NORMAL_RANGES = {
        'nitrogen': (0, 140),
        'phosphorus': (5, 145),
        'potassium': (5, 205),
        'temperature': (8, 44),
        'humidity': (14, 100),
        'ph': (3.5, 9.5),
        'rainfall': (20, 300)
    }

    class Meta:
        ordering = ['-created_at']
        verbose_name= 'Dato de Suelo'
        verbose_name_plural= 'Datos de Suelo'

    def __str__(self):
        return f"Soil Data - {self.user.username} - ({self.created_at.strftime('%Y-%m-%d')})"

    def get_alerts(self):
        """Retorna una lista de alertas para valores fuera de rango"""
        alerts = []
        
        checks = {
            'nitrogen': (self.nitrogen, 'Nitrógeno'),
            'phosphorus': (self.phosphorus, 'Fósforo'),
            'potassium': (self.potassium, 'Potasio'),
            'temperature': (self.temperature, 'Temperatura'),
            'humidity': (self.humidity, 'Humedad'),
            'ph': (self.ph, 'pH'),
            'rainfall': (self.rainfall, 'Lluvia')
        }
        
        for key, (value, name) in checks.items():
            min_val, max_val = self.NORMAL_RANGES[key]
            if value < min_val:
                alerts.append({
                    'type': 'danger',
                    'parameter': name,
                    'message': f'{name} muy bajo: {value} (mínimo recomendado: {min_val})'
                })
            elif value > max_val:
                alerts.append({
                    'type': 'danger',
                    'parameter': name,
                    'message': f'{name} muy alto: {value} (máximo recomendado: {max_val})'
                })
        
        return alerts



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
        return f"Prediction - {self.predicted_crop} -{self.confidence_score}% ({self.user.username})"
