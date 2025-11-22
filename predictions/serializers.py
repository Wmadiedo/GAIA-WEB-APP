from rest_framework import serializers
from .models import Dataset, SoilData, Prediction

class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ['id', 'name', 'file', 'file_size', 'rows_count', 'created_at', 'updated_at']
        read_only_fields = ['file_size', 'rows_count', 'created_at', 'updated_at']
    
    def validate_file(self, value):
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("Solo se permiten archivos CSV.")
        
        if value.size > 10 * 1024 * 1024:  # limite de 10 mb.
            raise serializers.ValidationError("El archivo es demasiado grande (máximo 10MB).")
        
        return value

class SoilDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoilData
        fields = ['id', 'nitrogen', 'phosphorus', 'potassium', 'temperature', 
                 'humidity', 'ph', 'rainfall', 'created_at', 'dataset']
        read_only_fields = ['created_at']
    
    def validate(self, data):
        if not (0 <= data.get('nitrogen', 0) <= 500):
            raise serializers.ValidationError({'nitrogen': 'El nitrógeno debe estar entre 0 y 500 mg/kg'})
        if not (0 <= data.get('phosphorus', 0) <= 500):
            raise serializers.ValidationError({'phosphorus': 'El fósforo debe estar entre 0 y 500 mg/kg'})
        if not (0 <= data.get('potassium', 0) <= 500):
            raise serializers.ValidationError({'potassium': 'El potasio debe estar entre 0 y 500 mg/kg'})
        if not (-10 <= data.get('temperature', 0) <= 50):
            raise serializers.ValidationError({'temperature': 'La temperatura debe estar entre -10 y 50°C'})
        if not (0 <= data.get('humidity', 0) <= 100):
            raise serializers.ValidationError({'humidity': 'La humedad debe estar entre 0 y 100%'})
        if not (0 <= data.get('ph', 0) <= 14):
            raise serializers.ValidationError({'ph': 'El pH debe estar entre 0 y 14'})
        if not (0 <= data.get('rainfall', 0) <= 3000):
            raise serializers.ValidationError({'rainfall': 'La precipitación debe estar entre 0 y 10000mm'})
        
        return data

class PredictionSerializer(serializers.ModelSerializer):
    soil_data = SoilDataSerializer(read_only=True)
    
    class Meta:
        model = Prediction
        fields = ['id', 'predicted_crop', 'confidence_score', 'second_crop', 
                 'second_confidence', 'third_crop', 'third_confidence', 
                 'model_version', 'created_at', 'soil_data', 'dataset']
        read_only_fields = ['created_at']

class ManualPredictionSerializer(serializers.Serializer):
    nitrogen = serializers.FloatField(min_value=0, max_value=500)
    phosphorus = serializers.FloatField(min_value=0, max_value=500)
    potassium = serializers.FloatField(min_value=0, max_value=500)
    temperature = serializers.FloatField(min_value=-10, max_value=50)
    humidity = serializers.FloatField(min_value=0, max_value=100)
    ph = serializers.FloatField(min_value=0, max_value=14)
    rainfall = serializers.FloatField(min_value=0, max_value=10000) 